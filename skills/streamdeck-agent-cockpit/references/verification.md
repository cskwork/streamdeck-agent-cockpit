# Verification and rollback

## Automated checks

From the skill root:

```bash
python3 -m compileall -q bin scripts tests
python3 -m unittest discover -s tests -v
python3 scripts/validate_cockpit.py assets/cockpit.example.json
python3 scripts/smoke_test.py
```

Expected properties:

- valid configuration passes;
- unknown controls are rejected;
- unauthenticated protected requests are rejected;
- raw commands cannot arrive through invocation JSON;
- confirmed destructive gestures require `confirmed: true`;
- explicit state reports are returned before TTL;
- stale reports fall back to coarse state;
- commands execute without a shell;
- launcher generation contains only configured control IDs.

## Environment check

```bash
python3 scripts/probe_environment.py --json
```

Record the installed versions separately when they materially affect commands or plugin APIs.

## Daemon smoke check

```bash
python3 bin/cockpitd.py --config ~/.agent-cockpit/cockpit.json
python3 bin/cockpitctl.py --config ~/.agent-cockpit/cockpit.json health
python3 bin/cockpitctl.py --config ~/.agent-cockpit/cockpit.json controls
```

Then invoke one harmless test control.

## Agent-session checks

For every configured agent:

1. Ensure the session is absent.
2. Tap once; confirm the correct session launches.
3. Tap again; confirm the intended terminal/session becomes active without a duplicate process.
4. Report `running`; confirm the plugin shows it with a reported source.
5. Stop reports and wait beyond TTL; confirm the UI falls back to coarse state.
6. Hold interrupt; confirm only the target session receives it.
7. Restart the terminal; confirm durable session behavior matches the chosen adapter.

Never claim step 3 passed merely because launch returned exit code 0.

## Plugin checks

- Invalid/missing `controlId` is visible.
- Stopped daemon is visible.
- Bad token is visible.
- Short press emits only tap.
- Long press emits only longPress.
- Polling stops when action disappears.
- Multiple instances do not leak timers.
- Titles/icons fit on actual keys.
- Encoder feedback and rotation direction are correct on target hardware.
- Stream Deck restart reconnects cleanly.

## Rollback

Runtime:

```bash
rm -rf ~/.agent-cockpit
```

Skill installs:

```bash
rm -rf ~/.claude/skills/streamdeck-agent-cockpit
rm -rf ~/.agents/skills/streamdeck-agent-cockpit
rm -rf ~/.jcode/skills/streamdeck-agent-cockpit
```

Plugin/profile:

- remove Agent Cockpit actions/profile through the Stream Deck application;
- uninstall only the Agent Cockpit plugin;
- restore only backups created by this skill's installer.

Do not restore or overwrite unrelated Stream Deck profile data.

## Evidence wording

Report results as:

- **Verified locally** — automated command and observed result.
- **Verified on device** — physical Stream Deck and terminal behavior observed.
- **Configured but unverified** — exact remaining external/device check.
- **Unsupported** — capability absent; fallback stated.
