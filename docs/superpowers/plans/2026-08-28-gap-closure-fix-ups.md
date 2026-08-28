# Product OS Gap Closure Fix-Ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the two remaining gaps found when auditing `docs/superpowers/plans/2026-08-26-product-os-gap-closure.md` against the repo's actual state: (1) the broken-reference checker has a false-positive blind spot that currently reports 1 broken reference repo-wide instead of 0, and (2) `.claude/commands/customer-call.md` still carries several stale, pre-rewrite references that Task 9 of the original plan was supposed to fully clear.

**Architecture:** No new files or subsystems — this plan only edits the two artifacts the original plan already created/modified: `scripts/check-references.ps1` (Task 1 of the original plan) and `.claude/commands/customer-call.md` (Task 9 of the original plan). Both fixes are independent of each other and can be done in either order.

**Tech Stack:** Same as the parent plan — Markdown content + one PowerShell 5.1 script. No application code, no test framework; verification is done by running the checker script and by `Select-String` greps, consistent with this repo's existing content-integrity-check convention.

**Spec:** `docs/superpowers/plans/2026-08-26-product-os-gap-closure.md` (the parent plan) and, transitively, `reference/01-ai-native-product-os.md` (the architecture spec the parent plan implements).

## Global Constraints

- Every edited file must use the existing placeholder product name `example_product` / `EXAMPLE_PRODUCT` — never reintroduce the pre-rebrand name `Forge`.
- After every task, re-run `scripts/check-references.ps1` from repo root (`powershell -ExecutionPolicy Bypass -File scripts\check-references.ps1` — the repo's default execution policy blocks unsigned scripts, so `-ExecutionPolicy Bypass` is required for local invocation) and confirm it reports exit code 0 with no broken references, since this plan's whole purpose is reaching that green state.
- Do not restructure or rename anything beyond what each task specifies — these are targeted fixes, not a rewrite of either file.

---

## Task 1: Fix the broken-reference checker's inline-code false positive

**Files:**
- Modify: `scripts/check-references.ps1:76-103` (Pass 2 — Markdown link scan)

**Interfaces:**
- Consumes: none new.
- Produces: the same `scripts/check-references.ps1` exit-code-0/1 contract Task 1 of the parent plan established, now with one additional, documented exclusion.

**Root cause:** `.claude/skills/setup-ts-deep-modules/SKILL.md:93` contains this sentence, entirely wrapped in a single pair of backticks as one inline code span:

```
One line is enough, e.g. `Packages are deep modules — see [src/packages/README.md](./src/packages/README.md) before adding or importing one.` This is what makes an agent discover the boundary rule instead of tripping over it.
```

This is example text showing an agent what line to add to some *other, future* repo's `CLAUDE.md` — it is not a real link in *this* repo, and `src/packages/README.md` does not exist here (nor should it; this repo has no `src/packages/`). The checker's Pass 2 already excludes content inside triple-backtick fenced code blocks and refs containing `{...}` placeholders (see `Test-IsExternalRef`), but it has no equivalent exclusion for a markdown link that is itself wrapped in inline (single-backtick) code — so this one line is currently misdetected as a broken reference. Confirm this is still the only false positive before starting:

```bash
powershell -ExecutionPolicy Bypass -File scripts\check-references.ps1
```

Expected current output: exit code 1, exactly one broken reference:
```
.claude\skills\setup-ts-deep-modules\SKILL.md:93: ./src/packages/README.md
```

- [ ] **Step 1: Set up an isolated fixture to prove the fix (and prove it doesn't regress real detection)**

Create a throwaway fixture outside the repo so this verification never touches real repo files. (The fenced-code-block test case is built via a `$FENCE` shell variable rather than a literal ``` line, so this plan document's own fenced block boundary — scanned by `check-references.ps1` itself — isn't closed early by a nested literal fence.)

```bash
mkdir -p /tmp/checker-fixture/product-development
cd /tmp/checker-fixture
git init -q
FENCE='```'
{
  echo '# Fixture'
  echo ''
  echo 'A real broken link that must still be caught: [broken](./does-not-exist.md)'
  echo ''
  echo 'An illustrative link inside inline code that must NOT be caught: `see [example](./also-does-not-exist.md) for details`'
  echo ''
  echo 'A fenced-code-block link that must NOT be caught (already handled, regression check):'
  echo "$FENCE"
  echo '[fenced](./still-does-not-exist.md)'
  echo "$FENCE"
} > real-broken-link.md
git add real-broken-link.md
```

- [ ] **Step 2: Run the current (unfixed) checker against the fixture to confirm the false positive reproduces there too**

```bash
powershell -ExecutionPolicy Bypass -File "<repo-root>/scripts/check-references.ps1" -RepoRoot "/tmp/checker-fixture"
```

Expected: exit code 1, with **two** broken references reported — the real broken link AND the illustrative inline-code one (the fenced one is already correctly excluded). This confirms the fixture reproduces the exact bug before the fix is applied.

- [ ] **Step 3: Fix `scripts/check-references.ps1`**

In the Pass 2 loop, strip inline code spans from the line before scanning it for Markdown links, so a link entirely inside a single-backtick span is treated the same way a link inside a fenced block already is — as illustrative text, not a real reference. Change:

```powershell
        if ($inFence) { continue }
        $linkMatches = [regex]::Matches($line, '\[[^\]]*\]\(([^)]+)\)')
        foreach ($m in $linkMatches) {
```

to:

```powershell
        if ($inFence) { continue }
        # Strip inline code spans first: a Markdown link entirely inside a
        # single-backtick span (e.g. an example line shown to an agent) is
        # illustrative text, not a real reference — same treatment as the
        # {...} placeholder exclusion in Test-IsExternalRef.
        $scanLine = [regex]::Replace($line, '`[^`\n]*`', '')
        $linkMatches = [regex]::Matches($scanLine, '\[[^\]]*\]\(([^)]+)\)')
        foreach ($m in $linkMatches) {
```

Also update the `.DESCRIPTION` comment block at the top of the file (currently ends `...External links (http/https/mailto) and anchor-only links (#foo) are ignored.`) to add one sentence:

```
      External links (http/https/mailto) and anchor-only links (#foo) are
      ignored, as are links entirely inside an inline code span (single
      backticks) — these are illustrative example text, not real references.
```

- [ ] **Step 4: Re-run the checker against the fixture and confirm both the fix and the regression check**

```bash
powershell -ExecutionPolicy Bypass -File "<repo-root>/scripts/check-references.ps1" -RepoRoot "/tmp/checker-fixture"
```

Expected: exit code 1, with **exactly one** broken reference now — `real-broken-link.md:...: ./does-not-exist.md`. The inline-code link and the fenced-code-block link must both be absent from the output. If the inline-code link still appears, the regex in Step 3 needs adjustment. If the real broken link stops appearing, the fix is too broad — do not proceed until both conditions hold simultaneously.

Clean up the fixture:

```bash
rm -rf /tmp/checker-fixture
```

- [ ] **Step 5: Run the checker against the real repo and confirm the known false positive is gone**

```bash
powershell -ExecutionPolicy Bypass -File scripts\check-references.ps1
```

Expected: exit code 0, "No broken references found." — this is the parent plan's Task 14 final-gate criterion, now actually met.

- [ ] **Step 6: Commit**

```bash
git add scripts/check-references.ps1
git commit -m "Fix broken-reference checker false positive on inline-code example links"
```

---

## Task 2: Finish cleaning up `.claude/commands/customer-call.md`'s stale pre-rewrite references

**Files:**
- Modify: `.claude/commands/customer-call.md:10` (Task Overview)
- Modify: `.claude/commands/customer-call.md:86` (5a heading template)
- Modify: `.claude/commands/customer-call.md:120` (5b heading template)
- Modify: `.claude/commands/customer-call.md:198-204` (File Organization section)
- Modify: `.claude/commands/customer-call.md:215-229` (Execution Steps section)

**Interfaces:**
- Consumes: the account-based, one-dated-file-per-call model already established earlier in the same file (Steps 1 and 2, `.claude/commands/customer-call.md:16-44`) by the parent plan's Task 9.
- Produces: a `customer-call.md` that is internally consistent throughout — no file mixes the old "one product-area, one running file per customer, background Task agent" model with the new "named account, one dated file per call, direct main-agent writes" model.

**Root cause:** The parent plan's Task 9 rewrote Steps 1, 2, and 5c to the current account-based model, but left five other spots in the same file still describing the pre-rewrite model:
1. Line 10 (`Task Overview`) still says "Determining the product area" instead of identifying the customer account.
2. Lines 86 and 120 use bracket-style `[CustomerName]` placeholders, inconsistent with the `{slug}`/`{date}` brace-style placeholders used everywhere else in the rewritten sections.
3. Lines 198-204 (`File Organization`) still assert "Each customer has ONE summary file and ONE transcript file (with multiple meetings inside)" — the exact one-running-file-per-customer model Step 2 explicitly says no longer applies.
4. Lines 215-229 (`Execution Steps`) still say "Confirm product area with user" (step 1) and describe a "background Task agent for feature requests update" (steps 8 and 12) — the file's own Step 5 section (`Why no Task agents for file writing`) and 5c (`Log Feature Requests`) explicitly rule this out.

Confirm the current state before starting:

```bash
grep -n -i "product area\|task agent\|one summary file\|CustomerName" .claude/commands/customer-call.md
```

Expected output (line numbers as of this plan being written — re-check if Task 9 or other edits have shifted them since):
```
10:1. Determining the product area
79:**Why no Task agents for file writing:** ...
86:   - The `# [CustomerName] - Meeting Summaries` heading
98:**Use the Write tool for the header, then Bash/Python for the transcript body.** Never pass large transcript content through the Write tool or a Task agent.
120:#   # [CustomerName] - Meeting Transcripts
201:- Each customer has ONE summary file and ONE transcript file (with multiple meetings inside)
217:1. Confirm product area with user
224:8. Launch background Task agent for feature requests update
```
(Lines 79 and 98 are correct as-is — they explain *why* Task agents are avoided — only lines 10, 86, 120, 201, 217, and 224 are stale.)

- [ ] **Step 1: Fix the Task Overview line**

Edit `.claude/commands/customer-call.md:10`, replacing:

```markdown
1. Determining the product area
```

with:

```markdown
1. Identifying the customer account
```

- [ ] **Step 2: Fix the two heading-template placeholders**

Edit `.claude/commands/customer-call.md:86`, replacing:

```markdown
   - The `# [CustomerName] - Meeting Summaries` heading
```

with:

```markdown
   - The `# {Account Name} - Meeting Summaries` heading
```

Edit `.claude/commands/customer-call.md:120`, replacing:

```
#   # [CustomerName] - Meeting Transcripts
```

with:

```
#   # {Account Name} - Meeting Transcripts
```

- [ ] **Step 3: Fix the File Organization section**

Edit `.claude/commands/customer-call.md:198-203`, replacing:

```markdown
### File Organization
- **Summaries** go in `summaries/` subfolder
- **Transcripts** go in `transcripts/` subfolder
- Each customer has ONE summary file and ONE transcript file (with multiple meetings inside)
- Meetings are in reverse chronological order (newest first)
- Use `---` as separator between meetings
```

with:

```markdown
### File Organization
- **Summaries** go in `summaries/` subfolder
- **Transcripts** go in `transcripts/` subfolder
- Each call gets its own dated file (`{date}.md`) in each folder — not one running file per customer (see Step 2)
- If a dated file already holds more than one same-day meeting, those meetings are in reverse chronological order (newest first) within that file
- Use `---` as separator between meetings within a file
```

- [ ] **Step 4: Fix the Execution Steps list**

Edit `.claude/commands/customer-call.md:215-229`, replacing the entire section:

```markdown
## Execution Steps

1. Confirm product area with user
2. Check for existing customer files in both summaries/ and transcripts/ folders
3. If existing files: review Open Action Items, ask user about unclear status
4. Gather meeting information
5. Get transcript content
6. Read summary skill guidelines and example
7. Generate summary content (sections), feature request list, and action item updates
8. Launch background Task agent for feature requests update
9. Write summary file directly (Write tool)
10. Write transcript file directly (Bash concatenation + wrap script)
11. Verify files exist and cross-reference links are correct
12. Check that feature requests agent completed
13. Generate and present Slack summary draft for user review
```

with:

```markdown
## Execution Steps

1. Identify the customer account (create the account folder if new)
2. Check for existing customer files in both summaries/ and transcripts/ folders
3. If existing files: review Open Action Items, ask user about unclear status
4. Gather meeting information
5. Get transcript content
6. Read summary skill guidelines and example
7. Generate summary content (sections), feature request list, and action item updates
8. Write summary file directly (Write tool)
9. Write transcript file directly (Bash concatenation + wrap script)
10. Log feature requests to Linear / Jira / Asana
11. Verify files exist and cross-reference links are correct
12. Generate and present Slack summary draft for user review
```

- [ ] **Step 5: Verify no stale references remain**

```bash
grep -n -i "product area\|one summary file\|one running file\|\[CustomerName\]" .claude/commands/customer-call.md
```

Expected: no matches. (This intentionally omits "Task agent" from the grep since lines 79 and 98 are correct, existing prose explaining why Task agents are *not* used — those must remain.)

Run the original parent-plan Task 9 verification too, since this task is completing that one:

```bash
powershell -ExecutionPolicy Bypass -File scripts\check-references.ps1
```

Expected: exit code 0 (this file has no Markdown-link-style references, so this run just confirms nothing regressed).

- [ ] **Step 6: Commit**

```bash
git add .claude/commands/customer-call.md
git commit -m "Finish clearing stale pre-account-model references in customer-call command"
```

---

## Task 3: Final full-repo verification

**Files:** none (verification only).

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: confirmation that the parent plan's Task 14 final gate ("exit code 0, no broken references found") now actually holds for the whole repo, and that both gaps identified in the audit are closed.

- [ ] **Step 1: Run the full checker one more time**

```bash
powershell -ExecutionPolicy Bypass -File scripts\check-references.ps1
```

Expected: exit code 0, "No broken references found."

- [ ] **Step 2: Re-confirm the customer-call.md cleanup is complete**

```bash
grep -n -i "product area\|one summary file\|one running file\|\[CustomerName\]" .claude/commands/customer-call.md
```

Expected: no matches.

- [ ] **Step 3: Report status**

No commit for this task — it is a verification-only checkpoint. If both Step 1 and Step 2 pass, both gaps from the audit are closed and this plan is complete.

---

## Self-Review Notes

**Gap coverage:**
- Gap 1 (checker false positive on `.claude/skills/setup-ts-deep-modules/SKILL.md:93`) — Task 1.
- Gap 2 (Task 9's incomplete cleanup of `.claude/commands/customer-call.md`) — Task 2, expanded beyond the two originally-flagged `[CustomerName]` lines to also cover the "product area" and "background Task agent" leftovers found on closer reading (lines 10, 217, 224) and the contradictory File Organization section (lines 198-204) — all in the same file, same category of staleness, so folding them into one task avoids re-flagging "complete" prematurely a second time.

**Not in scope, and why:** No other files are touched. The audit that produced this plan found exactly these two gaps against the parent plan's 14 tasks; broadening scope further (e.g., auditing every other file this repo's agents have ever touched) is out of bounds for a plan whose job is to close two specific, already-identified gaps.
