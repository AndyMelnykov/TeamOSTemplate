# Skill-Gap Detection, Acceptance Protocol, and Coverage Checklist Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three transcript-inspired improvements to this repo, each corrected against what the source material actually describes rather than its most flattering paraphrase: (1) a paired before/after acceptance check for new skills/reference docs, explicitly scoped as a regression check, not a statistical A/B test; (2) a skill-gap detection mechanism, modeled directly on the existing `papercuts` pattern; (3) a checklist-based context-coverage metric, replacing the transcript's ungrounded "ask the agent to self-report a percentage" with explicit, scored, inspectable criteria.

**Architecture:** No new top-level tree. Everything slots into existing conventions: a new file under `evaluation/` (protocol), a new root log file + `.claude/skills/` entry + `evaluation/` task-set (skill-gap detection, mirroring `PAPERCUTS.md` / `.claude/skills/papercuts/` / `evaluation/papercuts-task-set.md` exactly), and a new `reference/` doc + `docs/adr/` entry + `scripts/` helper (coverage checklist, mirroring how `reference/decision-types.md` + an ADR + `scripts/check-references.ps1` already work together).

**Tech Stack:** Markdown, YAML (`feature-index.yaml`), PowerShell (`scripts/`) — no code, no build step.

**Spec:** None — derived from a conversation reviewing a podcast transcript ("company OS.txt") against this repo's existing structure, corrected against the transcript's actual wording per the user's request. Rationale for each task is inline below and in `docs/adr/0006-checklist-based-context-coverage.md` (created in Task 7).

## Global Constraints

- New/changed files must keep `scripts/check-references.ps1` passing (exit 0).
- Every new top-level file gets wired into the doc index of its parent `CLAUDE.md` (this repo's established navigation pattern).
- `reference/` edits require a human approval checkpoint before committing (ADR 0003) — Task 8 creates a file under `reference/`, so it ends with an explicit pause for sign-off. Root-level, `.claude/`, `docs/`, and `evaluation/` edits are not gated by ADR 0003 and can be committed directly once verified.
- Log-style files use this repo's established entry format: `- **YYYY-MM-DD** [tag] text. (extra-field, status)` — see `PAPERCUTS.md`.
- The acceptance protocol (Task 1) must never be described as a statistically powered A/B test. It is a small, fixed, paired before/after comparison judged by a human or LLM-judge reading the outputs — report raw counts of what flipped, never a headline percentage implying a controlled experiment.
- The coverage metric (Tasks 7-9) must be checklist/rubric-based with written per-level criteria, never implemented as "prompt the agent to self-report a completeness percentage."
- Any eval task-set case that plants a fixture or writes a test log entry must revert that mutation after the run — see `evaluation/papercuts-task-set.md`'s existing convention.

---

### Task 1: Skill / reference-doc acceptance protocol (`evaluation/`)

**Files:**
- Create: `evaluation/skill-acceptance-protocol.md`
- Modify: `evaluation/CLAUDE.md` (Doc Index table)

**Interfaces:**
- Produces: the paired before/after methodology Task 6 applies to the skill built in Tasks 2-5.

- [ ] **Step 1: Write `evaluation/skill-acceptance-protocol.md`**

```markdown
# Skill / Reference-Doc Acceptance Protocol

A lightweight, paired before/after check to run before merging a new skill (`.claude/skills/`) or a new canonical reference doc (`reference/`). It answers one narrow question — "on the questions this addition is meant to help with, does having it available produce more correct, better-cited answers than not having it?" — not "is this proven at statistical significance."

## What this is not

This is explicitly **not** a statistically powered A/B test. A/B testing implies a large, randomly-sampled population and a significance threshold; this protocol runs a small, fixed, hand-written set of questions (typically 10-30) through two conditions and reports a raw before/after delta. That's enough to catch "this addition clearly helps," "this addition does nothing," or "this addition actively confuses the agent" — it is not enough to claim a measured percentage improvement holds beyond this specific question set. Report deltas as counts ("7 of 10 flipped wrong→right, 0 flipped right→wrong"), never as a headline percentage implying a controlled experiment.

## Which additions this fits

This protocol fits additions meant to improve **factual/retrieval answers** — a new reference doc, or a skill whose job is helping the agent locate or reason over existing canonical content. For a **trigger-behavior** skill — one meant to fire on some situation and take a small documented action, like `papercuts` or `skill-gap-detection` — the right acceptance check is a scripted-scenario task-set instead (see `evaluation/papercuts-task-set.md` for the pattern: positive cases where triggering is correct, negative cases where it isn't). Don't force a Q&A comparison onto a trigger skill; build it a scenario task-set instead.

## Method

1. **Scope the addition.** Name the 1-3 topic areas the new skill/doc is meant to improve answers on (e.g., "customer segment definitions," "how to triage a stakeholder feature request").
2. **Write ~10 questions per topic area**, each with a verifiable expected answer and expected source file — same bar as `evaluation/task-set.md`'s existing tasks. Reuse or extend `task-set.md` directly if the questions are general-purpose; keep addition-specific questions in this run's own results file if they're too narrow to belong there permanently.
3. **Run each question twice**, fresh session each time, no prior conversation context:
   - **Without** — the new skill file / reference doc is removed or the agent is told not to use it.
   - **With** — the addition is present and the agent is pointed at the repo as normal.
4. **Score each question** using the same metrics `protocol.md` already defines: task completion accuracy, wrong-source rate, citation accuracy. Record pass/fail per question per condition — not a partial-credit score.
5. **Report the delta**, not an aggregate percentage:
   - Flipped fail→pass (the addition helped)
   - Flipped pass→fail (the addition hurt — regression, investigate before shipping)
   - Unchanged pass, unchanged fail (the addition was neutral for this question)

## Decision rule

- Any pass→fail flip: do not ship as-is. Revise the addition or the questions until the regression is understood.
- Zero fail→pass flips: the addition isn't earning its place for the scope claimed — narrow the scope or don't ship it as a new skill/doc (a shorter note added to an existing file may be the right call instead).
- Otherwise: ship it, and keep the question set — it becomes the regression check the next time this same file is edited.

## Reporting

One file per run: `evaluation/results/YYYY-MM-DD-<addition-name>-acceptance.md`, containing the question list, the with/without answer for each, and the delta summary from step 5. Reuses the existing `evaluation/results/` folder rather than a new location.

## Relationship to `protocol.md`

`protocol.md` measures whether the *whole* repo structure beats an unstructured baseline. This protocol measures whether *one specific addition* to that structure earns its place. Run this one far more often — every time a skill or reference doc is proposed — and `protocol.md`'s full run only periodically.
```

- [ ] **Step 2: Add a row to `evaluation/CLAUDE.md`'s Doc Index table**

Insert after the `protocol.md` row:

```markdown
| `skill-acceptance-protocol.md` | Paired before/after check for a *specific* new skill or reference doc — narrower than `protocol.md`, run before merging any addition |
```

- [ ] **Step 3: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.` (exit 0)

- [ ] **Step 4: Commit**

```bash
git add evaluation/skill-acceptance-protocol.md evaluation/CLAUDE.md
git commit -m "docs: add paired acceptance protocol for new skills and reference docs"
```

---

### Task 2: `SKILL-GAPS.md` (root)

**Files:**
- Create: `SKILL-GAPS.md`

**Interfaces:**
- Produces: the log file Task 3's skill writes to and Task 4's eval task-set validates against.

- [ ] **Step 1: Write `SKILL-GAPS.md`**

```markdown
# Skill Gaps

A running log of manual, multi-step "recipes" an agent performed by hand that had no skill or command backing them — the mirror image of `PAPERCUTS.md`: papercuts logs things that are *broken*, this logs things that work fine but keep getting redone from scratch because nothing has turned the recipe into a reusable skill yet.

This is not a queue of feature ideas — it only holds recipes an agent actually performed, not proposals. An entry is evidence a real session hit this shape of task, not a wish.

## How agents use this

See [.claude/skills/skill-gap-detection/SKILL.md](.claude/skills/skill-gap-detection/SKILL.md) — it fires when an agent notices it is hand-executing a multi-step task that resembles one it (or a prior logged entry) has already done, with no `.claude/skills/` or `.claude/commands/` entry covering it. Short version: don't stop to build a skill on the spot, don't ask permission, append one line under **Log** below (or bump an existing matching entry's count), then keep going.

## Entry format

```
- **YYYY-MM-DD** [area] What manual recipe was performed (rough inputs → outputs), and why no existing skill covered it. (seen-Nx, status)
```

- **area** — free-form, e.g. `product`, `customers`, `analytics`, `process`
- **seen-Nx** — how many times this exact shape of recipe has been logged; bump the count and refresh the date on the existing line instead of adding a duplicate when the same shape recurs
- **status** — `unresolved` when filed; `resolved` once someone turns it into an actual skill/command, noting which one

## Reviewing the backlog

Periodically skim **Log** below. Any entry at `seen-2x` or higher is a real signal — draft a skill for it (see `superpowers:writing-skills`), then flip the entry to `resolved` and name the skill it became.

## Log

<!-- Newest entries at the bottom. Append here, or bump an existing matching entry's count and date — do not remove existing entries. -->
```

- [ ] **Step 2: Commit**

```bash
git add SKILL-GAPS.md
git commit -m "docs: add SKILL-GAPS.md log, mirroring PAPERCUTS.md for repeated manual recipes"
```

---

### Task 3: `skill-gap-detection` skill (`.claude/skills/`)

**Files:**
- Create: `.claude/skills/skill-gap-detection/SKILL.md`

**Interfaces:**
- Consumes: `SKILL-GAPS.md`'s entry format from Task 2.
- Produces: the trigger behavior Task 4's eval task-set scores.

- [ ] **Step 1: Write `.claude/skills/skill-gap-detection/SKILL.md`**

```markdown
---
name: skill-gap-detection
description: Use immediately whenever you catch yourself hand-executing a multi-step recipe (3+ mechanical steps with a recognizable input → transform → output shape) that has no `.claude/skills/` or `.claude/commands/` entry covering it, especially when it resembles something done before. Trigger the instant you notice you're improvising a repeatable recipe instead of following a named one. Not for genuinely one-off requests, trivial 1-2 step tasks, anything an existing skill/command already covers, or anything the user has explicitly said not to log.
---

# Skill Gap Detection

## Overview

Skills only get written when someone notices a pattern repeating. Left to chance, that noticing happens in a human's head, days later, from memory — this is the one-line complaint box that catches it in the moment instead: when a recipe-shaped task has no skill behind it, log it and keep moving. A human (or another agent, per `superpowers:writing-skills`) reviews the backlog later and promotes repeat offenders into real skills.

## When to use

Fire the moment you notice any of:
- You're about to hand-write the same multi-step sequence (gather X → transform Y → write Z in format W) you recall performing in this session or a prior one
- The user says something like "same as last time," "like we did for X," or "again"
- You're doing 3+ mechanical, nameable steps ad hoc and nothing under `.claude/skills/` or `.claude/commands/` already covers this shape of task

**Don't use it for:**
- A task an existing skill/command already covers — invoke that skill instead of logging a gap. (If you did the work by hand because you didn't realize the skill existed, that's a `PAPERCUTS.md` discoverability entry, not a skill gap.)
- A genuinely one-off request, especially one the user explicitly frames as non-recurring ("just this once")
- Trivial 1-2 step tasks — not every repeated action deserves a skill
- Anything the user has explicitly asked you not to log — user instructions override this skill, same as any other

## What to do

1. **Don't stop working, and don't ask.** Filing is a normal edit, like reading a file — not a suggestion to run past anyone.
2. Check `SKILL-GAPS.md` for an existing entry matching this recipe's shape.
   - If one exists: bump its count (`seen-1x` → `seen-2x`, etc.) and refresh the date.
   - If none exists: append a new line under **Log**:
     ```
     - **YYYY-MM-DD** [area] What manual recipe was performed (rough inputs → outputs), and why no existing skill covered it. (seen-1x, unresolved)
     ```
3. Continue the original task.

## Red flags — you should have logged one already

- You improvised the same shape of multi-step task you remember doing in an earlier turn or session, and didn't check `SKILL-GAPS.md`
- You thought "I keep doing this by hand" and moved on without noting it
- `SKILL-GAPS.md` is unedited and the repetition is only in your head or your final summary
- You're about to *tell the user* you keep redoing this, or ask if you should log it, instead of just editing the file

Any of these mid-task: stop, log it yourself, then resume. No exceptions.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/skill-gap-detection/SKILL.md
git commit -m "feat: add skill-gap-detection skill"
```

---

### Task 4: Skill-gap detection eval task-set (`evaluation/`)

**Files:**
- Create: `evaluation/skill-gap-task-set.md`
- Modify: `evaluation/CLAUDE.md` (Doc Index table)

**Interfaces:**
- Consumes: the trigger conditions from Task 3's `SKILL.md`.
- Produces: the case list Task 6 runs.

- [ ] **Step 1: Write `evaluation/skill-gap-task-set.md`**

```markdown
# Skill Gap Detection Trigger Eval

Tests whether an agent correctly invokes the `skill-gap-detection` skill (`.claude/skills/skill-gap-detection/SKILL.md`) — i.e. it notices a recipe-shaped task with no skill backing it and logs (or bumps) one `SKILL-GAPS.md` line — versus the two failure modes:

- **Silent repetition** — the agent does the recipe by hand and never mentions it.
- **Full stop** — the agent halts the actual task to ask "should I log this?" or announces the repetition in prose instead of editing the file.

Cases 1-3 are **positive** (a skill-gap entry is the correct outcome). Cases 4-7 are **negative/distractor** — the situation resembles a gap but the correct behavior is *not* to log, so the eval also catches over-triggering.

## Scoring

For each case, record:

| Signal | Pass condition |
|---|---|
| Task completion | Agent still produces a correct result for the underlying ask |
| `SKILL-GAPS.md` diff | Positive cases: exactly one new or bumped line, correct format. Negative cases: no diff |
| Stall check | Agent never asks permission to log, and never announces the repetition in chat as a substitute for editing the file |

Run each case in a fresh session (or fresh subagent). **Revert any `SKILL-GAPS.md` diff after each case** — these are synthetic scenarios, not real observed recurrence, and must not pollute the real log.

---

## 1. Manual feature-index wiring, framed as recurring

**Prompt:** "I just merged the new `team-workspaces-v2` PRD at `product-development/product/PRDs/team-workspaces-v2-prd.md`. Wire it into `feature-index.yaml` the same way we did for the last PRD."

**Expected:** Agent performs the manual edit correctly (this recipe is genuinely hand-maintained per ADR 0002 — no skill covers it), and — since the prompt explicitly frames it as recurring ("the same way we did") — logs a `[product]` entry to `SKILL-GAPS.md`.

**Fail modes:** Silently does the edit with no log entry; or stops to ask "should I create a skill for this?" instead of logging and continuing.

## 2. Manual stakeholder-request triage, framed as recurring

**Prompt:** "A stakeholder pinged me with a raw feature request for X. Can you run it through the same problem-framing/evidence/impact check we usually do before it becomes an opportunity file? We've done this a few times now."

**Expected:** Agent performs the check (clarifying questions, checks against `templates/opportunity.md` and current priorities), completes the task, and logs or bumps a `SKILL-GAPS.md` entry — this recipe has no skill/command behind it (`/triage` is scoped to GitHub issues/PRs per its `SKILL.md`, not raw stakeholder asks).

**Fail modes:** Completes the triage with no log entry; incorrectly treats `/triage` as already covering this and neither uses it correctly nor logs the gap.

## 3. Recurring CONTEXT.md audit

**Prompt:** "Check whether every folder under `product-development/` has a CONTEXT.md, like we checked last month."

**Expected:** Agent walks the tree, reports gaps, and logs a `SKILL-GAPS.md` entry (or bumps an existing one) noting there's no script/skill for this audit, unlike `check-references.ps1` for links.

**Fail modes:** Reports the audit result with no log entry.

---

## 4. Task already covered by an existing skill (should NOT trigger)

**Prompt:** "Summarize this customer call transcript and file it the usual way."

**Expected:** Agent recognizes `.claude/commands/customer-call.md` covers this exactly, invokes it, and does **not** log a skill gap — the skill already exists.

**Fail modes:** Does the work by hand instead of invoking the existing skill, and/or logs a spurious `SKILL-GAPS.md` entry for something already covered.

## 5. Explicitly one-off (should NOT trigger)

**Prompt:** "Just this once, merge these three scratch notes into a single file for me — this isn't something we'll need again."

**Expected:** Agent does the merge, logs nothing — the user explicitly framed it as non-recurring.

**Fail modes:** Logs a `SKILL-GAPS.md` entry despite the explicit "just this once" framing.

## 6. Trivial task (should NOT trigger)

**Prompt:** "Rename this file from `draft-v1.md` to `draft.md`."

**Expected:** Agent renames it, logs nothing — a 1-step task isn't a "recipe."

**Fail modes:** Logs a skill-gap entry for a trivial single-step action.

## 7. User explicitly opts out of logging (should NOT trigger)

**Prompt:** "Do this [a genuinely repetitive, recipe-shaped task] the manual way and don't bother logging it as a gap — I know it's repetitive, I just don't want a skill for this one."

**Expected:** Agent completes the task and respects the explicit instruction not to log — user instructions override skill defaults (same principle as this repo's root `CLAUDE.md`).

**Fail modes:** Logs the entry anyway despite the explicit instruction.

---

## Why cases 4-7 matter

`SKILL.md`'s trigger list is generous by design (any 3+-step recipe with no skill behind it), which is right for encouraging logging — but the same generosity makes over-triggering easy. Cases 4-7 are grounded in real mechanics already in this repo (the `customer-call-summary` skill's actual existence, `/triage`'s actual documented scope, and the "user instructions override skills" principle stated in root `CLAUDE.md`) rather than invented distractors, so a false positive here is a genuine miscalibration.
```

- [ ] **Step 2: Add a row to `evaluation/CLAUDE.md`'s Doc Index table**

Insert after the `papercuts-task-set.md` row:

```markdown
| `skill-gap-task-set.md` | Behavioral eval for the `skill-gap-detection` skill — positive cases where a gap should be logged, negative cases where it shouldn't |
```

- [ ] **Step 3: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.` (exit 0)

- [ ] **Step 4: Commit**

```bash
git add evaluation/skill-gap-task-set.md evaluation/CLAUDE.md
git commit -m "docs: add trigger eval task-set for skill-gap-detection"
```

---

### Task 5: Wire skill-gap detection into root `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md` (Agent skills section)

**Interfaces:**
- Consumes: Task 2/3's file paths.

- [ ] **Step 1: Add a "Skill gaps" subsection**

In root `CLAUDE.md`, under `## Agent skills`, insert a new subsection immediately after `### Papercuts` and before `### Issue tracker`:

```markdown
### Skill gaps

When you catch yourself hand-executing a multi-step recipe that has no skill or command behind it — especially one that resembles something done before — log it immediately: append one line to the **Log** section of `SKILL-GAPS.md` at the repo root. Don't stop to build the skill on the spot, don't ask permission, just log and keep going. Full trigger conditions: `.claude/skills/skill-gap-detection/SKILL.md`.
```

- [ ] **Step 2: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.` (exit 0)

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: wire skill-gap-detection into root CLAUDE.md agent skills index"
```

---

### Task 6: Run the skill-gap-detection eval task-set (first real usage)

**Files:**
- Create: `evaluation/results/2026-09-09-skill-gap-detection-eval.md`

**Interfaces:**
- Consumes: the 7 cases from Task 4.

- [ ] **Step 1: Run all 7 cases**

For each case in `evaluation/skill-gap-task-set.md`, dispatch a fresh subagent (or fresh session) with the exact prompt, observe the `SKILL-GAPS.md` diff and chat behavior, then revert any diff before the next case.

- [ ] **Step 2: Record results**

Write `evaluation/results/2026-09-09-skill-gap-detection-eval.md` with one row per case: case number, pass/fail per the scoring table in `skill-gap-task-set.md`, and a one-line note on what happened. Summarize at the top: N/7 passed, list any failures.

- [ ] **Step 3: Fix and re-run if any case fails**

If a case fails, the failure is in `SKILL.md`'s wording (ambiguous trigger condition), not the eval — revise Task 3's `SKILL.md` and re-run only the failing case(s) until all 7 pass.

- [ ] **Step 4: Verify `SKILL-GAPS.md` is unchanged from Task 2**

Run: `git diff SKILL-GAPS.md`
Expected: no output (all synthetic entries from the eval run were reverted).

- [ ] **Step 5: Commit**

```bash
git add evaluation/results/2026-09-09-skill-gap-detection-eval.md
git commit -m "test: run skill-gap-detection trigger eval, all cases passing"
```

---

### Task 7: ADR 0006 — checklist-based context coverage

**Files:**
- Create: `docs/adr/0006-checklist-based-context-coverage.md`

**Interfaces:**
- Produces: the rationale Task 8's checklist and Task 9's script implement.

- [ ] **Step 1: Write `docs/adr/0006-checklist-based-context-coverage.md`**

```markdown
# Checklist-based context coverage, not agent self-reported percentage

We track how complete this repo's canonical context is per domain area using an explicit, versioned checklist (`reference/context-coverage-checklist.md`) scored item-by-item — not by asking an agent to estimate "what percentage of your knowledge of X is loaded" and reporting that number directly.

## Considered Options

- Ask an agent directly for a self-reported completeness percentage per domain, the way an ungrounded prompt like "what % of our business model do you understand" produces a single number from whatever's in its context window.
- A checklist of concrete, inspectable items per domain area (does X exist, is Y cross-referenced, is Z non-stub), scored 0/1/2 per item against explicit written criteria, aggregated into a per-area percentage.

The first option was rejected: an LLM's self-estimate of how much it "knows" about a domain isn't grounded in anything checkable — the same repo state can produce different self-reported numbers across sessions or models, there's no way to point to what's missing from a bare percentage, and it rewards confident-sounding answers over accurate ones — the exact failure mode this repo's structured-navigation choice already guards against elsewhere (see [ADR 0001](0001-structured-navigation-over-embeddings.md)).

## Consequences

The checklist is more work to build and maintain than a one-line prompt, and it will always undercount qualities a rubric doesn't enumerate (checklists have coverage gaps of their own — extending the checklist is the intended response, not switching back to a free-form estimate). But every score is traceable to a specific missing or incomplete item, is reproducible across sessions, and can be partially automated the way `check-references.ps1` automates link-checking — deterministic where possible, rubric-scored with written criteria where not.
```

- [ ] **Step 2: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.` (exit 0)

- [ ] **Step 3: Commit**

```bash
git add docs/adr/0006-checklist-based-context-coverage.md
git commit -m "docs: record ADR 0006, checklist-based context coverage over agent self-report"
```

---

### Task 8: Coverage checklist (`reference/`)

**Files:**
- Create: `reference/context-coverage-checklist.md`
- Modify: `reference/CLAUDE.md` (Doc Index table)

**Interfaces:**
- Consumes: ADR 0006's rationale from Task 7.
- Produces: the item list Task 9's script scores.

- [ ] **Step 1: Write `reference/context-coverage-checklist.md`**

```markdown
# Context Coverage Checklist

A scored checklist for how complete this repo's canonical context is, per domain area — see [ADR 0006](../docs/adr/0006-checklist-based-context-coverage.md) for why this is a checklist and not an agent's self-reported percentage.

## How to score

Each item scores 0, 1, or 2 against the written criteria below. An area's coverage % = (sum of item scores) / (2 × item count) × 100. Items marked **[auto]** are computed by `scripts/score-context-coverage.ps1`; items marked **[reviewed]** require a human or agent to read the target content and judge it against the written criteria — never a bare estimate, always tied to the specific 0/1/2 description below.

## Product

1. **[auto] PRD coverage.** Every feature entry in `feature-index.yaml` has a `prd:` key or an inline `# no-prd:` comment explaining why.
   - 0: fewer than half of entries have either
   - 1: 50-99% have either
   - 2: 100% have either
2. **[reviewed] Segment definitions.** Every customer segment name used anywhere under `product-development/` is defined in `reference/segments.md`. (Not automated: reliably distinguishing a real segment reference from an unrelated capitalized phrase needs judgment a grep can't safely make — scoring this by hand, or with an agent doing the search, is more accurate than a fragile heuristic script.)
   - 0: 2+ undefined segment names found in use
   - 1: exactly 1 undefined segment name found
   - 2: zero undefined segment names found
3. **[reviewed] Strategy currency.** `product-development/product/strategy/` contains a vision doc and a roadmap/plan doc, each with a date in its content.
   - 0: missing, or most recent dated content is more than 2 quarters old
   - 1: present, 1-2 quarters old
   - 2: present, dated within the current quarter

## Customer insights

1. **[auto] Account call coverage.** Every folder under `product-development/product/customers/accounts/` has at least one file under its `calls/summaries/`.
   - 0: fewer than half of account folders have one
   - 1: 50-99% have one
   - 2: 100% have one
2. **[reviewed] Feature-request tracker linkage.** Spot-check the 3 most recently dated call summaries: each summary's Feature Requests section corresponds to an entry logged in Linear/Jira/Asana (per `customer-call-summary`'s Step 5c).
   - 0: none of the 3 have corresponding tracker entries
   - 1: 1-2 of the 3 do
   - 2: all 3 do

## Analytics

1. **[reviewed] Metric definitions.** Every metric named in a PRD's goals/success-signal section exists in `reference/metrics.md`.
   - 0: 2+ undefined metrics found across sampled PRDs
   - 1: exactly 1 undefined metric found
   - 2: zero undefined metrics found
2. **[reviewed] Dashboard doc completeness.** Every `dashboards:` link in `feature-index.yaml` resolves to a non-placeholder doc describing what the dashboard shows (not just a bare URL).
   - 0: fewer than half resolve to a real description
   - 1: 50-99% do
   - 2: 100% do

## Engineering

1. **[reviewed] RFC linkage.** Every feature-index entry with an `eng-plan:` either also has an `eng-rfc:` or the plan document contains an explicit "no RFC needed" note with a reason.
   - 0: fewer than half meet this
   - 1: 50-99% meet this
   - 2: 100% meet this

## Reference (canonical layer)

1. **[auto] No broken canonical links.** `reference/CLAUDE.md`'s Doc Index rows all resolve to existing files (this is a strict pass/fail check, reusing `scripts/check-references.ps1`'s output, not a graded rubric).
   - 0: 1 or more broken
   - 2: zero broken
   (no 1 value for this item — it's binary)

## Extending this checklist

Add new items under an existing area, or a new `##` area heading, following the same `[auto]`/`[reviewed]` + written 0/1/2 criteria format. A checklist item without written criteria for each score level is not a valid addition — see ADR 0006 for why.
```

- [ ] **Step 2: Add a row to `reference/CLAUDE.md`'s Doc Index table**

```markdown
| `context-coverage-checklist.md` | Scored checklist (not a self-reported estimate) for how complete canonical context is per domain area — see ADR 0006 |
```

- [ ] **Step 3: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.` (exit 0)

- [ ] **Step 4: Pause for human sign-off before committing**

This step creates a new file under `reference/`, which ADR 0003 gates behind human approval before it becomes canonical. Show the diff and get an explicit go-ahead — do not commit in the same action as drafting.

- [ ] **Step 5: Commit**

```bash
git add reference/context-coverage-checklist.md reference/CLAUDE.md
git commit -m "docs: add checklist-based context coverage scoring"
```

---

### Task 9: Coverage scoring script + first run

**Files:**
- Create: `scripts/score-context-coverage.ps1`
- Create: `evaluation/results/2026-09-09-context-coverage-run.md`

**Interfaces:**
- Consumes: the `[auto]` items defined in Task 8's checklist.

- [ ] **Step 1: Write `scripts/score-context-coverage.ps1`**

```powershell
<#
.SYNOPSIS
    Scores the [auto] items in reference/context-coverage-checklist.md and
    prints a template for the remaining [reviewed] items.
.DESCRIPTION
    Computes, deterministically:
      - Product #1: % of feature-index.yaml entries with a `prd:` key or a
        `# no-prd:` comment on the entry's line.
      - Product #2: undefined segment names — greps for capitalized segment-
        like tokens under product-development/ and diffs against the
        segment names defined in reference/segments.md.
      - Customer insights #1: % of account folders under
        product-development/product/customers/accounts/ that have at least
        one file under calls/summaries/.
      - Reference #1: delegates to scripts/check-references.ps1's exit code.
    All other checklist items are [reviewed] — this script prints their
    descriptions so a human/agent can score them by hand into the same
    results file.
.EXAMPLE
    powershell -File scripts/score-context-coverage.ps1
#>
[CmdletBinding()]
param(
    [string]$RepoRoot
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    $toplevel = & git -C $scriptDir rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0 -and $toplevel) {
        $RepoRoot = ($toplevel -replace '/', '\')
    } else {
        $RepoRoot = (Get-Location).Path
    }
}

function Write-Score {
    param([string]$Label, [int]$Score, [string]$Detail)
    Write-Host ("[{0}/2] {1} - {2}" -f $Score, $Label, $Detail)
}

# --- Product #1: PRD coverage in feature-index.yaml ---
$featureIndex = Join-Path $RepoRoot 'product-development\feature-index.yaml'
$totalEntries = 0
$coveredEntries = 0
if (Test-Path $featureIndex) {
    $lines = Get-Content $featureIndex
    $inEntry = $false
    $entryHasPrd = $false
    foreach ($line in $lines) {
        if ($line -match '^\s{2}[\w-]+:\s*$') {
            if ($inEntry) {
                $totalEntries++
                if ($entryHasPrd) { $coveredEntries++ }
            }
            $inEntry = $true
            $entryHasPrd = $false
        } elseif ($line -match '^\s{4}prd:' -or $line -match '#\s*no-prd:') {
            $entryHasPrd = $true
        }
    }
    if ($inEntry) {
        $totalEntries++
        if ($entryHasPrd) { $coveredEntries++ }
    }
}
$prdPct = if ($totalEntries -gt 0) { [math]::Round(($coveredEntries / $totalEntries) * 100, 1) } else { 0 }
$prdScore = if ($prdPct -ge 100) { 2 } elseif ($prdPct -ge 50) { 1 } else { 0 }
Write-Score -Label 'Product #1: PRD coverage' -Score $prdScore -Detail "$coveredEntries/$totalEntries entries ($prdPct%)"

# --- Customer insights #1: account call coverage ---
$accountsDir = Join-Path $RepoRoot 'product-development\product\customers\accounts'
$totalAccounts = 0
$coveredAccounts = 0
if (Test-Path $accountsDir) {
    Get-ChildItem -Path $accountsDir -Directory | ForEach-Object {
        $totalAccounts++
        $summariesDir = Join-Path $_.FullName 'calls\summaries'
        if ((Test-Path $summariesDir) -and (Get-ChildItem -Path $summariesDir -Filter '*.md' -ErrorAction SilentlyContinue)) {
            $coveredAccounts++
        }
    }
}
$acctPct = if ($totalAccounts -gt 0) { [math]::Round(($coveredAccounts / $totalAccounts) * 100, 1) } else { 0 }
$acctScore = if ($acctPct -ge 100) { 2 } elseif ($acctPct -ge 50) { 1 } else { 0 }
Write-Score -Label 'Customer insights #1: account call coverage' -Score $acctScore -Detail "$coveredAccounts/$totalAccounts accounts ($acctPct%)"

# --- Reference #1: no broken canonical links ---
$checkScript = Join-Path $RepoRoot 'scripts\check-references.ps1'
& powershell -File $checkScript -RepoRoot $RepoRoot | Out-Null
$refScore = if ($LASTEXITCODE -eq 0) { 2 } else { 0 }
Write-Score -Label 'Reference #1: no broken canonical links' -Score $refScore -Detail "check-references.ps1 exit code $LASTEXITCODE"

Write-Host "`n--- [reviewed] items: score these by hand into the results file ---"
Write-Host "Product #3: Strategy currency"
Write-Host "Customer insights #2: Feature-request tracker linkage"
Write-Host "Analytics #1: Metric definitions"
Write-Host "Analytics #2: Dashboard doc completeness"
Write-Host "Engineering #1: RFC linkage"
Write-Host "Product #2: Segment definitions (undefined-segment grep not yet automated - review by hand this run)"
```

- [ ] **Step 2: Run the script and record the first coverage run**

Run: `powershell -File scripts/score-context-coverage.ps1`

Write `evaluation/results/2026-09-09-context-coverage-run.md` containing: the script's `[auto]` output verbatim, plus hand-scored values (with a one-line justification each, citing what was checked) for the `[reviewed]` items, plus the computed per-area and overall percentage.

- [ ] **Step 3: Commit**

```bash
git add scripts/score-context-coverage.ps1 evaluation/results/2026-09-09-context-coverage-run.md
git commit -m "feat: add context-coverage scoring script and record first run"
```

---

### Task 10: Update `ROADMAP.md`

**Files:**
- Modify: `ROADMAP.md`

**Interfaces:**
- Consumes: file paths created in Tasks 1-9.

- [ ] **Step 1: Add three bullets to the "Already shipped" section**

```markdown
- **Skill/reference-doc acceptance protocol** — `evaluation/skill-acceptance-protocol.md`, a paired before/after check (not a statistical A/B test) run before merging a new skill or canonical reference doc.
- **Skill-gap detection** — `SKILL-GAPS.md` plus `.claude/skills/skill-gap-detection/`, mirroring the papercuts pattern for repeated manual recipes with no skill behind them yet.
- **Checklist-based context coverage** — `reference/context-coverage-checklist.md`, `docs/adr/0006-checklist-based-context-coverage.md`, and `scripts/score-context-coverage.ps1`; scores completeness per domain area against written criteria instead of an agent's self-reported percentage.
```

- [ ] **Step 2: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.` (exit 0)

- [ ] **Step 3: Commit**

```bash
git add ROADMAP.md
git commit -m "docs: mark skill-gap detection, acceptance protocol, and coverage checklist as shipped"
```
