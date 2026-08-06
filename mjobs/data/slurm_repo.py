#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2024 - Martin Beracochea
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from subprocess import CalledProcessError, check_output
from typing import Any, Dict, List, Optional

from rich.console import Console

from mjobs.models import SQUEUE_FIELDS, SlurmJob

from mjobs.data.repository import JobRepository, JobRepositoryError

SQUEUE_DELIMITER = "\x1f"


class SlurmRepository(JobRepository):
    """Repository for accessing real Slurm job data via squeue/scontrol commands.

    This implementation calls actual Slurm commands to retrieve job information,
    with robust error handling and parsing.
    """

    def __init__(self, console: Console, error_console: Console):
        """Initialize the Slurm repository.

        :param console: Rich console for output
        :param error_console: Rich console for error output
        """
        self.console = console
        self.error_console = error_console

    def get_jobs(
        self,
        job_ids: Optional[List[int]] = None,
        extra_args: Optional[List[str]] = None,
        full_fields: bool = False,
    ) -> List[SlurmJob]:
        """Retrieve jobs from Slurm using squeue command.

        :param job_ids: Specific job IDs to fetch (optional)
        :param extra_args: Additional squeue arguments (optional)
        :param full_fields: Request fields without scheduler-side truncation (optional)
        :return: List of SlurmJob instances
        :raises JobRepositoryError: If squeue command fails or parsing fails
        """
        try:
            squeue_cmd = self._build_squeue_command(job_ids, extra_args, full_fields=full_fields)

            # Execute squeue command
            squeue_output = check_output(squeue_cmd, universal_newlines=True)

            # Parse output into jobs
            delimiter = SQUEUE_DELIMITER if full_fields else "|"
            return self._parse_squeue_output(squeue_output, delimiter=delimiter)

        except CalledProcessError as e:
            raise JobRepositoryError(f"squeue command failed with exit code {e.returncode}: {e}", original_error=e)
        except Exception as e:
            raise JobRepositoryError(f"Failed to retrieve jobs: {e}", original_error=e)

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Get detailed job information using scontrol show job.

        :param job_id: The job ID to get details for
        :return: Dictionary containing parsed job details
        :raises JobRepositoryError: If scontrol command fails
        """
        try:
            scontrol_output = check_output(["scontrol", "show", "job", str(job_id)], universal_newlines=True).strip()

            return self._parse_scontrol_output(scontrol_output)

        except CalledProcessError as e:
            # Don't raise for non-existent jobs, return empty dict
            if e.returncode == 1:  # Job not found
                return {}
            raise JobRepositoryError(
                f"scontrol show job {job_id} failed with exit code {e.returncode}: {e}", original_error=e
            )
        except Exception as e:
            raise JobRepositoryError(f"Failed to get job details for {job_id}: {e}", original_error=e)

    def _build_squeue_command(
        self,
        job_ids: Optional[List[int]],
        extra_args: Optional[List[str]],
        full_fields: bool = False,
    ) -> List[str]:
        """Build the squeue command with proper formatting and arguments.

        :param job_ids: Job IDs to include
        :param extra_args: Additional arguments
        :param full_fields: Use the non-truncating squeue format option
        :return: Complete squeue command as list
        """
        # ``--Format`` expects long field names, while these definitions use
        # squeue's printf-style format language. Keep using ``--format`` and
        # remove precision limits when full fields are requested.
        format_specs = [field[0] for field in SQUEUE_FIELDS]
        if full_fields:
            format_specs = [re.sub(r"%\.(?:\d+)?", "%", spec) for spec in format_specs]
        delimiter = SQUEUE_DELIMITER if full_fields else "|"
        format_string = delimiter.join(format_specs)

        squeue = [
            "squeue",
            "-h",  # No header
            "--format",
            f'"{format_string}"',
        ]

        # Add extra arguments (user, partition, state filters, etc.)
        if extra_args:
            squeue.extend(list(map(str, extra_args)))

        # Add specific job IDs if requested
        if job_ids:
            squeue.extend(["-j", ",".join(list(map(str, job_ids)))])

        return squeue

    def _parse_squeue_output(self, output: str, delimiter: str = "|") -> List[SlurmJob]:
        """Parse squeue output into SlurmJob instances with robust error handling.

        :param output: Raw squeue output
        :return: List of parsed SlurmJob instances
        :raises JobRepositoryError: If parsing fails for critical errors
        """
        jobs = []
        failed_lines = []
        expected_field_count = len(SQUEUE_FIELDS)

        for line_num, line in enumerate(output.split("\n"), 1):
            line = line.strip()
            if not line:
                continue

            try:
                job = SlurmJob.from_squeue_line(line, expected_field_count, delimiter=delimiter)
                jobs.append(job)

            except ValueError as e:
                # Log parsing errors but don't fail completely
                failed_lines.append((line_num, line, str(e)))
                self.error_console.log(f"Warning: Failed to parse line {line_num}: {e}")

        # If we have some successful parses but some failures, warn but continue
        if failed_lines and jobs:
            self.error_console.log(f"Warning: Failed to parse {len(failed_lines)} out of {line_num} job lines")

        # If we couldn't parse anything and there was output, that's an error
        elif failed_lines and not jobs and output.strip():
            raise JobRepositoryError(
                f"Could not parse any job data from squeue output. First error: {failed_lines[0][2]}"
            )

        return jobs

    def _parse_scontrol_output(self, output: str) -> Dict[str, Any]:
        """Parse scontrol show job output into a dictionary.

        :param output: Raw scontrol output text
        :return: Dictionary with parsed job details
        """
        details = {}

        # Split the output into key=value pairs
        # scontrol output format: "Key=Value Key2=Value2 ..."
        # Handle multi-line output by joining lines
        text = " ".join(output.split("\n"))

        # Regular expression to match key=value pairs, handling quoted values
        pattern = r"(\w+)=([^\s]+(?:\s+[^\s=]+)*?)(?=\s+\w+=|\s*$)"

        for match in re.finditer(pattern, text):
            key, value = match.groups()

            # Clean up the value
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            details[key] = value

        return details
