# AGENTS

This is **commandcode-init**, a simple initializer for Command Code settings
and hooks in new projects.

## Goal

Avoid copying settings and hooks manually into every new project. The command
`cc-init .` sets everything up at once.

## Before anything else

Read **`README.md`** in full — it contains all project documentation, including
installation, usage, options, and limitations.

## How it works

- `cc-init <dir>` creates `.commandcode/settings.local.json` and
  `.commandcode/hooks/require-rtk.py` in the target directory.
- Existing files are preserved by default; `--force` makes timestamped backups.
- `--no-gitignore` disables `.gitignore` updates.
- `--venv`, `--uv-init`, and `--install-uv` are optional Python options (not
  applied unless requested).

## Project structure

```
commandcode_init/    # Python code (cli.py, __main__.py, templates/)
shell/               # Shell helper install scripts
README.md            # Full documentation
AGENTS.md            # This file
```

## Conventions

- Follow the existing code patterns and conventions.
- Tests, when added, go in a `tests/` directory.
- New or updated documentation should go in `README.md`.
