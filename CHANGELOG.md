# Changelog

## 3.1.1 — Windows CI fix

- `slotclaims._ps` returns `None` off POSIX instead of spawning `ps`, which hung the Windows job until it was cancelled. Ancestry and tty discovery were always POSIX-only; that is now explicit in code, tests, and docs.
- Split the claims round-trip test from the file-mode assertion and skipped POSIX-only tests on other platforms.

## 3.1.0 — Attach to sessions you already have open

Runtime:

- Added a slot model so agent sessions started by hand can appear on the deck. The daemon rejects reports for sessions absent from `cockpit.json`, so a fixed set of predeclared slots is bound to live sessions at runtime instead.
- Added `slotclaims.py` (bookkeeping), `claim_probe.py` (coarse probe), and `focus_terminal.py` (iTerm2 and Apple Terminal focus by tty).
- Added `claude_hook.py`, a Claude Code hook bridge mapping `SessionStart`/`Stop` to `idle`, `UserPromptSubmit` to `running`, and `Notification` to `needs_attention`. State comes from hook events only; terminal titles are never scraped.
- Added `install_claude_hooks.py`, which registers the bridge append-only and idempotently and supports `--dry-run`.
- Added `assets/cockpit.live-sessions.example.json`, pairing four attached slots with one tmux launch control.
- Liveness and tty are anchored on the `login` ancestor rather than the agent process, because agent CLIs are often launchers that exec `node` and shell wrappers can allocate an inner pty the terminal emulator never sees.
- A full slot set never evicts a live claim.

Documentation:

- `session-adapters.md`: attaching to already-running sessions, macOS terminal automation, and why attached slots carry no interrupt gesture.
- `progress-contract.md`: the Claude Code hook mapping, its TTL consequences, and the fact that sessions predating installation stay invisible.
- `plugin-playbook.md`: `@elgato/streamdeck` 2.x drift, the ESM/CommonJS bundling failure and its misleading log line, how to confirm a plugin reload actually happened, doubled key text, and the profile `Pages.Pages` requirement.
- `verification.md`: attached-session checks and a reload-confirmation step.

Tests:

- Added `test_slotclaims.py` covering claim reuse, staleness, eviction refusal, release, and owner discovery.

## 3.0.0 — Standalone architecture

Distribution (first public release):

- Restructured the repository as an installable skill package; payload lives under `skills/streamdeck-agent-cockpit/`.
- Added Claude Code, Codex, agents-marketplace, Gemini CLI, and Cursor manifests.
- Added `INSTALL.md` covering every supported harness plus the local runtime.
- Added a GitHub Pages landing page under `docs/`, with an English/Korean switch (English default, remembered per browser, deep-linkable via `?lang=ko`).
- Added `README.ko.md`, linked from the English README.
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
