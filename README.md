# mjobs

Just like squeue and bjobs but a bit nicer.

A command-line tool that displays Slurm (squeue) or LSF (bjobs) jobs in a more readable format. For Slurm users, mjobs also includes an interactive dashboard for browsing jobs with filtering and detailed views.

## Install

Currently, mjobs is not published to PyPI. Clone the repository and use uv for development:

```bash
git clone https://github.com/mberacochea/mjobs.git
cd mjobs
uv sync
```

## Usage

mjobs automatically detects your scheduler and shows a nice table:

```bash
mjobs                    # Show jobs table
mjobs -u alice           # Filter by user
mjobs --dashboard        # Launch interactive dashboard (Slurm only)
mjobs --test-data        # Use fake data for testing
```

The dashboard provides an interactive interface with job filtering, detailed views, and file path copying. Use arrow keys to navigate, Enter to show details, and Ctrl+F to search.

## Development

For development work, use the Taskfile commands:

```bash
task install            # Install dependencies
task dev               # Install with dev dependencies
task build             # Build macOS binary
task build-linux       # Build Linux binary via Docker
task clean             # Clean build artifacts
```

Development install:

```bash
uv sync --dev
```

## Build and Deploy

We use pyinstaller to create standalone binaries that don't require Python on HPC login nodes. The Taskfile includes build steps that handle cross-platform compilation:

```bash
task build              # For local platform
task build-linux       # Build Linux binary via Docker
```

Note: On Apple Silicon Macs, the Linux build uses Docker and requires Rosetta 2 to be enabled for x86_64 emulation.

Binaries are created in the `dist/` directory and can be deployed directly to HPC systems.
