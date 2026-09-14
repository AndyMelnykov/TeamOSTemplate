# Feature-Request Intake and Two-Track PRD Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two independent capabilities approved during this session's brainstorming pass: (1) a `/feature-request-intake` command + skill that turns a raw customer/internal ask into a structured, function-routed GitHub issue, reusing the existing tracker and feature-index; (2) a `Review Tier` field on PRDs (`Local` | `Strategy Review`) that routes cross-cutting PRDs through a required decision-file write under `product-development/product/strategy/`, which in turn falls inside the existing human-approval gate — no new approval mechanism.

**Architecture:** No new agents, no new subsystem, no live integrations. Feature 1 is a new command/skill pair following the existing `customer-call.md` → `customer-call-summary` skill split verbatim, producing one GitHub issue per invocation via `gh issue create` (per `docs/agents/issue-tracker.md`). Feature 2 is a new header-table field plus one new checklist item in `/prd`'s existing Step 6 (CPO check), backed by a new canonical rule in `reference/decision-types.md` and recorded in a new ADR. Both features are run by the same single agent session that already runs `/prd` and `/customer-call` (ADR 0004 — no new agent role).

**Tech Stack:** Markdown (commands, skills, reference docs, ADR), YAML (`feature-index.yaml`, read-only here), `gh` CLI (GitHub issues, read-only during this plan's dry runs), PowerShell (`scripts/check-references.ps1`) — no code, no build step.

**Spec:** None — both additions were designed and approved in chat during this session's brainstorming pass (see conversation history: a transcript-derived list of repo-improvement ideas, two of seven approved for implementation). This repo's own precedent, `docs/superpowers/plans/2026-09-12-prd-cpo-check-and-sources.md`, made the same call for a similarly-scoped, chat-approved pair of additions — design decisions are captured inline below as Global Constraints and per-task rationale instead of in a separate spec file.

## Global Constraints

- **No test runner/CI.** "Verification" means running `powershell -File scripts/check-references.ps1` from the repo root (expect `No broken references found.`) plus a manual read-through comparing new content against the canonical file it cites.
- **One-agent-per-session (ADR 0004):** both features are commands/skills the same session runs inline — no separate reviewer agent, no pipeline stage.
- **Human-approval-for-canonical-writes (ADR 0003)** applies to `reference/` and `product-development/product/strategy/`. This plan writes two files under `reference/` (Task 1: `reference/sla-policy.md`; Task 7: an edit to `reference/decision-types.md`) — both tasks include an explicit approval checkpoint before their commit step. No task in this plan writes to `product-development/product/strategy/` directly: Task 8's dry run only adds a header-table field to two existing PRDs under `product-development/product/PRDs/`, so no approval pause applies there. (If a real Strategy-Review-tier PRD is later resolved by writing a decision file under `strategy/`, that future write requires human approval per ADR 0003 — this plan documents that rule, it doesn't exercise it, since there is no real strategy review to resolve yet.)
- **Function/category labels are read live, not hardcoded.** The root `CLAUDE.md` Team table currently lists only two example rows (`EM`, `Engineering`). `feature-request-intake` reads whatever `Function` values exist in that table at run time rather than assuming a fixed list — this keeps the command generic across installs that add more rows (Product, Design, CS, etc.) without a plan change.
- **GitHub issue creation is real when the command runs for a user, simulated during this plan's dry run.** Task 5 exercises the command's dedup/evidence/routing/SLA steps against a real scenario and even runs a real, read-only `gh issue list` — but does not call `gh issue create`, so this plan's own execution doesn't leave a fabricated issue in the tracker.
- **Out of scope (per approved chat design):** Slack/live-chat integration, a real GitHub label-config script, a named-owner routing file, any new agent/orchestration layer. Do not build these.
- **Naming:** the new command is `/feature-request-intake` (`.claude/commands/feature-request-intake.md`), a descriptive multi-word name consistent with this repo's existing `customer-call.md` / `prd.md` commands (no enforced length limit found in repo).

---

### Task 1: Add the SLA policy reference (`reference/sla-policy.md`)

**⚠️ Human approval required (ADR 0003):** this task creates a new file under `reference/`. Do not commit until a human has reviewed and explicitly approved the content.

**Files:**
- Create: `reference/sla-policy.md`
- Modify: `reference/CLAUDE.md:7-14` (Doc Index table)

**Interfaces:**
- Produces: the canonical `Impact` vocabulary (`High` / `Medium` / `Low`) and its response-by window, keyed by name. Task 2's skill and Task 3's command both look up this table by `Impact` value; the exact three level names (`High`, `Medium`, `Low`) are load-bearing for both.

- [x] **Step 1: Write `reference/sla-policy.md`**

```markdown
# SLA Policy

Canonical response-time policy for inbound feature requests filed via `/feature-request-intake`. Every request is assigned exactly one `Impact` level, which determines how quickly it must get a substantive response (triage, not resolution).

| Impact | Definition | Respond by |
|--------|------------|------------|
| High | Blocking a paying account from renewing or expanding, or reported independently by more than one Enterprise account (see `segments.md` for the Enterprise definition) | 3 business days |
| Medium | Reported by multiple accounts of any segment, or by a single Enterprise account, without blocking renewal/expansion | 10 business days |
| Low | Reported by a single non-Enterprise account, or a workaround already exists | Next planning cycle |

"Respond by" means triage happens by that date (the request moves out of `needs-triage` — see `.claude/skills/triage/SKILL.md`), not that the request ships by then. Impact is stated explicitly by whoever files the request (see `.claude/skills/feature-request-intake/SKILL.md`) — it is never inferred automatically from evidence search results.
```

- [x] **Step 2: Add `sla-policy.md` to `reference/CLAUDE.md`'s Doc Index**

Replace (current lines 7-14):

```markdown
| File | Description |
|------|--------------|
| `terminology.md` | Product and company terminology (Project, Generation, tier names, etc.) |
| `metrics.md` | Metric definitions and targets (ESR, TTP, WCR, D7 retention, etc.) |
| `segments.md` | Customer account segments and call-synthesis lifecycle stages |
| `status-definitions.md` | Valid `**Status**` values for PRDs and RFCs |
| `decision-types.md` | Decision categories and the `YYYY-MM-DD-{topic}-decision.md` naming convention |
| `discovery-artifact-types.md` | Opportunity/hypothesis artifact types, ID scheme, and the `{feature}-opportunity.md` / `{feature}-hypothesis.md` naming convention |
| `01-ai-native-product-os.md` | The architecture spec this repo implements — the source of truth for *why* the repo is structured this way |
```

with:

```markdown
| File | Description |
|------|--------------|
| `terminology.md` | Product and company terminology (Project, Generation, tier names, etc.) |
| `metrics.md` | Metric definitions and targets (ESR, TTP, WCR, D7 retention, etc.) |
| `segments.md` | Customer account segments and call-synthesis lifecycle stages |
| `status-definitions.md` | Valid `**Status**` values for PRDs and RFCs |
| `decision-types.md` | Decision categories and the `YYYY-MM-DD-{topic}-decision.md` naming convention |
| `discovery-artifact-types.md` | Opportunity/hypothesis artifact types, ID scheme, and the `{feature}-opportunity.md` / `{feature}-hypothesis.md` naming convention |
| `sla-policy.md` | Response-time policy for feature requests filed via `/feature-request-intake`, keyed by `Impact` level |
| `01-ai-native-product-os.md` | The architecture spec this repo implements — the source of truth for *why* the repo is structured this way |
```

- [x] **Step 3: Human approval checkpoint**

Present the diff for `reference/sla-policy.md` and `reference/CLAUDE.md` to the human and wait for explicit approval before proceeding to Step 4.

- [x] **Step 4: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [x] **Step 5: Commit**

```bash
git add reference/sla-policy.md reference/CLAUDE.md
git commit -m "docs: add SLA policy reference for feature-request intake"
```

---

### Task 2: Write the feature-request-intake skill (`.claude/skills/feature-request-intake/SKILL.md`)

**Files:**
- Create: `.claude/skills/feature-request-intake/SKILL.md`

**Interfaces:**
- Consumes: `reference/sla-policy.md`'s `Impact` levels (Task 1), the root `CLAUDE.md` Team table's `Function` column, `docs/agents/issue-tracker.md`'s `gh` conventions.
- Produces: the field list, evidence-search method, function-classification method, and issue-body/label format that Task 3's command delegates to. Task 5's dry run exercises this exact format.

- [x] **Step 1: Write the skill file**

```markdown
---
name: feature-request-intake
description: Turn a raw feature ask into a structured, function-routed GitHub issue.
---

# Feature Request Intake

This skill defines the fields, evidence-gathering method, and issue format used by `/feature-request-intake`. The command orchestrates the steps; this file is the format reference.

## Required Fields

Every intake produces an issue with these fields, all stated explicitly by whoever files the request — none of them are inferred from search results:

| Field | Description |
|-------|-------------|
| Title | Short, specific description of the ask |
| Description | The raw ask, in the requester's own words or paraphrased with their intent preserved |
| Reporter | Who raised it — a named customer account (see `product-development/product/customers/CLAUDE.md`) if applicable, or "internal" plus the person's name |
| Frequency | How many times/accounts this has come up, as stated by the person filing it |
| Impact | One of `High` / `Medium` / `Low` — see `reference/sla-policy.md` for definitions |

## Dedup Check

Before filing, check both:
1. `product-development/feature-index.yaml` for an existing feature entry with a matching or near-matching name (same search this repo's `/prd` Step 2 already does).
2. Open GitHub issues labeled `feature-request`: `gh issue list --label feature-request --state open --json number,title,body`.

If either surfaces a clear match, tell the user and stop — do not file a duplicate. Report where you looked either way, per the same convention `.claude/skills/triage/SKILL.md` uses for its own redundancy check.

## Evidence Search

Grep `product-development/product/customers/accounts/*/calls/summaries/` for keywords from the request's title/description:

```bash
grep -ril "keyword1\|keyword2" product-development/product/customers/accounts/*/calls/summaries/
```

List any matches with a one-line snippet and ask the person filing the request whether each is actually related before citing it in the issue body. This is supplementary evidence only — it never substitutes for the explicit Frequency/Impact fields above, and an unconfirmed match must not be cited.

## Function Classification

Read the `Function` column of the root `CLAUDE.md` Team table and classify the request into the function whose remit it best matches (e.g. `Engineering`, `EM`, or whatever rows exist in a given install). This is a category label, not a named-owner assignment — final named ownership is a human triage decision, not something this skill automates. Render the label as `area:<function, lowercased, spaces to hyphens>` (e.g. `area:engineering`).

## SLA Lookup

Look up the stated `Impact` value in `reference/sla-policy.md`'s table and record the resulting "Respond by" window as an explicit target date (today + the stated business-day window) in the issue body.

## Issue Format

- **Title:** `[Feature Request] {title}`
- **Labels:** `feature-request`, `area:<function>`
- **Body:**

```markdown
**Reporter:** {reporter}
**Frequency:** {frequency}
**Impact:** {impact} — respond by {computed date} (see `reference/sla-policy.md`)
**Function:** {function}

## Description

{description}

## Supporting Evidence

{confirmed evidence matches, each as a bullet with a link to the call summary file, or "None found / provided" if none}
```

An issue created this way carries no state label (no `needs-triage` label applied here) — it starts in the "unlabeled" bucket that `.claude/skills/triage/SKILL.md`'s discovery step already treats as needing first triage. Intake and triage are sequential: this skill files the issue; `/triage` moves it from there.
```

- [x] **Step 2: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [x] **Step 3: Commit**

```bash
git add .claude/skills/feature-request-intake/SKILL.md
git commit -m "docs: add feature-request-intake skill"
```

---

### Task 3: Write the feature-request-intake command (`.claude/commands/feature-request-intake.md`)

**Files:**
- Create: `.claude/commands/feature-request-intake.md`

**Interfaces:**
- Consumes: Task 2's skill (field/format/evidence/classification/SLA rules).
- Produces: the `/feature-request-intake` entry point. Task 4 adds a cross-reference to it from `/prd` and `docs/agents/issue-tracker.md`; Task 5 dry-runs it end-to-end.

- [x] **Step 1: Write the command file**

```markdown
# Feature Request Intake

You are turning a raw feature ask into a structured, routed GitHub issue.

**Field, evidence-search, and format details:** read `.claude/skills/feature-request-intake/SKILL.md` before starting Step 3.

## Task Overview

Process a feature request by:
1. Gathering the raw ask and reporter
2. Checking for an existing entry (feature-index and open `feature-request` issues)
3. Searching for supporting evidence in customer call summaries
4. Classifying the request by function
5. Looking up the SLA target
6. Filing the GitHub issue

## Step 1: Gather the Raw Ask

Ask the user for:
- A short title
- The full description (paste, forward, or paraphrase)
- Who raised it — a named customer account (check `product-development/product/customers/CLAUDE.md` for the current list) or an internal reporter

## Step 2: Check for an Existing Entry

Run the Dedup Check from `.claude/skills/feature-request-intake/SKILL.md` against both `product-development/feature-index.yaml` and open `feature-request`-labeled issues. If a match is found, tell the user and stop.

## Step 3: Search for Evidence

Run the Evidence Search from the skill file against `product-development/product/customers/accounts/*/calls/summaries/`. Present any matches to the user and ask which, if any, are actually related before including them.

## Step 4: Gather Frequency and Impact

Ask the user directly for:
- **Frequency** — how many times/accounts this has come up
- **Impact** — `High`, `Medium`, or `Low` (see `reference/sla-policy.md` for definitions)

Do not infer either value from the evidence search in Step 3.

## Step 5: Classify by Function

Read the root `CLAUDE.md` Team table's `Function` column and pick the closest match, per the skill file's Function Classification section. Confirm the choice with the user if it's ambiguous.

## Step 6: Look Up the SLA

Look up the stated Impact level in `reference/sla-policy.md` and compute the "respond by" date.

## Step 7: File the Issue

Compose the issue per the skill file's Issue Format section and create it:

```bash
gh issue create --title "[Feature Request] {title}" --label "feature-request" --label "area:{function}" --body "{body}"
```

Use a heredoc for the body per `docs/agents/issue-tracker.md`'s conventions. Report the created issue's number and URL to the user. The issue starts unlabeled for triage state — `.claude/skills/triage/SKILL.md` picks it up from `needs-triage` onward; this command's job ends once the issue exists.
```

- [x] **Step 2: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [x] **Step 3: Commit**

```bash
git add .claude/commands/feature-request-intake.md
git commit -m "docs: add /feature-request-intake command"
```

---

### Task 4: Wire intake into `/prd`'s dedup check and document the intake→triage handoff

**Files:**
- Modify: `.claude/commands/prd.md:19-21` (Step 2: Check for an Existing Entry)
- Modify: `docs/agents/issue-tracker.md` (append a new section)

**Interfaces:**
- Consumes: Task 3's `/feature-request-intake` command and its `feature-request` label convention.
- Produces: a documented seam so a PRD author discovers an already-filed request, and so the intake→triage handoff is discoverable from the tracker doc rather than only from the skill file.

- [x] **Step 1: Extend `/prd`'s Step 2 to also check open feature-request issues**

Replace (current lines 19-21 of `.claude/commands/prd.md`):

```markdown
## Step 2: Check for an Existing Entry

Search `product-development/feature-index.yaml` under the given product area for an existing feature with this name or a close match. If found, tell the user and offer to edit the existing PRD instead of creating a new one.
```

with:

```markdown
## Step 2: Check for an Existing Entry

Search `product-development/feature-index.yaml` under the given product area for an existing feature with this name or a close match. If found, tell the user and offer to edit the existing PRD instead of creating a new one.

Also check for an open `feature-request`-labeled GitHub issue covering this feature: `gh issue list --label feature-request --state open --json number,title,body`. If found, tell the user and offer to link the issue from the new PRD's `Sources` section rather than treating this as an unrelated fresh request.
```

- [x] **Step 2: Add the intake→triage handoff note to `docs/agents/issue-tracker.md`**

Append after the file's final line (current line 46, end of the "Wayfinding operations" section):

```markdown

## Feature-request intake

`/feature-request-intake` (see `.claude/commands/feature-request-intake.md`) files a new `feature-request`-labeled issue for a raw ask. It intentionally applies no state label — the issue starts in the "unlabeled" bucket, which `/triage`'s discovery step already surfaces as needing first triage. Intake and triage are sequential, not overlapping: intake structures and files the request; `/triage` moves it through `needs-triage` → `ready-for-agent`/`ready-for-human`/`wontfix` from there.
```

- [x] **Step 3: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [x] **Step 4: Commit**

```bash
git add .claude/commands/prd.md docs/agents/issue-tracker.md
git commit -m "docs: wire feature-request-intake into /prd dedup and the issue tracker doc"
```

---

### Task 5: Dry-run feature-request-intake against a real scenario

**Files:** none created or modified — this task exercises Tasks 2-4 against a real scenario and real (read-only) commands. No commit.

**Interfaces:**
- Consumes: Task 1's SLA table, Task 2's skill, Task 3's command, Task 4's dedup wiring.
- Produces: confirmation that the evidence-search grep pattern and the dedup `gh issue list` call actually work against this real repo — the closest equivalent this docs-only repo has to a passing test for Feature 1.

- [x] **Step 1: Choose a scenario**

Use: "Stackline wants to export extracted fields as CSV in bulk across a workflow, not one document at a time." Title: "Bulk CSV export of extracted fields." Reporter: Stackline (Growth segment, see `product-development/product/customers/CLAUDE.md`). Frequency: "mentioned on 2 calls." Impact: `Medium` (single Growth account, no blocking).

- [x] **Step 2: Run the dedup check for real**

```bash
gh issue list --label feature-request --state open --json number,title,body
```

Expected: either no results (label doesn't exist yet in this repo) or an empty/unrelated list — confirms no duplicate exists. Also grep `product-development/feature-index.yaml` for `csv` or `export` to confirm no existing feature entry matches.

- [x] **Step 3: Run the evidence search for real**

```bash
grep -ril "csv\|export" product-development/product/customers/accounts/*/calls/summaries/
```

Record the actual output. For each file returned, open it and confirm (or rule out) relevance to the bulk-CSV-export scenario before treating it as evidence in Step 5.

- [x] **Step 4: Classify function and look up SLA**

Function: read the root `CLAUDE.md` Team table — with only `EM` and `Engineering` rows present in this template, classify as `Engineering` (closest match for an export/data-format feature) and note in the writeup that a real install with a `Product` row would likely route here instead.

SLA: `Medium` → per `reference/sla-policy.md`, respond by (today + 10 business days).

- [x] **Step 5: Compose the issue body (do not file it)**

Write out the full issue title, labels, and body per the skill file's Issue Format, using the real grep results from Step 3 as the Supporting Evidence section (or "None found" if Step 3 returned nothing relevant). Present this composed issue to confirm the field list and format read correctly end-to-end.

- [x] **Step 6: Do not run `gh issue create`**

This is a dry run — filing a real issue for a fictional scenario would pollute the tracker. Stop after Step 5 and note in the plan's execution log that the command was verified up to (not including) issue creation.

---

### Task 6: Add the `Review Tier` field to the PRD template and `/prd`

**Files:**
- Modify: `.claude/commands/prd.md` (Step 1, Step 4's header-table example, Step 6's CPO check)
- Modify: `product-development/product/PRDs/CLAUDE.md` (new "Review Tier" section)

**Interfaces:**
- Produces: the `Review Tier` field name and its two valid values (`Local`, `Strategy Review`), and the criteria for choosing between them. Task 7's ADR and Task 8's dry run both depend on these exact values.

- [x] **Step 1: Add Review Tier criteria to `product-development/product/PRDs/CLAUDE.md`**

Append after the file's final line (current line 67, end of "PRD Template Sections"):

```markdown

---

## Review Tier

Every PRD's header table carries a `**Review Tier**` field: `Local` or `Strategy Review`.

A PRD is `Strategy Review` tier if it meets any of:
- It spans more than one product area (see the areas listed in `product-development/feature-index.yaml`).
- It redefines or materially changes a term in `reference/terminology.md` or a metric in `reference/metrics.md`.
- It changes a cross-feature interaction model — a pattern or surface multiple other features already depend on (e.g. the shared clause/field block library, not a single feature's own UI).

Otherwise it is `Local` tier. Most PRDs are `Local` — this mirrors normal PR-level review. A `Strategy Review`-tier PRD additionally requires a decision file recording the review's outcome (see `reference/decision-types.md` and `docs/adr/0006-two-track-prd-review.md`) before `**Status**` can advance past `In Review`.
```

- [x] **Step 2: Add the Review Tier question to `/prd`'s Step 1**

Replace (current lines 15-17 of `.claude/commands/prd.md`):

```markdown
## Step 1: Confirm Feature Name and Product Area

Ask the user for the feature name and which product area it belongs to (`home-page`, `billing`, `prototyping`, `starter-templates`, or `deployment` — see `product-development/feature-index.yaml` for the current set).
```

with:

```markdown
## Step 1: Confirm Feature Name, Product Area, and Review Tier

Ask the user for the feature name and which product area it belongs to (`home-page`, `billing`, `prototyping`, `starter-templates`, or `deployment` — see `product-development/feature-index.yaml` for the current set).

Also determine the `Review Tier` (`Local` or `Strategy Review`) using the criteria in `product-development/product/PRDs/CLAUDE.md`'s "Review Tier" section. If any criterion is met, it's `Strategy Review`; otherwise `Local`. Tell the user which tier applies and why.
```

- [x] **Step 3: Add the field to `/prd`'s Step 4 header-table example**

Replace (current lines 39-48 of `.claude/commands/prd.md`):

```markdown
Use the header table format from any existing PRD (e.g. `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md`):

```markdown
# [Feature Name] - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | [Name] (PM) |
| **Status** | Draft |
| **Last Updated** | [YYYY-MM-DD] |
| **Related RFC** | `engineering/rfcs/{product-area}/{feature-name}-rfc.md` (once it exists) |
```
```

with:

```markdown
Use the header table format from any existing PRD (e.g. `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md`):

```markdown
# [Feature Name] - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | [Name] (PM) |
| **Status** | Draft |
| **Last Updated** | [YYYY-MM-DD] |
| **Related RFC** | `engineering/rfcs/{product-area}/{feature-name}-rfc.md` (once it exists) |
| **Review Tier** | [Local or Strategy Review — see `product-development/product/PRDs/CLAUDE.md`] |
```
```

- [x] **Step 4: Add the Review Tier check to `/prd`'s Step 6 (CPO check)**

Replace (current lines 62-67 of `.claude/commands/prd.md`, the numbered checklist through item 4):

```markdown
1. **All seven section headers are present and non-empty** - `## Overview`, `## User Stories`, `## Requirements`, `## Design`, `## Technical Considerations`, `## Launch Plan`, `## Sources`, each followed by real content (not a placeholder or an empty section).
2. **Every metric cited matches `reference/metrics.md`** - for each metric name mentioned in the PRD, confirm both the name and any target value match the corresponding row in `reference/metrics.md` exactly. If a cited metric doesn't appear in `reference/metrics.md` at all, flag it to the user rather than treating it as a new canonical metric — new canonical metrics are added to `reference/metrics.md` under the human-approval rule in `docs/adr/0003-human-approval-for-canonical-writes.md`, not invented inline in a PRD.
3. **`**Status**` is a valid value** - one of the five values in `reference/status-definitions.md` (`Draft`, `In Review`, `Approved`, `Shipped`, `Archived`).
4. **`**Related RFC**` is not left as a dangling placeholder** - either a real path, or explicit prose stating no RFC exists yet (e.g. "not yet planned").
```

with:

```markdown
1. **All seven section headers are present and non-empty** - `## Overview`, `## User Stories`, `## Requirements`, `## Design`, `## Technical Considerations`, `## Launch Plan`, `## Sources`, each followed by real content (not a placeholder or an empty section).
2. **Every metric cited matches `reference/metrics.md`** - for each metric name mentioned in the PRD, confirm both the name and any target value match the corresponding row in `reference/metrics.md` exactly. If a cited metric doesn't appear in `reference/metrics.md` at all, flag it to the user rather than treating it as a new canonical metric — new canonical metrics are added to `reference/metrics.md` under the human-approval rule in `docs/adr/0003-human-approval-for-canonical-writes.md`, not invented inline in a PRD.
3. **`**Status**` is a valid value** - one of the five values in `reference/status-definitions.md` (`Draft`, `In Review`, `Approved`, `Shipped`, `Archived`).
4. **`**Related RFC**` is not left as a dangling placeholder** - either a real path, or explicit prose stating no RFC exists yet (e.g. "not yet planned").
5. **`**Review Tier**` is a valid value** - either `Local` or `Strategy Review`, matching the criteria in `product-development/product/PRDs/CLAUDE.md`'s "Review Tier" section. If `Strategy Review`, `**Status**` may not advance past `In Review` unless a decision file recording the review's outcome already exists under `product-development/product/strategy/` (per `reference/decision-types.md` and `docs/adr/0006-two-track-prd-review.md`), linked from this PRD. If no such decision file exists yet, flag it to the user and hold `**Status**` at `In Review` rather than advancing it.
```

Renumber the old item 5 ("Every `Sources` citation resolves") to item 6 in the same list.

- [x] **Step 5: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [x] **Step 6: Commit**

```bash
git add .claude/commands/prd.md product-development/product/PRDs/CLAUDE.md
git commit -m "docs: add Review Tier field and two-track review to /prd"
```

---

### Task 7: Write ADR 0006 and tighten `reference/decision-types.md`

**⚠️ Human approval required (ADR 0003):** this task edits `reference/decision-types.md`. Do not commit until a human has reviewed and explicitly approved the change.

**Files:**
- Create: `docs/adr/0006-two-track-prd-review.md`
- Modify: `reference/decision-types.md`

**Interfaces:**
- Consumes: Task 6's `Review Tier` field and values.
- Produces: the canonical rule Task 8's dry run reasons against — a `Strategy Review`-tier PRD's resolution decision file *must* live under `product-development/product/strategy/`, not the PRD's own folder.

- [x] **Step 1: Write the ADR**

```markdown
# Two-track PRD review: a Review Tier field, not a second approval gate

Most PRDs get lightweight, PR-level review — read the diff, check it against `/prd`'s Step 6 CPO check, merge. A PRD that spans multiple product areas, redefines a canonical term or metric, or changes a cross-feature interaction model needs more: alignment across the areas it touches before implementation starts, not just a correctness check on the document. `product-development/product/PRDs/CLAUDE.md` now defines criteria for this and a `**Review Tier**` field (`Local` | `Strategy Review`) that `/prd` asks for and validates.

Rather than build a second approval mechanism, a `Strategy Review`-tier PRD's resolution is required to be written as a decision file — using the existing format in `reference/decision-types.md` — and that decision file must live under `product-development/product/strategy/`, not the PRD's own folder (the other location `decision-types.md` otherwise allows for a product decision). Writing under `strategy/` puts it inside the human-approval gate already defined in [ADR 0003](0003-human-approval-for-canonical-writes.md), so a `Strategy Review` can't quietly resolve without a human in the loop — with no new gate, no new agent, and no new file format to build.

## Consequences

`/prd`'s Step 6 CPO check now holds `**Status**` at `In Review` for a `Strategy Review`-tier PRD until a linked decision file exists under `strategy/`. This means a PRD author working through a genuinely cross-cutting change gets stopped by the same mechanism that already protects `reference/` and `strategy/`, rather than a bespoke one. If a future PRD's resolution decision is written to its own folder instead of `strategy/` by mistake, it won't trigger ADR 0003's gate — reviewers should treat a `Strategy Review`-tier PRD whose decision file isn't under `strategy/` as non-compliant, not merely differently organized.
```

- [x] **Step 2: Tighten `reference/decision-types.md`**

Replace (current lines 11-13):

```markdown
A decision file should state: the question being decided, the options considered, the decision, who made it, and the date. It should link back to the PRD, RFC, or feature-index entry it affects, and forward to any decision it supersedes.

Only the decision itself is durable and belongs here — see Principle 7 (Durable vs. transient context) in [`01-ai-native-product-os.md`](01-ai-native-product-os.md). Working hypotheses and unapproved alternatives stay out of this pattern.
```

with:

```markdown
A decision file should state: the question being decided, the options considered, the decision, who made it, and the date. It should link back to the PRD, RFC, or feature-index entry it affects, and forward to any decision it supersedes.

**Exception for `Strategy Review`-tier PRDs:** a Product decision that resolves a PRD marked `**Review Tier**: Strategy Review` (see `product-development/product/PRDs/CLAUDE.md`) must be recorded under `product-development/product/strategy/` specifically, not the PRD's own folder — this is what routes it through the human-approval gate in [ADR 0003](../docs/adr/0003-human-approval-for-canonical-writes.md). See [ADR 0006](../docs/adr/0006-two-track-prd-review.md) for why. This tightens the general "or" above into a "must" only for this case; other product decisions may still use either location.

Only the decision itself is durable and belongs here — see Principle 7 (Durable vs. transient context) in [`01-ai-native-product-os.md`](01-ai-native-product-os.md). Working hypotheses and unapproved alternatives stay out of this pattern.
```

- [x] **Step 3: Human approval checkpoint**

Present the diff for `reference/decision-types.md` (and the new ADR, for context) to the human and wait for explicit approval before proceeding to Step 4.

- [x] **Step 4: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [x] **Step 5: Commit**

```bash
git add docs/adr/0006-two-track-prd-review.md reference/decision-types.md
git commit -m "docs: add ADR 0006 and tighten decision-types.md for two-track PRD review"
```

---

### Task 8: Dry-run Review Tier against two real PRDs

**Files:**
- Modify: `product-development/product/PRDs/ai-gen-v3-prd.md:3-8` (header table)
- Modify: `product-development/product/PRDs/shared-components-prd.md:3-8` (header table)
- Modify: `PAPERCUTS.md` (log a real gap found during this dry run)

**Interfaces:**
- Consumes: Task 6's field/criteria, Task 7's decision-file placement rule.
- Produces: two worked examples (one `Local`, one `Strategy Review`) other PRD authors can model future `Review Tier` decisions on, and a real demonstration that the Step 6 checklist item added in Task 6 reasons correctly about both.

- [x] **Step 1: Classify `ai-gen-v3-prd.md` as `Local`**

It's a single-product-area backend model upgrade (`prototyping`), doesn't redefine any term in `terminology.md` or metric in `metrics.md` (it cites ESR/WCR without changing their definitions), and doesn't change a cross-feature interaction model (no UI change at all, per its own Design section). None of the `Strategy Review` criteria apply → `Local`.

- [x] **Step 2: Add the field to `ai-gen-v3-prd.md`**

Replace (current lines 3-8):

```markdown
| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-18 |
| **Related RFC** | `engineering/rfcs/gen-v3-rfc.md` |
```

with:

```markdown
| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-18 |
| **Related RFC** | `engineering/rfcs/gen-v3-rfc.md` |
| **Review Tier** | Local |
```

- [x] **Step 3: Classify `shared-components-prd.md` as `Strategy Review`**

The clause/field block library is explicitly meant to be reused "across a user's workflows" — every product area that uses the workflow builder depends on it, so it changes a cross-feature interaction model (the third `Strategy Review` criterion) even though no single criterion about product-area count or terminology applies on its own. → `Strategy Review`.

- [x] **Step 4: Add the field to `shared-components-prd.md`**

Replace (current lines 3-8):

```markdown
| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-17 |
| **Related Plan** | `engineering/plans/prototyping/component-library.md` |
```

with:

```markdown
| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-17 |
| **Related Plan** | `engineering/plans/prototyping/component-library.md` |
| **Review Tier** | Strategy Review |
```

- [x] **Step 5: Walk through the Step 6 checklist's new item against `shared-components-prd.md`**

`**Status**` is currently `Draft`, not past `In Review`, so the new checklist item does not yet block anything — this is expected and correct (the rule only holds `In Review` → `Approved`). Confirm no decision file currently exists under `product-development/product/strategy/` referencing this PRD (there shouldn't be one — no real strategy review has happened yet). Record in this task's notes: "if this PRD's Status is later advanced toward `Approved`, Step 6 must hold it at `In Review` until a decision file appears under `product-development/product/strategy/` per ADR 0006 — verified by inspection, not by forcing a real Status change here."

- [x] **Step 6: Log the pre-existing Sources gap found in `shared-components-prd.md`**

While reasoning through the Step 6 checklist in Step 5, note that `shared-components-prd.md` has only 6 of the 7 required section headers — no `## Sources` section — a pre-existing gap unrelated to `Review Tier`. This is real friction hit while doing this task's work, so log it per this repo's papercuts convention. Append to `PAPERCUTS.md`'s Log section (after its current final entry):

```markdown
- **2026-09-13** [docs] `product-development/product/PRDs/shared-components-prd.md` is missing the `## Sources` section required by `product-development/product/PRDs/CLAUDE.md`'s 7-section template — discovered while dry-running the Step 6 CPO check's new Review Tier item against it. Out of scope for the Review Tier work; a future pass should backfill Sources here the same way `ai-gen-v3-prd.md` was backfilled. (minor, unresolved)
```

- [x] **Step 7: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [x] **Step 8: Commit**

```bash
git add product-development/product/PRDs/ai-gen-v3-prd.md product-development/product/PRDs/shared-components-prd.md PAPERCUTS.md
git commit -m "docs: dry-run Review Tier against ai-gen-v3 (Local) and shared-components (Strategy Review)"
```

---

### Task 9: Reconcile `ROADMAP.md`

**Files:**
- Modify: `ROADMAP.md` (Already shipped section)

**Interfaces:**
- Consumes: the shipped capabilities from Tasks 1-8.
- Produces: an accurate roadmap reflecting both new capabilities.

- [x] **Step 1: Add both capabilities to "Already shipped"**

Append to the end of the "Already shipped" list (current final bullet is the PRD CPO check entry):

```markdown
- **Feature-request intake** — `.claude/commands/feature-request-intake.md` and `.claude/skills/feature-request-intake/SKILL.md` turn a raw ask into a structured, function-routed GitHub issue (dedup-checked against `feature-index.yaml` and open `feature-request` issues, evidence-searched against customer call summaries, SLA-assigned per `reference/sla-policy.md`). Filed issues start unlabeled for `.claude/skills/triage/SKILL.md` to pick up from `needs-triage`.
- **Two-track PRD review ("Review Tier")** — PRDs now carry a `**Review Tier**` field (`Local` | `Strategy Review`); `/prd`'s Step 6 CPO check holds a `Strategy Review`-tier PRD at `In Review` until a decision file resolving it exists under `product-development/product/strategy/`, which routes it through the existing human-approval gate in [ADR 0003](docs/adr/0003-human-approval-for-canonical-writes.md). See [ADR 0006](docs/adr/0006-two-track-prd-review.md).
```

- [x] **Step 2: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [x] **Step 3: Commit**

```bash
git add ROADMAP.md
git commit -m "docs: reconcile ROADMAP with feature-request intake and two-track PRD review"
```
