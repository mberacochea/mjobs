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

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from mjobs.models import SlurmJob
from mjobs.widgets.clickable_path import create_file_path_display


class JobDetailsPanel(Horizontal):
    """Panel for displaying detailed job information in two columns."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_job = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the three-column layout."""
        yield Static(id="left_panel")
        yield Static(id="middle_panel")
        yield Static(id="right_panel")

    def update_job_details(self, job: SlurmJob, slurm_instance=None):
        """Update the panel with job details.

        :param job: SlurmJob namedtuple to display details for
        :param slurm_instance: Optional Slurm instance to get detailed job information
        """
        self.current_job = job

        # Get enhanced details if available
        if slurm_instance and hasattr(slurm_instance, "get_job_details"):
            # Get detailed information from scontrol
            detailed_info = slurm_instance.get_job_details(job.job_id)
            if detailed_info:
                details = detailed_info
            else:
                # Fallback to basic info if scontrol fails
                details = self._basic_job_details(job)
        else:
            # Fallback to basic job details
            details = self._basic_job_details(job)

        # Format details for three-column display
        left_content, middle_content, right_content = self._format_job_details_three_columns(details)

        # Update all three panels
        left_panel = self.query_one("#left_panel", Static)
        middle_panel = self.query_one("#middle_panel", Static)
        right_panel = self.query_one("#right_panel", Static)

        left_panel.update(left_content)
        middle_panel.update(middle_content)
        right_panel.update(right_content)

    def _basic_job_details(self, job: SlurmJob) -> dict:
        """Basic job details when not using test data.

        :param job: SlurmJob namedtuple
        :return: Dictionary with basic job information
        """
        return {
            "JobId": job.job_id,
            "JobName": job.job_name,
            "JobState": job.job_state,
            "User": job.user_name,
            "Partition": job.partition,
            "Command": job.command,
            "WorkDir": job.workdir,
            "SubmitTime": job.submit_time,
            "StartTime": job.start_time,
            "EndTime": job.end_time,
            "TimeLimit": job.time_limit,
            "Memory": job.memory,
            "Nodes": job.nodes,
            "StateReason": job.state_reason,
        }

    def _format_job_details_three_columns(self, details: dict) -> tuple[str, str, str]:
        """Format job details for three-column display.

        :param details: Dictionary of job details
        :return: Tuple of (left_content, middle_content, right_content) strings
        """
        # Left column: Basic Information and Timing
        basic_info = ["JobId", "JobName", "JobState", "UserId", "User", "Partition", "Account", "QOS"]
        timing_info = [
            "SubmitTime",
            "StartTime",
            "EndTime",
            "TimeLimit",
            "RunTime",
            "EligibleTime",
            "AccrueTime",
            "Deadline",
        ]

        # Middle column: Execution and Resources
        execution_info = ["Command", "WorkDir", "StdIn", "StdOut", "StdErr", "AllocNode:Sid"]
        resource_info = [
            "Memory",
            "NumCPUs",
            "NumNodes",
            "NodeList",
            "MinMemoryNode",
            "MinCPUsNode",
            "MinTmpDiskNode",
            "ReqTRES",
            "AllocTRES",
            "TresPerTask",
            "CPUs/Task",
            "NumTasks",
        ]

        # Right column: Job Control and Other
        job_control = [
            "Priority",
            "Nice",
            "Reason",
            "Dependency",
            "Requeue",
            "Restarts",
            "BatchFlag",
            "Reboot",
            "ExitCode",
            "SuspendTime",
            "SecsPreSuspend",
            "LastSchedEval",
            "Scheduler",
        ]

        advanced_config = [
            "ReqB:S:C:T",
            "Socks/Node",
            "NtasksPerN:B:S:C",
            "CoreSpec",
            "DelayBoot",
            "OverSubscribe",
            "Contiguous",
            "Licenses",
            "Network",
            "MCS_label",
            "GroupId",
            "TimeMin",
        ]

        # Left panel sections
        left_sections = [("Basic Information", basic_info), ("Timing", timing_info)]

        # Middle panel sections
        middle_sections = [("Execution", execution_info), ("Resources", resource_info)]

        # Right panel sections
        right_sections = [
            ("Job Control", job_control),
            (
                "Other",
                [
                    k
                    for k in details.keys()
                    if k
                    not in basic_info + timing_info + execution_info + resource_info + job_control + advanced_config
                ],
            ),
        ]

        # Format left panel
        left_lines = ["[bold white on blue] Job Details [/bold white on blue]", ""]
        for section_name, fields in left_sections:
            if any(field in details for field in fields):
                left_lines.append(f"[bold yellow]{section_name}:[/bold yellow]")
                for field in fields:
                    if field in details:
                        formatted_key = self._format_field_name(field)
                        value = details[field]
                        left_lines.append(f"  [cyan]{formatted_key:16}[/cyan]: {value}")
                left_lines.append("")

        # Format middle panel
        middle_lines = ["[bold white on blue] Execution & Resources [/bold white on blue]", ""]
        for section_name, fields in middle_sections:
            if any(field in details for field in fields):
                middle_lines.append(f"[bold yellow]{section_name}:[/bold yellow]")
                for field in fields:
                    if field in details:
                        formatted_key = self._format_field_name(field)
                        value = details[field]

                        # Make file paths clickable for StdIn, StdOut, StdErr
                        if field in ["StdIn", "StdOut", "StdErr"]:
                            middle_lines.append(create_file_path_display(formatted_key, value))
                        else:
                            middle_lines.append(f"  [cyan]{formatted_key:16}[/cyan]: {value}")
                middle_lines.append("")

        # Format right panel
        right_lines = ["[bold white on blue] Control & Other [/bold white on blue]", ""]
        for section_name, fields in right_sections:
            if any(field in details for field in fields):
                right_lines.append(f"[bold yellow]{section_name}:[/bold yellow]")
                for field in fields:
                    if field in details:
                        formatted_key = self._format_field_name(field)
                        value = details[field]
                        right_lines.append(f"  [cyan]{formatted_key:16}[/cyan]: {value}")
                right_lines.append("")

        return "\n".join(left_lines), "\n".join(middle_lines), "\n".join(right_lines)

    def _format_field_name(self, field: str) -> str:
        """Format field names with proper capitalization.

        :param field: Raw field name from job details
        :return: Properly formatted field name
        """
        # Special cases for proper capitalization
        special_cases = {
            "JobId": "Job ID",
            "JobName": "Job Name",
            "JobState": "Job State",
            "UserId": "User ID",
            "GroupId": "Group ID",
            "SubmitTime": "Submit Time",
            "StartTime": "Start Time",
            "EndTime": "End Time",
            "TimeLimit": "Time Limit",
            "TimeMin": "Time Min",
            "EligibleTime": "Eligible Time",
            "AccrueTime": "Accrue Time",
            "WorkDir": "Work Dir",
            "StdIn": "StdIn",
            "StdOut": "StdOut",
            "StdErr": "StdErr",
            "NumCPUs": "Num CPUs",
            "NumNodes": "Num Nodes",
            "NumTasks": "Num Tasks",
            "CPUs/Task": "CPUs/Task",
            "MinMemoryNode": "Min Memory Node",
            "MinCPUsNode": "Min CPUs Node",
            "MinTmpDiskNode": "Min Tmp Disk Node",
            "ReqTRES": "Req TRES",
            "AllocTRES": "Alloc TRES",
            "TresPerTask": "TRES Per Task",
            "ReqB:S:C:T": "Req B:S:C:T",
            "NtasksPerN:B:S:C": "N tasks Per N:B:S:C",
            "CoreSpec": "Core Spec",
            "DelayBoot": "Delay Boot",
            "OverSubscribe": "Over Subscribe",
            "NodeList": "Node List",
            "BatchHost": "Batch Host",
            "AllocNode:Sid": "Alloc Node:Sid",
            "ReqNodeList": "Req Node List",
            "ExcNodeList": "Exc Node List",
            "LastSchedEval": "Last Sched Eval",
            "SecsPreSuspend": "Secs Pre Suspend",
            "SuspendTime": "Suspend Time",
            "ExitCode": "Exit Code",
            "BatchFlag": "Batch Flag",
            "MCS_label": "MCS Label",
            "QOS": "QOS",
        }

        # Return special case if it exists
        if field in special_cases:
            return special_cases[field]

        # Default: replace underscores and use title case
        return field.replace("_", " ").title()
