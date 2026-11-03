# AI-Native Product OS

A product operating system: an integration layer between all the tools a product team uses, built as version-controlled context that both humans and AI agents can navigate, reason over and act from. It covers the discovery → delivery loop — input signals, hypotheses, validation, prototyping, PRDs and the hand-off to engineering — and is populated here with a realistic example product (`example_product`, an AI-powered SaaS document automation platform) so every pattern is backed by real files instead of empty folders.

No application code. The deliverable is the context itself: how it's organized, how an agent moves through it, and where a human has to sign off.

---

## The loop

```text
signals → hypotheses → validation (A/B | prototype | survey | interviews)
  → PRD → engineering (out of scope) → rollout → measurement → signals
```

1. **Signals** are things that happen — from calls, research, tickets, analytics and external intelligence. A signal can be unique or repeat.
2. **Hypotheses** aggregate signals into testable bets. A hypothesis starts as `proposed` and moves toward testing.
3. **Validation** picks the cheapest adequate test.
4. **PRDs** carry validated bets to engineering; this repo owns the PRD → ticket hand-off, not the build.
5. **Rollout and measurement** write results back as new signals, closing the loop.

Canonical definition, vocabulary and the status of every stage: [`reference/product-loop.md`](reference/product-loop.md). The loop is open at both ends until Plans 1–4 land (see [Limitations](#limitations)).

## How each stage is implemented

This table mirrors the machine-checked stage status table in [`reference/product-loop.md`](reference/product-loop.md#stage-status); if they disagree, the reference wins.

| Stage | Status | Entry points |
| --- | --- | --- |
| 1. Input signals | partial | `/customer-call` ([`customer-call.md`](.claude/commands/customer-call.md)) and `/log-signal` ([`log-signal.md`](.claude/commands/log-signal.md)) add rows to [`signals.csv`](product-development/signals/signals.csv) through `scripts/signals/signals.py` ([contract](reference/signal-contract.md)); `/feature-request-intake` ([`feature-request-intake.md`](.claude/commands/feature-request-intake.md)) files the feature-request issue. Analytics feed: planned (Plan 4). |
| 2. Hypotheses | partial | The [hypothesis](templates/hypothesis.md) template; [`discovery-artifact-types.md`](reference/discovery-artifact-types.md). Derived reach and validation recommendation: planned (Plan 2). |
| 3. Validation | partial | [`analytics/experiments/`](product-development/analytics/experiments/). Results as signals: planned (Plans 1 and 4). |
| 4. Prototyping | partial | The [`prototype` skill](.claude/skills/prototype/SKILL.md). Prototypes are throwaway by design; linking them to a shared design system is a Later roadmap item. |
| 5. PRDs | partial | `/prd` ([`prd.md`](.claude/commands/prd.md)), then `/to-prd` → `/to-spec` → `/to-tickets` → `/implement`. Acceptance criteria: planned (Plan 3). |
| 6. Engineering | out-of-scope | The repo owns only the PRD → ticket hand-off ([`issue-tracker.md`](docs/agents/issue-tracker.md)). |
| 7. Rollout and measurement | planned | Metric and experiment results become signals: Plan 4. |
| Loop closure | planned | Plans 1 and 4. |

Across all stages, the [integrity checks](scripts/integrity-checks/README.md) detect missing or inconsistent artifacts (a hypothesis with no supporting signal, a PRD missing required sections, `feature-index.yaml` drift).

## Plug-and-play

TeamOSTemplate is the integration layer and system of record; it assumes no vendor, prioritisation framework or roadmap method.

- **Capabilities.** Every external tool — issue tracker, support desk, CRM / call recorder, analytics warehouse, external intelligence, design tool — is a capability filled by a named adapter per install. The current map is in [`docs/agents/capabilities.md`](docs/agents/capabilities.md). A skill names the capability, never the vendor.
- **One way to add a signal.** Every source adds signals through one script. Planned (Plan 1); until it lands, intake is manual.
- **Reference external adapter.** [product-intelligence-agent](https://github.com/AndyMelnykov/product-intelligence-agent) is the first external source adapter; its integration is planned (handoff 2a). See [ADR 0007](docs/adr/0007-teamos-is-the-integration-layer.md).

## Repository structure

Five structural moves make the context navigable:

1. **Nested routers.** A `CLAUDE.md` in the root and in each meaningful folder describes its contents and links deeper. An agent walks the tree instead of loading everything.
2. **Function × product-area matrix.** Functions (`product/`, `engineering/`, `analytics/`, `data-engineering/`, `design/`) are the top axis, so any path is guessable once the pattern is known.
3. **One join table.** The matrix scatters a feature across up to eight folders, so [`feature-index.yaml`](product-development/feature-index.yaml) reassembles it: PRD, RFCs, plans, Figma link, tickets, schemas, queries, dashboards, experiments and bug investigations. See [ADR 0002](docs/adr/0002-feature-index-as-join-table.md).
4. **Naming conventions as addresses.** `{feature}-prd.md`, `{feature}-rfc.md`, `YYYY-MM-DD-{topic}-decision.md`, so lookups are constructible rather than searched.
5. **Shared vocabulary in [`reference/`](reference/CLAUDE.md).** Terminology, metrics, segments, statuses, decision types and the product loop are defined once; every other doc links to them.

Raw evidence is kept beside derived summaries (`calls/transcripts/` next to `calls/summaries/`), and external systems are pointed at, not mirrored. Full diagrams: [`docs/architecture.md`](docs/architecture.md).

## Demo

Every path below is a real file, not an illustration.

### Why are we building Team Workspaces, and has it shipped?

1. Check the join table: [`feature-index.yaml`](product-development/feature-index.yaml) → `prototyping.team-workspaces` → points to a PRD and an eng RFC.
2. Load the PRD: [`team-workspaces-prd.md`](product-development/product/PRDs/team-workspaces-prd.md) → Problem Statement cites Acme Corp's account team asking for manager-level review workflows and pre-assigning internal owners for rollout.
3. Check the account for corroborating evidence: [`customers/accounts/acme-corp/`](product-development/product/customers/accounts/acme-corp/).
4. Check the canonical status enum: [`reference/status-definitions.md`](reference/status-definitions.md) → the PRD's `**Status**` is `Draft`, meaning *"being written; not yet shared for feedback."*
5. Answer: *Team Workspaces is still in Draft (not shipped). It's driven by validated demand from Acme Corp.*

Five file reads, no guessing what "Draft" means, no duplicated definitions. Run the same question against `evaluation/task-set.md`'s baseline condition (router files and `feature-index.yaml` removed) and the answer requires searching the raw tree unassisted — the comparison [`evaluation/`](evaluation/CLAUDE.md) is set up to measure (see [Evaluation](#evaluation)).

### Why does HYP-EXTRACT-001 exist?

1. Start at the hypothesis: [`extraction-confidence-scoring-hypothesis.md`](product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-hypothesis.md) → the bet is a plain-language confidence label on extracted fields; its Result is `pending`.
2. Follow its supporting signals, `SIG-002` and `SIG-003`, in [`signals.csv`](product-development/signals/signals.csv) → trust is the top concern, and users ask whether extraction is "good enough" rather than how OCR works.
3. Read each signal's `source_ref` → `SIG-002` and `SIG-003` both point to `r/PandaDoc` document-security threads from the Reddit customer research.
4. Answer: *the hypothesis exists because Reddit research surfaced a trust gap in extraction output; it is untested.*

`python scripts/signals/signals.py show SIG-002` returns the row and the hypotheses citing it. The hypothesis changes (Plan 2) are planned to make the rest of the chain one lookup.

## AI design decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Primary retrieval | Structured navigation (router tree + naming conventions + join table), not embeddings | The domain is small and stable enough to be fully addressable. [ADR 0001](docs/adr/0001-structured-navigation-over-embeddings.md) |
| Cross-functional reassembly | One join table (`feature-index.yaml`), not a feature-first folder structure | Keeps function-first ownership clarity while answering feature-shaped questions. [ADR 0002](docs/adr/0002-feature-index-as-join-table.md) |
| Canonical writes | Human approval before editing `reference/` or `strategy/` | Those files are read by many future sessions; a bad edit's blast radius is the shared vocabulary. [ADR 0003](docs/adr/0003-human-approval-for-canonical-writes.md) |
| Orchestration | One agent per session, not a multi-agent pipeline | The recurring tasks are sequential (gather → draft → human review). [ADR 0004](docs/adr/0004-single-agent-no-orchestration.md) |
| Discovery layer | Hypothesis files next to the PRDs they feed | Records why a PRD exists and what was bet on, without a new top-level tree. [ADR 0008](docs/adr/0008-hypothesis-is-the-discovery-artifact.md) |
| PRD review | A Review Tier field on the PRD, not a second approval gate | Two-track review without a second approval step. [ADR 0006](docs/adr/0006-two-track-prd-review.md) |
| Integration | This repo is the system of record; external agents and tools are source adapters | One store and one vocabulary, any number of adapters. [ADR 0007](docs/adr/0007-teamos-is-the-integration-layer.md) |
| Provenance | Raw evidence kept beside derived summaries, never overwritten | Lets a human or agent re-verify a claim without losing the source. |

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

- Editing `reference/` (terminology, metrics, segments, statuses, decision types, the product loop) or `product/strategy/` — see [ADR 0003](docs/adr/0003-human-approval-for-canonical-writes.md)
- Creating a dated decision file (`YYYY-MM-DD-{topic}-decision.md`) — the agent drafts, a human decides

### Blocked

- Overwriting raw source evidence (transcripts, existing decision files)
- Silently resolving a naming or status inconsistency instead of surfacing it

## Evaluation

`evaluation/` defines a small, reproducible benchmark for whether this structure helps an agent, rather than asserting that it does:

- [`task-set.md`](evaluation/task-set.md) — seven tasks, each with a verifiable expected answer and source file (e.g. "find the current ESR target" → `reference/metrics.md`, `> 92%`).
- [`protocol.md`](evaluation/protocol.md) — run each task twice, once against the repo as-is and once with router files and `feature-index.yaml` removed; record task accuracy, wrong-source rate, files opened, tokens consumed and citation accuracy.
- [`results/`](evaluation/results/) — **no run has been recorded.** This is a real gap, called out again under [Limitations](#limitations), not papered over with invented numbers.

## Observability

There's no model-call trace to capture; the observable surface is the repo's own audit trail:

- **Reference integrity** — `scripts/check-references.ps1` scans `feature-index.yaml` and every tracked Markdown file for links and paths that don't resolve, and exits non-zero if any are found:

  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1
  ```

  Expected on a clean tree: exit code 0, `No broken references found.`
- **Process integrity** — [`scripts/integrity-checks/`](scripts/integrity-checks/README.md) runs config-driven Python checks across the discovery → PRD → engineering → decision pipeline. A daily GitHub Actions workflow runs them and commits `scripts/integrity-checks/reports/status.json` and [`reports/summary.md`](scripts/integrity-checks/reports/summary.md), so open findings and their age show up in a normal `git log`.
- **Friction logs** — [`PAPERCUTS.md`](PAPERCUTS.md) (things that were broken) and [`SKILL-GAPS.md`](SKILL-GAPS.md) (recipes done by hand with no skill behind them) are live logs agents append to as they work.
- **Decision trail** — git history plus dated decision files ([`reference/decision-types.md`](reference/decision-types.md)) are the durable record of what changed and why.

To work with the repo, clone it and point any coding agent at the root; it starts from `CLAUDE.md` and routes to everything else. Run `pytest -q` from the root to run the tests.

## Adopting this on a real team

Two step-by-step guides, depending on where the team is starting from:

- [`docs/install-from-scratch.md`](docs/install-from-scratch.md) — a new product with no existing knowledge base to reconcile.
- [`docs/install-existing-product.md`](docs/install-existing-product.md) — a product already in development, with docs scattered across Notion/Confluence/Slack — an incremental, function-by-function migration rather than a big-bang rewrite.

## Limitations

- **The loop is open at both ends until Plans 1–4 land.** Signals have one store and entry point (Plan 1) but only manual and agent-driven intake, with no analytics feed (Plan 4), hypotheses show no derived reach or validation recommendation (Plan 2), PRDs lack acceptance criteria (Plan 3), and measurement doesn't flow back as signals (Plan 4).
- **The evaluation has never been run.** The methodology exists and `evaluation/results/` is empty. Treat every claim here about the structure "helping" as a hypothesis with a defined test, not a measured result.
- **Structured navigation degrades on unstructured collections.** `competitive-research/` is closer to a document pile than an addressable table (the customer `Insights/` folder, also flagged, is now the structured `signals.csv`; see [ADR 0001](docs/adr/0001-structured-navigation-over-embeddings.md)).
- **Unwired artifacts are detected, not fixed.** The `feature-index-join-completeness` integrity check detects artifacts missing from `feature-index.yaml`, but nothing writes the entries automatically.
- **No automated staleness or conflict detection for content.** A decision file that contradicts an earlier one, or a reference definition nobody has touched since its dependents changed, isn't caught.
- **One example product, one team's shape.** The taxonomy and naming conventions are tuned to `example_product`; adopting this elsewhere means adapting them, not copying them.

## Roadmap

[`ROADMAP.md`](ROADMAP.md) lists what's next and why; the loop work is sequenced in the [plans index](docs/superpowers/plans/2026-11-03-product-loop-plans-index.md).

## License

This work is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). See [LICENSE](LICENSE) for details.
