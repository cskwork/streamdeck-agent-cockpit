#!/usr/bin/env python3
"""Claude Code hook bridge: report an already-running session to cockpitd.

Reads a hook payload on stdin, claims a cockpit slot for the Claude Code
session, and reports an evidence-backed semantic state. State comes only from
hook events; terminal titles are never scraped.

Register with `install_claude_hooks.py`. Other agents need their own bridge —
the slot and focus machinery is agent-neutral, only this event mapping is not.

This script never fails loudly. A broken cockpit must not disturb the agent
session that is hosting it.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import slotclaims  # noqa: E402

AGENT = "claude"
SLOT_COUNT = int(os.environ.get("COCKPIT_SLOT_COUNT", "4"))

# hook_event_name -> (state, detail, ttl seconds)
EVENT_MAP = {
    "SessionStart": ("idle", "session started", 7200),
    "UserPromptSubmit": ("running", "working", 1800),
    "Stop": ("idle", "response complete", 7200),
}

# Substring of the Notification message -> (state, detail, ttl seconds)
NOTIFICATION_MAP = (
    ("permission", ("needs_attention", "approval required", 3600)),
    ("idle", ("needs_attention", "waiting for input", 3600)),
    ("elicit", ("needs_attention", "input requested", 3600)),
    ("waiting", ("needs_attention", "waiting", 3600)),
)


def config_path() -> str:
    return str(slotclaims.cockpit_home() / "cockpit.json")


def project_label(cwd: str) -> str:
    return (os.path.basename(cwd.rstrip("/")) or cwd or AGENT)[:40]


def resolve(event: str, payload: Dict[str, Any]) -> Optional[Tuple[str, str, int]]:
    if event in EVENT_MAP:
        return EVENT_MAP[event]
    if event == "Notification":
        message = str(payload.get("message") or "").lower()
        for needle, result in NOTIFICATION_MAP:
            if needle in message:
                return result
        return ("needs_attention", "notification", 3600)
    return None


def post_report(slot: str, state: str, label: str, detail: str, ttl: int) -> None:
    from cockpitctl import Client, load_config, read_token  # noqa: E402

    config = load_config(config_path())
    server = config.get("server", {})
    client = Client(
        f"http://{server.get('host', '127.0.0.1')}:{int(server.get('port', 39393))}",
        read_token(server.get("tokenFile", "~/.agent-cockpit/token")),
        timeout=5.0,
    )
    client.request(
        "POST",
        f"/v1/sessions/{slot}/report",
        {
            "state": state,
            "label": label[:120],
            "detail": detail[:500],
            "ttl": ttl,
            "source": "claude-hook",
        },
    )


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, OSError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    session_id = str(payload.get("session_id") or "")
    if not session_id:
        return 0
    event = str(payload.get("hook_event_name") or "")
    cwd = str(payload.get("cwd") or "")

    data = slotclaims.load()

    if event == "SessionEnd":
        if slotclaims.release(data, session_id):
            slotclaims.save(data)
        return 0

    resolved = resolve(event, payload)
    if resolved is None:
        return 0
    state, detail, ttl = resolved

    slot = slotclaims.acquire(data, session_id, AGENT, SLOT_COUNT)
    if slot is None:
        return 0  # every slot is busy; stay silent rather than evict a session

    owner = slotclaims.discover_owner()
    data.setdefault("slots", {})[slot] = {
        "agentSessionId": session_id,
        "agent": AGENT,
        "cwd": cwd,
        "project": project_label(cwd),
        "pid": owner.get("pid"),
        "tty": owner.get("tty"),
        "updatedAt": time.time(),
    }
    slotclaims.save(data)

    try:
        post_report(slot, state, project_label(cwd), detail, ttl)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        raise SystemExit(0)
