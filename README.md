# AI-Native Product OS

A reference architecture for structuring product-team knowledge so that both humans and AI agents can navigate, reason, and execute from the same shared, version-controlled context — populated here with a realistic example product (`example_product`, an AI prototyping platform) so every pattern is backed by real files instead of empty folders.

No application code. The deliverable is the context itself: how it's organized, how an agent is meant to move through it, and where a human has to sign off.

---

## Problem

Product teams generate knowledge across dozens of disconnected surfaces — Slack threads, meeting notes, Figma comments, a PM's head, scattered Google Docs, ticket descriptions. Three failure modes follow directly from that:

- **Humans re-explain context constantly.** A new hire, a new agent session, or a teammate from another function all start from zero, so the same background gets retold every time.
- **Definitions drift.** "Active user," "Growth tier," "Shipped" mean something slightly different depending on who wrote the doc, and nothing forces convergence.
- **A single feature has no home.** Its PRD, RFC, schema, dashboard, ticket, and customer evidence live in five different tools owned by five different functions, so answering "what's the state of X" means manually reassembling it every time.

Bolting an LLM onto this doesn't fix it — an agent with no navigation model either loads everything (expensive, slow, and prone to citing the wrong or stale copy of a definition) or misses context it needed because nothing pointed it there.

## Product

This repo is a working example of an organization's shared knowledge base, structured for both a human skimming it and an agent starting a cold session. It answers, concretely, what "context engineering for product teams" looks like as files on disk rather than as a slide.

Six structural moves make it work:

1. **Progressive disclosure through nested routers.** A `CLAUDE.md` in the root and one per meaningful folder — each describing its own contents and linking deeper. An agent walks the tree instead of loading everything at once.
2. **A function × product-area matrix.** Functions (`product/`, `engineering/`, `analytics/`, `data-engineering/`, `design/`) are the top axis. Once you know the pattern, you can guess any path.
3. **One join table to defeat the matrix.** That grid scatters a single feature across as many as eight folders, so [`feature-index.yaml`](product-development/feature-index.yaml) reassembles it: per feature, the PRD, eng RFC + plan, data-eng RFC + plan, Figma link, tickets, table schemas, queries, dashboards, experiments, and bug investigations. This is the keystone — it's what lets a strict folder taxonomy coexist with feature-shaped questions. See [ADR 0002](docs/adr/0002-feature-index-as-join-table.md).
4. **Naming conventions as an addressing scheme.** `{feature}-prd.md`, `{feature}-rfc.md`, `YYYY-MM-DD-{topic}-decision.md`. Lookups become constructible rather than searched.
5. **Shared vocabulary defined once**, in [`reference/`](reference/CLAUDE.md) — terminology, metric targets, segments, statuses, decision types. Every downstream doc cites these instead of re-defining them.
6. **Raw kept beside derived.** `calls/transcripts/` sits next to `calls/summaries/`; a claim can always be traced back to its source.

Throughout, external systems are pointed at, not mirrored — Figma, Linear/Jira/Asana, Snowflake, Segment, Amplitude, Stripe, Sigma/Mode are listed with purpose and access path, not duplicated. Only what benefits from version control lives here.

## Demo

A concrete, verifiable walk through the repo — every path below is a real file, not an illustration.

**Question:** *"Why are we building Team Workspaces, what evidence supports it, and has it shipped?"*

1. Check the join table: [`feature-index.yaml`](product-development/feature-index.yaml) → `prototyping.team-workspaces` → points to a PRD and an eng RFC.
2. Load the PRD: [`team-workspaces-prd.md`](product-development/product/PRDs/team-workspaces-prd.md) → Problem Statement cites Acme Corp's account team asking for manager-level review workflows and pre-assigning internal owners for rollout.
3. Check the account for corroborating evidence: [`customers/accounts/acme-corp/`](product-development/product/customers/accounts/acme-corp/).
4. Check the canonical status enum before answering "has it shipped": [`reference/status-definitions.md`](reference/status-definitions.md) → the PRD's `**Status**` field reads `Draft`, which per that table means *"being written; not yet shared for feedback."*
5. Answer, with citations: *Team Workspaces is still in Draft (not shipped). It's driven by validated demand from Acme Corp, who asked for manager review flows over shared projects and already assigned internal rollout owners.*

Five file reads, zero guessing at what "Draft" or "Shipped" means, zero duplicated definitions. Run the same question against `evaluation/task-set.md`'s baseline condition (router files and `feature-index.yaml` removed) and the same answer requires searching the raw tree unassisted — that comparison is exactly what `evaluation/` is set up to measure (see [Evaluation](#evaluation)).

## Architecture

There's no runtime service here — the "architecture" is the shape of the file tree plus the rules for how an agent is meant to move through it. Full diagram and walkthrough: [`docs/architecture.md`](docs/architecture.md). Short version:

```text
Human ──► Coding agent ──► CLAUDE.md router tree ──► reference/ (canonical definitions)
                                    │
                                    ▼
                        feature-index.yaml (join table)
                                    │
                                    ▼
                 product-development/* (raw + derived artifacts)
                                    │
                                    ▼
        .claude/ skills + commands (executable workflows) ──► deterministic policy
        (scripts/check-references.ps1, human approval gate)  ──► external systems
```

## Core workflows

Processes are executable, not just written down. `.claude/` turns recurring work into runnable units:

- **Onboarding** — [`.claude/agents/onboarding.md`](.claude/agents/onboarding.md) asks a new team member's role, loads the general guide plus their role-specific guide from `team/onboarding-guides/`, and tracks the checklist.
- **Customer call capture** — [`.claude/commands/customer-call.md`](.claude/commands/customer-call.md) turns a transcript into a dated summary + transcript pair under the right account folder, extracts feature requests, and drafts a Slack recap for review.
- **PRD authoring** — [`.claude/commands/prd.md`](.claude/commands/prd.md) drives the [PRD template](product-development/product/PRDs/CLAUDE.md#prd-template-sections) end to end.
- **Bi-weekly product update** — [`workflow-spec.md`](product-development/product/workflows/bi-weekly-update/workflow-spec.md) decomposes a recurring report into five ordered steps, each with an automated half (gather, draft) and an interactive half (PM reviews, approves), and separates what changes every cycle from what carries forward.
- **New feature intake** — [`workflow-spec.md`](product-development/product/workflows/new-feature-intake/workflow-spec.md) gates a new PRD behind an explicit check for existing feature/problem entries and a resolved-constraints step, so intake can't silently duplicate `feature-index.yaml`.

## AI design decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Primary retrieval | Structured navigation (router tree + naming conventions + join table), not embeddings | The domain is small and stable enough to be fully addressable — an agent can construct the right path instead of searching for it. [ADR 0001](docs/adr/0001-structured-navigation-over-embeddings.md) |
| Cross-functional reassembly | One join table (`feature-index.yaml`), not a feature-first folder structure | Keeps function-first ownership clarity while still answering feature-shaped questions. [ADR 0002](docs/adr/0002-feature-index-as-join-table.md) |
| Canonical writes | Require human approval before editing `reference/` or `strategy/` | Those files are read by many future sessions before any human necessarily reviews the diff — the blast radius of a bad edit is the whole repo's shared vocabulary. [ADR 0003](docs/adr/0003-human-approval-for-canonical-writes.md) |
| Orchestration | One agent per session, not a multi-agent pipeline | The recurring tasks here are sequential (gather → draft → human review), not parallelizable — a second agent would add coordination cost with no measurable gain. [ADR 0004](docs/adr/0004-single-agent-no-orchestration.md) |
| Provenance | Raw transcripts/evidence kept beside derived summaries, never overwritten | Lets a human or agent re-verify or re-interpret a claim without losing the source. |

## Human-agent boundary

### Autonomous

- Read any file, walk the router tree, use `feature-index.yaml` and `reference/` to answer questions
- Search, classify, and summarize (e.g. a call transcript into a structured summary)
- Draft new dated artifacts — call summaries, decision files, PRDs — without asking first
- Run read-only tooling (`scripts/check-references.ps1`, `gh issue list`)

### Requires review

- Draft PRDs and RFCs before they carry a `Status` beyond `Draft` (see [`reference/status-definitions.md`](reference/status-definitions.md))
- Feature-request extractions logged against an account, before they're treated as validated demand

### Requires approval

- Editing `reference/` (terminology, metrics, segments, statuses, decision types) or `product/strategy/` — see [ADR 0003](docs/adr/0003-human-approval-for-canonical-writes.md)
- Creating a dated decision file (`YYYY-MM-DD-{topic}-decision.md`) — the decision itself is a human call; the agent drafts, a human decides

### Blocked

- Overwriting raw source evidence (transcripts, existing decision files)
- Silently resolving a naming or status inconsistency instead of surfacing it

## Evaluation

`evaluation/` defines a small, reproducible benchmark for whether this structure actually helps an agent, rather than asserting that it does:

- [`task-set.md`](evaluation/task-set.md) — seven tasks, each with a real, verifiable expected answer and source file (e.g. "find the current GSR target" → `reference/metrics.md`, `> 92%`).
- [`protocol.md`](evaluation/protocol.md) — run each task twice, once against the repo as-is and once with router files and `feature-index.yaml` removed; record task accuracy, wrong-source rate, files opened, tokens consumed, and citation accuracy.
- [`results/`](evaluation/results/) — currently empty. **No run has been recorded yet** — this is a real gap, not a rounding error, and it's called out again under [Limitations](#limitations) rather than papered over with invented numbers.

## Observability

There's no model-call trace to capture — the observable surface is the repo's own audit trail:

- **Structural integrity** — `scripts/check-references.ps1` deterministically scans `feature-index.yaml` and every tracked Markdown file for links/paths that don't resolve, and exits non-zero if any are found. This is the one piece of enforcement in the repo that isn't left to an agent's judgment.
- **Friction log** — [`PAPERCUTS.md`](PAPERCUTS.md) is where an agent appends one line the moment it hits a dead end, a broken link, or a footgun, without stopping to fix it first. It's currently empty (no entries logged yet), which is itself a data point about how much this structure has actually been exercised — see [Limitations](#limitations).
- **Decision trail** — git history plus dated decision files (`YYYY-MM-DD-{topic}-decision.md`, convention in [`reference/decision-types.md`](reference/decision-types.md)) are the durable record of what changed and why; nothing here relies on chat logs no one can re-read.

## Running locally

There's no server to start. To work with this repo:

```bash
git clone <this-repo>
```

Point any coding agent (Claude Code, or another agent that reads a root instructions file) at the repo root and tell it to start from `CLAUDE.md` — it routes to everything else.

Validate structural integrity before or after making changes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1
```

Expected output on a clean tree: exit code 0, `No broken references found.`

## Limitations

- **The evaluation has never been run.** `evaluation/task-set.md` and `protocol.md` define a real methodology; `evaluation/results/` is empty. Treat every claim in this README about the structure "helping" as a hypothesis with a defined test, not a measured result.
- **Structured navigation degrades on unstructured collections.** `competitive-research/` and the customer `Insights/` folder are closer to loosely-organized document piles than addressable tables — the router-tree pattern is weakest exactly there (see [ADR 0001](docs/adr/0001-structured-navigation-over-embeddings.md)).
- **`feature-index.yaml` is hand-maintained.** Nothing currently forces a new PRD or RFC to be wired into the join table; it can silently go stale.
- **No automated staleness or conflict detection.** A decision file that contradicts an earlier one, or a reference definition nobody's touched since its dependents changed, isn't caught by anything in this repo today.
- **One example product, one team's shape.** The function × product-area matrix, the five-pillar structure, and the naming conventions are all tuned to `example_product`'s specific org shape — adopting this pattern elsewhere means adapting the taxonomy, not copying it verbatim.
- **The friction log is unexercised.** `PAPERCUTS.md` has no entries yet, so its main value so far is structural (the practice exists and is wired into agent skills), not yet demonstrated through real recorded friction.

## Roadmap

Full list with rationale: [`ROADMAP.md`](ROADMAP.md). Near-term priorities: enforce the `feature-index.yaml` join table automatically instead of trusting it stays current, add canonical-document validation (a PRD can't ship an invalid `Status` value), and actually run the evaluation protocol and publish real numbers.

## License

This work is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). See [LICENSE](LICENSE) for details.
