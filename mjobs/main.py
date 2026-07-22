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

from mjobs.core.factory import detect_scheduler

from .version import VERSION


def main():
    """Main entry point for the mjobs application."""

    if "--version" in sys.argv:
        print(f"mjobs {VERSION}")
        return

    test_data_mode = "--test-data" in sys.argv
    scheduler = detect_scheduler()

    if scheduler == "none" and not test_data_mode:
        error_console = Console(stderr=True, style="bold red")
        error_console.log("I can't find bjobs or squeue... so, I can't do anything.")
        error_console.log("Use --test-data flag to run with fake data for testing.")
        sys.exit(1)
        return

    if scheduler == "lsf" and not test_data_mode:
        from mjobs.cli import lsf as lsf_cli

        lsf_cli()
    else:
        from mjobs.cli import slurm as slurm_cli

        slurm_cli()


if __name__ == "__main__":
    main()
