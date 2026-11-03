# Plan 5: PRD Acceptance Criteria — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every PRD carries testable, ID'd acceptance criteria that cover every must-have requirement. A PRD reads as instructions an AI agent (or an engineer briefing one) can build and test against, and the criteria are the declared source for automated tests. One PRD template, produced identically by both entry points.

**Background:** this repo has two ways to write a PRD:
- `/to-prd`, a **skill** (`.claude/skills/to-prd/SKILL.md`) that synthesises a PRD from the conversation.
- `/prd`, a **slash command** (`.claude/commands/prd.md`, listed as "prd: PRD Writing") that interviews section by section and runs a "CPO check".

They embed different templates. A `/to-prd` PRD has no `Sources` section and no `Review Tier`, so it fails `/prd`'s check and the `prd-missing-sections` integrity check. `/to-prd` has per-story acceptance-criteria bullets; `/prd` has none.

**Architecture:**
- **One template:** `product-development/product/PRDs/CLAUDE.md` becomes the single canonical template. It gains an `## Acceptance Criteria` table (IDs, Given/When/Then, Covers, Verify by), priority-ID'd requirement tables, and two header fields: `**Hypothesis**` (traceability to Plan 3) and `**Execution Path**` (agent-direct vs engineering-mediated).
- **Both entry points:** `/to-prd` and `/prd` both point at that template instead of embedding one. `/to-prd` runs the same CPO check.
- **Deterministic check:** a new integrity check enforces format and P0 coverage.
- **Hand-off doc:** `docs/agents/prd-handoff.md` tells the vendored engineering skills (`/to-spec`, `/to-tickets`, which must not be edited because `skills-lock.json` tracks them) how to carry AC IDs into tickets and tests.

**Tech Stack:** Markdown, Python 3.12, pytest.

**Spec:** the owner's stage 5 description (PRDs as agent instructions; simple → PM hands to agent, complex → engineering briefs the agent; acceptance criteria are test sources; PRDs include success metrics); [gap analysis](../../../gap-analysis-product-loop-2026-11-03.md) §3 Stage 5; the owner's 2026-11-03 instruction "acceptance criteria should be added to this skill" (`/to-prd`).

## Global Constraints

- Canonical section order:
  1. `## Overview`
  2. `## User Stories`
  3. `## Requirements`
  4. `## Acceptance Criteria`
  5. `## Design`
  6. `## Technical Considerations`
  7. `## Launch Plan`
  8. `## Sources`

  `## Open Questions` may follow `## Sources`. `## Overview` holds these subsections: `### Problem`, `### Why Now`, `### Goals & Success Metrics` (table `| Metric | Baseline | Target | Timeline | Source |`), `### Non-Goals`.
- Requirements: `### Must Have (P0)`, `### Should Have (P1)`, `### Nice to Have (P2)`, each a table `| ID | Requirement |` with ids `P0-1`, `P0-2`, … / `P1-n` / `P2-n`.
- Acceptance Criteria: one table `| ID | Given | When | Then | Covers | Verify by |`.
  - IDs `AC-1`, `AC-2`, … unique within the PRD.
  - `Covers` lists requirement ids and/or `Story N`.
  - `Verify by` is one of `automated-test`, `manual-qa`, `analytics`.
  - Every `P0-n` must appear in at least one `Covers` cell.
- Header table fields, in order:

  | Field | Value |
  |---|---|
  | `**Author**` | |
  | `**Status**` | |
  | `**Last Updated**` | |
  | `**Related RFC**` | |
  | `**Review Tier**` | |
  | `**Hypothesis**` | `HYP-…` or `none — <reason>` |
  | `**Execution Path**` | `agent-direct` or `engineering-mediated` |

- `agent-direct` only when **all** hold:
  - Review Tier `Local`.
  - One product area.
  - No data migration or schema change.
  - No new external integration.
  - Every AC's `Verify by` is `automated-test` or `manual-qa`.

  Otherwise `engineering-mediated`.
- Do not edit skills listed in `skills-lock.json` (vendored from `mattpocock/skills`, including `to-spec` and `to-tickets`); an update would overwrite the edit. `/to-prd` is not in the lock file and is edited.
- Format/coverage enforcement applies at `**Status**` `In Review` and later; `Draft` PRDs get only the missing-section finding.

## Review Focus

1. **A `/to-prd` PRD run through `/prd`'s CPO check.** Expected: passes, because both produce the canonical template. Pinned in Task 2 Step 4 (dry run).
2. **A P0 requirement no criterion covers.** Expected: `prd-acceptance-criteria` names the uncovered id. Pinned in Task 3 (`test_uncovered_p0_is_reported`).
3. **An AC row with an empty `Then` or a `Verify by` outside the enum.** Expected: one finding per row naming the AC id. Pinned in Task 3 (`test_bad_rows_are_reported`).
4. **Old-style headers** (`**Status:** Draft` on a line, as five PRDs have). Expected: normalised to the table so status-based checks see them. Pinned in Task 4 (`test_line_style_status_is_reported`) and fixed in Task 4 Step 3.
5. **A pipe character inside a Given/When/Then cell.** Expected: authors write `\|`, and the parser doesn't split on escaped pipes. Pinned in Task 3 (`test_escaped_pipe_in_cell`).

---

## File Structure

| File | Responsibility |
|---|---|
| `product-development/product/PRDs/CLAUDE.md` (modify) | Canonical template, AC rules, Execution Path definition |
| `.claude/skills/to-prd/SKILL.md` (modify) | Use the canonical template; write AC; run the CPO check |
| `.claude/commands/prd.md` (modify) | Gather AC; extended CPO check; no section count hard-coded |
| `docs/agents/prd-handoff.md` (create) | How AC ids flow into tickets and tests per Execution Path |
| `CLAUDE.md` (modify) | Point engineering skills at the hand-off doc |
| `scripts/integrity-checks/checks/prd_content.py` (modify) | Required sections; new AC, header and execution-path checks |
| `tests/integrity_checks/test_prd_content.py` (modify) | Tests |
| `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md` (modify) | Backfill (the only non-Draft PRD) |
| 5 PRDs with `**Status:**` line headers (modify) | Normalise headers |

---

### Task 1: The canonical template

**Files:**
- Modify: `product-development/product/PRDs/CLAUDE.md`

- [ ] **Step 1: Replace "PRD Template Sections"** with the canonical order and the subsection, requirement, AC and header rules from Global Constraints. Include one complete AC example table of three rows, covering `P0-1`, `P0-2` and `Story 1`, with one `analytics` row tied to a success metric.
- [ ] **Step 2: Add a "Writing acceptance criteria" subsection.** Each criterion is observable behaviour, not implementation. One Given/When/Then per row. Edge and error cases get their own rows. `analytics` rows name the metric from `### Goals & Success Metrics`. AC ids are stable once the PRD leaves Draft: append new ones, never renumber.
- [ ] **Step 3: Add an "Execution Path" subsection** with the rule from Global Constraints and one example of each path.
- [ ] **Step 4: Commit** — `git commit -m "docs: canonical PRD template with acceptance criteria and execution path"`.

### Task 2: `/to-prd` and `/prd` use it

**Files:**
- Modify: `.claude/skills/to-prd/SKILL.md`, `.claude/commands/prd.md`

- [ ] **Step 1: `/to-prd`.**
  - Delete the embedded `<prd-template>`. Replace it with "Write the PRD using the canonical template in `product-development/product/PRDs/CLAUDE.md`, all sections in that order."
  - Keep its synthesis guidance, mapped onto the canonical sections: Problem Statement → `### Problem`; Business Opportunity and Why Now → `### Why Now`; Customer Requests → cite `SIG-`/`EV-` ids in `## Sources` and summarise in `### Problem`; Open Questions → optional trailing section.
  - Add a step: "Derive acceptance criteria from every user story and every P0 requirement; each P0 must be covered; choose Verify by per row."
  - Add a step: "Set `**Hypothesis**` (link the hypothesis this PRD commits to, or `none — <reason>`) and `**Execution Path**` per the rule."
  - Add a final step: "Run the CPO check in `.claude/commands/prd.md` Step 6 against the file."
  - Update the area list to read areas from `feature-index.yaml` instead of hard-coding five.
- [ ] **Step 2: `/prd`.**
  - Step 3 gathers content "for each section of the canonical template" (no count), with AC and the two new header fields.
  - Step 4's header example matches Global Constraints.
  - Step 6 (CPO check) adds:
    - (7) AC table present, ids unique, every row complete, `Verify by` valid.
    - (8) every `P0-n` covered.
    - (9) every metric in `### Goals & Success Metrics` is instrumented (`reference/metrics.md` or `analytics/metrics/`), with `Source` filled.
    - (10) `**Hypothesis**` cites an existing `HYP-` id or says `none — <reason>`.
    - (11) `**Execution Path**` follows the rule.
  - Item 1's wording becomes "every canonical section".
- [ ] **Step 3: Write `docs/agents/prd-handoff.md`.**
  - **`agent-direct`:** the PM runs `/to-tickets` on the PRD. Each ticket body lists the `AC-n` ids it satisfies under "Acceptance criteria", copied verbatim. Tests are named `test_ac_<n>_<slug>` or carry the AC id in their description. The PR closing the ticket lists the AC ids it verified.
  - **`engineering-mediated`:** the named engineer runs `/to-spec` with the PRD as input. Its "Testing Decisions" map every AC id to a test or a manual-QA step. Then `/to-tickets`.
  - **`analytics` rows** become a measurement task (Plan 6 metric watch) rather than a test.
- [ ] **Step 4: Point the engineering skills at the hand-off doc.** In root `CLAUDE.md` under "Agent skills", add a "PRD hand-off" paragraph: "When a ticket or spec is derived from a PRD, follow `docs/agents/prd-handoff.md`." Vendored skills read the project instructions, so this reaches them without edits.
- [ ] **Step 5: Dry run.** In a scratch worktree, run `/to-prd` on a short conversation about "export usage report as CSV" and then `/prd`'s Step 6 on the result. Both pass, and `python scripts/integrity-checks/run_checks.py --repo-root <worktree>` reports no `prd-*` finding for that file. Delete the worktree.
- [ ] **Step 6: Commit** — `git commit -m "feat: /to-prd and /prd share the canonical template; acceptance criteria and hand-off"`.

### Task 3: Deterministic acceptance-criteria check

**Files:**
- Modify: `scripts/integrity-checks/checks/prd_content.py`, `scripts/integrity-checks/config.yaml`, `tests/integrity_checks/test_prd_content.py`

**Interfaces:**
- Produces:
  - `REQUIRED_SECTIONS` gains `"Acceptance Criteria"`, inserted after `"Requirements"`.
  - `parse_table(section_text: str) -> list[dict[str, str]]`: splits on unescaped `|` and unescapes `\|`.
  - `check_acceptance_criteria(repo_root: Path, thresholds: dict) -> list[Finding]`, id `prd-acceptance-criteria`. It runs on PRDs whose `**Status**` is not `Draft`. Keys: `f"{rel}::{ac_id}"` for row problems, `f"{rel}::uncovered::{p0_id}"` for coverage.
  - `check_execution_path(repo_root: Path, thresholds: dict) -> list[Finding]`, id `prd-execution-path`. The value must be one of the two. `agent-direct` is flagged when Review Tier ≠ `Local` or any AC `Verify by` is `analytics`. The other rule conditions need judgment, so the CPO check covers them.

- [ ] **Step 1: Write the failing tests.**

```python
def test_missing_ac_section_is_a_missing_section(): ...      # Draft PRD -> prd-missing-sections mentions "Acceptance Criteria"
def test_draft_prds_skip_row_checks(): ...
def test_bad_rows_are_reported(): ...                         # empty Then; Verify by "eyeball"; duplicate AC-2
def test_uncovered_p0_is_reported(): ...                      # P0-3 not in any Covers -> key ends "uncovered::P0-3"
def test_escaped_pipe_in_cell(): ...                          # Then "returns a\|b" -> one cell
def test_agent_direct_with_strategy_review_is_reported(): ...
def test_clean_in_review_prd_has_no_findings(): ...
```

- [ ] **Step 2: Run them and confirm they fail** — `pytest tests/integrity_checks/test_prd_content.py -q`.
- [ ] **Step 3: Implement.** Register both ids in `CHECKS`; add `prd-acceptance-criteria: true` and `prd-execution-path: true` to `config.yaml`.
- [ ] **Step 4: Run them and confirm they pass.** Then run `pytest -q`.
- [ ] **Step 5: Commit** — `git commit -m "feat(integrity): acceptance-criteria and execution-path checks"`.

### Task 4: Normalise headers and backfill the shipped PRD

**Files:**
- Modify: `scripts/integrity-checks/checks/prd_content.py` (new check), tests, and these PRDs:
  - `product-development/product/PRDs/deployment/custom-domains-prd.md`
  - `deployment/one-click-deploy-prd.md`
  - `home-page/project-search-prd.md`
  - `prototyping/version-history-prd.md`
  - `starter-templates/community-marketplace-prd.md`
  - `billing/credit-usage-dashboard-prd.md`

**Interfaces:**
- Produces: `check_header_format(repo_root, thresholds) -> list[Finding]`, id `prd-header-format`. It reports a PRD whose `**Status**` appears only in `**Status:** X` line form, or that lacks any header-table field from Global Constraints. Key = rel path.

- [ ] **Step 1: Write the failing test** `test_line_style_status_is_reported`, plus one test for a missing `**Execution Path**`.
- [ ] **Step 2: Run it and confirm it fails.**
- [ ] **Step 3: Implement and register** (`prd-header-format: true`).
- [ ] **Step 4: Normalise the five line-style headers** to the table, keeping each value. New fields: `**Hypothesis**` `none — predates hypothesis layer`; `**Execution Path**` per the rule, decided from each PRD's content and noted in the PR.
- [ ] **Step 5: Backfill `credit-usage-dashboard-prd.md`** (Status `Shipped`).
  - Give requirements `P0-n`/`P1-n`/`P2-n` ids if missing.
  - Derive the AC table from its existing user stories and requirements without inventing behaviour the PRD doesn't state. A requirement too vague to test gets an `## Open Questions` row instead of an invented criterion.
  - Map its success metrics to `### Goals & Success Metrics` with `Source`.
- [ ] **Step 6: Run the checks** — `python scripts/integrity-checks/run_checks.py --repo-root .`. Expect no `prd-header-format` findings and no `prd-acceptance-criteria` findings for the shipped PRD. Draft PRDs still report a missing `Acceptance Criteria` section; that's content debt for their owners, recorded and left open on purpose.
- [ ] **Step 7: Commit** — `git commit -m "fix: normalise PRD headers; backfill acceptance criteria for the shipped PRD"`.

### Task 5: Loop status and verification

- [ ] **Step 1: Update `reference/product-loop.md`.** Row `5. PRDs` → `implemented`: Delivered by `product-development/product/PRDs/CLAUDE.md`, `.claude/skills/to-prd/SKILL.md`, `.claude/commands/prd.md`, `docs/agents/prd-handoff.md`. Update the README row and its Core workflows line. Remove "the two PRD templates disagree" from the README Limitations if Plan 0 added it.
- [ ] **Step 2: Verify** — `pytest -q`; `powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1` → clean.
- [ ] **Step 3: Commit, then ask before pushing.**
