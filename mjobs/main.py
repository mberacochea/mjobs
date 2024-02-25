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

import shutil
import sys

from rich.console import Console

from mjobs.lsf import LSF
from mjobs.slurm import Slurm

if __name__ == "__main__":

    console = Console()

    if shutil.which("bjobs"):
        lsf = LSF()
        lsf.main(console)
    elif shutil.which("squeue"):
        slurm = Slurm()
        slurm.main(console)
    else:
        print(
            "I can't find bjobs or slurm... so, I can't do anything.", file=sys.stderr
        )
        sys.exit(1)
