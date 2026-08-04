<p align="center">
  <img src="docs/logo.png" width="88" alt="">
</p>

<h1 align="center">Stream Deck Agent Cockpit</h1>

<p align="center">
  Hardware controls for Claude Code, Codex, Pi, JCode, and any other terminal agent.<br>
  Standalone, local, and evidence-backed.
</p>

<p align="center">
  <a href="https://cskwork.github.io/streamdeck-agent-cockpit/"><strong>Landing page</strong></a> ·
  <a href="INSTALL.md"><strong>Install</strong></a> ·
  <a href="skills/streamdeck-agent-cockpit/SKILL.md"><strong>SKILL.md</strong></a> ·
  <a href="CHANGELOG.md"><strong>Changelog</strong></a>
</p>

<p align="center">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-10B981">
  <img alt="version" src="https://img.shields.io/badge/version-3.1.1-10B981">
  <img alt="python" src="https://img.shields.io/badge/python-3.9%2B%20stdlib%20only-10B981">
  <img alt="no mcp" src="https://img.shields.io/badge/MCP-not%20required-10B981">
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

---

A single portable skill and reference runtime for turning Stream Deck into a local cockpit for Claude Code, Codex, Pi, JCode, and other terminal-based agents.

**No MCP server is required.** The default implementation uses a loopback-only Python daemon, predeclared local commands, and either generated launchers or a Stream Deck SDK plugin.

## Quick install

```bash
claude plugin marketplace add cskwork/streamdeck-agent-cockpit
claude plugin install streamdeck-agent-cockpit@streamdeck-agent-cockpit
```

Codex, Gemini CLI, Cursor, OpenCode, Amp, Antigravity, and manual installs are all in
[INSTALL.md](INSTALL.md).

## What is standalone

```text
┌──────────────────────────────────────────────────────────────┐
│ Stream Deck                                                  │
│  A. built-in Open action → generated launcher               │
│  B. local Agent Cockpit plugin → dynamic key/dial UI         │
└───────────────────────┬──────────────────────────────────────┘
                        │ authenticated localhost API
┌───────────────────────▼──────────────────────────────────────┐
│ cockpitd                                                     │
│  config · command allowlist · state TTL · adapter registry   │
└───────────────────────┬──────────────────────────────────────┘
                        │ argv execution, never remote MCP
┌───────────────────────▼──────────────────────────────────────┐
│ tmux / terminal / agent CLI                                  │
│  Claude Code · Codex · Pi · JCode · custom commands          │
└──────────────────────────────────────────────────────────────┘
```

`streamdeck-mcp` and AgentDeck are not installed, imported, called, or expected by the runtime. They may be studied as prior art, but the skill's operation does not depend on them.

## Modes

| Mode | Requirements | Best for | Limitation |
|---|---|---|---|
| Launcher-only | Stream Deck app, Python 3.9+, configured terminal tools | Static tap-to-launch/focus actions | No live label/icon updates or dial events |
| Native plugin | Above plus current official Stream Deck SDK toolchain | Live state, dynamic visuals, hold, dials, Property Inspector | Requires building/installing a local plugin |

The daemon and CLI use only Python's standard library.

## Repository layout

```text
streamdeck-agent-cockpit/
├── README.md · INSTALL.md · CHANGELOG.md · LICENSE · VERSION
├── .claude-plugin/          # Claude Code plugin + marketplace manifests
├── .codex-plugin/           # Codex plugin manifest
├── .agents/plugins/         # agents marketplace manifest
├── .cursor/skills/…         # Cursor mirror of SKILL.md
├── gemini-extension.json    # Gemini CLI extension (context: GEMINI.md)
├── docs/index.html          # landing page (GitHub Pages)
└── skills/streamdeck-agent-cockpit/
    ├── SKILL.md
    ├── assets/
    │   ├── cockpit.example.json
    │   ├── cockpit.live-sessions.example.json
    │   └── cockpit.schema.json
    ├── bin/
    │   ├── cockpitd.py
    │   ├── cockpitctl.py
    │   ├── focus_tmux.py
    │   ├── report_state.py
    │   ├── slotclaims.py            # slot bookkeeping for attached sessions
    │   ├── claim_probe.py           # coarse probe for a claimed slot
    │   ├── focus_terminal.py        # iTerm2 / Apple Terminal focus by tty
    │   ├── claude_hook.py           # Claude Code hook → semantic state
    │   └── install_claude_hooks.py  # append-only hook registration
    ├── scripts/
    │   ├── generate_launchers.py
    │   ├── install_runtime.py
    │   ├── install_skill.py
    │   ├── probe_environment.py
    │   ├── smoke_test.py
    │   └── validate_cockpit.py
    ├── templates/streamdeck-plugin/
    ├── references/
    ├── evals/
    └── tests/
```

Every command below that starts with `python3 scripts/…` runs from
`skills/streamdeck-agent-cockpit/`.

## Install the skill manually

For plugin-manager installs (Claude Code, Codex, Gemini CLI, `npx skills`, agy), see
[INSTALL.md](INSTALL.md). To copy the skill into a skills directory yourself:

```bash
cd skills/streamdeck-agent-cockpit

# preview all supported locations
python3 scripts/install_skill.py --target all --dry-run

# install
python3 scripts/install_skill.py --target all
```

Supported targets:

| Target | Destination |
|---|---|
| `claude` | `~/.claude/skills/streamdeck-agent-cockpit` |
| `agents` | `~/.agents/skills/streamdeck-agent-cockpit` |
| `jcode` | convenience default `~/.jcode/skills/streamdeck-agent-cockpit`; override with `--destination` when the installed build uses a different discovery path |
| `all` | all unique destinations above |

Use `--destination /verified/local/skills/path` when a harness uses another discovery directory. Use `--mode symlink` for an editable development install. Existing destinations are refused unless `--force` is supplied; forced replacement first creates a timestamped backup.

## Install the local runtime

```bash
cd skills/streamdeck-agent-cockpit
python3 scripts/probe_environment.py --json   # inspect before assuming anything
python3 scripts/install_runtime.py
```

This creates:

```text
~/.agent-cockpit/
├── bin/
├── cockpit.json
├── state.json       # created as needed
└── token            # generated by the daemon with mode 0600
```

The installer does not register a startup service or modify Stream Deck profiles.

## Configure sessions and controls

Edit `~/.agent-cockpit/cockpit.json`. The included example defines one named `tmux` session for each agent:

- `session.claude.main`
- `session.codex.main`
- `session.pi.main`
- `session.jcode.main`

Verify the actual command names and flags installed on the machine:

```bash
claude --help
codex --help
pi --help
jcode --help
```

Then validate:

```bash
python3 ~/.agent-cockpit/bin/validate_cockpit.py \
  ~/.agent-cockpit/cockpit.json
```

## Start and inspect the daemon

```bash
python3 ~/.agent-cockpit/bin/cockpitd.py \
  --config ~/.agent-cockpit/cockpit.json
```

In another terminal:

```bash
python3 ~/.agent-cockpit/bin/cockpitctl.py \
  --config ~/.agent-cockpit/cockpit.json health

python3 ~/.agent-cockpit/bin/cockpitctl.py \
  --config ~/.agent-cockpit/cockpit.json controls
```

Invoke a configured tap:

```bash
python3 ~/.agent-cockpit/bin/cockpitctl.py \
  --config ~/.agent-cockpit/cockpit.json \
  invoke session.claude.main --gesture tap
```

A hold-confirmed interrupt is explicit:

```bash
python3 ~/.agent-cockpit/bin/cockpitctl.py \
  --config ~/.agent-cockpit/cockpit.json \
  invoke session.claude.main --gesture longPress --confirm
```

## Launcher-only setup

Generate platform launchers:

```bash
python3 ~/.agent-cockpit/bin/generate_launchers.py \
  --config ~/.agent-cockpit/cockpit.json \
  --output ~/.agent-cockpit/launchers
```

In the Stream Deck application, place a built-in **Open** action and select the launcher for the desired control. This path is fully independent and does not compile a plugin. It supports tap actions only.

## Dynamic plugin setup

Use the current official Stream Deck SDK to create a local plugin scaffold. Apply the files in [`skills/streamdeck-agent-cockpit/templates/streamdeck-plugin/`](skills/streamdeck-agent-cockpit/templates/streamdeck-plugin/) as described in its README. Each action instance stores only a logical `controlId` and contacts the local daemon for state and invocation.

The plugin must not read or rewrite Stream Deck's internal profile database. Users place the action normally or install an optional profile owned by this plugin.

It also cannot generically inspect or invoke arbitrary third-party plugin actions. Combine those actions manually in Stream Deck, or connect to the underlying service only when that service/plugin exposes a documented local API.

## Honest progress reporting

Infrastructure can verify that a tmux session exists, but that does not prove an agent is running, waiting, blocked, or done. Without an event source, the UI shows only coarse state.

An agent hook or workflow can report semantic state:

```bash
python3 ~/.agent-cockpit/bin/report_state.py \
  --config ~/.agent-cockpit/cockpit.json \
  --session session.codex.main \
  --state running \
  --label "Reviewing changes" \
  --ttl 180
```

Later:

```bash
python3 ~/.agent-cockpit/bin/report_state.py \
  --config ~/.agent-cockpit/cockpit.json \
  --session session.codex.main \
  --state needs_attention \
  --label "Approval required" \
  --ttl 600
```

When a report expires, the daemon falls back to coarse adapter state. A percentage is accepted only when explicitly reported by a real workflow.

## Sessions you already have open

The sections above cover sessions the cockpit launches. Agent work usually already runs in terminal tabs you opened yourself, and those can appear on the deck too — with live state, and without moving them into tmux.

The daemon only accepts reports for sessions declared in `cockpit.json`, so a running session cannot register itself. Instead, predeclare a fixed number of **slots** and let a Claude Code hook bind live sessions to them. Start from [`cockpit.live-sessions.example.json`](skills/streamdeck-agent-cockpit/assets/cockpit.live-sessions.example.json), which pairs four attached slots with one tmux launch control:

```bash
cp skills/streamdeck-agent-cockpit/assets/cockpit.live-sessions.example.json \
   ~/.agent-cockpit/cockpit.json
python3 ~/.agent-cockpit/bin/validate_cockpit.py ~/.agent-cockpit/cockpit.json
```

Register the hook bridge — append-only, idempotent, and previewable:

```bash
python3 ~/.agent-cockpit/bin/install_claude_hooks.py --dry-run
python3 ~/.agent-cockpit/bin/install_claude_hooks.py
```

Back up your settings file before the first write. State then comes from hook events only:

| Hook event | Key shows |
|---|---|
| `SessionStart`, `Stop` | `IDLE` |
| `UserPromptSubmit` | `RUN` |
| `Notification` (permission, idle, elicitation) | `CHECK` |
| `SessionEnd` | slot released, key returns to `OFF` |

Each key label carries the session's project directory name, never prompt text or model output.

Tapping a slot focuses the owning pane. `focus_terminal.py` supports iTerm2 and Apple Terminal, matching on the tty recorded when the slot was claimed.

Known limits of this path, all deliberate:

- **Sessions already running when you install the bridge stay invisible** until they restart.
- **Slots are finite.** When all are held by live sessions, a new one is ignored rather than evicting someone.
- **No interrupt gesture on attached slots.** There is no supported way to send a scoped `Ctrl-C` through terminal automation, so interrupt stays on tmux-backed sessions where `tmux send-keys` is exact.
- **macOS only.** The bundled probe and focus helpers depend on `ps` ancestry and AppleScript; other platforms need their own commands behind the same adapter.
- **Terminal titles are never scraped.** They look like a usable signal but cannot separate "thinking" from "waiting for approval".

## Verification

From `skills/streamdeck-agent-cockpit/`:

```bash
python3 -m compileall -q bin scripts tests
python3 -m unittest discover -s tests -v
python3 scripts/validate_cockpit.py assets/cockpit.example.json
python3 scripts/validate_cockpit.py assets/cockpit.live-sessions.example.json
python3 scripts/smoke_test.py
```

Physical-device behavior still requires testing in the Stream Deck application and on the target terminal. See [`skills/streamdeck-agent-cockpit/references/verification.md`](skills/streamdeck-agent-cockpit/references/verification.md).

## Deliberate limitations

- Launcher-only mode cannot display live state, distinguish hold, or process dial input.
- The reference plugin template must be adapted and built with the current official SDK; no prebuilt plugin binary is included.
- The official plugin boundary does not provide a safe generic API for editing arbitrary profiles or controlling unrelated third-party plugin actions.
- Terminal focus behavior is terminal-specific and requires on-device verification.
- Without a hook/RPC/workflow report, session state is coarse only.
- Attached sessions occupy a fixed number of slots and carry no interrupt gesture; the reference hook bridge covers Claude Code only, and the bundled probe and focus helpers are macOS-only.

## Security boundary

- Loopback binding by default.
- Random token stored in a local mode-0600 file.
- No raw command endpoint.
- Command argv arrays with `shell=False`.
- No command output returned unless a future implementation deliberately adds a reviewed redaction path.
- Confirmed hold required for the example interrupt actions.
- No arbitrary Stream Deck profile edits.
- No credentials in cockpit JSON, launchers, button settings, icons, or logs.

## Uninstall

Stop the daemon, remove the action/profile owned by Agent Cockpit through the Stream Deck application, uninstall the local plugin if installed, and delete:

```bash
rm -rf ~/.agent-cockpit
rm -rf ~/.claude/skills/streamdeck-agent-cockpit
rm -rf ~/.agents/skills/streamdeck-agent-cockpit
rm -rf ~/.jcode/skills/streamdeck-agent-cockpit
```

This does not remove or alter unrelated profiles or third-party actions.
