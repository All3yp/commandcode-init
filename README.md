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

## Usage

    cc-init .
    cc-init ../my-project
    cc-init . --force
    cc-init . --no-gitignore

Existing files are preserved by default. --force makes timestamped backups.
Creates .commandcode/settings.local.json and .commandcode/hooks/require-rtk.py.
Updates .gitignore unless disabled. No Git repository is required or created.
The hook command uses the absolute current Python interpreter and hook path;
rerun with --force if you move the project or remove that Python installation.
Restart Command Code after initialization, opening it in the project root.

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
