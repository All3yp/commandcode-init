# commandcode-init helper for fish.
#
# Source this file from your fish config:
#
#     source /path/to/commandcode-init/shell/cc-init.fish
#
# The checkout directory is detected from this file's location. If you copy the
# file somewhere else, set COMMANDCODE_INIT_DIR to the checkout path first, e.g.
# `set -gx COMMANDCODE_INIT_DIR /path/to/commandcode-init`.
#
# Prefer the automatic installer (`shell/install.sh`), which writes an
# equivalent function straight into your config with the path already resolved.

set -q COMMANDCODE_INIT_DIR; or set -g COMMANDCODE_INIT_DIR (cd (status dirname)/..; and pwd)

function cc-init --description "Initialize project-local Command Code settings and hooks" --inherit-variable COMMANDCODE_INIT_DIR
    set -l project_dir "$COMMANDCODE_INIT_DIR"

    if not test -f "$project_dir/commandcode_init/__main__.py"
        printf 'Error: commandcode-init was not found in %s\n' "$project_dir" >&2
        printf 'Set COMMANDCODE_INIT_DIR to the checkout path and try again.\n' >&2
        return 1
    end

    set -l python_cmd
    if command -q python3
        set python_cmd python3
    else if command -q python
        set python_cmd python
    else
        printf 'Error: Python was not found in PATH.\n' >&2
        return 1
    end

    command env PYTHONPATH="$project_dir" $python_cmd -m commandcode_init $argv
end
