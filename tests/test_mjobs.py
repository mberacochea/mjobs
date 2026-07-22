import io
from unittest.mock import patch

from click.testing import CliRunner
from rich.console import Console

from mjobs.cli import lsf as lsf_cli
from mjobs.cli import slurm as slurm_cli
from mjobs.data.test_repo import TestJobRepository
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


def test_lsf_cli_help():
    runner = CliRunner()
    result = runner.invoke(lsf_cli, ["--help"])
    assert result.exit_code == 0
    assert "queue" in result.output


def test_slurm_cli_with_test_data():
    runner = CliRunner()
    result = runner.invoke(slurm_cli, ["--test-data"])
    assert result.exit_code == 0


def test_lsf_bkill_flag_accepted():
    runner = CliRunner()
    result = runner.invoke(lsf_cli, ["--help"])
    assert "bkill" in result.output
