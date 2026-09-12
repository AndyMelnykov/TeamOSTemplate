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

## Step 1: Confirm Feature Name and Product Area

Ask the user for the feature name and which product area it belongs to (`home-page`, `billing`, `prototyping`, `starter-templates`, or `deployment` — see `product-development/feature-index.yaml` for the current set).

## Step 2: Check for an Existing Entry

Search `product-development/feature-index.yaml` under the given product area for an existing feature with this name or a close match. If found, tell the user and offer to edit the existing PRD instead of creating a new one.

## Step 3: Gather Content

For each of the seven sections defined in `product-development/product/PRDs/CLAUDE.md` ("PRD Template Sections"), ask the user for the relevant content, or draft it from context already available (feature-index entries, customer call summaries under `product-development/product/customers/accounts/`, competitive research) and confirm with the user before finalizing:

1. **Overview** - Problem statement, goals, success metrics (cite `reference/metrics.md` for any metric target referenced)
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes (link the Figma file if one exists)
5. **Technical Considerations** - Architecture, dependencies; link the related RFC if one exists or is planned
6. **Launch Plan** - Rollout strategy, feature flags
7. **Sources** - Every `INS-###`, `SRC-###`, or file path already cited in sections 1-6 above, listed once each as its own bullet. Use the same citation format as `templates/opportunity.md`'s "Evidence" section; write a file-path citation as a Markdown link (`[label](relative/path)`) rather than a bare backtick reference. If a claim in sections 1-6 has no citable source, leave it as uncited prose rather than inventing a citation here.

## Step 4: Write the PRD

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

`**Status**` starts at `Draft` per `reference/status-definitions.md` and should be updated as the PRD progresses.

Write the file to `product-development/product/PRDs/{product-area}/{feature-name}-prd.md`, following the naming convention in `product-development/product/PRDs/CLAUDE.md`.

Include all seven section headers (`## Overview` through `## Sources`) in the order defined in `product-development/product/PRDs/CLAUDE.md`, each followed by real content.

## Step 5: Update the Feature Index

Add or update the entry in `product-development/feature-index.yaml` under the correct product area, setting the `prd` key to the new file's path (relative to `product-development/`).

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
