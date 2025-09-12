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

import shutil
from typing import Optional

from rich.console import Console

from mjobs.data import JobRepository, SlurmRepository, TestJobRepository


def create_job_repository(
    test_mode: bool = False, console: Optional[Console] = None, error_console: Optional[Console] = None
) -> JobRepository:
    """Factory function to create the appropriate job repository.

    :param test_mode: If True, create test repository; otherwise create real repository
    :param console: Rich console for output (required for real repository)
    :param error_console: Rich console for errors (required for real repository)
    :return: JobRepository instance (either SlurmRepository or TestJobRepository)
    :raises RuntimeError: If Slurm is not available and not in test mode
    """
    if test_mode:
        return TestJobRepository()

    # Check for Slurm availability
    if not shutil.which("squeue"):
        raise RuntimeError("Slurm 'squeue' command not found. Use --test-data flag for testing without Slurm.")

    if console is None or error_console is None:
        raise ValueError("console and error_console are required for real Slurm repository")

    return SlurmRepository(console, error_console)


def detect_scheduler() -> str:
    """Detect available job scheduler.

    :return: Scheduler name ('lsf', 'slurm', or 'none')
    """
    if shutil.which("bjobs"):
        return "lsf"
    elif shutil.which("squeue"):
        return "slurm"
    else:
        return "none"
