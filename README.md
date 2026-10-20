# commandcode-init

Initialize personal Command Code settings and an RTK-enforcement hook.

## Install
From this extracted directory:

    python -m pip install --user .

Or, if pipx is installed:

    pipx install .

Use `python3` or `py` instead of `python` if needed.
The Python scripts directory must be on PATH for cc-init to be available.
Alternative without installing: python -m commandcode_init .

## Shell helper

Installing with pip already gives you a `cc-init` command. If you would rather
run commandcode-init straight from this checkout, add a small `cc-init` helper
to your shell. The installer detects your shell (bash, zsh, fish or sh) and
appends the helper to the matching config file:

    ./shell/install.sh

It writes a block wrapped in `# >>> commandcode-init >>>` and
`# <<< commandcode-init <<<` markers. Your existing configuration and aliases
are never overwritten, and re-running the installer only refreshes that block.
Preview without writing:

    ./shell/install.sh --dry-run
    ./shell/install.sh --print
    ./shell/install.sh --shell zsh --rc ~/.zshrc

Then reload your shell (`source` the config file, or open a new terminal) and
run `cc-init .`.

To set it up by hand instead:

fish (`~/.config/fish/config.fish`):

    source /path/to/commandcode-init/shell/cc-init.fish

bash (`~/.bashrc`), zsh (`~/.zshrc`) or sh (`~/.profile`):

    cc-init() {
        PYTHONPATH="/path/to/commandcode-init" python3 -m commandcode_init "$@"
    }

If you move the checkout, re-run `./shell/install.sh` (or update the path) so
the helper points at the new location.

## Usage

    cc-init .
    cc-init ../my-project
    cc-init . --force
    cc-init . --no-gitignore
    cc-init . --venv
    cc-init . --uv-init
    cc-init . --venv --install-uv

Existing files are preserved by default. --force makes timestamped backups.
Creates .commandcode/settings.local.json and .commandcode/hooks/require-rtk.py.
Updates .gitignore unless disabled. No Git repository is required or created.
The hook command uses the absolute current Python interpreter and hook path;
rerun with --force if you move the project or remove that Python installation.
Restart Command Code after initialization, opening it in the project root.

Optional Python setup, never applied unless you ask for it, so non-Python
projects are left untouched:

* `--venv` creates a `.venv` in the target directory. It uses `uv venv` when uv
  is on PATH and falls back to `python -m venv` otherwise.
* `--uv-init` runs `uv init` in the target directory (pyproject.toml, src/, and,
  if the directory is not already a repository, a Git repo). It requires uv on
  PATH; use it only for Python projects.
* `--install-uv` installs uv when it is not already on PATH (see below).

## Installing uv

`--install-uv` runs the official Astral installer:

    curl -LsSf https://astral.sh/uv/install.sh | sh     # Linux / macOS
    irm https://astral.sh/uv/install.ps1 | iex          # Windows (PowerShell)

It installs the `uv` binary into `~/.local/bin`, which must be on PATH. If you
would rather install uv yourself, any of these work:

    pipx install uv
    python -m pip install --user uv
    pacman -S uv                                        # Arch / CachyOS
    brew install uv                                     # macOS

uv is only needed for `--venv` (as the preferred backend) and `--uv-init`;
cc-init itself needs nothing beyond Python.

## Policy and limitations

Settings are copied from your supplied configuration: yolo default, sensitive
file deny rules, git push asks, and a shell PreToolUse hook. Bypass push ask
patterns are included as defense in depth, not as a complete push detector.
Global settings remain in effect. This does not fix an application/version
that ignores defaultMode; verify the actual mode separately.

The hook requires the first executable to be rtk or rtk.exe, and conservatively
rejects shell metacharacters in the command string even inside quotes. It is
not a shell parser, sandbox, trusted-executable check, or secrets boundary.
RTK commands may run arbitrary programs; RTK does not guarantee compression
of every command. Scripts, internal wrappers and arguments can bypass the
intent of the policy. Native file tools do not go through this shell hook.
Read/Edit deny rules do not restrict OS-level reads by shell programs.
Cave compress is not included: the exact tool has not been identified.
No runtime dependency beyond Python; RTK and Command Code must be installed
separately. Review the generated settings before use.
