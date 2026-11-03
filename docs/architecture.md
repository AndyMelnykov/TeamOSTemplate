# Architecture

There is no runtime service in this repo — no model calls to trace, no tool-execution loop to diagram in the usual agent-product sense. What there is instead is a fixed shape for how a coding agent (or a human) is meant to move through the file tree, and a small set of places where a deterministic check or a human sign-off sits between "agent proposed this" and "this is now true."

## The read/write path

```
                         ┌───────────────────────────┐
                         │   Human (PM / eng / etc.)  │
                         └──────────────┬─────────────┘
                                        │ asks a question / requests a change
                                        ▼
                         ┌───────────────────────────┐
                         │   Coding agent             │
                         │   (Claude Code, Codex, …)  │
                         └──────────────┬─────────────┘
                                        │ reads
                                        ▼
                         ┌───────────────────────────┐
                         │   Root CLAUDE.md           │  ◄── universally-needed
                         │   (team roster, channels,  │      context only
                         │    top-level doc index)    │
                         └──────────────┬─────────────┘
                                        │ routes to
                    ┌───────────────────┼────────────────────┐
                    ▼                   ▼                    ▼
        ┌───────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │ reference/         │ │ Folder CLAUDE.md  │ │ evaluation/        │
        │ canonical           │ │ routers            │ │ CLAUDE.md          │
        │ definitions         │ │ (product-dev/*,    │ │                    │
        │ (terms, metrics,    │ │  team/)            │ │                    │
        │  segments, statuses,│ │                    │ │                    │
        │  decision types)    │ │                    │ │                    │
        └───────────────────┘ └─────────┬──────────┘ └──────────────────┘
                                         │ routes to
                                         ▼
                         ┌───────────────────────────┐
                         │ feature-index.yaml         │  ◄── the join table;
                         │ (join table across          │      see ADR 0002
                         │  product/eng/analytics/     │
                         │  data-eng/design)            │
                         └──────────────┬─────────────┘
                                        │ points into
                                        ▼
                         ┌───────────────────────────┐
                         │ Raw + derived artifacts     │
                         │ PRDs, RFCs, plans, schemas,  │
                         │ transcripts, summaries,      │
                         │ decision files                │
                         └──────────────┬─────────────┘
                                        │
                    ┌───────────────────┴────────────────────┐
                    ▼                                        ▼
        ┌───────────────────┐                    ┌──────────────────────┐
        │ .claude/            │                    │ Deterministic policy   │
        │ skills, commands,    │  ── executes ──►   │  layer                │
        │ agents               │                    │ - check-references.ps1│
        │ (onboarding,          │                    │   (broken-link gate)  │
        │  /customer-call,      │                    │ - human approval gate │
        │  /prd)                │                    │   before writes to    │
        └───────────────────┘                    │   reference/ or        │
                                                    │   strategy/ (ADR 0003)│
                                                    └───────────┬───────────┘
                                                                │
                                                                ▼
                                                ┌───────────────────────────┐
                                                │ External systems            │
                                                │ (pointed at, not mirrored)   │
                                                │ Figma · Linear/Jira/Asana ·  │
                                                │ Snowflake · Segment ·        │
                                                │ Amplitude · Stripe ·         │
                                                │ Sigma/Mode                   │
                                                └───────────────────────────┘
```

## Integration layer

The read/write path above shows how an agent moves through the tree. This diagram shows how signals move through it: the repo is the system of record for the [product loop](../reference/product-loop.md), and everything outside it is a source adapter or a capability ([`docs/agents/capabilities.md`](agents/capabilities.md), [ADR 0007](adr/0007-teamos-is-the-integration-layer.md)). The signal store and the script that writes it are planned (Plan 1); today the first two boxes are filled by `/customer-call` and `Insights/insights.csv`.

```
  Source adapters
  +--------------------------------------------------------------+
  | product-intelligence-agent | /customer-call | analytics sweep |
  | MCP-backed adapters                                          |
  +------------------------------+-------------------------------+
                                 | add signals (Plan 1)
                                 v
                  +-----------------------------+
                  | Signals                      |
                  +--------------+--------------+
                                 v
                  +-----------------------------+
                  | Hypotheses                   |
                  | (aggregate signals)          |
                  +--------------+--------------+
                                 v
                  +-----------------------------+
                  | PRD                          |
                  +--------------+--------------+
                                 v
                  +-----------------------------+
                  | Tickets (external tracker)   |  engineering is out of scope
                  +--------------+--------------+
                                 v
                  +-----------------------------+
                  | Rollout -> measurement       |
                  +--------------+--------------+
                                 | results become new signals (Plans 1, 4)
                                 v
                           back to Signals
```

## Mapping onto the usual agent-product architecture vocabulary

| Usual element | What plays that role here |
|---|---|
| Model | The coding agent's own model (Claude, or whichever the operator points at the repo) — this repo doesn't call a model itself |
| Tools | File read/search (`Read`, `Grep`, `Glob`), shell (`Bash`/`gh`), and the skills/commands under `.claude/` |
| Data sources | The repo plus signals added by source adapters — `reference/` for canonical definitions, `product-development/` for raw + derived artifacts |
| Policy layer | `scripts/check-references.ps1` (deterministic, always runs the same way) plus the human-approval requirement on canonical writes (judgment-based, documented in [ADR 0003](adr/0003-human-approval-for-canonical-writes.md)) |
| Storage | Git text files; signals move to a single `signals.csv` (Plan 1) |
| External APIs | The systems listed in the diagram above, referenced by link/path and purpose, never mirrored into the repo |

## Why this shape

- **Progressive disclosure** keeps an agent from loading the whole repo just to answer one question — it should stop walking the tree as soon as the relevant router or reference file answers it.
- **The join table exists because the routing tree, by itself, fragments any single feature** across as many as eight folders. See [ADR 0002](adr/0002-feature-index-as-join-table.md).
- **The policy layer is split deliberately** into a deterministic check (broken links — no judgment involved, so a script does it) and a human gate (editing shared vocabulary — judgment involved, so a person does it). See [ADR 0003](adr/0003-human-approval-for-canonical-writes.md).
