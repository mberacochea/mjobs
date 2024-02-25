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


class Slurm(Base):
    def __init__(self):
        super().__init__()

    def status_style(self, job_entry) -> Text:
        colours = {
            "RUNNING": "bold green",
            "PENDING": "dark_orange",
            "COMPLETED": "honeydew2",
            "FAILED": "red",
        }
        return Text(
            job_entry["job_state"], style=colours.get(job_entry["job_state"], "grey93")
        )

    def get_args(self):
        parser = super().get_args("squeue")
        parser.add_argument(
            dest="job_id",
            help="Specifies the jobs or job arrays that bjobs displays.",
            nargs="*",
        )
        parser.add_argument(
            "-p",
            "--partition",
            dest="partition",
            required=False,
            help="""Specify the partitions of the jobs or steps to view.
            Accepts a comma separated list of partition names.""",
        )
        parser.add_argument(
            "-u",
            "--user",
            dest="user",
            required=False,
            help="""
            Request jobs or job steps from a comma separated list of users.
            The list can consist of user names or user id numbers.
            Performance of the command can be measurably improved for systems with
            large numbers of jobs when a single user is specified.
            """,
        )
        parser.add_argument(
            "-t",
            "--states",
            dest="states",
            required=False,
            help="""
            Specify the states of jobs to view. Accepts a comma separated list of state names or 'all'.
            If 'all' is specified then jobs of all states will be reported.
            If no state is specified then pending, running, and completing jobs are reported.
            See the JOB STATE CODES section below for a list of valid states.
            Both extended and compact forms are valid.
            Note the <state_list> supplied is case insensitive ('pd' and 'PD' are equivalent).
            """,
        )
        parser.add_argument(
            "-w",
            "--nodelist",
            dest="nodelist",
            required=False,
            help="""
            Report only on jobs allocated to the specified node or list of nodes.
            This may either be the NodeName or NodeHostname as defined in slurm.conf(5) in the event that they differ.
            A node_name of localhost is mapped to the current host name.
            """,
        )
        parser.add_argument(
            "-e",
            dest="extended",
            action="store_true",
            help="Add the execution nodes, stdoutput file and stderror file to the table.",
        )
        self.args = parser.parse_args()
        return parser

    def get_jobs(
        self, job_ids: Optional[list[int]] = None, args: Optional[list[str]] = None
    ):
        """Call squeue to obtain the jobs, it uses the json output."""
        squeue_args = ["squeue", "--json"]
        if args:
            squeue_args.extend(list(map(str, args)))
        if job_ids:
            squeue_args.extend(["--job", " ".join(list(map(str, job_ids)))])
        squeue_output = check_output(squeue_args, universal_newlines=True)
        return json.loads(squeue_output).get("jobs", [])

    def main(self, console: Console):
        """Main execution point, should contain all the code to handle the Slurm implementation"""

        self.get_args()

        jobs = []
        extra_args = []

        if self.args.user:
            extra_args.extend(["-u", self.args.user])
        if self.args.partition:
            extra_args.extend(["-p", self.args.partition])
        if self.args.states:
            extra_args.extend(["-t", self.args.states])
        if self.args.nodelist:
            extra_args.extend(["-w", self.args.nodelist])

        try:
            status = console.status("Getting jobs from Slurm...")
            if not self.args.tsv:
                status.start()

            jobs = self.get_jobs(self.args.job_id, extra_args)

            if not self.args.tsv:
                status.stop()

        except Exception:
            console.print_exception()

        if self.args.filter:
            filter_regex = re.compile(self.args.filter)
            jobs = list(
                filter(
                    lambda j: filter_regex.search(j["command"])
                    or filter_regex.search(j["command"]),
                    jobs,
                )
            )

        if not jobs:
            console.print(Text("No jobs.", style="bold white", justify="left"))
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
            {"header": "End Time"},
            # {"header": "Pending reason"}, // TODO: implement, I don't know how this looks like in the json
        ]
        if self.args.extended:
            cols.append({"header": "Nodes"})
            cols.append({"header": "StdOut"})
            cols.append({"header": "StdErr"})

        rows = []

        for job in sorted(jobs, key=lambda j: j["job_id"]):
            job_name = Text(job["name"])
            if self.args.filter:
                job_name.highlight_regex(rf"{self.args.filter}", "bold red")

            row = [
                str(job["job_id"]),
                self.status_style(job),
                job_name,
                job["user_name"],
                job["partition"],
                # TODO: Convert to something useful
                str(job["submit_time"]),
                str(job["start_time"]),
                str(job["end_time"]),
                # pending_reason,
            ]
            if self.args.extended:
                row.extend(
                    [
                        Text(job["nodes"], overflow="fold"),
                        job["standard_error"],
                        job["standard_output"],
                    ]
                )

            rows.append(row)

        self.render(title=title, console=console, columns=cols, rows=rows)
