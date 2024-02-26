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
import json
import re
import sys
from subprocess import check_output
from typing import Optional

from rich.console import Console
from rich.text import Text

from mjobs.base import Base


class LSF(Base):
    def __init__(self, console: Console, error_console: Console):
        super().__init__(console, error_console)

    def status_style(self, job_entry) -> Text:
        if job_entry["STAT"] == "RUN":
            return Text(job_entry["STAT"], style="bold green")
        elif job_entry["STAT"] == "PEND":
            return Text(job_entry["STAT"], style="dark_orange")
        elif job_entry["STAT"] == "DONE":
            return Text(job_entry["STAT"], style="honeydew2")
        return Text(job_entry["STAT"], style="grey93")

    def get_args(self):
        parser = super().get_args("bjobs")
        parser.add_argument(
            dest="job_id",
            help="Specifies the jobs or job arrays that bjobs displays.",
            nargs="*",
        )
        parser.add_argument(
            "-q",
            dest="queue",
            required=False,
            help="Displays jobs in the specified queue",
        )
        parser.add_argument(
            "-u",
            dest="user",
            required=False,
            help="Displays jobs in the specified user",
        )
        parser.add_argument(
            "-r", dest="run", action="store_true", help="Displays running jobs."
        )
        parser.add_argument(
            "-a",
            dest="all",
            action="store_true",
            help="Displays information about jobs in all states, including jobs that finished recently.",
        )
        parser.add_argument(
            "-d",
            dest="recent",
            action="store_true",
            help="Displays information about jobs that finished recently.",
        )
        parser.add_argument(
            "-G",
            dest="user_group",
            required=False,
            help="Displays jobs associated with the specified user group.",
        )
        parser.add_argument(
            "-g",
            dest="group",
            required=False,
            help="Displays information about jobs attached to the specified job group.",
        )
        parser.add_argument(
            "-m",
            dest="hosts",
            required=False,
            help="Displays jobs dispatched to the specified hosts.",
        )
        parser.add_argument(
            "-p",
            dest="pend",
            action="store_true",
            help=(
                "Displays pending jobs, together with the pending reasons that caused each job "
                "not to be dispatched during the last dispatch turn."
            ),
        )
        parser.add_argument(
            "-e",
            dest="extended",
            action="store_true",
            help="Add the execution hosts, output file and error file to the table.",
        )
        parser.add_argument(
            "--bkill",
            dest="bkill",
            action="store_true",
            help="Terminate found or filtered jobs with bkill.",
        )
        self.args = parser.parse_args()
        return parser

    def parse_bjobs(self, bjobs_output_str):
        """Parse records from bjobs json type output.
        This snippet comes from: https://github.com/DataBiosphere/toil/blob/master/src/toil/batchSystems/lsf.py
        :param bjobs_output_str: stdout of bjobs json type output
        :return: list with the jobs
        """
        bjobs_dict = None
        bjobs_records = None
        # Handle Cannot connect to LSF. Please wait ... type messages
        dict_start = bjobs_output_str.find("{")
        dict_end = bjobs_output_str.rfind("}")
        if dict_start != -1 and dict_end != -1:
            bjobs_output = bjobs_output_str[dict_start : (dict_end + 1)]
            bjobs_dict = json.loads(bjobs_output)
            return bjobs_dict["RECORDS"]
        if bjobs_records is None:
            raise ValueError(f"Could not find bjobs output json in: {bjobs_output_str}")
        return []

    def get_jobs(
        self, job_ids: Optional[list[int]] = None, lsf_args: Optional[list[str]] = None
    ):
        """bjobs command, it uses the json output and includes [stat, name and jobid].
        Any other parameters in lsf_args will be included in the call to bjobs.
        """
        fields = [
            "stat",
            "name",
            "jobid",
            "job_group",
            "user",
            "queue",
            "submit_time",
            "start_time",
            "finish_time",
            "exec_host",
            "command",
            "exit_reason",
            "exit_code",
            "error_file",
            "output_file",
            "pend_reason",
        ]
        args = ["bjobs", "-json", "-o", " ".join(fields)]
        if lsf_args:
            args.extend(list(map(str, lsf_args)))
        if job_ids:
            args.extend(list(map(str, job_ids)))
        bjobs_output = check_output(args, universal_newlines=True)
        jobs = self.parse_bjobs(bjobs_output)
        return jobs

    def bkill(self, job: int) -> None:
        args = ["bkill", str(job)]
        return check_output(args, universal_newlines=True)

    def main(self):
        """Main execution point, should contain all the code to handle the LSF implementation"""

        self.get_args()

        jobs = []
        lsf_args = []

        if self.args.user:
            lsf_args.extend(["-u", self.args.user])
        if self.args.queue:
            lsf_args.extend(["-q", self.args.queue])
        if self.args.run:
            lsf_args.extend(["-r"])
        if self.args.all:
            lsf_args.extend(["-a"])
        if self.args.recent:
            lsf_args.extend(["-d"])
        if self.args.user_group:
            lsf_args.extend(["-G", self.args.user_group])
        if self.args.group:
            lsf_args.extend(["-g", self.args.group])
        if self.args.hosts:
            lsf_args.extend(["-m", self.args.hosts])
        if self.args.pend:
            lsf_args.extend(["-p"])

        try:
            status = self.console.status("Getting jobs from LSF...")
            if not self.args.tsv:
                status.start()

            jobs = self.get_jobs(self.args.job_id, lsf_args)

            if not self.args.tsv:
                status.stop()

        except Exception:
            if not self.args.tsv:
                status.stop()
            self.console.print_exception()

        if self.args.filter:
            filter_regex = re.compile(self.args.filter)
            jobs = list(
                filter(
                    lambda j: filter_regex.search(j["JOB_NAME"])
                    or filter_regex.search(j["PEND_REASON"]),
                    jobs,
                )
            )

        if not jobs:
            self.console.print(Text("No jobs.", style="bold white", justify="left"))
            sys.exit(0)

        title = f"LSF jobs for {self.args.user or getpass.getuser()}"
        if self.args.queue:
            title += f" on queue {self.args.queue}"
        if self.args.hosts:
            title += f" running on hosts {self.args.hosts}"

        cols = [
            {"header": "JobId", "justify": "right"},
            {"header": "Status"},
            {"header": "JobName", "overflow": "fold"},
            {"header": "JobGroup"},
            {"header": "User"},
            {"header": "Queue"},
            {"header": "Submit Time"},
            {"header": "Start Time"},
            {"header": "Finish Time"},
            {"header": "Pending reason"},
        ]
        if self.args.extended:
            cols.append({"header": "Exec. Host"})
            cols.append({"header": "Error File", "overflow": "fold"})
            cols.append({"header": "Output File", "overflow": "fold"})

        rows = []

        for job in sorted(jobs, key=lambda j: j["JOBID"]):
            if "ERROR" in job:
                self.error_console.log(
                    f"The job {job['JOBID']} has an error: {job['ERROR']}"
                )
                continue
            job_name = Text(job["JOB_NAME"])
            pending_reason = Text(job["PEND_REASON"]) or Text("----", justify="center")
            if self.args.filter:
                job_name.highlight_regex(rf"{self.args.filter}", "bold red")
                pending_reason.highlight_regex(rf"{self.args.filter}", "bold red")

            row = [
                job["JOBID"],
                self.status_style(job),
                job_name,
                job["JOB_GROUP"] or Text("----", justify="center"),
                job["USER"],
                job["QUEUE"],
                job["SUBMIT_TIME"],
                job["START_TIME"],
                job["FINISH_TIME"],
                pending_reason,
            ]
            if self.args.extended:
                row.extend(
                    [
                        Text(job["EXEC_HOST"], overflow="fold"),
                        job["ERROR_FILE"],
                        job["OUTPUT_FILE"],
                    ]
                )

            rows.append(row)

        self.render(title=title, columns=cols, rows=rows)

        if self.args.bkill:
            self.console.rule()
            self.console.print(
                Text("Running bkill for each job..."),
                style="bold white",
                justify="center",
            )
            for job in jobs:
                job_id = job["JOBID"]
                try:
                    lsf_bkill_output = self.bkill(job_id)
                    self.console.print(lsf_bkill_output.replace("\n", ""))
                except Exception:
                    self.error_console.print(
                        Text(f"bkill for {job_id} failed"), style="bold red"
                    )
