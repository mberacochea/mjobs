## AGENTS.md

### Key Commands
- `mjobs --dashboard`: Launch interactive TUI
- `mjobs -f "pattern"`: Filter jobs by regex on name/command
- `mjobs --test-data`: Use fake job data during development
- `mjobs --kill`: Cancel/kill filtered jobs (Slurm: `scancel`, LSF: use `--bkill` instead)
- `mjobs --kill` without `-f` or job IDs: prompts for confirmation before killing all jobs

### Build Commands
```bash
 task install        # Install dependencies
 task dev           # Install with dev dependencies
 task build        # Build macOS binary
 task build-linux  # Build Linux binary (via Docker)
 task clean        # Clean build artifacts
```

### Testing
```bash
 uv run pytest tests/ -v
```
- `test_repo.py` generates deterministic fake SlurmJob data (seed=42)
- Run tests with seeded data for reproducible results
- Mock `kill_job` when testing kill logic without `scancel` installed
- Use `click.testing.CliRunner` to test CLI command parsing

### Architecture
- **CLI framework**: Click (migrated from argparse)
- **CLI commands**: Defined in `cli.py` — two `@click.command()` functions (`slurm`, `lsf`)
- **Scheduler dispatch**: `main.py` detects scheduler + `--test-data` flag, routes to the right click command
- **Class hierarchy**: `Base` (render helpers) → `Slurm` / `LSF` (each has `run(**kwargs)`)
- **Data layer**: `JobRepository` ABC → `SlurmRepository` (real) / `TestJobRepository` (fake)
- **Output**: Rich for CLI tables, Textual for TUI dashboard
- **Scheduler priority**: Slurm-first approach

### CLI Option Notes
- LSF flags `-d`/`--recent` and `-p`/`--pend` lost their short forms in the click migration (conflicts with `--dashboard` and `--partition`). Use `--recent` and `--pend` instead.
- LSF option `-r`/`--run` and `-a`/`--all` are renamed internally to `show_run` and `show_all` in the click function to avoid Python builtin conflicts, then mapped back in `LSF.run()`.

### Constraints
- Keep Slurm/LSF implementations separate
- Use ruff for linting and formatting (line length: 120)
