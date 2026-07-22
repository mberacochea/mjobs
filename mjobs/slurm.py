#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-2024 - Martin Beracochea
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

import getpass
import re
import sys
from datetime import datetime
from subprocess import CalledProcessError, check_output
from types import SimpleNamespace
from typing import Any, Dict, Optional

from rich.console import Console
from rich.text import Text

from mjobs.base import Base
from mjobs.data import JobRepository


class Slurm(Base):
    def __init__(self, console: Console, error_console: Console, job_repository: Optional[JobRepository] = None):
        super().__init__(console, error_console)
        self.job_repository = job_repository

    def status_style(self, job_state) -> Text:
        colours = {
            "RUNNING": "bold green",
            "PENDING": "dark_orange",
            "COMPLETED": "honeydew2",
            "FAILED": "red",
        }
        return Text(job_state, style=colours.get(job_state, "grey93"))

    def run(self, **kwargs):
        args_dict = dict(kwargs)
        args_dict["job_id"] = args_dict.pop("job_ids", ())
        self.args = SimpleNamespace(**args_dict)

        if self.args.dashboard:
            from mjobs.dashboard import launch_dashboard

            launch_dashboard(self)
            return

        jobs = []
        extra_args = []

        if self.args.user:
            extra_args.extend(["-u", self.args.user])
        if self.args.partition:
            extra_args.extend(["-p", self.args.partition])
        for state in self.args.states or []:
            extra_args.extend(["-t", state])
        for node in self.args.nodelist or []:
            extra_args.extend(["-w", node])

        try:
            status = self.console.status("Getting jobs from Slurm...")
            if not self.args.tsv:
                status.start()

            jobs = self.get_jobs(self.args.job_id, extra_args)

            if not self.args.tsv:
                status.stop()

        except CalledProcessError:
            if not self.args.tsv:
                status.stop()
            sys.exit(1)
        except Exception:
            if not self.args.tsv:
                status.stop()
            self.console.print_exception()

        if self.args.filter:
            filter_regex = re.compile(self.args.filter)
            jobs = list(
                filter(
                    lambda j: filter_regex.search(j.job_name) or filter_regex.search(j.command),
                    jobs,
                )
            )

        if self.args.kill:
            if not jobs:
                self.console.print(Text("No jobs to kill."))
                return
            if not self.args.filter and not self.args.job_id:
                self.console.print(Text("Are you sure? This will kill all listed jobs.", style="bold yellow"))
                answer = self.console.input(f"Type [bold yellow]'yes'[/] to confirm ([bold cyan]{len(jobs)}[/] jobs): ")
                if answer.strip().lower() != "yes":
                    self.console.print(Text("Aborted."))
                    return
            self.console.print(Text(f"Cancelling {len(jobs)} job(s)..."), style="bold white")
            killed = 0
            failed = 0
            for job in jobs:
                try:
                    self.kill_job(job.job_id)
                    self.console.print(f"  {job.job_id} {job.job_name}: cancelled")
                    killed += 1
                except CalledProcessError:
                    self.error_console.print(Text(f"  {job.job_id} {job.job_name}: failed"), style="bold red")
                    failed += 1
            self.console.print(Text(f"Done. Killed: {killed}, Failed: {failed}"))
            return

        if not jobs:
            self.console.print(Text("No jobs.", style="bold white", justify="left"))
            sys.exit(0)

        title = f"Slurm jobs for {self.args.user or getpass.getuser()}"
        if self.args.partition:
            title += f" on partition {self.args.partition}"
        if self.args.nodelist:
            title += f" running on hosts {self.args.nodelist}"

        cols = [
            {"header": "JobId", "justify": "right"},
            {"header": "Status"},
            {"header": "JobName", "overflow": "fold"},
            {"header": "User"},
            {"header": "Partition"},
            {"header": "Submit Time"},
            {"header": "Start Time"},
            {"header": "Time rem."},
            {"header": "Status reason"},
        ]
        if self.args.extended:
            cols.append({"header": "WorkDir"})
            cols.append({"header": "Nodes"})

        rows = []

        for job in sorted(jobs, key=lambda j: j.job_id):
            job_name = Text(job.job_name)
            if self.args.filter:
                job_name.highlight_regex(rf"{self.args.filter}", "bold red")

            row = [
                job.job_id,
                self.status_style(job.job_state),
                job_name,
                job.user_name,
                job.partition,
                self.parse_timestamp_str(job.submit_time),
                self.parse_timestamp_str(job.start_time),
                job.end_time,
                job.state_reason,
            ]
            if self.args.extended:
                row.extend(
                    [
                        job.workdir,
                        Text(job.nodes, overflow="fold"),
                    ]
                )
            rows.append(row)

        self.render(title=title, columns=cols, rows=rows)

    def get_jobs(self, job_ids: Optional[list[int]] = None, args: Optional[list[str]] = None):
        if not self.job_repository:
            raise ValueError("No job repository configured. This should not happen in the new architecture.")

        return self.job_repository.get_jobs(job_ids, args)

    def parse_timestamp_str(self, timestamp: Optional[str]) -> str:
        if timestamp is None:
            return f"Invalid timestamp. {timestamp}"
        try:
            dt_object = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            return str(dt_object)
        except (TypeError, ValueError):
            return f"Invalid timestamp. {timestamp}"

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        if not self.job_repository:
            raise ValueError("No job repository configured. This should not happen in the new architecture.")

        return self.job_repository.get_job_details(job_id)

    def kill_job(self, job_id: str) -> str:
        args = ["scancel", str(job_id)]
        return check_output(args, universal_newlines=True)
