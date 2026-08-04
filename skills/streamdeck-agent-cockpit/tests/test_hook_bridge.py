"""Tests for the Claude Code event mapping and the Windows Terminal focus path."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))

import claude_hook  # noqa: E402
import focus_terminal  # noqa: E402
import install_claude_hooks  # noqa: E402


class EventMappingTest(unittest.TestCase):
    def test_stop_is_idle_not_a_success_state(self) -> None:
        state, _, _ = claude_hook.EVENT_MAP["Stop"]
        self.assertEqual(state, "idle")

    def test_permission_events_split_attention_from_blocked(self) -> None:
        self.assertEqual(claude_hook.EVENT_MAP["PermissionRequest"][0], "needs_attention")
        self.assertEqual(claude_hook.EVENT_MAP["PermissionDenied"][0], "blocked")

    def test_stop_failure_is_the_only_failed_event(self) -> None:
        failed = [name for name, (state, _, _) in claude_hook.EVENT_MAP.items() if state == "failed"]
        self.assertEqual(failed, ["StopFailure"])

    def test_every_state_is_part_of_the_published_vocabulary(self) -> None:
        allowed = {"idle", "running", "needs_attention", "blocked", "succeeded", "failed"}
        for name, (state, _, ttl) in claude_hook.EVENT_MAP.items():
            self.assertIn(state, allowed, name)
            self.assertGreater(ttl, 0, name)

    def test_notification_type_wins_over_the_message_fallback(self) -> None:
        payload = {"notification_type": "permission_prompt", "message": "all quiet"}
        self.assertEqual(claude_hook.resolve("Notification", payload)[0], "needs_attention")

    def test_notification_falls_back_to_the_message(self) -> None:
        payload = {"message": "Claude needs your permission to run Bash"}
        self.assertEqual(claude_hook.resolve("Notification", payload)[0], "needs_attention")

    def test_completion_notification_is_idle(self) -> None:
        self.assertEqual(claude_hook.resolve("Notification", {"notification_type": "agent_completed"})[0], "idle")

    def test_unknown_event_is_ignored(self) -> None:
        self.assertIsNone(claude_hook.resolve("SomethingElse", {}))

    def test_registered_events_are_all_mapped(self) -> None:
        registered = set(install_claude_hooks.EVENTS) | set(install_claude_hooks.EXTENDED_EVENTS)
        handled = set(claude_hook.EVENT_MAP) | {"Notification", "SessionEnd"}
        self.assertEqual(registered - handled, set())

    def test_extended_events_are_opt_in(self) -> None:
        self.assertEqual(set(install_claude_hooks.EVENTS) & set(install_claude_hooks.EXTENDED_EVENTS), set())


class WindowsTerminalFocusTest(unittest.TestCase):
    def test_helper_script_ships_with_the_runtime(self) -> None:
        self.assertTrue(focus_terminal.WINDOWS_TERMINAL_SCRIPT.exists())

    def test_focus_reports_a_problem_when_no_tab_matches(self) -> None:
        captured = {}

        def fake_run(argv, **kwargs):
            captured["argv"] = argv
            return type("R", (), {"returncode": 3, "stdout": "", "stderr": "no tab"})()

        original = focus_terminal.subprocess.run
        focus_terminal.subprocess.run = fake_run  # type: ignore[assignment]
        try:
            problem = focus_terminal.focus_windows_terminal("Claude · Main")
        finally:
            focus_terminal.subprocess.run = original  # type: ignore[assignment]
        self.assertEqual(problem, "no tab")
        self.assertIn("-TabTitle", captured["argv"])
        self.assertEqual(captured["argv"][-1], "Claude · Main")

    def test_focus_succeeds_only_on_the_focused_marker(self) -> None:
        def fake_run(argv, **kwargs):
            return type("R", (), {"returncode": 0, "stdout": "focused\n", "stderr": ""})()

        original = focus_terminal.subprocess.run
        focus_terminal.subprocess.run = fake_run  # type: ignore[assignment]
        try:
            self.assertIsNone(focus_terminal.focus_windows_terminal("Claude · Main"))
        finally:
            focus_terminal.subprocess.run = original  # type: ignore[assignment]

    def test_missing_powershell_is_an_honest_failure(self) -> None:
        def fake_run(argv, **kwargs):
            raise FileNotFoundError(argv[0])

        original = focus_terminal.subprocess.run
        focus_terminal.subprocess.run = fake_run  # type: ignore[assignment]
        try:
            problem = focus_terminal.focus_windows_terminal("Claude · Main")
        finally:
            focus_terminal.subprocess.run = original  # type: ignore[assignment]
        self.assertIn("not found", str(problem))


if __name__ == "__main__":
    unittest.main()
