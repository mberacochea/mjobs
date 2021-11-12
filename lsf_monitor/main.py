#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2019-2021 EMBL - European Bioinformatics Institute
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

from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.text import Text

import getpass

import lsf


def _status_style(job) -> Text:
    if job["STAT"] == "RUN":
        return Text(job["STAT"], style="bold green")
    elif job["STAT"] == "PEND":
        return Text(job["STAT"], style="white")
    return Text(job["STAT"], style="grey93")


def main(
    user: str = "", queue: str = "", status_filters: Optional[list[str]] = None
) -> None:
    """Call bjobs and build the table with the results
    :param user: "bjobs -u" displays jobs in the specified user
    :param queue: "bjobs -q" displays jobs in the specified queue
    :param status_filters: job status filters such as -r for RUN or -p for PEND
    """
    console = Console()

    jobs = []
    with console.status("Getting the jobs from LSF...", spinner="monkey"):
        lsf_args = []
        if user:
            lsf_args.extend(["-u", user])
        if queue:
            lsf_args.extend(["-q", queue])
        if status_filters:
            lsf_args.extend(status_filters)

        jobs = lsf.get_jobs()

    table = Table(title=f"LSF jobs for {getpass.getuser()}", show_lines=True)

    table.add_column("JobId", justify="right")
    table.add_column("Status")
    table.add_column("JobName")
    table.add_column("JobGroup")
    table.add_column("User")
    table.add_column("Queue")
    table.add_column("Start Time")
    table.add_column("Finish Time")
    # table.add_column("Error File", overflow="fold")
    # table.add_column("Output File", overflow="fold")
    table.add_column("Pending reason")  # only if there are any pending jobs

    for job in sorted(jobs, key=lambda j: j["JOBID"]):
        table.add_row(
            job["JOBID"],
            _status_style(job),
            job["JOB_NAME"],
            job["JOB_GROUP"],
            job["USER"],
            job["QUEUE"],
            job["START_TIME"],
            job["FINISH_TIME"],
            job["ERROR_FILE"],
            job["OUTPUT_FILE"],
            job["PENDING_REASON"],
        )

    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate the input.yaml for the CWL pipeline"
    )
    parser.add_argument(
        "-q", dest="queue", required=False, help="Displays jobs in the specified queue"
    )
    parser.add_argument(
        "-u", dest="user", required=False, help="Displays jobs in the specified user"
    )
    args = parser.parse_args()

    # TODO: add filters by status
    main(user=args.user, queue=args.queue)
