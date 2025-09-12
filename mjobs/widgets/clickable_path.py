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

from textual.message import Message
from textual.widgets import Static


class ClickableFilePath(Static):
    """A widget that displays a file path and can be clicked to open it."""

    class FilePathClicked(Message):
        """Message sent when a file path is clicked."""

        def __init__(self, file_path: str) -> None:
            super().__init__()
            self.file_path = file_path

    def __init__(self, file_path: str, display_text: str = None, **kwargs):
        self.file_path = file_path
        display = display_text or file_path
        # Make it look clickable with underline and different color
        content = f"[link={file_path}][cyan underline]{display}[/cyan underline][/link]"
        super().__init__(content, **kwargs)

    def on_click(self) -> None:
        """Handle click events on the file path."""
        self.post_message(self.FilePathClicked(self.file_path))


def create_file_path_display(field_name: str, file_path: str) -> str:
    """Create a display string with clickable file path if it looks like a file."""
    if not file_path or file_path in ["/dev/null", "None", "N/A", ""]:
        return f"  [cyan]{field_name:16}[/cyan]: {file_path}"

    # Check if it looks like a file path
    if "/" in file_path and not file_path.startswith("("):
        # Create a clickable version - show only filename but keep full path for clicking
        filename = file_path.split("/")[-1] if "/" in file_path else file_path
        # Escape the file path to prevent markup issues
        escaped_path = file_path.replace("[", "\\[").replace("]", "\\]")
        escaped_filename = filename.replace("[", "\\[").replace("]", "\\]")
        return (
            f"  [cyan]{field_name:16}[/cyan]: [cyan underline]{escaped_filename}[/cyan underline]"
            f" ([dim]{escaped_path}[/dim])"
        )
    else:
        return f"  [cyan]{field_name:16}[/cyan]: {file_path}"
