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

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import RichLog


class FileViewerScreen(ModalScreen[None]):
    """Modal screen for viewing file contents."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
        Binding("g", "go_to_top", "Go to Top"),
        Binding("G", "go_to_bottom", "Go to Bottom"),
        Binding("j", "scroll_down", "Scroll Down"),
        Binding("k", "scroll_up", "Scroll Up"),
        Binding("space", "page_down", "Page Down"),
        Binding("b", "page_up", "Page Up"),
    ]

    CSS = """
    FileViewerScreen {
        align: center middle;
    }

    #file_viewer_dialog {
        width: 90%;
        height: 85%;
        border: thick $primary;
        background: $surface;
    }

    #file_header {
        height: 3;
        background: $primary;
        color: $text;
        padding: 1;
    }

    #file_log {
        height: 1fr;
        border: solid $secondary;
        scrollbar-gutter: stable;
        text-wrap: wrap;
    }

    """

    def __init__(self, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.file_lines = []
        self.error_message = ""

    def compose(self) -> ComposeResult:
        """Create the file viewer interface."""
        with Container(id="file_viewer_dialog"):
            with Vertical():
                yield RichLog(id="file_header", max_lines=1, markup=True)
                yield RichLog(id="file_log", markup=True, highlight=True, auto_scroll=False, wrap=True)

    def on_mount(self) -> None:
        """Load and display file content when screen mounts."""
        self.load_file_content()
        self.display_content()
        # Focus the log widget so scrolling works
        log_widget = self.query_one("#file_log", RichLog)
        log_widget.focus()

    def load_file_content(self) -> None:
        """Load the file content or set error message."""
        try:
            file_path = Path(self.file_path)

            if not file_path.exists():
                self.error_message = f"File does not exist: {self.file_path}"
                return

            if not file_path.is_file():
                self.error_message = f"Path is not a file: {self.file_path}"
                return

            # Check if file is too large (increase limit to 10MB)
            file_size = file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB
                self.error_message = f"File too large to display: {file_size:,} bytes (limit: 10MB)"
                return

            # Read file content line by line for better performance
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.file_lines = f.readlines()
                # Remove trailing newlines to avoid double spacing
                self.file_lines = [line.rstrip("\n\r") for line in self.file_lines]
            except UnicodeDecodeError:
                # Try reading as binary and display hex or basic info
                self.error_message = f"File appears to be binary. Size: {file_size:,} bytes"
                return

        except PermissionError:
            self.error_message = f"Permission denied reading file: {self.file_path}"
        except Exception as e:
            self.error_message = f"Error reading file: {str(e)}"

    def display_content(self) -> None:
        """Display the file content in the RichLog widget."""
        # Update header
        header_widget = self.query_one("#file_header", RichLog)
        header_widget.clear()
        header_widget.write(
            f"[bold]File: {self.file_path}[/bold] (Press ESC/Q to close, g/G for top/bottom, j/k/space/b to scroll)"
        )

        # Update content
        log_widget = self.query_one("#file_log", RichLog)
        log_widget.clear()

        if self.error_message:
            log_widget.write(f"[red]{self.error_message}[/red]")
            return

        if not self.file_lines:
            log_widget.write("[dim]Empty file[/dim]")
            return

        # Add each line with line numbers
        for i, line_content in enumerate(self.file_lines):
            line_num = i + 1
            # RichLog handles Rich markup automatically, no need to escape
            log_widget.write(f"[dim]{line_num:6}:[/dim] {line_content}")

        # Add status information
        total_lines = len(self.file_lines)
        log_widget.write(f"\n[dim]File contains {total_lines} lines[/dim]")

    def action_close(self) -> None:
        """Close the file viewer."""
        self.dismiss()

    def action_go_to_top(self) -> None:
        """Go to the beginning of the file."""
        log_widget = self.query_one("#file_log", RichLog)
        log_widget.scroll_home()

    def action_go_to_bottom(self) -> None:
        """Go to the end of the file."""
        log_widget = self.query_one("#file_log", RichLog)
        log_widget.scroll_end()

    def action_scroll_down(self) -> None:
        """Scroll down one line."""
        log_widget = self.query_one("#file_log", RichLog)
        log_widget.scroll_down()

    def action_scroll_up(self) -> None:
        """Scroll up one line."""
        log_widget = self.query_one("#file_log", RichLog)
        log_widget.scroll_up()

    def action_page_down(self) -> None:
        """Scroll down one page."""
        log_widget = self.query_one("#file_log", RichLog)
        log_widget.scroll_page_down()

    def action_page_up(self) -> None:
        """Scroll up one page."""
        log_widget = self.query_one("#file_log", RichLog)
        log_widget.scroll_page_up()
