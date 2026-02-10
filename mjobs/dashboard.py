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

from typing import List

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Input, Label

from mjobs.widgets.file_viewer import FileViewerScreen
from mjobs.widgets.job_details import JobDetailsPanel
from mjobs.widgets.jobs_table import JobsTable


class SearchScreen(ModalScreen[str]):
    """Simple modal search screen."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Search"),
    ]

    CSS = """
    SearchScreen {
        align: center middle;
    }

    #search_dialog {
        width: 90;
        height: 15;
        border: thick $background 80%;
        background: $surface;
        padding: 2;
    }

    #search_input {
        margin: 1 1;
        min-height: 3;
        height: 3;
        width: 1fr;
    }

    Label {
        margin: 1 1;
        text-align: center;
        height: 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="search_dialog"):
            yield Label("Search Jobs")
            yield Input(placeholder="Filter by job name, state, user, command...", id="search_input")

    def on_mount(self):
        search_input = self.query_one("#search_input", Input)
        search_input.focus()

    def action_submit(self):
        search_input = self.query_one("#search_input", Input)
        search_text = search_input.value
        self.dismiss(search_text)

    def action_cancel(self):
        self.dismiss("")

    def on_input_submitted(self, event: Input.Submitted):
        """Handle Enter key in input field."""
        self.action_submit()


class ConfirmKillScreen(ModalScreen[bool]):
    """Modal confirmation dialog for killing a job."""

    BINDINGS = [
        Binding("y", "confirm", "Yes"),
        Binding("enter", "confirm", "Confirm"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ConfirmKillScreen {
        align: center middle;
    }

    #confirm_dialog {
        width: 70;
        height: 12;
        border: thick $background 80%;
        background: $surface;
        padding: 2;
    }

    #confirm_dialog Label {
        margin: 1 1;
        text-align: center;
        width: 1fr;
    }
    """

    def __init__(self, job_id: str, job_name: str, **kwargs):
        super().__init__(**kwargs)
        self.job_id = job_id
        self.job_name = job_name

    def compose(self) -> ComposeResult:
        with Container(id="confirm_dialog"):
            yield Label(f"Kill job {self.job_id} ({self.job_name})?")
            yield Label("[y/Enter] Confirm  [n/Escape] Cancel")

    def action_confirm(self):
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)


class AutoRefreshScreen(ModalScreen[str]):
    """Modal screen to configure auto-refresh interval."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    AutoRefreshScreen {
        align: center middle;
    }

    #auto_refresh_dialog {
        width: 70;
        height: 15;
        border: thick $background 80%;
        background: $surface;
        padding: 2;
    }

    #auto_refresh_input {
        margin: 1 1;
        min-height: 3;
        height: 3;
        width: 1fr;
    }

    #auto_refresh_dialog Label {
        margin: 1 1;
        text-align: center;
        height: 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="auto_refresh_dialog"):
            yield Label("Auto-Refresh Interval (seconds)")
            yield Input(value="10", placeholder="Interval in seconds", id="auto_refresh_input")

    def on_mount(self):
        refresh_input = self.query_one("#auto_refresh_input", Input)
        refresh_input.focus()

    def on_input_submitted(self, event: Input.Submitted):
        """Handle Enter key in input field."""
        refresh_input = self.query_one("#auto_refresh_input", Input)
        self.dismiss(refresh_input.value)

    def action_cancel(self):
        self.dismiss("")


class Dashboard(App):
    """Main dashboard application."""

    CSS = """
    Dashboard {
        layout: vertical;
    }

    #jobs_table {
        height: 1fr;
        border: solid $secondary;
        overflow: hidden;
    }

    #details_panel {
        height: 0;
        max-height: 35;
        border: solid $primary;
        overflow: hidden;
    }

    #details_panel.visible {
        height: 35;
    }

    #left_panel {
        width: 1fr;
        overflow: hidden;
        padding: 1;
        border-right: solid $secondary;
    }

    #middle_panel {
        width: 1fr;
        overflow: hidden;
        padding: 1;
        border-right: solid $secondary;
    }

    #right_panel {
        width: 1fr;
        overflow: hidden;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+f", "search", "Search"),
        Binding("enter", "show_details", "Show Details"),
        Binding("escape", "hide_details", "Hide Details"),
        Binding("r", "refresh", "Refresh"),
        Binding("o", "open_stdout", "Open StdOut"),
        Binding("e", "open_stderr", "Open StdErr"),
        Binding("ctrl+o", "copy_stdout_path", "Copy StdOut Path"),
        Binding("ctrl+e", "copy_stderr_path", "Copy StdErr Path"),
        Binding("x", "kill_job", "Kill Job"),
        Binding("ctrl+r", "toggle_auto_refresh", "Auto Refresh"),
    ]

    def __init__(self, slurm_instance, **kwargs):
        super().__init__(**kwargs)
        self.slurm = slurm_instance
        self.jobs = []
        self.details_visible = False
        self.auto_refresh_timer = None
        self.auto_refresh_interval: int = 0

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield JobsTable(id="jobs_table")
        yield JobDetailsPanel(id="details_panel")
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self._update_title()
        self.refresh_jobs()

    def _update_title(self) -> None:
        """Update the app title, including auto-refresh status if active."""
        if self.auto_refresh_interval > 0:
            self.title = f"mjobs dashboard [Auto-refresh: {self.auto_refresh_interval}s]"
        else:
            self.title = "mjobs dashboard"

    def refresh_jobs(self):
        """Refresh job data."""
        try:
            # Get jobs from slurm instance (could be real or test implementation)
            extra_args = self._build_extra_args()
            self.jobs = self.slurm.get_jobs(self.slurm.args.job_id, extra_args)

            # Update table
            jobs_table = self.query_one("#jobs_table", JobsTable)
            jobs_table.populate_table(self.jobs)

        except Exception as e:
            self.notify(f"Error refreshing jobs: {e}", severity="error")

    def _build_extra_args(self) -> List[str]:
        """Build extra arguments for slurm job query."""
        extra_args = []
        args = self.slurm.args

        if args.user:
            extra_args.extend(["-u", args.user])
        if args.partition:
            extra_args.extend(["-p", args.partition])
        for state in args.states or []:
            extra_args.extend(["-t", state])
        for node in args.nodelist or []:
            extra_args.extend(["-w", node])

        return extra_args

    def action_search(self):
        """Show search modal."""

        def handle_search(search_text: str):
            if search_text:
                jobs_table = self.query_one("#jobs_table", JobsTable)
                jobs_table.filter_jobs(search_text)
                self.notify(f"Filtered jobs by: {search_text}", timeout=2)
            else:
                # Clear filter
                jobs_table = self.query_one("#jobs_table", JobsTable)
                jobs_table.filter_jobs("")
                self.notify("Cleared filter", timeout=2)

        self.push_screen(SearchScreen(), handle_search)

    def on_jobs_table_row_selected(self, message: JobsTable.RowSelected):
        """Handle job selection from table."""
        details_panel = self.query_one("#details_panel", JobDetailsPanel)
        details_panel.update_job_details(message.job, slurm_instance=self.slurm)
        details_panel.add_class("visible")
        self.details_visible = True

    def action_show_details(self):
        """Show details panel for selected job."""
        jobs_table = self.query_one("#jobs_table", JobsTable)
        selected_job = jobs_table.get_selected_job()

        if selected_job:
            details_panel = self.query_one("#details_panel", JobDetailsPanel)
            details_panel.update_job_details(selected_job, slurm_instance=self.slurm)
            details_panel.add_class("visible")
            self.details_visible = True

    def action_hide_details(self):
        """Hide details panel."""
        if self.details_visible:
            details_panel = self.query_one("#details_panel", JobDetailsPanel)
            details_panel.remove_class("visible")
            self.details_visible = False

    def action_refresh(self):
        """Manually refresh job data."""
        self.refresh_jobs()
        self.notify("Jobs refreshed", timeout=2)

    def action_open_stdout(self):
        """Open stdout file for the selected job."""
        self._open_specific_file("StdOut")

    def action_open_stderr(self):
        """Open stderr file for the selected job."""
        self._open_specific_file("StdErr")

    def _open_specific_file(self, file_type: str):
        """Open a specific file type (StdOut, StdErr, StdIn) for the selected job."""
        jobs_table = self.query_one("#jobs_table", JobsTable)
        selected_job = jobs_table.get_selected_job()

        if not selected_job:
            self.notify("No job selected", severity="warning")
            return

        # Get job details to find file paths
        if hasattr(self.slurm, "get_job_details"):
            details = self.slurm.get_job_details(selected_job.job_id)
        else:
            details = {}

        # Check if the requested file type exists and is valid
        if file_type not in details:
            self.notify(f"{file_type} not found for this job", severity="warning")
            return

        file_path = details[file_type]
        if not file_path or file_path in ["/dev/null", "None", "N/A", ""]:
            self.notify(f"{file_type} is not a valid file path: {file_path}", severity="info")
            return

        # Open the specific file
        self.open_file_viewer(file_path)

    def open_file_viewer(self, file_path: str):
        """Open the file viewer overlay for the given file path."""

        def handle_viewer_result(result):
            # File viewer doesn't return anything, just closes
            pass

        try:
            viewer = FileViewerScreen(file_path)
            self.push_screen(viewer, handle_viewer_result)
        except Exception as e:
            self.notify(f"Error opening file viewer: {e}", severity="error")

    def action_copy_stdout_path(self):
        """Copy stdout file path to clipboard."""
        self._copy_file_path("StdOut")

    def action_copy_stderr_path(self):
        """Copy stderr file path to clipboard."""
        self._copy_file_path("StdErr")

    def _copy_file_path(self, file_type: str):
        """Copy a specific file path to clipboard."""
        jobs_table = self.query_one("#jobs_table", JobsTable)
        selected_job = jobs_table.get_selected_job()

        if not selected_job:
            self.notify("No job selected", severity="warning")
            return

        # Get job details (reusing existing logic)
        if hasattr(self.slurm, "get_job_details"):
            details = self.slurm.get_job_details(selected_job.job_id)
        else:
            details = {}

        if file_type not in details:
            self.notify(f"{file_type} not found for this job", severity="warning")
            return

        file_path = details[file_type]
        if not file_path or file_path in ["/dev/null", "None", "N/A", ""]:
            self.notify(f"{file_type} path not available: {file_path}", severity="info")
            return

        # Copy to clipboard using Textual's built-in method
        try:
            self.copy_to_clipboard(file_path)
            self.notify(f"{file_type} path copied: {file_path}", timeout=3)
        except Exception as e:
            self.notify(f"Failed to copy {file_type} path: {e}", severity="error")

    def action_kill_job(self):
        """Kill the selected job after confirmation."""
        jobs_table = self.query_one("#jobs_table", JobsTable)
        selected_job = jobs_table.get_selected_job()

        if not selected_job:
            self.notify("No job selected", severity="warning")
            return

        def handle_confirm(confirmed: bool):
            if not confirmed:
                return
            try:
                self.slurm.cancel_job(selected_job.job_id)
                self.notify(f"Job {selected_job.job_id} cancelled", timeout=3)
                self.refresh_jobs()
            except Exception as e:
                self.notify(f"Failed to cancel job {selected_job.job_id}: {e}", severity="error")

        self.push_screen(ConfirmKillScreen(selected_job.job_id, selected_job.job_name), handle_confirm)

    def action_toggle_auto_refresh(self):
        """Toggle auto-refresh on/off."""
        if self.auto_refresh_timer is not None:
            self.auto_refresh_timer.stop()
            self.auto_refresh_timer = None
            self.auto_refresh_interval = 0
            self._update_title()
            self.notify("Auto-refresh off", timeout=2)
            return

        def handle_auto_refresh(value: str):
            if not value:
                return
            try:
                interval = int(value)
                if interval <= 0:
                    raise ValueError("must be positive")
            except ValueError:
                self.notify(f"Invalid interval: {value!r}", severity="error")
                return
            self.auto_refresh_interval = interval
            self.auto_refresh_timer = self.set_interval(interval, self.refresh_jobs)
            self._update_title()
            self.notify(f"Auto-refresh every {interval}s", timeout=2)

        self.push_screen(AutoRefreshScreen(), handle_auto_refresh)

    def action_quit(self):
        """Quit the application."""
        if self.auto_refresh_timer is not None:
            self.auto_refresh_timer.stop()
        self.exit()


def launch_dashboard(slurm_instance):
    """Launch the interactive dashboard."""
    app = Dashboard(slurm_instance)
    app.run()
