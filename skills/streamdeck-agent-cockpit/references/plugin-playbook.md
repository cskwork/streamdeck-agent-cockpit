# Stream Deck plugin playbook

## When a plugin is justified

Build the plugin only for requirements the launcher path cannot satisfy:

- dynamic title or icon;
- semantic/coarse state display;
- long-press distinction;
- encoder rotation or press;
- Property Inspector configuration;
- visible daemon/auth/error state.

## Scaffold from the installed official SDK

SDK manifests, Node versions, CLI commands, encoder layouts, and TypeScript types can change. Create a fresh plugin with the **currently installed official Stream Deck SDK tooling**, then adapt the reference files under `templates/streamdeck-plugin/`. Do not blindly copy an old manifest or package lock.

Recommended plugin identity:

```text
plugin UUID: com.agentcockpit.streamdeck
action UUID: com.agentcockpit.streamdeck.control
```

Use another reverse-DNS namespace when publishing under an organization.

## One generic action

The action settings should stay small:

```json
{
  "controlId": "session.codex.main",
  "daemonUrl": "http://127.0.0.1:39393",
  "tokenFile": "~/.agent-cockpit/token"
}
```

The plugin:

1. reads the local token file in its Node process;
2. fetches the bound control state;
3. renders a compact title/image/encoder feedback;
4. converts SDK input events to canonical gestures;
5. invokes the named control with no raw command text;
6. shows an alert/error state on any non-success response.

The Property Inspector edits the action settings. It does not hold the bearer token or execute commands.

## Event mapping

| SDK interaction | Canonical gesture |
|---|---|
| Key up after short press | `tap` |
| Key up after configured threshold | `longPress` |
| Dial press | `dialPress` |
| Negative rotation | `dialLeft` |
| Positive rotation | `dialRight` |

Do not fire both tap and long press for one interaction. Debounce dial events and pass only bounded step values.

## Polling

Start with 1–2 second polling while a key is visible. Stop polling on disappearance. Add WebSocket/SSE only when measured scale or latency justifies the additional lifecycle complexity.

Use one request per visible control per interval only for small decks. For larger layouts, add a batched state endpoint or plugin-side shared cache.

## Rendering

Prefer short stable labels. Render source/staleness as a small cue rather than pretending confidence. Keep full error details in logs or the Property Inspector, not on the key.

Avoid remote icon URLs. Bundle static SVG/PNG assets or generate local data-URI SVGs from sanitized text/state.

## Encoders

Encoder support must start from a current official encoder action scaffold because required layouts and feedback contracts vary by SDK release. Keep the same `controlId` and daemon gesture API; only the Stream Deck presentation layer changes.

## Third-party plugin boundary

One Stream Deck plugin should not pretend it can enumerate, configure, or invoke arbitrary unrelated plugin actions. For a third-party integration, choose one of these supported paths:

1. The user combines Agent Cockpit and the third-party action in a Stream Deck Multi Action.
2. Agent Cockpit calls the underlying application/service through its documented local API or CLI.
3. The third-party plugin exposes and documents an inter-plugin protocol.

Otherwise keep the actions separate. Do not read another plugin's private settings or patch its action data.

## Profile handling

Safe options:

- user manually places generic actions;
- ship a profile created through supported Stream Deck tooling and clearly owned by this plugin;
- provide a control map and icon set for manual placement.

Unsafe option:

- editing undocumented profile files/databases to insert or rewrite arbitrary actions.

## Build gate

Before packaging:

- formatter/linter pass;
- TypeScript check pass;
- tests pass;
- production bundle pass;
- official SDK validation pass;
- install/uninstall tested;
- daemon-down, bad-token, and unknown-control states tested;
- actual key and encoder behavior tested on target hardware.
