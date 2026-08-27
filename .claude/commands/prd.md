# PRD Writing

You are an expert at writing example_product Product Requirement Documents.

## Task Overview

Create a new PRD by:
1. Confirming the feature name and product area
2. Checking `product-development/feature-index.yaml` for an existing entry (do not create a duplicate PRD for a feature that already has one)
3. Gathering the required content for each template section
4. Writing the PRD file with the correct name and location
5. Updating `product-development/feature-index.yaml` with the new PRD's path

## Step 1: Confirm Feature Name and Product Area

Ask the user for the feature name and which product area it belongs to (`home-page`, `billing`, `prototyping`, `starter-templates`, or `deployment` — see `product-development/feature-index.yaml` for the current set).

## Step 2: Check for an Existing Entry

Search `product-development/feature-index.yaml` under the given product area for an existing feature with this name or a close match. If found, tell the user and offer to edit the existing PRD instead of creating a new one.

## Step 3: Gather Content

For each of the six sections defined in `product-development/product/PRDs/CLAUDE.md` ("PRD Template Sections"), ask the user for the relevant content, or draft it from context already available (feature-index entries, customer call summaries under `product-development/product/customers/accounts/`, competitive research) and confirm with the user before finalizing:

1. **Overview** - Problem statement, goals, success metrics (cite `reference/metrics.md` for any metric target referenced)
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes (link the Figma file if one exists)
5. **Technical Considerations** - Architecture, dependencies; link the related RFC if one exists or is planned
6. **Launch Plan** - Rollout strategy, feature flags

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

## Step 5: Update the Feature Index

Add or update the entry in `product-development/feature-index.yaml` under the correct product area, setting the `prd` key to the new file's path (relative to `product-development/`).
