# mjobs - Claude Code Instructions

## Project Overview
mjobs (v2.0.0) is a Python CLI tool that provides a nicer interface on top of Slurm and LSF job schedulers. It uses Rich for CLI table output and Textual for an interactive TUI dashboard. Apache-2.0 licensed, authored by Martin Beracochea.

## Architecture

### Entry Flow
`mjobs/main.py:main()` -> detects scheduler via `core/factory.py:detect_scheduler()` -> creates `JobRepository` via factory -> instantiates `Slurm` or `LSF` -> calls `.main()`.

### Key Patterns
- **Repository pattern**: `data/repository.py:JobRepository` (ABC) with `SlurmRepository` (real squeue/scontrol) and `TestJobRepository` (fake data). Slurm uses this; LSF still uses direct subprocess calls.
- **Inheritance**: `Base` (ABC) -> `Slurm` / `LSF`. Base handles argparse, table rendering (Rich), TSV output.
- **Dashboard**: `Slurm.main()` launches `dashboard.py:Dashboard` (Textual App) when `--dashboard` flag is set. Dashboard only works with Slurm (not LSF).
- **Data model**: `models/job.py:SlurmJob` (Pydantic BaseModel) with validators, `from_squeue_line()` parser, `from_dict()` for test data.

### Key Files
- `mjobs/main.py` - Entry point, scheduler detection
- `mjobs/base.py` - Base class: argparse, Rich table rendering
- `mjobs/slurm.py` - Slurm CLI implementation (uses repository)
- `mjobs/lsf.py` - LSF CLI implementation (direct bjobs JSON parsing)
- `mjobs/dashboard.py` - Textual TUI app (Dashboard, SearchScreen)
- `mjobs/models/job.py` - SlurmJob Pydantic model, SQUEUE_FIELDS
- `mjobs/data/repository.py` - JobRepository ABC, JobRepositoryError
- `mjobs/data/slurm_repo.py` - SlurmRepository (real squeue/scontrol)
- `mjobs/data/test_repo.py` - TestJobRepository (fake data generator)
- `mjobs/core/factory.py` - create_job_repository(), detect_scheduler()
- `mjobs/widgets/` - Textual widgets: JobsTable, JobDetailsPanel, FileViewerScreen, ClickablePath, SearchOverlay

### Dashboard Keybindings
q=Quit, Ctrl+F=Search, Enter=Details, Escape=Hide Details, r=Refresh, o=StdOut, e=StdErr, Ctrl+O/E=Copy paths, j/k=Navigate

## Code Style
- Line length: 120 (ruff + black)
- Type hints on all functions
- Docstrings: reStructuredText (reST) style
- All files have Apache-2.0 license headers

## Build & Dev Commands
```bash
task install        # uv sync
task dev            # uv sync --extra dev
task run            # uv run mjobs
task run-dashboard  # uv run mjobs --dashboard --test-data
task lint           # uv run ruff check .
task lint-fix       # uv run ruff check --fix .
task format         # uv run ruff format .
task format-check   # uv run ruff format --check .
task test           # uv run pytest
task build          # pyinstaller macOS binary
task build-linux    # Docker cross-compile Linux binary
task check          # lint + format-check
task clean          # rm build artifacts
```

## Usage
```bash
mjobs                          # Show jobs table (auto-detects scheduler)
mjobs -f "pattern"             # Filter jobs by regex
mjobs -u alice -t running      # Filter by user and state (Slurm)
mjobs -e                       # Extended output (nodes, workdir)
mjobs --dashboard              # Interactive TUI (Slurm only)
mjobs --dashboard --test-data  # TUI with fake data (no Slurm needed)
mjobs --tsv                    # TSV output for piping
```

## Dependencies
- `rich>=13.7.0` - CLI tables and formatting
- `rich-argparse>=1.4.0` - Pretty help text
- `textual>=0.75.1` - Interactive TUI dashboard
- `pydantic>=2.0.0` - Data model validation
- Build tooling: hatchling, pyinstaller, ruff, pytest

## Development Notes
- Use `--test-data` flag for development without Slurm/LSF installed
- LSF implementation has not been refactored to use the repository pattern yet
- LSF does not support `--dashboard` mode
- `Base.__init__` has a bug: `self.error_console = console` (ignores error_console param)
- Test with various terminal sizes when working on TUI components
