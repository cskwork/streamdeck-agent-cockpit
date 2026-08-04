# Changelog

## 3.0.0 — Standalone architecture

Distribution (first public release):

- Restructured the repository as an installable skill package; payload lives under `skills/streamdeck-agent-cockpit/`.
- Added Claude Code, Codex, agents-marketplace, Gemini CLI, and Cursor manifests.
- Added `INSTALL.md` covering every supported harness plus the local runtime.
- Added a GitHub Pages landing page under `docs/`.
- Added CI: a Claude Code plugin load check, and byte-compile, unit tests, config validation, and smoke test on Linux/macOS/Windows for Python 3.9 and 3.12.

Runtime:

- Removed `streamdeck-mcp` and AgentDeck from the core runtime path.
- Replaced physical key-coordinate ownership with logical `controlId` bindings.
- Added a stdlib-only localhost daemon and CLI.
- Added launcher-only mode for static controls without a custom plugin.
- Added a current-SDK plugin adaptation template for dynamic controls.
- Added explicit state evidence tiers, TTL handling, and stale fallback.
- Added confirmation gates for destructive gestures.
- Added safe config validation, environment probing, runtime installation, tests, and smoke checks.
- Clarified that arbitrary Stream Deck profile databases are never inspected or rewritten.

## 2.0.0

- Earlier experimental architecture combined external Stream Deck and agent-session integrations.
- Superseded because those integrations are no longer required by this skill.
