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

from typing import List, Optional

from rich.text import Text
from textual.message import Message
from textual.widgets import DataTable

from mjobs.models import SlurmJob


class JobsTable(DataTable):
    """Interactive jobs table widget."""

    class RowSelected(Message):
        """Message sent when a row is selected."""

        def __init__(self, job: SlurmJob):
            super().__init__()
            self.job = job

    BINDINGS = [
        ("enter", "select_row", "Show Details"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
    ]

    def __init__(self, jobs: List[SlurmJob] = None, **kwargs):
        super().__init__(**kwargs)
        self.jobs = jobs or []
        self.filtered_jobs = self.jobs.copy()
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.show_header = True
        self.show_row_labels = False

    def status_style(self, job_state: str) -> Text:
        """Apply the same status colors as the CLI version.

        :param job_state: The job state to style
        :return: Rich Text object with styling applied
        """
        colours = {
            "RUNNING": "bold green",
            "PENDING": "dark_orange",
            "COMPLETED": "honeydew2",
            "FAILED": "red",
        }
        return Text(job_state, style=colours.get(job_state, "grey93"))

    def populate_table(self, jobs: List[SlurmJob]):
        """Populate the table with job data.

        :param jobs: List of SlurmJob namedtuples to display
        """
        self.jobs = jobs
        self.filtered_jobs = jobs.copy()
        self.clear()

        # Add columns only if they don't exist
        if not self.columns:
            self.add_columns(
                "JobId",
                "Status",
                "JobName",
                "User",
                "Partition",
                "Submit Time",
                "Start Time",
                "Time Rem.",
                "State Reason",
            )

        # Add rows
        for job in self.filtered_jobs:
            self.add_row(
                job.job_id,
                self.status_style(job.job_state),
                job.job_name,
                job.user_name,
                job.partition,
                job.submit_time,
                job.start_time,
                job.end_time,
                job.state_reason,
                key=job.job_id,
            )

    def filter_jobs(self, search_text: str):
        """Filter jobs based on search text.

        :param search_text: Text to filter jobs by (searches job name, state, user, command)
        """
        if not search_text:
            self.filtered_jobs = self.jobs.copy()
        else:
            self.filtered_jobs = [
                job
                for job in self.jobs
                if (
                    search_text.lower() in job.job_name.lower()
                    or search_text.lower() in job.job_state.lower()
                    or search_text.lower() in job.user_name.lower()
                    or search_text.lower() in job.command.lower()
                )
            ]

        # Clear rows but keep columns
        self.clear(columns=False)

        # Add rows
        for job in self.filtered_jobs:
            self.add_row(
                job.job_id,
                self.status_style(job.job_state),
                job.job_name,
                job.user_name,
                job.partition,
                job.submit_time,
                job.start_time,
                job.end_time,
                job.state_reason,
                key=job.job_id,
            )

    def get_selected_job(self) -> Optional[SlurmJob]:
        """Get the currently selected job.

        :return: Selected SlurmJob namedtuple or None if no selection
        """
        if self.cursor_row >= 0 and self.cursor_row < len(self.filtered_jobs):
            return self.filtered_jobs[self.cursor_row]
        return None

    def action_select_row(self):
        """Handle row selection."""
        # Post message to parent to handle job details
        selected_job = self.get_selected_job()
        if selected_job:
            self.post_message(self.RowSelected(selected_job))
