#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2019-2021 - Martin Beracochea
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

import argparse
import csv
import getpass
import re
import sys

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich_argparse import RichHelpFormatter

from mjobs import lsf


def _status_style(job_entry) -> Text:
    if job_entry["STAT"] == "RUN":
        return Text(job_entry["STAT"], style="bold green")
    elif job_entry["STAT"] == "PEND":
        return Text(job_entry["STAT"], style="dark_orange")
    elif job_entry["STAT"] == "DONE":
        return Text(job_entry["STAT"], style="honeydew2")
    return Text(job_entry["STAT"], style="grey93")


def _get_args():
    parser = argparse.ArgumentParser(
        description="bjobs but a bit nicer", formatter_class=RichHelpFormatter
    )
    parser.add_argument(
        dest="job_id",
        help="Specifies the jobs or job arrays that bjobs displays.",
        nargs="*",
    )
    parser.add_argument(
        "-q", dest="queue", required=False, help="Displays jobs in the specified queue"
    )
    parser.add_argument(
        "-u", dest="user", required=False, help="Displays jobs in the specified user"
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
        help="Add the execution josts, output file and error file to the table.",
    )
    parser.add_argument(
        "-f",
        dest="filter",
        required=False,
        help="Filter the jobs using the specified regex on the job name or pending reason.",
    )
    parser.add_argument(
        "-t",
        dest="tsv",
        action="store_true",
        help="No fancy table, a good ol' tsv",
    )
    parser.add_argument(
        "-nh",
        dest="no_header",
        action="store_true",
        help="Don't print the table header, useful to pipe the tsv ouput",
    )
    parser.add_argument(
        "--bkill",
        dest="bkill",
        action="store_true",
        help="Run `bkill` on found or filtered jobs.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _get_args()

    console = Console()

    jobs = []
    lsf_args = []

    if args.user:
        lsf_args.extend(["-u", args.user])
    if args.queue:
        lsf_args.extend(["-q", args.queue])
    if args.run:
        lsf_args.extend(["-r"])
    if args.all:
        lsf_args.extend(["-a"])
    if args.recent:
        lsf_args.extend(["-d"])
    if args.user_group:
        lsf_args.extend(["-G", args.user_group])
    if args.group:
        lsf_args.extend(["-g", args.group])
    if args.hosts:
        lsf_args.extend(["-m", args.hosts])
    if args.pend:
        lsf_args.extend(["-p"])

    try:
        status = console.status("Getting jobs from LSF...")
        if not args.tsv:
            status.start()

        jobs = lsf.get_jobs(args.job_id, lsf_args)

        if not args.tsv:
            status.stop()

    except Exception:
        console.print_exception()

    if args.filter:
        filter_regex = re.compile(args.filter)
        jobs = list(
            filter(
                lambda j: filter_regex.search(j["JOB_NAME"])
                or filter_regex.search(j["PEND_REASON"]),
                jobs,
            )
        )

    if not jobs:
        console.print(Text("No jobs.", style="bold white", justify="left"))
        sys.exit(0)

    title = f"LSF jobs for {args.user or getpass.getuser()}"
    if args.queue:
        title += f" on queue {args.queue}"
    if args.hosts:
        title += f" running on hosts {args.hosts}"

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
    if args.extended:
        cols.append({"header": "Exec. Host"})
        cols.append({"header": "Error File", "overflow": "fold"})
        cols.append({"header": "Output File", "overflow": "fold"})

    rows = []

    for job in sorted(jobs, key=lambda j: j["JOBID"]):
        if "ERROR" in job:
            console.print(f"The job {job['JOBID']} has an error: {job['ERROR']}")
            continue
        job_name = Text(job["JOB_NAME"])
        pending_reason = Text(job["PEND_REASON"]) or Text("----", justify="center")
        if args.filter:
            job_name.highlight_regex(rf"{args.filter}", "bold red")
            pending_reason.highlight_regex(rf"{args.filter}", "bold red")

        row = [
            job["JOBID"],
            _status_style(job),
            job_name,
            job["JOB_GROUP"] or Text("----", justify="center"),
            job["USER"],
            job["QUEUE"],
            job["SUBMIT_TIME"],
            job["START_TIME"],
            job["FINISH_TIME"],
            pending_reason,
        ]
        if args.extended:
            row.extend(
                [
                    Text(job["EXEC_HOST"], overflow="fold"),
                    job["ERROR_FILE"],
                    job["OUTPUT_FILE"],
                ]
            )

        rows.append(row)

    if args.tsv:
        # print with no styles
        writer = csv.writer(sys.stdout, delimiter="\t")
        if not args.no_header:
            writer.writerow([c.get("header") for c in cols])
        writer.writerows(rows)
    else:
        # print the fancy table
        table = Table(title=title, show_lines=True, show_header=not args.no_header)
        for col in cols:
            table.add_column(**col)
        for row in rows:
            table.add_row(*row)
        console.print(table)

    if args.bkill:
        console.rule()
        console.print(
            Text("Running bkill for each job..."), style="bold white", justify="center"
        )
        for job in jobs:
            job_id = job["JOBID"]
            try:
                lsf_bkill_output = lsf.bkill(job_id)
                console.print(lsf_bkill_output.replace("\n", ""))
            except Exception:
                console.print(Text(f"bkill for {job_id} failed"), style="bold red")
