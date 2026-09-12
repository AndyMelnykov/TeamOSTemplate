# PRD CPO Check and Sources Section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a 7th PRD template section (`Sources`, citing evidence the same way `templates/opportunity.md`/`templates/hypothesis.md` already do) and a new `/prd` Step 6 ("CPO check") that validates a drafted PRD's completeness, metric accuracy, status validity, and source citations before it's treated as ready to share.

**Architecture:** No new files, no new subsystem, no new agent role. `product-development/product/PRDs/CLAUDE.md`'s template gains one section; `.claude/commands/prd.md` gains one drafting instruction and one new step, run by the same single agent session that already drafts the PRD (per ADR 0004 — no separate reviewer agent). Verification reuses the existing `scripts/check-references.ps1` for file-path citations and simple grep-equivalent lookups against `insights.csv`/`sources.csv` for ID citations — no new script.

**Tech Stack:** Markdown, YAML (`feature-index.yaml`, read-only here), CSV (`insights.csv`/`sources.csv`, read-only here), PowerShell (`scripts/check-references.ps1`) — no code, no build step.

**Spec:** None — this is a bounded change scoped directly in chat during brainstorming (see conversation history: two suggestions approved out of a seven-item list generated from a transcript review). Design decisions are captured inline in this plan's Global Constraints and per-task rationale rather than in a separate spec file.

## Global Constraints

- This repo has no test runner/CI. "Verification" means running `powershell -File scripts/check-references.ps1` from the repo root (expect `No broken references found.`) plus a manual read-through comparing cited content against `reference/metrics.md` and `reference/status-definitions.md`.
- One-agent-per-session (ADR 0004): the CPO check is a step the same session runs inline, not a separate reviewer agent or pipeline stage.
- Human-approval-for-canonical-writes (ADR 0003) applies only to `reference/` and `product-development/product/strategy/`. No task in this plan writes to either — all edits are to `product-development/product/PRDs/CLAUDE.md`, `.claude/commands/prd.md`, one existing PRD file, and `ROADMAP.md` — so no approval-gate pause is required before committing.
- Reuse the existing citation convention verbatim: `INS-###` (`product-development/product/Insights/insights.csv`) and `SRC-###` (`product-development/product/Insights/sources.csv`), already established by `templates/opportunity.md` and `templates/hypothesis.md`. Do not invent a new ID scheme.
- A `Sources` bullet that cites a file path must use Markdown-link syntax `[label](relative/path)`, not a bare backtick reference — `scripts/check-references.ps1`'s Pass 2 only validates actual Markdown links (`[text](path)`), not backtick spans. This is a narrower convention than the bare-backtick style used elsewhere in PRD prose (e.g. `**Related RFC**` cells), and applies only inside the new `Sources` section.
- Scope is limited to: the PRD template, the `/prd` command, one worked-example PRD, and `ROADMAP.md` bookkeeping. Do not implement RFC auto-scaffolding, dependency surfacing, the GitHub-integration worked example, or the show-and-tell ritual — those were other suggestions from the same brainstorming pass and were not approved for this round. Do not retrofit the other three existing top-level PRDs (`sso-prd.md`, `shared-components-prd.md`, `team-workspaces-prd.md`) with a `Sources` section — one worked example is sufficient to prove the convention; backfilling the rest is a separate, later task if wanted.

---

### Task 1: Define the `Sources` section in the PRD template and `/prd`'s drafting step

**Files:**
- Modify: `product-development/product/PRDs/CLAUDE.md:52-54` (Creating New PRDs list) and `:60-65` (PRD Template Sections list)
- Modify: `.claude/commands/prd.md:7-12` (Task Overview list) and `:22-31` (Step 3: Gather Content)

**Interfaces:**
- Produces: the 7th PRD section name (`Sources`), its citation format (`INS-###` / `SRC-###` / `[label](relative/path)` Markdown link), and the rule that it consolidates citations already made elsewhere in the PRD rather than introducing new ones. Task 2's CPO check and Task 3's worked example both depend on this exact format.

- [ ] **Step 1: Add the `Sources` section to `product-development/product/PRDs/CLAUDE.md`'s template list**

Replace the "PRD Template Sections" list (current lines 60-65):

```markdown
1. **Overview** - Problem statement, goals, success metrics
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes
5. **Technical Considerations** - Architecture, dependencies
6. **Launch Plan** - Rollout strategy, feature flags
```

with:

```markdown
1. **Overview** - Problem statement, goals, success metrics
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes
5. **Technical Considerations** - Architecture, dependencies
6. **Launch Plan** - Rollout strategy, feature flags
7. **Sources** - `INS-###`, `SRC-###`, or file-path citations for claims already made in sections 1-6, one bullet each, in the same citation format as `templates/opportunity.md`'s "Evidence" section. A file-path citation must be a Markdown link (`[label](relative/path)`), not a bare backtick reference, so `scripts/check-references.ps1` can verify it resolves. This section consolidates citations already made elsewhere in the PRD — it is not a place to introduce a new unsupported claim. See `.claude/commands/prd.md`'s Step 6 (CPO check) for how these are validated.
```

- [ ] **Step 2: Update the "Creating New PRDs" list in the same file**

Replace (current lines 51-54):

```markdown
Use the `/prd` command to create new PRDs. The command will:
1. Load the PRD writing style
2. Guide you through required sections
3. Format according to example_product Labs standards
```

with:

```markdown
Use the `/prd` command to create new PRDs. The command will:
1. Load the PRD writing style
2. Guide you through required sections
3. Format according to example_product Labs standards
4. Run a CPO check against the finished draft before it's treated as ready to share
```

- [ ] **Step 3: Update `/prd`'s Task Overview list**

In `.claude/commands/prd.md`, replace (current lines 7-12):

```markdown
Create a new PRD by:
1. Confirming the feature name and product area
2. Checking `product-development/feature-index.yaml` for an existing entry (do not create a duplicate PRD for a feature that already has one)
3. Gathering the required content for each template section
4. Writing the PRD file with the correct name and location
5. Updating `product-development/feature-index.yaml` with the new PRD's path
```

with:

```markdown
Create a new PRD by:
1. Confirming the feature name and product area
2. Checking `product-development/feature-index.yaml` for an existing entry (do not create a duplicate PRD for a feature that already has one)
3. Gathering the required content for each template section
4. Writing the PRD file with the correct name and location
5. Updating `product-development/feature-index.yaml` with the new PRD's path
6. Running the CPO check against the finished draft before treating it as ready to share
```

- [ ] **Step 4: Update `/prd`'s Step 3 (Gather Content) to draft the `Sources` section**

Replace (current lines 22-31):

```markdown
## Step 3: Gather Content

For each of the six sections defined in `product-development/product/PRDs/CLAUDE.md` ("PRD Template Sections"), ask the user for the relevant content, or draft it from context already available (feature-index entries, customer call summaries under `product-development/product/customers/accounts/`, competitive research) and confirm with the user before finalizing:

1. **Overview** - Problem statement, goals, success metrics (cite `reference/metrics.md` for any metric target referenced)
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes (link the Figma file if one exists)
5. **Technical Considerations** - Architecture, dependencies; link the related RFC if one exists or is planned
6. **Launch Plan** - Rollout strategy, feature flags
```

with:

```markdown
## Step 3: Gather Content

For each of the seven sections defined in `product-development/product/PRDs/CLAUDE.md` ("PRD Template Sections"), ask the user for the relevant content, or draft it from context already available (feature-index entries, customer call summaries under `product-development/product/customers/accounts/`, competitive research) and confirm with the user before finalizing:

1. **Overview** - Problem statement, goals, success metrics (cite `reference/metrics.md` for any metric target referenced)
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes (link the Figma file if one exists)
5. **Technical Considerations** - Architecture, dependencies; link the related RFC if one exists or is planned
6. **Launch Plan** - Rollout strategy, feature flags
7. **Sources** - Every `INS-###`, `SRC-###`, or file path already cited in sections 1-6 above, listed once each as its own bullet. Use the same citation format as `templates/opportunity.md`'s "Evidence" section; write a file-path citation as a Markdown link (`[label](relative/path)`) rather than a bare backtick reference. If a claim in sections 1-6 has no citable source, leave it as uncited prose rather than inventing a citation here.
```

- [ ] **Step 5: Note the required section headers in `/prd`'s Step 4 (Write the PRD)**

After the existing line (current line 50):

```markdown
Write the file to `product-development/product/PRDs/{product-area}/{feature-name}-prd.md`, following the naming convention in `product-development/product/PRDs/CLAUDE.md`.
```

add:

```markdown
Include all seven section headers (`## Overview` through `## Sources`) in the order defined in `product-development/product/PRDs/CLAUDE.md`, each followed by real content.
```

- [ ] **Step 6: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 7: Commit**

```bash
git add product-development/product/PRDs/CLAUDE.md .claude/commands/prd.md
git commit -m "docs: add Sources as a 7th PRD template section"
```

---

### Task 2: Add the CPO check (`/prd` Step 6)

**Files:**
- Modify: `.claude/commands/prd.md` (append after the current Step 5, i.e. after current line 54)

**Interfaces:**
- Consumes: the `Sources` section format and the seven-section list produced by Task 1.
- Produces: the Step 6 checklist Task 3 exercises against a real PRD.

- [ ] **Step 1: Append the new step to `.claude/commands/prd.md`**

Add after the existing Step 5 content (current line 54, "Add or update the entry in `product-development/feature-index.yaml`... (relative to `product-development/`)."):

```markdown

## Step 6: Run the CPO Check

Before treating the PRD as ready to share (i.e. before advancing `**Status**` past `Draft`), verify all of the following against the file you just wrote:

1. **All seven section headers are present and non-empty** - `## Overview`, `## User Stories`, `## Requirements`, `## Design`, `## Technical Considerations`, `## Launch Plan`, `## Sources`, each followed by real content (not a placeholder or an empty section).
2. **Every metric cited matches `reference/metrics.md`** - for each metric name mentioned in the PRD, confirm both the name and any target value match the corresponding row in `reference/metrics.md` exactly. If a cited metric doesn't appear in `reference/metrics.md` at all, flag it to the user rather than treating it as a new canonical metric — new canonical metrics are added to `reference/metrics.md` under the human-approval rule in `docs/adr/0003-human-approval-for-canonical-writes.md`, not invented inline in a PRD.
3. **`**Status**` is a valid value** - one of the five values in `reference/status-definitions.md` (`Draft`, `In Review`, `Approved`, `Shipped`, `Archived`).
4. **`**Related RFC**` is not left as a dangling placeholder** - either a real path, or explicit prose stating no RFC exists yet (e.g. "not yet planned").
5. **Every `Sources` citation resolves**:
   - For a file-path citation (written as a Markdown link per Step 3), run `powershell -File scripts/check-references.ps1` from the repo root and confirm it reports `No broken references found.` This script already scans every tracked Markdown file's links and `feature-index.yaml`'s path tokens, so a PRD's file-path citations are covered as soon as the PRD is on disk — no PRD-specific script changes are needed.
   - For an `INS-###` citation, confirm that ID exists as a row in `product-development/product/Insights/insights.csv`.
   - For a `SRC-###` citation, confirm that ID exists as a row in `product-development/product/Insights/sources.csv`.

Report any failures to the user and fix them before moving on. This check only reads `reference/`, `feature-index.yaml`, `insights.csv`, and `sources.csv`, and validates the PRD draft — it never writes to `reference/` or `product-development/product/strategy/`, so it does not trigger the human-approval gate in ADR 0003.
```

- [ ] **Step 2: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/prd.md
git commit -m "docs: add CPO check as /prd Step 6"
```

---

### Task 3: Dry-run both changes against an existing PRD

**Files:**
- Modify: `product-development/product/PRDs/ai-gen-v3-prd.md` (append a `## Sources` section)

**Interfaces:**
- Consumes: Task 1's `Sources` format, Task 2's Step 6 checklist, the existing content of `product-development/product/PRDs/ai-gen-v3-prd.md`, its `feature-index.yaml` entry (`prototyping.ai-generation-v3`), and `reference/metrics.md`'s ESR/WCR rows.
- Produces: a worked example of a `Sources` section other PRD authors (human or agent) can model future PRDs on, and a demonstration that the Step 6 checklist actually passes end-to-end on a real file — the closest equivalent this docs-only repo has to a passing test.

`ai-gen-v3-prd.md` already cites its evidence in prose without a dedicated section: the Overview cites Extraction Success Rate (ESR) with its target, the Problem Statement cites Workflow Completion Rate (WCR) and "the `analytics/investigations/` history," and Technical Considerations cites the `table-schemas` entry in `feature-index.yaml`. This task formalizes those into a checkable `Sources` list without inventing new claims.

- [ ] **Step 1: Confirm the real paths to cite (do not skip — these must resolve on disk)**

- `reference/metrics.md` defines both ESR (target `> 92%`) and WCR (target `> 60%`) — matches what's already stated in the PRD's Overview.
- `product-development/feature-index.yaml`'s `prototyping.ai-generation-v3` entry lists `table-schemas: [analytics/schemas/prototyping/project-generations.md]` — this is the schema already referenced in Technical Considerations.
- `product-development/engineering/rfcs/gen-v3-rfc.md` exists on disk and matches the PRD's `**Related RFC**` field.

- [ ] **Step 2: Append the `Sources` section to `product-development/product/PRDs/ai-gen-v3-prd.md`**

Add after the existing `## Launch Plan` section (current final line, "Staged rollout by cohort, monitored against the ESR target in `reference/metrics.md`."):

```markdown

## Sources

- [reference/metrics.md](../../../reference/metrics.md) — Extraction Success Rate (ESR) and Workflow Completion Rate (WCR) definitions and targets, cited in Overview and Problem Statement
- [analytics/schemas/prototyping/project-generations.md](../../analytics/schemas/prototyping/project-generations.md) — automation-run event schema cited in Technical Considerations (see `feature-index.yaml`'s `prototyping.ai-generation-v3.table-schemas` entry)
```

- [ ] **Step 3: Run the Step 6 CPO check against this file**

Walk through `.claude/commands/prd.md`'s Step 6 checklist against `ai-gen-v3-prd.md`:
1. All seven headers present and non-empty — confirm by reading the file.
2. ESR (`> 92%`) and WCR (`> 60%`) as cited match `reference/metrics.md` exactly — confirm by reading `reference/metrics.md`.
3. `**Status**` is `Draft` — valid per `reference/status-definitions.md`.
4. `**Related RFC**` is `engineering/rfcs/gen-v3-rfc.md`, a real path (confirmed in Step 1) — not a placeholder.
5. Run `powershell -File scripts/check-references.ps1` and confirm it reports `No broken references found.` (no `INS-###`/`SRC-###` citations in this particular PRD, so only the file-path check applies here.)

- [ ] **Step 4: Run the reference checker**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 5: Commit**

```bash
git add product-development/product/PRDs/ai-gen-v3-prd.md
git commit -m "docs: add Sources section to ai-gen-v3-prd.md as a worked example"
```

---

### Task 4: Reconcile `ROADMAP.md`'s "Canonical-document validation" item

**Files:**
- Modify: `ROADMAP.md:13-14` (Now section) and its "Already shipped" section (current lines 38-46)

**Interfaces:**
- Consumes: the shipped capability from Tasks 1-3.
- Produces: an accurate roadmap that doesn't claim PRD-level validation is still fully missing, while keeping the still-open part (decision-file enforcement) visible.

- [ ] **Step 1: Narrow the "Canonical-document validation" Now item**

Replace (current lines 13-14):

```markdown
### Canonical-document validation
**Why:** `reference/status-definitions.md` and `reference/decision-types.md` define valid conventions, but nothing currently enforces them — a PRD can carry an invalid `Status` value or a definition can get re-stated outside `reference/` and nothing catches it.
```

with:

```markdown
### Canonical-document validation
**Why:** `reference/decision-types.md` defines a valid decision-file format, but nothing currently enforces it — a definition can get re-stated outside `reference/` and nothing catches it. (PRD-level validation — `Status` value, and metric name/target match against `reference/metrics.md` — is now covered by `/prd`'s Step 6 CPO check; this item is now scoped to decision files, and to enforcement outside of a PRD author's own `/prd` run, e.g. a PRD edited by hand after the fact.)
```

- [ ] **Step 2: Add a bullet to "Already shipped"**

Add to the end of the "Already shipped" list (after the current last bullet, the opportunity/hypothesis layer bullet):

```markdown
- **PRD self-review before sharing ("CPO check")** — `.claude/commands/prd.md` Step 6 validates section completeness, `Status` validity, metric name/target match against `reference/metrics.md`, and that `Sources` citations resolve, before a PRD is treated as ready. Scoped to PRDs only; decision-file validation remains open (see "Canonical-document validation" above).
```

- [ ] **Step 3: Verify references resolve**

Run: `powershell -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 4: Commit**

```bash
git add ROADMAP.md
git commit -m "docs: reconcile ROADMAP with the new PRD CPO check"
```
