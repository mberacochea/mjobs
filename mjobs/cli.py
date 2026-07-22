#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from rich.console import Console

from mjobs.core.factory import create_job_repository
from mjobs.lsf import LSF
from mjobs.slurm import Slurm
from mjobs.version import VERSION

SLURM_JOB_STATES = [
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

console = Console()
error_console = Console(stderr=True, style="bold red")


@click.command()
@click.version_option(version=VERSION, prog_name="mjobs")
@click.option("-f", "--filter", default=None, help="Filter jobs by regex on the job name or pending reason.")
@click.option("-ts", "--tsv", is_flag=True, help="No fancy table, a good ol' tsv")
@click.option("-nh", "--no-header", is_flag=True, help="Don't print the table header, useful to pipe the tsv output")
@click.option(
    "-d",
    "--dashboard",
    is_flag=True,
    help="Launch interactive dashboard mode",
)
@click.option("--test-data", is_flag=True, help="Use fake test data (useful for development)")
@click.option("--kill", is_flag=True, help="Cancel/kill the listed jobs")
@click.argument("job_ids", nargs=-1)
@click.option(
    "-p",
    "--partition",
    default=None,
    help="Specify the partitions of the jobs or steps to view. Accepts a comma separated list of partition names.",
)
@click.option(
    "-u",
    "--user",
    default=None,
    help="Request jobs or job steps from a comma separated list of users.",
)
@click.option(
    "-t",
    "--states",
    multiple=True,
    type=click.Choice(SLURM_JOB_STATES),
    help="Specify the states of jobs to view. Accepts a comma separated list of state names.",
)
@click.option(
    "-w",
    "--nodelist",
    multiple=True,
    help="Report only on jobs allocated to the specified node or list of nodes.",
)
@click.option("-e", "--extended", is_flag=True, help="Add the execution nodes, stdoutput file and stderror file.")
def slurm(
    filter,
    tsv,
    no_header,
    dashboard,
    test_data,
    kill,
    job_ids,
    partition,
    user,
    states,
    nodelist,
    extended,
):
    job_repository = create_job_repository(
        test_mode=test_data,
        console=console if not test_data else None,
        error_console=error_console if not test_data else None,
    )
    slurm = Slurm(console, error_console, job_repository=job_repository)
    slurm.run(
        filter=filter,
        tsv=tsv,
        no_header=no_header,
        dashboard=dashboard,
        test_data=test_data,
        kill=kill,
        job_ids=job_ids,
        partition=partition,
        user=user,
        states=states,
        nodelist=nodelist,
        extended=extended,
    )


@click.command()
@click.version_option(version=VERSION, prog_name="mjobs")
@click.option("-f", "--filter", default=None, help="Filter jobs by regex on the job name or pending reason.")
@click.option("-ts", "--tsv", is_flag=True, help="No fancy table, a good ol' tsv")
@click.option("-nh", "--no-header", is_flag=True, help="Don't print the table header, useful to pipe the tsv output")
@click.option(
    "-d",
    "--dashboard",
    is_flag=True,
    help="Launch interactive dashboard mode",
)
@click.option("--kill", is_flag=True, help="Cancel/kill the listed jobs")
@click.argument("job_ids", nargs=-1)
@click.option("-q", "--queue", default=None, help="Displays jobs in the specified queue")
@click.option("-u", "--user", default=None, help="Displays jobs in the specified user")
@click.option("-r", "--run", "show_run", is_flag=True, help="Displays running jobs.")
@click.option("-a", "--all", "show_all", is_flag=True, help="Displays information about jobs in all states.")
@click.option("--recent", is_flag=True, help="Displays information about jobs that finished recently.")
@click.option("-G", "--user-group", default=None, help="Displays jobs associated with the specified user group.")
@click.option(
    "-g", "--group", default=None, help="Displays information about jobs attached to the specified job group."
)
@click.option("-m", "--hosts", default=None, help="Displays jobs dispatched to the specified hosts.")
@click.option("--pend", is_flag=True, help="Displays pending jobs with pending reasons.")
@click.option("-e", "--extended", is_flag=True, help="Add the execution hosts, output file and error file.")
@click.option("--bkill", is_flag=True, help="Terminate found or filtered jobs with bkill.")
def lsf(
    filter,
    tsv,
    no_header,
    dashboard,
    kill,
    job_ids,
    queue,
    user,
    show_run,
    show_all,
    recent,
    user_group,
    group,
    hosts,
    pend,
    extended,
    bkill,
):
    LSF(console, error_console).run(
        filter=filter,
        tsv=tsv,
        no_header=no_header,
        dashboard=dashboard,
        kill=kill,
        job_ids=job_ids,
        queue=queue,
        user=user,
        show_run=show_run,
        show_all=show_all,
        recent=recent,
        user_group=user_group,
        group=group,
        hosts=hosts,
        pend=pend,
        extended=extended,
        bkill=bkill,
    )
