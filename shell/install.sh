#!/bin/sh
# Add a `cc-init` helper to your shell so you can run commandcode-init directly
# from this checkout, without installing the package.
#
# Your shell configuration is only ever appended to. Existing content and
# aliases are never overwritten, and re-running the installer is safe: when the
# managed markers are already present, only that block is refreshed.

set -eu

BEGIN_MARK="# >>> commandcode-init >>>"
END_MARK="# <<< commandcode-init <<<"
PROGRAM=${0##*/}

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)

usage() {
    cat <<EOF
Usage: $PROGRAM [options]

Add a 'cc-init' function to your shell configuration so you can run
commandcode-init from this checkout without installing it.

Options:
  --shell NAME   Target shell: bash, zsh, fish or sh (default: from \$SHELL)
  --rc FILE      Write to FILE instead of the shell's default config file
  --print        Print the snippet and exit (nothing is written)
  --dry-run      Show the target file and snippet without writing
  -h, --help     Show this help

The snippet is wrapped in '$BEGIN_MARK' and
'$END_MARK' markers. When those markers already exist, only that
block is replaced; any other line in your config is left untouched.
EOF
}

print_snippet() {
    case $shell in
    fish)
        cat <<EOF
$BEGIN_MARK
function cc-init --description "Initialize project-local Command Code settings and hooks"
    set -l project_dir "$project_dir"
    if not test -f "\$project_dir/commandcode_init/__main__.py"
        printf 'Error: commandcode-init was not found in %s\n' "\$project_dir" >&2
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
    command env PYTHONPATH="\$project_dir" \$python_cmd -m commandcode_init \$argv
end
$END_MARK
EOF
        ;;
    *)
        cat <<EOF
$BEGIN_MARK
cc-init() {
    local project_dir="$project_dir"
    if [ ! -f "\$project_dir/commandcode_init/__main__.py" ]; then
        printf 'Error: commandcode-init was not found in %s\n' "\$project_dir" >&2
        return 1
    fi
    local python_cmd
    if command -v python3 >/dev/null 2>&1; then
        python_cmd=python3
    elif command -v python >/dev/null 2>&1; then
        python_cmd=python
    else
        printf 'Error: Python was not found in PATH.\n' >&2
        return 1
    fi
    PYTHONPATH="\$project_dir" command "\$python_cmd" -m commandcode_init "\$@"
}
$END_MARK
EOF
        ;;
    esac
}

detect_rc() {
    case $shell in
    fish) printf '%s\n' "${XDG_CONFIG_HOME:-$HOME/.config}/fish/config.fish" ;;
    zsh) printf '%s\n' "${ZDOTDIR:-$HOME}/.zshrc" ;;
    bash)
        if [ "$(uname -s 2>/dev/null)" = "Darwin" ] && [ -f "$HOME/.bash_profile" ] && [ ! -f "$HOME/.bashrc" ]; then
            printf '%s\n' "$HOME/.bash_profile"
        else
            printf '%s\n' "$HOME/.bashrc"
        fi
        ;;
    *) printf '%s\n' "$HOME/.profile" ;;
    esac
}

write_rc() {
    rc=$1
    db=$(dirname -- "$rc")
    [ -d "$db" ] || mkdir -p -- "$db"

    if [ -f "$rc" ] && grep -qF -- "$BEGIN_MARK" "$rc"; then
        tmp=$rc.cc-init.$$
        trap 'rm -f -- "$tmp"' EXIT HUP INT TERM
        awk -v b="$BEGIN_MARK" -v e="$END_MARK" \
            '$0==b{s=1;next} $0==e{s=0;next} !s' "$rc" > "$tmp"
        mv -- "$tmp" "$rc"
        trap - EXIT HUP INT TERM
    fi

    [ -f "$rc" ] || : > "$rc"
    if [ -s "$rc" ]; then
        last=$(tail -c 1 -- "$rc" || true)
        [ -z "$last" ] || printf '\n' >> "$rc"
    fi
    print_snippet >> "$rc"
    printf '\n' >> "$rc"
}

shell=""
rc=""
mode=write
while [ $# -gt 0 ]; do
    case $1 in
    --shell) shell=$2; shift 2 ;;
    --shell=*) shell=${1#*=}; shift ;;
    --rc) rc=$2; shift 2 ;;
    --rc=*) rc=${1#*=}; shift ;;
    --print) mode=print; shift ;;
    --dry-run) mode=dry; shift ;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
        printf 'Unknown option: %s\n\n' "$1" >&2
        usage >&2
        exit 2
        ;;
    esac
done

if [ -z "$shell" ]; then
    case ${SHELL:-} in
    */fish) shell=fish ;;
    */zsh) shell=zsh ;;
    */bash) shell=bash ;;
    *) shell=sh ;;
    esac
fi

case $shell in
bash | zsh | fish | sh) ;;
*)
    printf 'Unsupported shell: %s (use bash, zsh, fish or sh)\n' "$shell" >&2
    exit 2
    ;;
esac

if [ ! -f "$project_dir/commandcode_init/__main__.py" ]; then
    printf 'Error: commandcode-init was not found in %s\n' "$project_dir" >&2
    exit 1
fi

[ -n "$rc" ] || rc=$(detect_rc)

case $mode in
print)
    print_snippet
    ;;
dry)
    printf 'Shell:  %s\n' "$shell"
    printf 'Target: %s\n' "$rc"
    printf 'Snippet that would be written:\n\n'
    print_snippet
    ;;
write)
    write_rc "$rc"
    printf 'Added cc-init to %s\n' "$rc"
    printf 'Reload it with: source %s   (or open a new shell)\n' "$rc"
    ;;
esac
