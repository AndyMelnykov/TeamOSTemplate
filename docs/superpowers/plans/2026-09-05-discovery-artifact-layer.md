# Discovery Artifact Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a lightweight opportunity/hypothesis layer between raw customer signal (`product/Insights/insights.csv`) and PRDs, plus the small set of supporting conventions (per-area `CONTEXT.md`, `feature-index.yaml` loading hints) identified as genuinely missing when comparing this repo against `product-team-github-structure.md`.

**Architecture:** No new top-level tree. Two new artifact types (`{feature}-opportunity.md`, `{feature}-hypothesis.md`) live next to the PRD they feed, under `product-development/product/PRDs/{area}/`, following the same "lives next to what it affects" convention `reference/decision-types.md` already establishes for decision files. `feature-index.yaml` gains two new pointer keys plus optional loading-hint keys. Per-area `CONTEXT.md` files give each `PRDs/{area}/` folder a short orientation doc.

**Tech Stack:** Markdown, YAML (`feature-index.yaml`), CSV (`insights.csv`), PowerShell (`scripts/check-references.ps1`) — no code, no build step.

**Spec:** None — no separate spec doc exists in-repo. This plan is derived from an ad hoc review comparing the user-supplied `product-team-github-structure.md` (not tracked in this repo) against the current repo structure; the rationale for each task is inline below and in `docs/adr/0005-opportunity-hypothesis-layer.md` (created in Task 5).

## Global Constraints

- New/changed files must keep `scripts/check-references.ps1` passing (exit 0) — it scans `feature-index.yaml` tokens and every tracked Markdown file's relative links.
- Every new top-level file gets wired into the doc index of its parent `CLAUDE.md` — this repo's established navigation pattern.
- Artifacts live next to what they affect, not in a new parallel tree (`reference/decision-types.md`'s convention, reaffirmed by ADR 0002).
- `reference/` edits require a human approval checkpoint before committing (ADR 0003) — Task 1 creates a new file under `reference/`, so it ends with an explicit pause for sign-off rather than an immediate commit.
- `product-development/` and `docs/` edits (Tasks 2–5) are not gated by ADR 0003 and can be committed directly once verified.
- Placeholder tokens in template files use `{curly-brace}` syntax — `check-references.ps1` already special-cases this pattern as illustrative, not a broken link, so templates don't trip the checker.

---

### Task 1: Canonical discovery-artifact conventions (`reference/`)

**Files:**
- Create: `reference/discovery-artifact-types.md`
- Modify: `reference/CLAUDE.md` (Doc Index table)

**Interfaces:**
- Produces: the `OPP-{AREA}-{NNN}` / `HYP-{AREA}-{NNN}` ID scheme and the two artifact-type definitions that Tasks 2–4 instantiate.

- [ ] **Step 1: Write `reference/discovery-artifact-types.md`**

```markdown
# Discovery Artifact Types

Canonical artifact types for framing a problem before it becomes a PRD. An opportunity or hypothesis file is named `{feature}-opportunity.md` / `{feature}-hypothesis.md` and placed in the same folder as the PRD it feeds — there is no separate top-level discovery tree, matching how decision files live next to what they decided (see `decision-types.md`).

| Type | Where it's recorded | Example location |
|------|---------------------|-------------------|
| Opportunity | `product-development/product/PRDs/{area}/` | `product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-opportunity.md` |
| Hypothesis | Same folder as its opportunity | `product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-hypothesis.md` |

## ID scheme

- `OPP-{AREA}-{NNN}` — one per opportunity. `{AREA}` is a short mnemonic for the feature-index area (doesn't have to match the `feature-index.yaml` key exactly — e.g. `EXTRACT` for `extraction-quality`). `{NNN}` is sequential starting at 001 within that area.
- `HYP-{AREA}-{NNN}` — one per hypothesis, same numbering rule, references exactly one `OPP-` id in its own `## Opportunity` section.

IDs are for cross-referencing only (in `feature-index.yaml`, PRDs, and `product/Insights/insights.csv` rows) — they don't replace the dated-filename convention used elsewhere in this repo (`decision-types.md`).

## When to write one

Write an opportunity file when a pattern in `product/Insights/insights.csv` (or an analytics investigation, or competitive research) looks worth solving but nothing has committed engineering time yet. Write a hypothesis file once a specific bet is chosen and needs a falsifiable test before a PRD gets written. Skip both for small, uncontested fixes — they exist to make "why does this PRD exist" answerable, not to gate every change.

## Templates

Start from `templates/opportunity.md` and `templates/hypothesis.md`.

## Wiring into feature-index.yaml

Add `opportunity:` and `hypothesis:` keys to the feature's entry once the files exist, the same way `prd:` or `eng-rfc:` are added today. Optional `read_first:` and `do_not_load_by_default:` list keys may also be added to any feature-index entry — `read_first` names the paths (relative to `product-development/`) an agent should open before anything else in that entry; `do_not_load_by_default` names paths that exist but shouldn't be pulled in without a specific reason (e.g. an archived experiment). Both are hints, not enforced by tooling.

## Promotion

Once an opportunity file cites an `insight_id`, bump that row's `status` in `insights.csv` to `validated`. Once a PRD is committed against the hypothesis, bump the same rows to `actioned`. If the resulting initiative surfaces a learning worth keeping beyond this one feature, promote it into the relevant `PRDs/{area}/CONTEXT.md`'s "Active opportunities" section becoming a closed line, or into `product/CLAUDE.md` if it's broadly applicable — don't leave durable learnings stranded only in a closed opportunity file.
```

- [ ] **Step 2: Add a row to `reference/CLAUDE.md`'s Doc Index table**

Insert after the `decision-types.md` row:

```markdown
| `discovery-artifact-types.md` | Opportunity/hypothesis artifact types, ID scheme, and the `{feature}-opportunity.md` / `{feature}-hypothesis.md` naming convention |
```

- [ ] **Step 3: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.` (exit 0)

- [ ] **Step 4: Pause for human sign-off before committing**

This step creates a new file under `reference/`, which ADR 0003 gates behind human approval before it becomes canonical. Show the diff and get an explicit go-ahead — do not commit in the same action as drafting.

- [ ] **Step 5: Commit**

```bash
git add reference/discovery-artifact-types.md reference/CLAUDE.md
git commit -m "docs: define opportunity/hypothesis discovery artifact conventions"
```

---

### Task 2: Templates (`templates/`)

**Files:**
- Create: `templates/opportunity.md`
- Create: `templates/hypothesis.md`

**Interfaces:**
- Consumes: the ID scheme and field list from Task 1's `reference/discovery-artifact-types.md`.
- Produces: the exact section headers Task 3's worked example fills in.

- [ ] **Step 1: Write `templates/opportunity.md`**

```markdown
# OPP-{AREA}-{NNN}: {Opportunity title}

## Problem

{What friction or unmet need are users experiencing, stated in their own terms.}

## Who experiences it

- {Segment or role}

## Evidence

- {INS-### from insights.csv, AN-### or a file path to an analytics investigation, or competitive research finding}

## Why it matters

{What it costs the business or the user if unaddressed.}

## Success signal

{What "solved" would look like, in observable terms — not a solution, a signal.}

## Status

`{new | validated | in-progress | shipped | archived}`
```

- [ ] **Step 2: Write `templates/hypothesis.md`**

```markdown
# HYP-{AREA}-{NNN}

If {change}, then {expected user behavior change}, because {underlying belief}.

## Opportunity

OPP-{AREA}-{NNN}

## Supporting evidence

- {INS-### / AN-### / file path}

## Test

{Method: interviews, prototype, fake door, live experiment, etc.}

## Success criteria

- {Measurable threshold 1}
- {Measurable threshold 2}

## Result

`{pending | supported | not supported}` — {one-line outcome once known; link to the relevant `analytics/experiments/` file if a live experiment ran}
```

- [ ] **Step 3: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.` (the `{...}` placeholders are already excluded by the checker's `Test-IsExternalRef`.)

- [ ] **Step 4: Commit**

```bash
git add templates/opportunity.md templates/hypothesis.md
git commit -m "docs: add opportunity and hypothesis templates"
```

---

### Task 3: Worked example — extraction confidence scoring

**Files:**
- Create: `product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-opportunity.md`
- Create: `product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-hypothesis.md`
- Modify: `product-development/feature-index.yaml` (new `extraction-quality` top-level area)
- Modify: `product-development/product/Insights/insights.csv` (bump `INS-002`, `INS-003` status)
- Modify: `product-development/product/PRDs/CLAUDE.md` ("Opportunities in progress" section)

**Interfaces:**
- Consumes: `templates/opportunity.md`, `templates/hypothesis.md` (Task 2); `INS-002`/`INS-003` rows already in `insights.csv`; the "Extraction Quality" pillar already named in `product-development/product/CLAUDE.md`'s Five Core Pillars table, which lists "extraction confidence scoring" as a P0 feature with no PRD behind it yet.
- Produces: `OPP-EXTRACT-001`, `HYP-EXTRACT-001` — real IDs Task 4's `CONTEXT.md` references.

- [ ] **Step 1: Write the opportunity file**

`product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-opportunity.md`:

```markdown
# OPP-EXTRACT-001: Users can't tell whether extracted data is trustworthy enough to publish

## Problem

Non-technical ops/legal users have no way to judge whether AI-extracted fields are accurate enough to route into a live workflow. They either over-trust the output — and ship errors downstream — or manually re-check everything, losing the time automation was supposed to save.

## Who experiences it

- Ops and legal admins running document workflows without an engineering background
- Teams moving from a manual pilot to production volume (see `INS-001`, `INS-004`)

## Evidence

- `INS-002` — trust/security is the top named concern for non-technical users evaluating extraction output
- `INS-003` — users ask whether extraction is "good enough", not how OCR works internally

## Why it matters

Low trust in extraction output blocks the exact production-readiness transition Pillar 1 (Extraction Quality) is supposed to enable — see [`product/CLAUDE.md`](../../CLAUDE.md)'s Five Core Pillars table, which already lists "extraction confidence scoring" as a P0 feature with no PRD behind it yet.

## Success signal

Users can look at any extracted field and get a plain-language confidence read ("high confidence" / "needs review" / "not ready to publish") with a concrete reason, without needing to understand OCR.

## Status

`validated`
```

- [ ] **Step 2: Write the hypothesis file**

`product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-hypothesis.md`:

```markdown
# HYP-EXTRACT-001

If extracted fields show a plain-language confidence label (high confidence / needs review / not ready to publish) with a one-line reason, then non-technical users will correctly identify which fields need manual review before publishing, because they're currently guessing rather than being told.

## Opportunity

OPP-EXTRACT-001

## Supporting evidence

- `INS-002`
- `INS-003`

## Test

Prototype + usability study: show test users a workflow with mixed-confidence extracted fields and ask them to identify which fields they'd manually check before publishing.

## Success criteria

- 70%+ of test users correctly flag the deliberately-low-confidence fields
- 0 high-confidence fields flagged as needing review (false positives undermine trust in the label itself)

## Result

`pending`
```

- [ ] **Step 3: Add the `extraction-quality` area to `feature-index.yaml`**

Append at the end of `product-development/feature-index.yaml`:

```yaml
extraction-quality:
  extraction-confidence-scoring:
    opportunity: product/PRDs/extraction-quality/extraction-confidence-scoring-opportunity.md
    hypothesis: product/PRDs/extraction-quality/extraction-confidence-scoring-hypothesis.md
    read_first:
      - product/PRDs/extraction-quality/extraction-confidence-scoring-opportunity.md
```

- [ ] **Step 4: Bump `insights.csv` status for the cited rows**

In `product-development/product/Insights/insights.csv`, change the `status` field from `new` to `validated` on the `INS-002` and `INS-003` rows (leave every other column untouched).

- [ ] **Step 5: Add an "Opportunities in progress" section to `PRDs/CLAUDE.md`**

Insert before the "## Creating New PRDs" section in `product-development/product/PRDs/CLAUDE.md`:

```markdown
## Opportunities in progress (no PRD yet)

Framed but not yet committed to engineering time. See [reference/discovery-artifact-types.md](../../../reference/discovery-artifact-types.md).

| Opportunity | Hypothesis | Area |
|-------------|-----------|------|
| `extraction-quality/extraction-confidence-scoring-opportunity.md` (`OPP-EXTRACT-001`) | `extraction-quality/extraction-confidence-scoring-hypothesis.md` (`HYP-EXTRACT-001`) | Extraction Quality |
```

- [ ] **Step 6: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 7: Commit**

```bash
git add product-development/feature-index.yaml \
        product-development/product/Insights/insights.csv \
        product-development/product/PRDs/CLAUDE.md \
        product-development/product/PRDs/extraction-quality/
git commit -m "feat: add extraction-confidence-scoring opportunity and hypothesis as a worked example"
```

---

### Task 4: Per-area `CONTEXT.md` files

**Files:**
- Create: `product-development/product/PRDs/extraction-quality/CONTEXT.md`
- Create: `product-development/product/PRDs/billing/CONTEXT.md`

**Interfaces:**
- Consumes: `OPP-EXTRACT-001` / `HYP-EXTRACT-001` from Task 3; the existing `billing/credit-usage-dashboard-prd.md` and `../sso-prd.md` paths already present under `product-development/product/PRDs/`.

- [ ] **Step 1: Write `product-development/product/PRDs/extraction-quality/CONTEXT.md`**

```markdown
# Extraction Quality

## Purpose

Make AI-extracted data trustworthy enough that non-technical ops/legal users can publish a workflow without manually re-checking every field. Maps to Pillar 1 in [`product/CLAUDE.md`](../../CLAUDE.md)'s Five Core Pillars.

## Core metrics

Canonical definitions live in [reference/metrics.md](../../../../reference/metrics.md). Extraction success rate (ESR) is the metric most relevant here.

## Active opportunities

- `OPP-EXTRACT-001` — `extraction-confidence-scoring-opportunity.md`

## Active hypotheses

- `HYP-EXTRACT-001` — `extraction-confidence-scoring-hypothesis.md`

Read deeper only when required.
```

- [ ] **Step 2: Write `product-development/product/PRDs/billing/CONTEXT.md`**

```markdown
# Billing

## Purpose

Let customers understand and control what they're spending on credits/usage, and let teams manage seats — without a support ticket.

## Core metrics

Canonical definitions live in [reference/metrics.md](../../../../reference/metrics.md).

## Shipped

- Credit usage dashboard — `credit-usage-dashboard-prd.md`
- SSO integration — [`../sso-prd.md`](../sso-prd.md)

## Active opportunities

None currently. Add a `{feature}-opportunity.md` here before the next billing PRD — see [reference/discovery-artifact-types.md](../../../../reference/discovery-artifact-types.md).

Read deeper only when required.
```

- [ ] **Step 3: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 4: Commit**

```bash
git add product-development/product/PRDs/extraction-quality/CONTEXT.md \
        product-development/product/PRDs/billing/CONTEXT.md
git commit -m "docs: add per-area CONTEXT.md for extraction-quality and billing PRD folders"
```

---

### Task 5: Record the decision and update the roadmap

**Files:**
- Create: `docs/adr/0005-opportunity-hypothesis-layer.md`
- Modify: `ROADMAP.md` ("Already shipped" section)
- Modify: `product-development/CLAUDE.md` (feature-index schema note)

**Interfaces:**
- Consumes: the rationale already established in Tasks 1–4; references ADR 0002 and ADR 0003 by number.

- [ ] **Step 1: Write `docs/adr/0005-opportunity-hypothesis-layer.md`**

```markdown
# Opportunity and hypothesis files as a discovery layer before PRDs

Nothing between `product/Insights/insights.csv` (raw customer signal) and a PRD currently records why a PRD exists or what was actually being bet on. We add two lightweight artifact types — `{feature}-opportunity.md` and `{feature}-hypothesis.md` — defined in [`reference/discovery-artifact-types.md`](../../reference/discovery-artifact-types.md), living next to the PRD they feed rather than in a separate top-level tree, consistent with how decision files already live next to what they decided ([`reference/decision-types.md`](../../reference/decision-types.md)).

## Considered Options

- A separate top-level `discovery/` or `opportunities/` tree. Rejected: it would fragment a feature's history across yet another folder on top of the eight functions ADR 0002 already reassembles through `feature-index.yaml`, for artifacts that are only ever read alongside the PRD they justify.
- Folding "why this PRD" reasoning directly into the PRD's Overview section instead of a separate file. Rejected: a PRD's Overview is written after a bet is already chosen; there's no place to record the opportunity before a hypothesis narrows it, or to keep the falsifiable test/result visible once the PRD ships.
- A full domain-first restructure (`CONTEXT.md`/`CURRENT.md`/`METRICS.md` per product domain) instead of this narrower addition. Rejected for the same reason ADR 0002 rejected feature-first folders: it would give up the ownership clarity function-first folders give each team. A lighter per-area `CONTEXT.md` under `PRDs/{area}/` is added instead, without moving anything.

## Consequences

`insights.csv` rows cited by an opportunity should have their `status` bumped to `validated`; rows behind a hypothesis whose PRD is committed should bump to `actioned` — this is a manual step until the "Automatic feature-index maintenance" roadmap item is extended to cover it. `feature-index.yaml` entries may now also carry `opportunity:` / `hypothesis:` keys and optional `read_first:` / `do_not_load_by_default:` loading hints.
```

- [ ] **Step 2: Add a line to `ROADMAP.md`'s "Already shipped" section**

```markdown
- **Opportunity/hypothesis discovery layer** — `reference/discovery-artifact-types.md`, `templates/opportunity.md`, `templates/hypothesis.md`, worked example under `product-development/product/PRDs/extraction-quality/`. See [ADR 0005](docs/adr/0005-opportunity-hypothesis-layer.md).
```

- [ ] **Step 3: Add a feature-index schema note to `product-development/CLAUDE.md`**

Append a new section after the Doc Index table:

```markdown
## `feature-index.yaml` optional keys

Beyond the artifact pointers already in use (`prd:`, `eng-rfc:`, etc.), any entry may carry:

| Key | Purpose |
|-----|---------|
| `opportunity:` / `hypothesis:` | Pointers to the discovery artifacts that justify the feature — see [reference/discovery-artifact-types.md](../reference/discovery-artifact-types.md) |
| `read_first:` | Paths an agent should open before anything else in this entry |
| `do_not_load_by_default:` | Paths that exist but shouldn't be pulled in without a specific reason (e.g. an archived experiment) |
```

- [ ] **Step 4: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 5: Commit**

```bash
git add docs/adr/0005-opportunity-hypothesis-layer.md ROADMAP.md product-development/CLAUDE.md
git commit -m "docs: record ADR 0005 and document feature-index.yaml discovery-layer keys"
```

---

## Self-Review

**Spec coverage** — every item flagged in the prior analysis as "genuinely missing" is covered: discovery layer + stable IDs (Tasks 1–3), insight promotion (Task 3 Step 4, promotion rule in Task 1), templates (Task 2), loading hints on `feature-index.yaml` (Task 1 Step 1 + Task 5 Step 3), pre-registered success criteria (folded into the hypothesis template's `## Success criteria`, no separate `measurement-plan.md` needed), per-area `CONTEXT.md` as the domain-vs-function middle ground (Task 4), and the architectural tension itself recorded as an explicit rejected option in ADR 0005 (Task 5). The `_catalog/` auto-generation and Codex/`AGENTS.md` items from the original doc were deliberately left out of this plan — they're already tracked in `ROADMAP.md` and aren't new findings.

**Placeholder scan** — all Task 1–5 content blocks are complete, real text; the only `{curly-brace}` tokens are inside `templates/opportunity.md` / `templates/hypothesis.md`, which are meant to be fill-in-the-blank and are already excluded by `check-references.ps1`.

**Type/ID consistency** — `OPP-EXTRACT-001` and `HYP-EXTRACT-001` are used identically across the opportunity file, hypothesis file, `feature-index.yaml`, `PRDs/CLAUDE.md`, and `extraction-quality/CONTEXT.md`. `INS-002`/`INS-003` match the actual rows in `insights.csv`.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-09-05-discovery-artifact-layer.md`. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session using `executing-plans`, batch execution with checkpoints.

Which approach?
