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

import csv
import sys
from abc import ABC

from rich.console import Console
from rich.table import Table


class Base(ABC):
    def __init__(self, console: Console, error_console: Console) -> None:
        self.console = console
        self.error_console = error_console
        super().__init__()

    def render(
        self,
        title: str,
        columns: list[dict[str, any]],
        rows: list[dict[str, any]],
    ):
        if self.args.tsv:
            writer = csv.writer(sys.stdout, delimiter="\t")
            if not self.args.no_header:
                writer.writerow([c.get("header") for c in columns])
            writer.writerows(rows)
        else:
            table = Table(title=title, show_lines=True, show_header=not self.args.no_header)
            for col in columns:
                table.add_column(**col)
            for row in rows:
                table.add_row(*row)
            self.console.print(table)
