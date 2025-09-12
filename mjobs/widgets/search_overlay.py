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

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Input, Label, Static


class SearchOverlay(Static):
    """Search overlay widget for filtering jobs."""

    BINDINGS = [
        Binding("escape", "close_search", "Close Search"),
        Binding("enter", "apply_search", "Apply Search"),
    ]

    CSS = """
    SearchOverlay {
        layer: overlay;
        align: center top;
        offset: 1 0;
        width: 80%;
        height: 3;
        max-height: 3;
        background: $surface;
        border: solid $primary;
        visibility: hidden;
    }

    SearchOverlay.visible {
        visibility: visible;
    }

    SearchOverlay Input {
        width: 1fr;
        margin: 0 1;
    }

    SearchOverlay Label {
        width: auto;
        margin: 0 1;
        color: $text-muted;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_callback = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the search overlay."""
        with Horizontal():
            yield Label("Search:")
            yield Input(placeholder="Filter jobs by name, state, user, command...", id="search_input")

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Don't focus automatically - only focus when search is shown
        pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """Called when search input changes."""
        if self.search_callback:
            self.search_callback(event.value)

    def set_search_callback(self, callback):
        """Set the callback function to call when search text changes.

        Args:
            callback: Function to call with search text
        """
        self.search_callback = callback

    def show_search(self):
        """Show the search overlay."""
        self.add_class("visible")
        search_input = self.query_one("#search_input", Input)
        search_input.focus()
        search_input.clear()

    def hide_search(self):
        """Hide the search overlay."""
        self.remove_class("visible")
        if self.search_callback:
            self.search_callback("")  # Clear search when hiding

    def action_close_search(self):
        """Close the search overlay."""
        self.hide_search()

    def action_apply_search(self):
        """Apply current search and close overlay."""
        # The search is already applied via on_input_changed
        # This just closes the overlay while keeping the search active
        self.remove_class("visible")
