#!/usr/bin/env python3
"""Register the Claude Code hook bridge in a Claude Code settings file.

Append-only and idempotent: existing hook blocks are never rewritten, reordered,
or removed, and re-running adds nothing. Always preview with `--dry-run` first,
and keep a backup of the settings file before the first write.

Events registered, matching the state mapping in `claude_hook.py`:

    SessionStart · UserPromptSubmit · Notification · Stop · SessionEnd
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

HOOK_SCRIPT = Path(__file__).resolve().parent / "claude_hook.py"

# event -> whether the event supports a matcher (per Claude Code hook docs)
EVENTS = {
    "SessionStart": True,
    "UserPromptSubmit": False,
    "Notification": True,
    "Stop": False,
    "SessionEnd": True,
}


def command_string(interpreter: str) -> str:
    # `|| true` keeps a cockpit failure from surfacing in the user's session.
    return f"{interpreter} {HOOK_SCRIPT} || true"


def block(command: str, with_matcher: bool) -> Dict[str, Any]:
    handler = {"type": "command", "command": command, "async": True, "timeout": 15}
    return {"matcher": "*", "hooks": [handler]} if with_matcher else {"hooks": [handler]}


def already_present(blocks: List[Any]) -> bool:
    for entry in blocks:
        for handler in (entry or {}).get("hooks", []):
            if HOOK_SCRIPT.name in str((handler or {}).get("command", "")):
                return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", default="~/.claude/settings.json",
                        help="Claude Code settings file to modify")
    parser.add_argument("--interpreter", default=sys.executable,
                        help="Absolute path to a Python 3.10+ interpreter")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    settings = Path(os.path.expanduser(args.settings))
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"settings file not found: {settings}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid JSON in {settings}: {exc}", file=sys.stderr)
        return 1

    command = command_string(args.interpreter)
    hooks = data.setdefault("hooks", {})
    added = []
    for event, with_matcher in EVENTS.items():
        blocks = hooks.setdefault(event, [])
        if already_present(blocks):
            continue
        blocks.append(block(command, with_matcher))
        added.append(event)

    if not added:
        print("no change; the hook bridge is already registered")
        return 0

    print(f"command: {command}")
    print("events to add: " + ", ".join(added))
    if args.dry_run:
        print("(dry run; nothing written)")
        return 0

    tmp = settings.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(settings)
    print(f"installed: {settings}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
