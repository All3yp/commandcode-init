import json
import shlex
import sys
from pathlib import Path
from typing import NoReturn


def deny(reason: str) -> NoReturn:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason
    }}))
    sys.exit(0)


try:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command", "")
    args = tool_input.get("args", [])
    if not isinstance(command, str):
        deny("The shell command must be a string.")
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        deny("Shell arguments must be a list of strings.")
    if any(c in command for c in "\n\r;&|<>`$"):
        deny("Submit a single RTK command without shell operators or expansions.")
    tokens = shlex.split(command)
    tokens.extend(args)
except Exception:
    deny("Unable to parse the shell request. Submit a simple RTK command.")

if not tokens:
    deny("Empty shell commands are not allowed.")
if Path(tokens[0]).name.lower() not in {"rtk", "rtk.exe"}:
    deny(
        "Token-saving policy: every shell command must run through RTK. "
        "Retry using the equivalent command supported by RTK. "
        "Examples: rtk git status, rtk ls, rtk read filename. "
        "Do not bypass this policy using bash -c, scripts, aliases, or other wrappers."
    )
