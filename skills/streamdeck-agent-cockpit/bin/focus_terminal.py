#!/usr/bin/env python3
"""Focus the macOS terminal pane that owns a claimed slot.

Matches on the tty recorded when the slot was claimed, because agent session
ids are invisible to the terminal emulator. Supports iTerm2 and Apple Terminal;
both expose a documented `tty` property through AppleScript.

Exits non-zero when the slot is unclaimed or the pane is gone, so a key reports
an honest failure instead of a false success.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import slotclaims  # noqa: E402

ITERM2 = '''
on run argv
  set wantedTty to item 1 of argv
  tell application "iTerm2"
    repeat with w in windows
      repeat with t in tabs of w
        repeat with s in sessions of t
          if (tty of s) is wantedTty then
            select w
            select t
            select s
            activate
            return "ok"
          end if
        end repeat
      end repeat
    end tell
  end tell
  return "not_found"
end run
'''

APPLE_TERMINAL = '''
on run argv
  set wantedTty to item 1 of argv
  tell application "Terminal"
    repeat with w in windows
      repeat with t in tabs of w
        if (tty of t) is wantedTty then
          set selected tab of w to t
          set index of w to 1
          activate
          return "ok"
        end if
      end repeat
    end repeat
  end tell
  return "not_found"
end run
'''

APPS = (("iTerm2", ITERM2), ("Terminal", APPLE_TERMINAL))


def is_running(app: str) -> bool:
    try:
        result = subprocess.run(
            ["osascript", "-e", f'application "{app}" is running'],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.stdout.strip() == "true"


def try_focus(script: str, tty: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["osascript", "-", tty],
            input=script, capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"osascript failed: {exc}"
    if result.returncode != 0:
        return result.stderr.strip() or "osascript returned an error"
    return None if result.stdout.strip() == "ok" else "not_found"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slot", required=True, help="Session id declared in cockpit.json")
    parser.add_argument("--app", choices=[name for name, _ in APPS],
                        help="Restrict to one terminal application")
    args = parser.parse_args()

    claim = slotclaims.load().get("slots", {}).get(args.slot)
    if not slotclaims.claim_is_live(claim):
        print(f"slot not claimed: {args.slot}", file=sys.stderr)
        return 1
    tty = str((claim or {}).get("tty") or "")
    if not tty:
        print(f"no terminal recorded for {args.slot}", file=sys.stderr)
        return 1

    candidates = [(n, s) for n, s in APPS if args.app in (None, n)]
    problems = []
    for name, script in candidates:
        if not is_running(name):
            continue
        problem = try_focus(script, tty)
        if problem is None:
            return 0
        problems.append(f"{name}: {problem}")

    print(f"no terminal session with tty {tty}" if not problems else "; ".join(problems),
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
