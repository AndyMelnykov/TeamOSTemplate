# PRD Writing

You are an expert at writing example_product Product Requirement Documents.

## Task Overview

Create a new PRD by:
1. Confirming the feature name and product area
2. Checking `product-development/feature-index.yaml` for an existing entry (do not create a duplicate PRD for a feature that already has one)
3. Gathering the required content for each template section
4. Writing the PRD file with the correct name and location
5. Updating `product-development/feature-index.yaml` with the new PRD's path
6. Running the CPO check against the finished draft before treating it as ready to share

## Step 1: Confirm Feature Name, Product Area, and Review Tier

Ask the user for the feature name and which product area it belongs to (`home-page`, `billing`, `prototyping`, `starter-templates`, or `deployment` — see `product-development/feature-index.yaml` for the current set).

Also determine the `Review Tier` (`Local` or `Strategy Review`) using the criteria in `product-development/product/PRDs/CLAUDE.md`'s "Review Tier" section. If any criterion is met, it's `Strategy Review`; otherwise `Local`. Tell the user which tier applies and why.

## Step 2: Check for an Existing Entry

Search `product-development/feature-index.yaml` under the given product area for an existing feature with this name or a close match. If found, tell the user and offer to edit the existing PRD instead of creating a new one.

Also check for an open `feature-request`-labeled GitHub issue covering this feature: `gh issue list --label feature-request --state open --json number,title,body`. If found, tell the user and offer to link the issue from the new PRD's `Sources` section rather than treating this as an unrelated fresh request.

## Step 3: Gather Content

For each section of the canonical template in `product-development/product/PRDs/CLAUDE.md` ("PRD Template Sections"), ask the user for the relevant content, or draft it from context already available (feature-index entries, customer call summaries under `product-development/product/customers/accounts/`, competitive research) and confirm with the user before finalizing. Go in template order and use the template's subsections and tables:

- **Overview** - `### Problem`, `### Why Now`, `### Goals & Success Metrics` (a table with a `Source` for each metric; cite `reference/metrics.md` for any metric target referenced), `### Non-Goals`
- **User Stories** - numbered `Story 1`, `Story 2`, …
- **Requirements** - P0/P1/P2 tables with ids (`P0-1`, …)
- **Acceptance Criteria** - draft the table from the stories and P0s, following "Writing acceptance criteria" in `PRDs/CLAUDE.md`. Confirm each row's `Verify by` with the user. A requirement too vague to test goes to `## Open Questions`.
- **Design** - UX flows, wireframes (link the Figma file if one exists)
- **Technical Considerations** - Architecture, dependencies; link the related RFC if one exists or is planned
- **Launch Plan** - Rollout strategy, feature flags
- **Sources** - Every `SIG-###` or file path already cited in the sections above, listed once each as its own bullet. Use the same citation format as `templates/hypothesis.md`'s "Signals" section; write a file-path citation as a Markdown link (`[label](relative/path)`) rather than a bare backtick reference. If a claim above has no citable source, leave it as uncited prose rather than inventing a citation here.

Also ask for the two header fields: `**Hypothesis**` (an existing `HYP-` id, or `none — <reason>`) and `**Execution Path**` (apply the rule in "Execution Path" in `PRDs/CLAUDE.md` and tell the user which path applies and why).

## Step 4: Write the PRD

Use the header table format from any existing PRD (e.g. `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md`):

```markdown
# [Feature Name] - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | [Name] (PM) |
| **Status** | Draft |
| **Last Updated** | [YYYY-MM-DD] |
| **Related RFC** | `engineering/rfcs/{product-area}/{feature-name}-rfc.md`, or "not yet planned" |
| **Review Tier** | [Local or Strategy Review — see `product-development/product/PRDs/CLAUDE.md`] |
| **Hypothesis** | [`HYP-…` id, or `none — <reason>`] |
| **Execution Path** | [`agent-direct` or `engineering-mediated`] |
```

`**Status**` starts at `Draft` per `reference/status-definitions.md` and should be updated as the PRD progresses.

Write the file to `product-development/product/PRDs/{product-area}/{feature-name}-prd.md`, following the naming convention in `product-development/product/PRDs/CLAUDE.md`.

Include every section header of the canonical template (`## Overview` through `## Sources`, with `## Open Questions` after if needed) in the order defined in `product-development/product/PRDs/CLAUDE.md`, each followed by real content.

## Step 5: Update the Feature Index

Add or update the entry in `product-development/feature-index.yaml` under the correct product area, setting the `prd` key to the new file's path (relative to `product-development/`).

## Step 6: Run the CPO Check

Before treating the PRD as ready to share (i.e. before advancing `**Status**` past `Draft`), verify all of the following against the file you just wrote:

1. **All canonical section headers are present and non-empty** - `## Overview`, `## User Stories`, `## Requirements`, `## Acceptance Criteria`, `## Design`, `## Technical Considerations`, `## Launch Plan`, `## Sources`, each followed by real content (not a placeholder or an empty section).
2. **Every metric cited matches `reference/metrics.md`** - for each metric name mentioned in the PRD, confirm both the name and any target value match the corresponding row in `reference/metrics.md` exactly. If a cited metric doesn't appear in `reference/metrics.md` at all, flag it to the user rather than treating it as a new canonical metric — new canonical metrics are added to `reference/metrics.md` under the human-approval rule in `docs/adr/0003-human-approval-for-canonical-writes.md`, not invented inline in a PRD.
3. **`**Status**` is a valid value** - one of the five values in `reference/status-definitions.md` (`Draft`, `In Review`, `Approved`, `Shipped`, `Archived`).
4. **`**Related RFC**` is not left as a dangling placeholder** - either a real path, or explicit prose stating no RFC exists yet (e.g. "not yet planned").
5. **`**Review Tier**` is a valid value** - either `Local` or `Strategy Review`, matching the criteria in `product-development/product/PRDs/CLAUDE.md`'s "Review Tier" section. If `Strategy Review`, `**Status**` may not advance past `In Review` unless a decision file recording the review's outcome already exists under `product-development/product/strategy/` (per `reference/decision-types.md` and `docs/adr/0006-two-track-prd-review.md`), linked from this PRD. If no such decision file exists yet, flag it to the user and hold `**Status**` at `In Review` rather than advancing it.
6. **Every `Sources` citation resolves**:
   - For a file-path citation (written as a Markdown link per Step 3), run `powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1` from the repo root and confirm it reports `No broken references found.` This script already scans every tracked Markdown file's links and `feature-index.yaml`'s path tokens, so a PRD's file-path citations are covered as soon as the PRD is on disk — no PRD-specific script changes are needed.
   - For a `SIG-###` citation, confirm that ID exists as a row in `product-development/signals/signals.csv`. An `INS-###` or `SRC-###` citation is a retired id: replace it with its `SIG-###`.

7. **The Acceptance Criteria table is complete** - columns `| ID | Given | When | Then | Covers | Verify by |`; ids `AC-1`, `AC-2`, … are unique; `Given`, `When`, `Then` and `Covers` are non-empty on every row; `Verify by` is `automated-test`, `manual-qa` or `analytics` on every row; a literal `|` in a cell is written `\|`.
8. **Every P0 is covered** - each `P0-n` id in `### Must Have (P0)` appears in the `Covers` cell of at least one AC row. List any that don't, by id.
9. **Every success metric is instrumented** - each row of `### Goals & Success Metrics` has `Baseline`, `Target`, `Timeline` and `Source` filled, and each `analytics` AC row names a metric from that table.
10. **`**Hypothesis**` resolves** - either an existing `HYP-` id (find the file under `product-development/product/PRDs/` or via `feature-index.yaml`) or `none — <reason>` with a real reason.
11. **`**Execution Path**` follows the rule** - `agent-direct` or `engineering-mediated`; `agent-direct` only when `**Review Tier**` is `Local`, the change is in one product area, there is no migration or schema change, no new external integration, and no AC has `Verify by` = `analytics`.

Report any failures to the user and fix them before moving on. This check only reads `reference/`, `feature-index.yaml`, and `signals.csv`, and validates the PRD draft — it never writes to `reference/` or `product-development/product/strategy/`, so it does not trigger the human-approval gate in ADR 0003.
