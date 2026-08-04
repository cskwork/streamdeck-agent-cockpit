# Session adapters

## Contract

Every adapter must provide or explicitly omit these capabilities:

```text
probe(target)      -> coarse existence/availability evidence
launch(session)    -> start the configured agent/session
focus(session)     -> bring the intended terminal/session to the user
resume(session)    -> optional, only with locally verified CLI syntax
interrupt(session) -> graceful, scoped interrupt
report(event)      -> optional semantic state source
```

A process probe is not a semantic event source.

## Default tmux adapter

The reference config uses named tmux sessions because they survive terminal-window changes and expose a simple existence probe.

- Probe: `tmux has-session -t <target>`.
- Launch: configured `tmux new-session` argv.
- Focus: `focus_tmux.py` or another explicit terminal command.
- Interrupt: `tmux send-keys -t <target> C-c`.

`focus_tmux.py` opens or activates a compatible terminal path; verify the selected terminal in practice. A successful tmux command does not prove the intended GUI window is foreground.

## Agent-specific guidance

| Agent | Baseline session behavior | Rich state option |
|---|---|---|
| Claude Code | Start its installed CLI inside a named terminal session | Configure a reviewed local hook/event bridge when supported by the installed version |
| Codex | Start its installed CLI inside a named terminal session | Configure a reviewed notify/event bridge when supported by the installed version |
| Pi | Start the CLI normally; use the same generic session contract | A local RPC/event adapter may translate documented events into reports |
| JCode | Start or connect using syntax verified from the installed CLI | A local server/SDK adapter may translate documented lifecycle events into reports |

Do not hard-code remembered resume flags. Run each installed binary's `--help`, inspect its local configuration, and then record the exact verified command as argv.

## Generic command adapter

When tmux is unavailable, define:

- a probe command whose exit code 0 means present;
- launch/focus/interrupt command arrays;
- optional semantic reporter integration.

This supports WezTerm workspaces, iTerm automation, Windows Terminal, SSH jump hosts, or a custom session manager without changing the daemon API.

## Focus behavior

“Switch session” can mean different things:

1. Switch the active pane within an already attached multiplexer client.
2. Focus an existing terminal window/tab.
3. Open a new terminal tab attached to the durable session.

Resolve this explicitly. The reference helper chooses option 3 when a direct existing-client target is unavailable because it is deterministic. If the user requires option 1 or 2, implement the terminal's supported automation API and verify foreground focus.

## Interrupt versus kill

An interrupt should be scoped to the intended session and normally map to Ctrl-C or an agent-native cancel operation. It may still discard in-flight work, so require hold/explicit confirmation.

A process kill is a different, higher-risk operation. Do not include it by default. If required, add a separate control with stronger confirmation and a documented recovery path.
