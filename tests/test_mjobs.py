import io
import json
import re
from unittest.mock import patch

from click.testing import CliRunner
from rich.console import Console

from mjobs.cli import lsf as lsf_cli, slurm as slurm_cli
from mjobs.data.slurm_repo import SQUEUE_DELIMITER, SlurmRepository
from mjobs.data.test_repo import TestJobRepository
from mjobs.models import SQUEUE_FIELDS
from mjobs.slurm import Slurm


def make_console():
    return Console(file=io.StringIO())


def make_slurm(repo=None):
    return Slurm(make_console(), make_console(), job_repository=repo or TestJobRepository(seed=42))


def test_test_repo_returns_jobs():
    repo = TestJobRepository(seed=42)
    jobs = repo.get_jobs()
    assert len(jobs) == 50
    assert all(j.job_id for j in jobs)


def test_test_repo_filter_by_user():
    repo = TestJobRepository(seed=42)
    jobs = repo.get_jobs(extra_args=["-u", "alice"])
    assert all(j.user_name == "alice" for j in jobs)
    assert len(jobs) > 0


def test_test_repo_filter_by_state():
    repo = TestJobRepository(seed=42)
    jobs = repo.get_jobs(extra_args=["-t", "RUNNING"])
    assert all(j.job_state == "RUNNING" for j in jobs)
    assert len(jobs) > 0


def test_test_repo_job_details():
    repo = TestJobRepository(seed=42)
    details = repo.get_job_details("123456")
    assert details["JobId"] == "123456"
    assert "JobName" in details
    assert "JobState" in details


def test_slurm_get_jobs():
    slurm = make_slurm()
    jobs = slurm.get_jobs()
    assert len(jobs) == 50


def test_slurm_full_fields_command_uses_printf_format():
    repository = SlurmRepository(make_console(), make_console())

    command = repository._build_squeue_command([15722940], [], full_fields=True)

    assert command[2] == "--format"
    expected_format = SQUEUE_DELIMITER.join(re.sub(r"%\.(?:\d+)?", "%", field[0]) for field in SQUEUE_FIELDS)
    assert command[3] == f'"{expected_format}"'
    assert "%." not in command[3]


def test_slurm_full_fields_preserve_delimiters_in_values():
    repository = SlurmRepository(make_console(), make_console())
    values = [
        "123",
        "job|name",
        "1:00",
        "1G",
        "partition",
        "RUNNING",
        "user",
        "command|with|pipes",
        "None",
        "2024-01-01T00:00:00",
        "2024-01-01T00:00:00",
        "N/A",
        "/work|dir",
        "node",
    ]

    jobs = repository._parse_squeue_output(SQUEUE_DELIMITER.join(values), delimiter=SQUEUE_DELIMITER)

    assert jobs[0].job_name == "job|name"
    assert jobs[0].command == "command|with|pipes"
    assert jobs[0].workdir == "/work|dir"


def test_slurm_run_with_test_data():
    slurm = make_slurm()
    slurm.run(
        test_data=True,
        job_ids=(),
        tsv=True,
        no_header=True,
        dashboard=False,
        kill=False,
        filter=None,
        user=None,
        partition=None,
        states=(),
        nodelist=(),
        extended=False,
    )


def test_slurm_kill_prompts_without_filter():
    slurm = make_slurm()
    with patch("builtins.input", return_value="no"):
        slurm.run(
            test_data=True,
            job_ids=(),
            tsv=True,
            no_header=True,
            dashboard=False,
            kill=True,
            filter=None,
            user=None,
            partition=None,
            states=(),
            nodelist=(),
            extended=False,
        )


def test_slurm_kill_skips_prompt_with_filter():
    slurm = make_slurm()
    run_kwargs = dict(
        test_data=True,
        job_ids=(),
        tsv=True,
        no_header=True,
        dashboard=False,
        kill=True,
        filter="blast",
        user=None,
        partition=None,
        states=(),
        nodelist=(),
        extended=False,
    )

    with patch("builtins.input") as mock_input:
        with patch.object(slurm, "kill_job"):
            slurm.run(**run_kwargs)

    mock_input.assert_not_called()


def test_slurm_cli_help():
    runner = CliRunner()
    result = runner.invoke(slurm_cli, ["--help"])
    assert result.exit_code == 0
    assert "partition" in result.output
    assert "--details" in result.output


def test_lsf_cli_help():
    runner = CliRunner()
    result = runner.invoke(lsf_cli, ["--help"])
    assert result.exit_code == 0
    assert "queue" in result.output
    assert "--details" in result.output


def test_slurm_cli_with_test_data():
    runner = CliRunner()
    result = runner.invoke(slurm_cli, ["--test-data"])
    assert result.exit_code == 0


def test_slurm_cli_json_with_test_data():
    runner = CliRunner()
    result = runner.invoke(slurm_cli, ["--test-data", "--details", "123456"])

    assert result.exit_code == 0
    job = json.loads(result.output)
    assert job["job_id"] == "123456"
    assert "workdir" in job
    assert "nodes" in job


def test_lsf_bkill_flag_accepted():
    runner = CliRunner()
    result = runner.invoke(lsf_cli, ["--help"])
    assert "bkill" in result.output
