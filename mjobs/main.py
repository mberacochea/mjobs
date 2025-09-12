#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2019-2024 - Martin Beracochea
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

import sys

from rich.console import Console

from mjobs.core import create_job_repository
from mjobs.core.factory import detect_scheduler
from mjobs.lsf import LSF
from mjobs.slurm import Slurm


def main():
    """Main entry point for the mjobs application."""
    console = Console()
    error_console = Console(stderr=True, style="bold red")

    # Check if test-data mode is requested
    test_data_mode = "--test-data" in sys.argv

    # Detect available scheduler
    scheduler = detect_scheduler()

    try:
        if scheduler == "lsf":
            # Use LSF (unchanged for now)
            lsf = LSF(console, error_console)
            lsf.main()
        elif scheduler == "slurm" or test_data_mode:
            # Create repository through factory
            job_repository = create_job_repository(
                test_mode=test_data_mode,
                console=console if not test_data_mode else None,
                error_console=error_console if not test_data_mode else None,
            )

            # Create Slurm instance with repository
            slurm = Slurm(console, error_console, job_repository=job_repository)
            slurm.main()
        else:
            error_console.log("I can't find bjobs or squeue... so, I can't do anything.")
            error_console.log("Use --test-data flag to run with fake data for testing.")
            sys.exit(1)

    except Exception as e:
        error_console.log(f"Failed to initialize: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
