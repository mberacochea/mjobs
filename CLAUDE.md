# mjobs - Claude Code Instructions

## Project Overview
mjobs is a Python application that provides a nicer interface on top of Slurm and LSF job schedulers. It uses the Rich library for beautiful CLI table output and is being extended with an interactive dashboard using Textual.

## Current Development Focus
- Interactive Dashboard: Adding a persistent TUI interface with job filtering, selection, and detailed views
- Slurm-first approach: Initial implementation focuses on Slurm support before extending to LSF
- Test data generation: Creating fake job data for development without requiring actual Slurm/LSF installation

## Development Guidelines

### Code Style
- Follow existing patterns in the codebase
- Use type hints extensively
- Add docstrings following reStructuredText (reST) style
- Format with black (line length: 120)
- Use ruff for linting

### Architecture
- Maintain backward compatibility with existing CLI functionality
- Extend the existing `Base` class for new features
- Keep Slurm and LSF implementations separate
- Use Rich for CLI output, Textual for TUI components

### Key Files
- `mjobs/base.py`: Base class with common functionality and argument parsing
- `mjobs/slurm.py`: Slurm-specific implementation
- `mjobs/lsf.py`: LSF-specific implementation
- `mjobs/main.py`: Entry point that detects available scheduler
- `robots/dashboard-implementation-plan.md`: Detailed implementation plan and progress tracking

### Testing
- Use test data generation during development (`--test-data` flag)
- Test with various terminal sizes for TUI components
- Validate both CLI and dashboard modes
- Ensure compatibility with existing functionality

### Dependencies
- Rich: For CLI table formatting and colors
- Textual: For interactive TUI dashboard (to be added)
- Standard library modules for subprocess calls and data handling

## Implementation Status
Current focus is on implementing the interactive dashboard feature. Progress is tracked in:
- `robots/dashboard-implementation-plan.md`: Comprehensive implementation plan with progress tracking
- Todo list maintained during development sessions

## Build Commands
```bash
task install           # Install dependencies
task dev               # Install with dev dependencies
task build             # Build macOS binary
task build-linux       # Build Linux binary (via Docker)
task clean             # Clean build artifacts
```

## Usage
```bash
mjobs                   # Show jobs table
mjobs -f "pattern"     # Filter jobs by pattern
mjobs --dashboard      # Launch interactive TUI (planned)
```

## Notes for Future Sessions
- Update progress in `robots/dashboard-implementation-plan.md` as work progresses
- Use TodoWrite tool to track current session progress
- Test both CLI and dashboard modes before completing features
- Consider performance implications with large job lists
