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
from collections import namedtuple
from datetime import datetime
from subprocess import CalledProcessError, check_output
from typing import Optional

from rich.console import Console
from rich.text import Text

from mjobs.base import Base


class Slurm(Base):
    def __init__(self, console: Console, error_console: Console):
        super().__init__(console, error_console)

    def status_style(self, job_state) -> Text:
        colours = {
            "RUNNING": "bold green",
            "PENDING": "dark_orange",
            "COMPLETED": "honeydew2",
            "FAILED": "red",
        }
        return Text(job_state, style=colours.get(job_state, "grey93"))

    def get_args(self):
        JOB_STATES = [
            "pending",
            "running",
            "suspended",
            "completed",
            "cancelled",
            "failed",
            "timeout",
            "node_fail",
            "preempted",
            "boot_fail",
            "deadline",
            "out_of_memory",
            "completing",
            "configuring",
            "resizing",
            "resv_del_hold",
            "requeued",
            "requeue_fed",
            "requeue_hold",
            "revoked",
            "signaling",
            "special_exit",
            "stage_out",
            "stopped",
        ]
        parser = super().get_args("squeue")
        parser.add_argument(
            dest="job_id",
            help="Specifies the jobs or job arrays that squeue displays.",
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
            help="""Request jobs or job steps from a comma separated list of users.
            The list can consist of user names or user id numbers.
            Performance of the command can be measurably improved for systems with
            large numbers of jobs when a single user is specified.
            """,
        )
        parser.add_argument(
            "-t",
            "--states",
            dest="states",
            choices=JOB_STATES,
            nargs="+",
            help="""
            Specify the states of jobs to view. Accepts a comma separated list of state names or 'all'.
            If 'all' is specified then jobs of all states will be reported.
            If no state is specified then pending, running, and completing jobs are reported.
            See the JOB STATE CODES section below for a list of valid states.
            Both extended and compact forms are valid.
            Note the <state_list> supplied is case insensitive ('pending' and 'PENDING' are equivalent).
            """,
        )
        parser.add_argument(
            "-w",
            "--nodelist",
            dest="nodelist",
            nargs="+",
            help="""
            Report only on jobs allocated to the specified node or list of nodes.
            This may either be the NodeName or NodeHostname as defined in slurm.conf(5)
            in the event that they differ.
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
        # fmt: off
        squeue_fields = [
            ["%.18i", "job_id"],       # job id
            ["%.200j", "job_name"],     # job name
            ["%l", "time_limit"],      # time limit for the job (it can be NOT_SET), format: days-hours:minutes:seconds
            ["%m", "memory"],          # Minimum size of memory (in MB) requested by the job
            ["%.50P", "partition"],    # Partition of the job or job step.
            ["%T", "job_state"],       # Job state in extended form.
            ["%u", "user_name"],       # User name for a job or job step.
            ["%.200o", "command"],      # The command to be executed.
            ["%.20r", "state_reason"], # The reason for the job status.
            ["%S", "start_time"],      # Job start time, format: days-hours:minutes:seconds.
            ["%V", "submit_time"],     # Job submission time, format: days-hours:minutes:seconds.
            ["%L", "end_time"],        # time left (it can be NOT_SET), format: days-hours:minutes:seconds
            ["%.100Z", "workdir"],     # Working directory
            ["%.N", "nodes"],          # List of nodes allocated to the job or job step.
        ]
        # fmt: on

        SlurmJob = namedtuple("SlurmJob", " ".join(x[1] for x in squeue_fields))

        jobs = []

        squeue = [
            "squeue",
            "-h",
            "--format",
            f"\"{'|'.join(x[0] for x in squeue_fields)}\"",
        ]

        if args:
            squeue.extend(list(map(str, args)))
        if job_ids:
            squeue.extend(["-j", ",".join(list(map(str, job_ids)))])
        try:
            print(check_output(squeue, universal_newlines=True))
            squeue_output = check_output(squeue, universal_newlines=True).split("\n")
            for line in squeue_output:
                if line.strip() == "":
                    continue

                # TODO we need a more robust parsing mechanism
                values = [element.strip() for element in line.strip('"').split("|")]
                if len(values) == len(squeue_fields) - 1:
                    # The nodes are missing, as the job is not running
                    values.append("-----")

                jobs.append(SlurmJob(*values))

            return jobs

        except CalledProcessError as ex:
            self.error_console.log(
                f"squeue call failed. Arguments: {' '.join(squeue)}. Error {ex.output}"
            )
            raise ex

    def parse_timestamp_str(self, timestamp: Optional[int]) -> str:
        if timestamp is None:
            return f"Invalid timestamp. {timestamp}"
        try:
            dt_object = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            return str(dt_object)
        except (TypeError, ValueError):
            return f"Invalid timestamp. {timestamp}"

    def main(self):
        """Main execution point, should contain all the code to handle the Slurm implementation"""

        self.get_args()

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
            # This is handled by get_jobs
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
                    lambda j: filter_regex.search(j.job_name)
                    or filter_regex.search(j.command),
                    jobs,
                )
            )

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
