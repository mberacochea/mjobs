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

import argparse
import csv
import sys
from abc import ABC

from rich.console import Console
from rich.table import Table
from rich_argparse import RichHelpFormatter


class Base(ABC):
    def get_args(self, implementation_name: str):
        """Base arguments that every implementation should support"""
        parser = argparse.ArgumentParser(
            description=f"Just like {implementation_name} but a bit nicer",
            formatter_class=RichHelpFormatter,
        )
        parser.add_argument(
            "-f",
            dest="filter",
            required=False,
            help="Filter the jobs using the specified regex on the job name or pending reason.",
        )
        parser.add_argument(
            "-ts",
            "--tsv",
            dest="tsv",
            action="store_true",
            help="No fancy table, a good ol' tsv",
        )
        parser.add_argument(
            "-nh",
            dest="no_header",
            action="store_true",
            help="Don't print the table header, useful to pipe the tsv output",
        )
        return parser

    def render(
        self,
        console: Console,
        title: str,
        columns: list[dict[str, any]],
        rows: list[dict[str, any]],
    ):
        """Render the jobs"""
        if self.args.tsv:
            # print with no styles
            writer = csv.writer(sys.stdout, delimiter="\t")
            if not self.args.no_header:
                writer.writerow([c.get("header") for c in columns])
            writer.writerows(rows)
        else:
            # print the fancy table
            table = Table(
                title=title, show_lines=True, show_header=not self.args.no_header
            )
            for col in columns:
                table.add_column(**col)
            for row in rows:
                table.add_row(*row)
            console.print(table)

    def main(self, console: Console):
        """Main execution point.
        Should handle the logic to get jobs, build the table and any other features"""
        pass
