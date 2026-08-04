# Install streamdeck-agent-cockpit

The skill instructions install through any agent harness below. The **local runtime**
(daemon, CLI, launcher generator) is installed separately — see
[Local runtime](#local-runtime) at the end.

<details>
<summary><strong>Claude Code</strong></summary>

### Install

```bash
claude plugin marketplace add cskwork/streamdeck-agent-cockpit
claude plugin install streamdeck-agent-cockpit@streamdeck-agent-cockpit
```

Type `/streamdeck-agent-cockpit`.

### Verify

```bash
claude plugin list
```

### Update

```bash
claude plugin marketplace update streamdeck-agent-cockpit
```

### Uninstall

```bash
claude plugin uninstall streamdeck-agent-cockpit
claude plugin marketplace remove streamdeck-agent-cockpit
```

</details>

<details>
<summary><strong>Codex</strong></summary>

### Install

```bash
codex plugin marketplace add cskwork/streamdeck-agent-cockpit --ref main
codex plugin add streamdeck-agent-cockpit@streamdeck-agent-cockpit
```

Type `$streamdeck-agent-cockpit`.

### Verify

```bash
codex plugin list
```

### Uninstall

```bash
codex plugin remove streamdeck-agent-cockpit
codex plugin marketplace remove streamdeck-agent-cockpit
```

</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

### Install (extension, always-on)

```bash
gemini extensions install https://github.com/cskwork/streamdeck-agent-cockpit
```

### Verify

```bash
gemini extensions list
```

### Uninstall

```bash
gemini extensions uninstall streamdeck-agent-cockpit
```

</details>

<details>
<summary><strong>Cursor, OpenCode, Amp, and other agent-skills harnesses</strong></summary>

### Install

```bash
npx skills add cskwork/streamdeck-agent-cockpit
npx skills add cskwork/streamdeck-agent-cockpit -g
```

Type `/streamdeck-agent-cockpit` in a new agent chat.

### Verify

```bash
npx skills list
```

### Update

```bash
npx skills update streamdeck-agent-cockpit
```

### Uninstall

```bash
npx skills remove streamdeck-agent-cockpit
```

</details>

<details>
<summary><strong>Antigravity (agy)</strong></summary>

### Install

```bash
agy plugin install https://github.com/cskwork/streamdeck-agent-cockpit
```

### Verify

```bash
agy plugin list
```

### Uninstall

```bash
agy plugin uninstall streamdeck-agent-cockpit
```

</details>

<details>
<summary><strong>Manual copy (JCode and any other skills directory)</strong></summary>

### Install

```bash
git clone https://github.com/cskwork/streamdeck-agent-cockpit
cd streamdeck-agent-cockpit/skills/streamdeck-agent-cockpit
python3 scripts/install_skill.py --target all
```

Supported `--target` values:

| Target | Destination |
|---|---|
| `claude` | `~/.claude/skills/streamdeck-agent-cockpit` |
| `agents` | `~/.agents/skills/streamdeck-agent-cockpit` |
| `jcode` | `~/.jcode/skills/streamdeck-agent-cockpit` (override with `--destination`) |
| `all` | every unique destination above |

Use `--mode symlink` for an editable development install. Existing destinations are
refused unless `--force` is supplied; a forced replacement first writes a timestamped
backup.

### Uninstall

```bash
rm -rf ~/.claude/skills/streamdeck-agent-cockpit
rm -rf ~/.agents/skills/streamdeck-agent-cockpit
rm -rf ~/.jcode/skills/streamdeck-agent-cockpit
```

</details>

## Local runtime

The skill instructions alone do not start anything. The cockpit daemon, CLI, config, and
launcher generator install into `~/.agent-cockpit`:

```bash
cd skills/streamdeck-agent-cockpit
python3 scripts/probe_environment.py --json     # inspect what is actually available
python3 scripts/install_runtime.py              # install ~/.agent-cockpit
```

Then start and check it:

```bash
python3 ~/.agent-cockpit/bin/cockpitd.py   --config ~/.agent-cockpit/cockpit.json
python3 ~/.agent-cockpit/bin/cockpitctl.py --config ~/.agent-cockpit/cockpit.json health
```

Requirements: Python 3.9+ and the Stream Deck application. Everything else — `tmux`, a
specific terminal, the Stream Deck SDK — is optional and only needed for the mode you
choose.

### Uninstall the runtime

```bash
rm -rf ~/.agent-cockpit
```

Removing the runtime does not touch Stream Deck profiles or third-party plugin actions.
