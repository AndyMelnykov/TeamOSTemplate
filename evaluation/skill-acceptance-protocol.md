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
