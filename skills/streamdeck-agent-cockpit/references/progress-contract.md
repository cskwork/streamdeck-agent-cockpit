# Progress and state contract

## Principle

Display only what the evidence supports. The UI must preserve the difference between infrastructure presence and agent lifecycle state.

## Evidence tiers

| Tier | Source | Allowed claims |
|---|---|---|
| `reported` | Agent hook, RPC/event adapter, workflow callback, explicit reporter | Exact reported semantic state and optional explicit progress |
| `coarse` | tmux/process/probe exit code | Present, offline, or unavailable only |
| `stale` | Expired semantic report plus current probe | Coarse state, with last report marked stale |
| `unknown` | No valid report and no working probe | Unknown/unavailable |

## Semantic states

Accepted reference states:

```text
idle
running
needs_attention
blocked
succeeded
failed
```

Reports may carry:

- a short label;
- a redaction-safe detail;
- explicit progress from 0 through 100;
- TTL in seconds;
- source metadata.

Do not report prompt text, generated code, terminal output, tokens, secrets, customer data, or file contents to a key label.

## Coarse states

```text
present
offline
unavailable
```

`present` means only that the configured session/probe exists. It must not be renamed to “working”, “idle”, or “ready for input” unless a semantic event says so.

## TTL and staleness

Every semantic report expires. After expiration:

1. preserve its timestamp as historical metadata;
2. mark it stale;
3. run the coarse adapter probe;
4. render only the coarse result.

This prevents a key from remaining “running” after an agent, hook, daemon, or terminal failure.

## Percentages

A progress percentage is valid only when explicitly emitted from a measurable workflow, such as 27 of 40 tests or 8 of 10 files processed. Never derive it from elapsed time, token count, terminal activity, number of log lines, or model prose.

## Recommended rendering

| State | Primary title | Secondary metadata |
|---|---|---|
| `running` | Configured short label | Activity label, age |
| `needs_attention` | `CHECK` | Session label |
| `blocked` | `BLOCKED` | Redaction-safe reason |
| `succeeded` | `DONE` | Age; expires to coarse state |
| `failed` | `FAILED` | Age; details remain off-device |
| `present` | Session label | `present · coarse` |
| `offline` | Session label | `offline` |
| `unavailable` | `NO LINK` | Daemon/adapter source |

The source tier should be inspectable in the Property Inspector or CLI even when omitted from the small key display.
