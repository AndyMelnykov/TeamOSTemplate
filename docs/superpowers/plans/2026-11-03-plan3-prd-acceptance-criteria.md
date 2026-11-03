# Plan 3: PRD Acceptance Criteria — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every PRD carries testable, ID'd acceptance criteria that cover every must-have requirement, so a PRD reads as instructions an AI agent or engineer can build and test against. `/to-prd` and `/prd` produce the same template.

**Background:** this repo has two ways to write a PRD, with different templates:
- `/to-prd`, a skill (`.claude/skills/to-prd/SKILL.md`) that synthesises a PRD from the conversation. It has per-story acceptance bullets but no `Sources` section and no `Review Tier`, so its output fails `/prd`'s check and the `prd-missing-sections` integrity check.
- `/prd`, a command (`.claude/commands/prd.md`) that interviews section by section and runs a "CPO check". It has no acceptance criteria.

**Architecture:**
- `product-development/product/PRDs/CLAUDE.md` becomes the single canonical template, gaining an `## Acceptance Criteria` table, ID'd requirement tables and two header fields: `**Hypothesis**` and `**Execution Path**`.
- `/to-prd` and `/prd` both point at it; `/to-prd` runs `/prd`'s CPO check.
- One integrity check enforces the table format and P0 coverage on PRDs past `Draft`.
- A short "Hand-off" section in the same template file says how AC ids flow into tickets and tests (the vendored `/to-spec` and `/to-tickets` skills are not edited; they read root `CLAUDE.md`).

**Tech Stack:** Markdown, Python 3.12, pytest.

**Spec:** the owner's stage 5 description (PRDs as agent instructions; simple → PM hands it to an agent, complex → engineering briefs the agent; acceptance criteria are the source for tests; PRDs include success metrics), [plans index](2026-11-03-product-loop-plans-index.md).

## Global Constraints

- Canonical section order: `## Overview` (`### Problem`, `### Why Now`, `### Goals & Success Metrics` as a table `| Metric | Baseline | Target | Timeline | Source |`, `### Non-Goals`), `## User Stories`, `## Requirements`, `## Acceptance Criteria`, `## Design`, `## Technical Considerations`, `## Launch Plan`, `## Sources`. `## Open Questions` may follow.
- Requirements: `### Must Have (P0)`, `### Should Have (P1)`, `### Nice to Have (P2)`, each a table `| ID | Requirement |` with ids `P0-1`, `P1-1`, `P2-1`, ….
- Acceptance Criteria: one table `| ID | Given | When | Then | Covers | Verify by |`. IDs `AC-1`, `AC-2`, … unique within the PRD. `Covers` lists requirement ids and/or `Story N`. `Verify by` is `automated-test`, `manual-qa` or `analytics`. Every `P0-n` appears in at least one `Covers` cell. A literal `|` in a cell is written `\|`.
- Header fields added: `**Hypothesis**` (`HYP-…` or `none — <reason>`) and `**Execution Path**` (`agent-direct` or `engineering-mediated`). `agent-direct` only when Review Tier is `Local`, one product area, no migration or schema change, no new external integration, and no AC is `analytics`.
- Do not edit skills listed in `skills-lock.json` (vendored; an update would overwrite the edit). `/to-prd` is not in it.
- Enforcement applies at `**Status**` `In Review` and later; `Draft` PRDs get only the existing missing-section finding.

## Review Focus

1. **A `/to-prd` PRD run through `/prd`'s CPO check.** Expected: passes. Pinned in Task 2 Step 3 (dry run).
2. **A P0 no criterion covers.** Expected: the finding names the id. Pinned in Task 3 (`test_uncovered_p0_is_reported`).
3. **An AC row with an empty `Then` or an invalid `Verify by`.** Expected: one finding per row naming the AC id. Pinned in Task 3.
4. **A pipe inside a cell.** Expected: `\|` doesn't split the cell. Pinned in Task 3 (`test_escaped_pipe_in_cell`).
5. **`agent-direct` with a `Strategy Review` PRD.** Expected: reported. Pinned in Task 3.

---

## File Structure

| File | Responsibility |
|---|---|
| `product-development/product/PRDs/CLAUDE.md` (modify) | Canonical template, AC rules, Execution Path, Hand-off |
| `.claude/skills/to-prd/SKILL.md` (modify) | Use the canonical template; write AC; run the CPO check |
| `.claude/commands/prd.md` (modify) | Gather AC and the new fields; extend the CPO check |
| `CLAUDE.md` (modify) | One paragraph pointing the engineering skills at the Hand-off section |
| `scripts/integrity-checks/checks/prd_content.py`, `config.yaml`; `tests/integrity_checks/test_prd_content.py` (modify) | Checks |
| `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md` (modify) | Backfill (the only PRD past `Draft`) |

---

### Task 1: The canonical template

**Files:**
- Modify: `product-development/product/PRDs/CLAUDE.md`

- [ ] **Step 1: Replace "PRD Template Sections"** with the canonical order and rules from Global Constraints, including one complete three-row AC example (covering `P0-1`, `P0-2` and `Story 1`, one `analytics` row tied to a success metric).
- [ ] **Step 2: Add "Writing acceptance criteria"**: observable behaviour, not implementation; one Given/When/Then per row; edge and error cases get their own rows; `analytics` rows name a metric from `### Goals & Success Metrics`; ids are stable once the PRD leaves Draft (append, never renumber).
- [ ] **Step 3: Add "Execution Path"** with the rule and one example of each path, and **"Hand-off"**: for `agent-direct` the PM runs `/to-tickets` and each ticket lists the `AC-n` ids it satisfies; for `engineering-mediated` the engineer runs `/to-spec` with the PRD and maps every AC id to a test or manual-QA step. Tests carry the AC id in their name or description.
- [ ] **Step 4: Commit** — `git commit -m "docs: canonical PRD template with acceptance criteria"`.

### Task 2: `/to-prd` and `/prd` use it

**Files:**
- Modify: `.claude/skills/to-prd/SKILL.md`, `.claude/commands/prd.md`, `CLAUDE.md`

- [ ] **Step 1: `/to-prd`.** Delete the embedded template; say "write the PRD using the canonical template in `product-development/product/PRDs/CLAUDE.md`, all sections in that order". Map its synthesis guidance onto the canonical sections. Add steps: derive AC from every story and every P0 (each P0 covered); set `**Hypothesis**` and `**Execution Path**`; run the CPO check in `.claude/commands/prd.md` Step 6. Read the area list from `feature-index.yaml`.
- [ ] **Step 2: `/prd`.** Step 3 gathers "each section of the canonical template" (no count); the header example matches Global Constraints; Step 6 adds checks: AC table complete with unique ids and valid `Verify by`; every P0 covered; every metric in `### Goals & Success Metrics` instrumented with `Source` filled; `**Hypothesis**` cites an existing `HYP-` id or says `none — <reason>`; `**Execution Path**` follows the rule.
- [ ] **Step 3: Dry run** in a scratch worktree: `/to-prd` on "export usage report as CSV", then `/prd` Step 6 on the result. Both pass and `run_checks.py` shows no `prd-*` finding for that file. Delete the worktree.
- [ ] **Step 4: Root `CLAUDE.md`**: under "Agent skills" add "PRD hand-off: when a ticket or spec is derived from a PRD, follow the Hand-off section of `product-development/product/PRDs/CLAUDE.md`."
- [ ] **Step 5: Commit** — `git commit -m "feat: /to-prd and /prd share the canonical template"`.

### Task 3: Acceptance-criteria check

**Files:**
- Modify: `scripts/integrity-checks/checks/prd_content.py`, `config.yaml`, `tests/integrity_checks/test_prd_content.py`

**Interfaces:**
- Produces: `REQUIRED_SECTIONS` gains `"Acceptance Criteria"` after `"Requirements"`; `parse_table(section_text) -> list[dict[str, str]]` (splits on unescaped `|`); `check_acceptance_criteria` (id `prd-acceptance-criteria`; keys `f"{rel}::{ac_id}"` and `f"{rel}::uncovered::{p0_id}"`); `check_execution_path` (id `prd-execution-path`: value must be one of the two, and `agent-direct` is flagged when Review Tier ≠ `Local` or any AC is `analytics`).

- [ ] **Step 1: Write the failing tests.**

```python
def test_missing_ac_section_is_a_missing_section(): ...      # Draft PRD
def test_draft_prds_skip_row_checks(): ...
def test_bad_rows_are_reported(): ...                         # empty Then; Verify by "eyeball"; duplicate AC-2
def test_uncovered_p0_is_reported(): ...
def test_escaped_pipe_in_cell(): ...
def test_agent_direct_with_strategy_review_is_reported(): ...
def test_clean_in_review_prd_has_no_findings(): ...
```

- [ ] **Step 2: Run them and confirm they fail** — `pytest tests/integrity_checks/test_prd_content.py -q`.
- [ ] **Step 3: Implement**, register both ids, set them `true` in `config.yaml`.
- [ ] **Step 4: Run them and confirm they pass**, then `pytest -q`.
- [ ] **Step 5: Commit** — `git commit -m "feat(integrity): acceptance-criteria and execution-path checks"`.

### Task 4: Backfill the shipped PRD, loop status, verification

- [ ] **Step 1: Backfill `credit-usage-dashboard-prd.md`** (Status `Shipped`): requirement ids, an AC table derived only from what the PRD already states (a requirement too vague to test goes to `## Open Questions`, not an invented criterion), success metrics with `Source`, and the two new header fields. Draft PRDs keep reporting the missing section; that is content debt for their owners and stays open on purpose.
- [ ] **Step 2: Update `reference/product-loop.md`.** `5. PRDs` → `implemented` (Delivered by `product-development/product/PRDs/CLAUDE.md`, `.claude/skills/to-prd/SKILL.md`, `.claude/commands/prd.md`). Update the README row.
- [ ] **Step 3: Verify** — `pytest -q`; `run_checks.py` (no `prd-acceptance-criteria` finding for the shipped PRD); `check-references.ps1` clean.
- [ ] **Step 4: Commit, then ask before pushing.**
