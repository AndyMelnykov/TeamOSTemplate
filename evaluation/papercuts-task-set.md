# Papercuts Trigger Eval

Tests whether an agent correctly invokes the `papercuts` skill (`.claude/skills/papercuts/SKILL.md`) — i.e. it notices friction, appends one line to `PAPERCUTS.md`, and keeps working — versus the two failure modes:

- **Silent workaround** — the agent routes around the friction (retries with different args, reads a different file, infers the missing info) and never mentions it.
- **Full stop** — the agent halts the actual task to ask the user "should I log this?" or to report the friction in prose instead of just editing the file.

A correct run looks like neither a crash nor silence: the agent pauses just long enough to append one `PAPERCUTS.md` line in the documented format, then finishes the original task.

Cases 1–5 are **positive** (a papercut entry is the correct outcome). Cases 6–9 are **negative/distractor** — the situation resembles friction but the correct behavior is *not* to file, so the eval also catches over-triggering.

## Scoring

For each case, record:

| Signal | Pass condition |
|---|---|
| Task completion | Agent still produces a correct answer/output for the underlying ask |
| `PAPERCUTS.md` diff | Positive cases: exactly one new line, correct format (`- **YYYY-MM-DD** [tag] ... (severity, unresolved)`), appended below existing entries, nothing else edited. Negative cases: no diff to `PAPERCUTS.md` |
| Stall check | Agent never asks permission to log, and never announces the friction in chat as a substitute for editing the file |
| Halt check | Agent does not abandon or block the original task on the friction (positive cases only — case 8 is the one scenario where blocking the task *is* correct, see below) |

Run each case in a fresh session (or fresh subagent) with the repo at its current state, since several cases plant a temporary fixture that must be reverted after the run (noted per case).

---

## 1. Broken relative link hit mid-research

**Setup:** Temporarily add a link to a nonexistent file inside an existing doc the prompt will make the agent open, e.g. in `product-development/product/PRDs/CLAUDE.md` add a line `See [rollout notes](rollout-notes-that-do-not-exist.md).` Revert after the run.

**Prompt:** "What PRDs exist for the billing area, and is there anything about rollout notes I should read first?"

**Expected:** Agent answers the PRD question from what does resolve, notices the dead link when it tries to follow it, and appends a `[docs]` entry to `PAPERCUTS.md` citing the file and the broken path — without stopping to ask whether it should.

**Fail modes:** Silently drops the rollout-notes mention from its answer with no log entry; or stops and asks the user "this link looks broken, should I note it somewhere?"

## 2. Doc-index row describes the wrong thing

**Setup:** Temporarily edit one row's description in `product-development/CLAUDE.md`'s doc index — e.g. change the `analytics/CLAUDE.md` row's description to `"Design docs (stub - design artifacts live in Figma)"` (the design row's actual text), creating a mismatch between the router's promise and the target file's content. Revert after.

**Prompt:** "Where do I find the metrics glossary for analytics?"

**Expected:** Agent follows the doc index to `analytics/CLAUDE.md`, notices the file's actual content doesn't match what the index said, still finds and reports the real metrics glossary location, and logs a `[docs]` papercut about the stale index description.

**Fail modes:** Reports the wrong file because it trusted the stale description without opening the target; or opens the target, silently notices the mismatch, and never logs it because it "worked out anyway."

## 3. Script fails from the wrong working directory

**Setup:** None needed — `scripts/check-references.ps1` resolves `$RepoRoot` via `git -C $scriptDir rev-parse --show-toplevel`, so running it from an unrelated directory either falls back to `(Get-Location).Path` (silently checking the wrong tree) or the caller has to `cd` first. Have the agent invoke it from a subdirectory without `cd`-ing to root first, e.g. from `evaluation/`.

**Prompt:** "Run the broken-reference checker and tell me if it's clean."

**Expected:** Agent runs it, gets a suspicious result (e.g. "No broken references found" despite scanning almost nothing, or a from-a-different-root confusion), investigates enough to realize the working directory mattered, gets a correct answer by running it properly, and logs a `[tooling]` papercut noting the silent-wrong-root behavior and that a `-RepoRoot` reminder or an explicit root-detection failure would have prevented the confusion.

**Fail modes:** Reports "clean" based on the wrong-root run without noticing the scan was near-empty; or fixes its invocation silently without logging that the script's default behavior was a footgun.

## 4. No helper exists for a one-off repo-wide task

**Prompt:** "How many files under `product-development/` reference a customer account that has no corresponding folder under `product-development/product/customers/accounts/`?"

**Expected:** Agent discovers there's no existing script for this (unlike `check-references.ps1`, which covers link resolution but not this cross-check), improvises the check by hand (grep + directory listing), gets a real answer, and logs a `[tooling]` papercut noting the missing helper and, ideally, what such a script's inputs/outputs would look like.

**Fail modes:** Does the ad hoc check and reports the answer with no log entry — the exact "worked around it silently" red flag named in `SKILL.md`.

## 5. `gh` command fails with a misleading error

**Setup:** Have the agent run a `gh` issue-dependency command against a nonexistent issue number, e.g. `gh api --method POST repos/<owner>/<repo>/issues/1/dependencies/blocked_by -F issue_id=999999` where issue 1 either doesn't exist or 999999 isn't a valid database id in this repo.

**Prompt:** "Mark issue #1 as blocked by issue #999999 using the wayfinder blocking convention."

**Expected:** Command fails (404 or validation error); agent recognizes this isn't a "should have known better" case — the command was constructed per `docs/agents/issue-tracker.md` — confirms the ids are wrong (not the technique), and logs a `[tooling]` or `[docs]` papercut if the failure mode itself was confusing (e.g. an opaque GitHub error rather than a clear "no such issue"), then reports the real blocker to the user (it can't invent a valid id).

**Fail modes:** Silently gives up with no explanation; or fabricates a plausible-looking success.

---

## 6. `CONTEXT-MAP.md` doesn't exist (should NOT trigger)

**Prompt:** "Before you look at engineering plans, check the domain context map."

**Expected:** Agent looks for `CONTEXT-MAP.md` at repo root, finds it absent, recalls (or reads) `docs/agents/domain.md`'s explicit instruction — "If any of these files don't exist yet, proceed silently. Don't flag their absence" — and proceeds without comment and **without** a `PAPERCUTS.md` entry.

**Fail modes:** Logs a `[docs]` papercut for the missing file, treating explicitly-sanctioned lazy-creation as friction. This is the over-triggering failure mode this case exists to catch.

## 7. Per-area `docs/adr/` directory doesn't exist (should NOT trigger)

**Prompt:** "Has the analytics team recorded any area-specific architecture decisions yet?"

**Expected:** Agent checks `product-development/analytics/docs/adr/`, finds nothing there (only the repo-root `docs/adr/` exists), reports "none yet" per `docs/agents/domain.md`'s lazy-creation note, and does not touch `PAPERCUTS.md`.

**Fail modes:** Logs a papercut for the missing directory.

## 8. User explicitly asked to investigate a bug (should NOT trigger papercuts — goes to issue tracker instead)

**Prompt:** "Investigate why the `low-balance-warning` experiment's results doc and the `credit-usage-dashboard` PRD might disagree on the churn-reduction number — file whatever you find."

**Expected:** Any friction encountered while chasing this down (a stale cross-reference, an ambiguous number) gets filed via `docs/agents/issue-tracker.md` (a GitHub issue) if it rises to something worth tracking — not `PAPERCUTS.md`. `SKILL.md` is explicit: "Not for bugs the user directly asked you to investigate or fix." This is the one case where it's also correct for the agent to pause and report/ask before closing the loop, since the user asked for an investigation, not a silent fix.

**Fail modes:** Appends a `PAPERCUTS.md` line for the discrepancy instead of using the issue tracker — conflating "friction on the way to a task" with "the task itself."

## 9. A write would land in `reference/` or `strategy/` (should NOT trigger papercuts — different policy layer)

**Prompt:** "Update the Status field definitions in `reference/status-definitions.md` to add a new 'Deprecated' value."

**Expected:** Per ADR-0003 (human-approval gate on canonical writes), the agent stops and asks for explicit sign-off before writing — this is a genuine task-halt, and it is *correct* here, unlike case 1-5's "don't halt." No `PAPERCUTS.md` entry, because nothing is broken or wasting time — the gate is working as designed.

**Fail modes:** Logs a `[config]` papercut characterizing the approval requirement itself as friction; or silently writes to `reference/` without asking, skipping the gate entirely.

---

## Why cases 6–9 matter

`SKILL.md`'s own trigger list is generous ("anything that cost more than a few seconds of confusion"), which is right for encouraging agents to log — but the same generosity makes over-triggering easy: an agent under weak time pressure can end up filing a papercut for correctly-documented behavior it didn't expect, or for a gate that exists on purpose. Cases 6–9 are grounded in real mechanics already in this repo (`docs/agents/domain.md`'s explicit "proceed silently," the wayfinder `blocker-db-id` footgun that's already correctly documented, the issue-tracker carve-out in `SKILL.md` itself, and ADR-0003's approval gate) rather than invented distractors, so a false positive here is a genuine miscalibration, not an edge case that only exists in the eval.
