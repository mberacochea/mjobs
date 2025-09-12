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

from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator


class SlurmJob(BaseModel):
    """Pydantic model for Slurm job data with validation and type safety.

    This replaces the namedtuple approach with a proper data model that provides:
    - Type validation
    - Field validation
    - Serialization/deserialization
    - Better error messages
    """

    job_id: str = Field(..., description="Job ID")
    job_name: str = Field(..., description="Job name")
    time_limit: str = Field(..., description="Time limit (format: days-hours:minutes:seconds)")
    memory: str = Field(..., description="Memory requirement")
    partition: str = Field(..., description="Partition name")
    job_state: str = Field(..., description="Job state")
    user_name: str = Field(..., description="User name")
    command: str = Field(..., description="Command to execute")
    state_reason: str = Field(..., description="Reason for job state")
    start_time: str = Field(..., description="Job start time")
    submit_time: str = Field(..., description="Job submission time")
    end_time: str = Field(..., description="Job end time or time remaining")
    workdir: str = Field(..., description="Working directory")
    nodes: str = Field(..., description="Allocated nodes")

    @field_validator("job_id")
    @classmethod
    def validate_job_id(cls, v: str) -> str:
        """Validate job ID is not empty."""
        if not v or v.strip() == "":
            raise ValueError("Job ID cannot be empty")
        return v.strip()

    @field_validator("job_state")
    @classmethod
    def validate_job_state(cls, v: str) -> str:
        """Validate and normalize job state."""
        valid_states = {
            "PENDING",
            "RUNNING",
            "SUSPENDED",
            "COMPLETED",
            "CANCELLED",
            "FAILED",
            "TIMEOUT",
            "NODE_FAIL",
            "PREEMPTED",
            "BOOT_FAIL",
            "DEADLINE",
            "OUT_OF_MEMORY",
        }
        normalized_state = v.upper().strip()
        if normalized_state not in valid_states:
            # Don't fail validation for unknown states, just normalize
            pass
        return normalized_state

    @field_validator("user_name", "job_name", "partition")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Ensure critical string fields are not empty."""
        if not v or v.strip() == "":
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("nodes")
    @classmethod
    def validate_nodes(cls, v: str) -> str:
        """Handle empty nodes field for non-running jobs."""
        return v.strip() if v and v.strip() not in ["", "-----", "None"] else "N/A"

    @classmethod
    def from_squeue_line(cls, line: str, field_count: int) -> "SlurmJob":
        """Create SlurmJob from squeue output line with robust parsing.

        :param line: Raw line from squeue output
        :param field_count: Expected number of fields
        :return: SlurmJob instance
        :raises ValueError: If line cannot be parsed
        """
        if not line or line.strip() == "":
            raise ValueError("Cannot parse empty line")

        try:
            # Parse the pipe-separated values, handling quoted strings
            values = [element.strip() for element in line.strip('"').split("|")]

            # Handle missing nodes field for non-running jobs
            if len(values) == field_count - 1:
                values.append("-----")
            elif len(values) != field_count:
                raise ValueError(f"Expected {field_count} fields, got {len(values)}")

            # Create the job with proper field mapping
            return cls(
                job_id=values[0],
                job_name=values[1],
                time_limit=values[2],
                memory=values[3],
                partition=values[4],
                job_state=values[5],
                user_name=values[6],
                command=values[7],
                state_reason=values[8],
                start_time=values[9],
                submit_time=values[10],
                end_time=values[11],
                workdir=values[12],
                nodes=values[13] if len(values) > 13 else "N/A",
            )

        except (IndexError, TypeError) as e:
            raise ValueError(f"Failed to parse squeue line: {line}. Error: {e}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SlurmJob":
        """Create SlurmJob from dictionary (useful for test data).

        :param data: Dictionary with job data
        :return: SlurmJob instance
        """
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        :return: Dictionary representation of the job
        """
        return self.model_dump()

    def to_table_row(self) -> Dict[str, str]:
        """Convert to dictionary suitable for table display.

        :return: Dictionary with formatted fields for table display
        """
        return {
            "JobId": self.job_id,
            "Status": self.job_state,
            "JobName": self.job_name,
            "User": self.user_name,
            "Partition": self.partition,
            "Submit Time": self.submit_time,
            "Start Time": self.start_time,
            "Time Rem.": self.end_time,
            "State Reason": self.state_reason,
        }


# Field mapping for squeue output - matches the order in slurm.py
SQUEUE_FIELDS = [
    ("%.18i", "job_id"),
    ("%.200j", "job_name"),
    ("%l", "time_limit"),
    ("%m", "memory"),
    ("%.50P", "partition"),
    ("%T", "job_state"),
    ("%u", "user_name"),
    ("%.200o", "command"),
    ("%.20r", "state_reason"),
    ("%S", "start_time"),
    ("%V", "submit_time"),
    ("%L", "end_time"),
    ("%.100Z", "workdir"),
    ("%.N", "nodes"),
]
