# Bi-Weekly Update Workflow

## Purpose

Automated workflow that generates the bi-weekly product review document for example_product. This runs before each bi-weekly review meeting and compiles progress, metrics, and next steps into a presentation-ready format.

## What This Workflow Does

1. **Compiles metrics** - Pulls key product health and adoption metrics from the business review
4. **Generates the update doc** - Writes a structured bi-weekly review document to `product/meetings/team-bi-weekly/docs/`

## Steps Overview

1. Summarize key metrics and trends
5. Flag blockers or items needing discussion
6. Write the output doc with the standard template

## Output Format

The generated doc follows this structure:

```
# example_product Bi-Weekly Review - [Date]

## Highlights
- Top 3-5 accomplishments from the last two weeks

## Workstream Updates
- Table of active workstreams with status, progress notes, and next steps

## Launches
- Features shipped since last review

## Metrics Snapshot
- Key product health numbers

## Discussion Items
- Blockers, decisions needed, or topics for group discussion

## Next Two Weeks
- P0 priorities for the upcoming sprint
```

## File Naming

Output files follow the convention: `YYYY-MM-DD-example_product-bi-weekly-review.md`
