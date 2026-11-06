# PRDs

## Purpose
Product Requirement Documents for example_product features.

Valid `**Status**` values are defined in [reference/status-definitions.md](../../../reference/status-definitions.md).

---

## Naming Convention

```
[feature-name]-prd.md
```

Examples:
- `generation-quality-prd.md`
- `one-click-deploy-prd.md`
- `collaboration-prd.md`
- `template-library-prd.md`

---

## Current PRDs

PRDs are organized by product area:

| PRD | Feature |
|-----|---------|
| `billing/credit-usage-dashboard-prd.md` | Credit usage dashboard |
| `deployment/one-click-deploy-prd.md` | One-click deployment to production infrastructure |
| `deployment/custom-domains-prd.md` | Custom domains |
| `home-page/project-search-prd.md` | Project search |
| `prototyping/version-history-prd.md` | Project version history and rollback |
| `starter-templates/community-marketplace-prd.md` | Community template marketplace |

---

## Hypotheses in progress (no PRD yet)

Framed but not yet committed to engineering time. See [reference/discovery-artifact-types.md](../../../reference/discovery-artifact-types.md).

| Hypothesis | Area |
|-----------|------|
| `extraction-quality/extraction-confidence-scoring-hypothesis.md` (`HYP-EXTRACT-001`) | Extraction Quality |

---

## Creating New PRDs

Use the `/prd` command to create new PRDs. The command will:
1. Load the PRD writing style
2. Guide you through required sections
3. Format according to example_product Labs standards
4. Run a CPO check against the finished draft before it's treated as ready to share

---

## PRD Template Sections

This is the single canonical PRD template. `/prd` and `/to-prd` both write to it. A PRD reads as instructions an AI agent or engineer can build and test against.

### Header

```markdown
# [Feature Name] - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | [Name] (PM) |
| **Status** | Draft |
| **Last Updated** | [YYYY-MM-DD] |
| **Related RFC** | `engineering/rfcs/{product-area}/{feature-name}-rfc.md`, or "not yet planned" |
| **Review Tier** | Local or Strategy Review (see "Review Tier" below) |
| **Hypothesis** | `HYP-…` id, or `none — <reason>` |
| **Execution Path** | `agent-direct` or `engineering-mediated` (see "Execution Path" below) |
```

### Sections, in this order

1. **`## Overview`** - with these subsections:
   - `### Problem`
   - `### Why Now`
   - `### Goals & Success Metrics` - a table `| Metric | Baseline | Target | Timeline | Source |`. Metric names and targets match `reference/metrics.md`. `Source` says where the metric is measured (a dashboard, query or table).
   - `### Non-Goals`
2. **`## User Stories`** - Who benefits and how. Number them (`Story 1`, `Story 2`, …) so acceptance criteria can cover them.
3. **`## Requirements`** - three subsections, each a table `| ID | Requirement |`:
   - `### Must Have (P0)` - ids `P0-1`, `P0-2`, …
   - `### Should Have (P1)` - ids `P1-1`, …
   - `### Nice to Have (P2)` - ids `P2-1`, …
4. **`## Acceptance Criteria`** - one table, see below.
5. **`## Design`** - UX flows, wireframes (link the Figma file if one exists).
6. **`## Technical Considerations`** - Architecture, dependencies; link the related RFC if one exists or is planned.
7. **`## Launch Plan`** - Rollout strategy, feature flags.
8. **`## Sources`** - `SIG-###` or file-path citations for claims already made in the sections above, one bullet each, in the same citation format as `templates/hypothesis.md`'s "Signals" section. A file-path citation must be a Markdown link (`[label](relative/path)`), not a bare backtick reference, so `scripts/check-references.ps1` can verify it resolves. This section consolidates citations already made elsewhere in the PRD — it is not a place to introduce a new unsupported claim. See `.claude/commands/prd.md`'s Step 6 (CPO check) for how these are validated.

`## Open Questions` may follow `## Sources`.

### Acceptance Criteria table

One table with these columns:

```markdown
| ID | Given | When | Then | Covers | Verify by |
|----|-------|------|------|--------|-----------|
```

- **ID** - `AC-1`, `AC-2`, … unique within the PRD.
- **Given / When / Then** - all three filled in on every row.
- **Covers** - the requirement ids (`P0-1`, `P1-2`, …) and/or `Story N` the row verifies, comma-separated.
- **Verify by** - exactly one of `automated-test`, `manual-qa`, `analytics`.
- **Coverage rule:** every `P0-n` appears in the `Covers` cell of at least one row. P1 and P2 requirements may be left uncovered.
- **Pipes:** a literal `|` inside a cell is written `\|` so it does not split the cell.

Complete example (a CSV export of the usage report):

```markdown
### Goals & Success Metrics

| Metric | Baseline | Target | Timeline | Source |
|--------|----------|--------|----------|--------|
| Usage report export rate | 0% | 15% of weekly active billing users | 30 days after launch | Product analytics event `usage_report_exported` |

### Must Have (P0)

| ID | Requirement |
|----|-------------|
| P0-1 | A signed-in user can export the usage report for a chosen date range as a CSV file. |
| P0-2 | The export is limited to the user's own workspace. |

| ID | Given | When | Then | Covers | Verify by |
|----|-------|------|------|--------|-----------|
| AC-1 | A user with 30 days of usage data is on the usage report | They choose "Last 30 days" and select Export CSV | A CSV downloads with one row per day and the columns Date, Activity, Credits | P0-1, Story 1 | automated-test |
| AC-2 | A user belongs to workspace A and workspace B has usage data | They request an export while viewing workspace A | The file contains only workspace A rows; a request for a workspace B id returns 403 | P0-2 | automated-test |
| AC-3 | The feature has been live for 30 days | Weekly active billing users are counted against users who exported at least once | At least 15% of weekly active billing users have exported once (metric: "Usage report export rate" in Goals & Success Metrics) | P0-1 | analytics |
```

### Writing acceptance criteria

- Describe observable behaviour, not implementation. "The file contains only workspace A rows" — not "the query adds a `WHERE workspace_id` clause".
- One Given/When/Then per row. If a row needs "and" in `When` or `Then`, split it.
- Edge and error cases (empty data, no permission, invalid input, failure of a dependency) get their own rows.
- An `analytics` row names a metric from `### Goals & Success Metrics` and states the threshold; the metric's `Source` is where it is checked.
- IDs are stable once the PRD leaves `Draft`: append new ids, never renumber or reuse one. Retire a criterion by editing its row and noting why, not by deleting it.
- A requirement too vague to turn into a testable criterion goes to `## Open Questions`, not into an invented criterion.

---

## Review Tier

Every PRD's header table carries a `**Review Tier**` field: `Local` or `Strategy Review`.

A PRD is `Strategy Review` tier if it meets any of:
- It spans more than one product area (see the areas listed in `product-development/feature-index.yaml`).
- It redefines or materially changes a term in `reference/terminology.md` or a metric in `reference/metrics.md`.
- It changes a cross-feature interaction model — a pattern or surface multiple other features already depend on (e.g. the shared clause/field block library, not a single feature's own UI).

Otherwise it is `Local` tier. Most PRDs are `Local` — this mirrors normal PR-level review. A `Strategy Review`-tier PRD additionally requires a decision file recording the review's outcome (see `reference/decision-types.md` and `docs/adr/0006-two-track-prd-review.md`) before `**Status**` can advance past `In Review`.

---

## Execution Path

Every PRD's header carries an `**Execution Path**` field saying who turns the PRD into working code:

- **`agent-direct`** - the PM hands the PRD to an agent (via `/to-tickets`) and the agent builds against the acceptance criteria.
- **`engineering-mediated`** - an engineer reads the PRD, writes a spec, and briefs the agent (or builds it themselves).

`agent-direct` is allowed only when **all** of these hold:
- `**Review Tier**` is `Local`.
- The change stays within one product area.
- No data migration or schema change.
- No new external integration.
- No acceptance criterion has `Verify by` = `analytics` (those need instrumentation decisions an engineer owns).

Otherwise use `engineering-mediated`. When in doubt, use `engineering-mediated`.

Examples:
- `agent-direct` - "Export usage report as CSV": `Local`, billing only, reads existing tables, no new integration, every AC is `automated-test` or `manual-qa`.
- `engineering-mediated` - a hypothetical "SSO login" feature: needs a new external identity-provider integration and a schema change, so an engineer scopes it first.

---

## Hand-off

Acceptance-criteria ids are the thread from PRD to ticket to test.

- **`agent-direct`:** the PM runs `/to-tickets` on the PRD. Each ticket lists the `AC-n` ids it satisfies, and every AC id appears in at least one ticket.
- **`engineering-mediated`:** the engineer runs `/to-spec` with the PRD as input and maps every `AC-n` id to an automated test or a manual-QA step in the spec.
- **Tests:** a test that verifies a criterion carries its AC id in its name or description (e.g. `test_ac2_export_limited_to_own_workspace`). A `manual-qa` criterion carries its id in the QA checklist item.
- **Changes:** if a criterion changes after the PRD leaves `Draft`, update the row in place and tell the owners of the tickets and tests that reference its id.

`/to-spec` and `/to-tickets` are vendored skills and are not edited; they read the root `CLAUDE.md`, which points them here.
