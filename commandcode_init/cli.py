import argparse
import json
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path


def install_uv():
    if sys.platform == "win32":
        command = ["powershell", "-ExecutionPolicy", "ByPass", "-c", "irm https://astral.sh/uv/install.ps1 | iex"]
    else:
        command = ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"]
    print("Installing uv...")
    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(prog="cc-init", description="Initialize project-local Command Code settings and hooks.")
    parser.add_argument("directory", nargs="?", default=".")
    parser.add_argument("--force", action="store_true", help="Replace existing files, keeping backups")
    parser.add_argument("--no-gitignore", action="store_true")
    parser.add_argument("--venv", action="store_true", help="Create a .venv in the target directory (uv, falling back to python -m venv)")
    parser.add_argument("--install-uv", action="store_true", dest="install_uv", help="Install uv if it is not already on PATH")
    parser.add_argument("--uv-init", action="store_true", dest="uv_init", help="Run `uv init` in the target directory (for Python projects)")
    ns = parser.parse_args()
    root = Path(ns.directory).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    resources = files("commandcode_init").joinpath("templates")
    config = json.loads(resources.joinpath("settings.local.json").read_text(encoding="utf-8"))
    script = root / ".commandcode/hooks/require-rtk.py"
    argv = [sys.executable, str(script)]
    command = subprocess.list2cmdline(argv) if sys.platform == "win32" else shlex.join(argv)
    config["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = command
    targets = {
        root / ".commandcode/settings.local.json": json.dumps(config, indent=2) + "\n",
        script: resources.joinpath("require-rtk.py").read_text(encoding="utf-8"),
    }
    for path, content in targets.items():
        if path.exists():
            if not ns.force:
                print(f"KEEP    {path}")
                continue
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = path.with_name(path.name + ".bak." + stamp)
            backup.write_bytes(path.read_bytes())
            print(f"BACKUP  {backup}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"WRITE   {path}")
    if not ns.no_gitignore:
        ignore = root / ".gitignore"
        existing = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
        entries = ["/.commandcode/settings.local.json", "/.commandcode/hooks/require-rtk.py", "/.commandcode/**/*.bak.*"]
        missing = [entry for entry in entries if entry not in existing.splitlines()]
        if missing:
            separator = "" if not existing or existing.endswith("\n") else "\n"
            with ignore.open("a", encoding="utf-8") as f:
                f.write(separator + "\n# Personal Command Code configuration\n" + "\n".join(missing) + "\n")
            print(f"UPDATE  {ignore}")
    if ns.install_uv:
        sys.stdout.flush()
        if shutil.which("uv") is None:
            try:
                install_uv()
            except (FileNotFoundError, subprocess.CalledProcessError) as exc:
                print(f"Error: uv installation failed ({exc}).", file=sys.stderr)
                sys.exit(1)
        else:
            print("uv is already installed.")
    if ns.uv_init:
        sys.stdout.flush()
        uv = shutil.which("uv")
        if uv is None:
            print("Error: uv was not found in PATH. Pass --install-uv to install uv.", file=sys.stderr)
            sys.exit(1)
        try:
            subprocess.run([uv, "init"], cwd=root, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"Error: `uv init` failed with exit code {exc.returncode}.", file=sys.stderr)
            sys.exit(exc.returncode)
    if ns.venv:
        sys.stdout.flush()
        uv = shutil.which("uv")
        try:
            if uv:
                subprocess.run([uv, "venv"], cwd=root, check=True)
            else:
                print(
                    "uv was not found in PATH; falling back to `python -m venv`. "
                    "Pass --install-uv to install uv.",
                    file=sys.stderr,
                )
                subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=root, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"Error: virtual environment creation failed with exit code {exc.returncode}.", file=sys.stderr)
            sys.exit(exc.returncode)
    print("Done. Existing global Command Code settings still apply.")


if __name__ == "__main__":
    main()
