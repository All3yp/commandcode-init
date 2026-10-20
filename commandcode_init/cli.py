import argparse
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Initialize project-local Command Code settings and hooks.")
    parser.add_argument("directory", nargs="?", default=".")
    parser.add_argument("--force", action="store_true", help="Replace existing files, keeping backups")
    parser.add_argument("--no-gitignore", action="store_true")
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
    print("Done. Existing global Command Code settings still apply.")


if __name__ == "__main__":
    main()
