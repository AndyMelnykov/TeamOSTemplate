# Bi-Weekly Update Workflow Spec

## Overview

This workflow produces a dated bi-weekly example_product update document. It runs interactively: each step has an automated part (data gathering, drafting) and an interactive part (the PM reviews, adds context, approves). Each section is written to the output file as it completes so progress is visible in real time. The final step auto-pushes the compiled document to a Google Doc via the Google Workspace MCP.

---

## Process Flow

```
1. Create dated output file
2. Step 1: Engineering Status     -> writes "What the Team Is Building Now" section
3. Step 2: Customer Call Synthesis -> writes "Customer Calls" section
4. Step 3: Customer Updates       -> writes pilot/launch status sections
5. Step 4: Push to Google Doc     -> auto-push via Google Workspace MCP
6. Step 5: Review & Finalization  -> PM reviews, edits, publishes
```

Each step reads its own instruction file (`step-1-eng-status.md`, etc.) for detailed process.

---

## What Changes Every Cycle vs. What's Stable

### Changes every cycle
- **Eng status:** Workstream statuses update based on Linear / Jira / Asana + PM's context dump
- **Customer calls section:** Completely rewritten each cycle based on last 2 weeks of calls
- **What We're Hearing / Highlights:** Completely rewritten based on new call data
- **Pilot/customer exec summaries:** Updated only if new call data changes the narrative

### Stable across cycles (carried forward, not rewritten)
- **OKR structure and goals:** Updated only when OKRs change (quarterly)
- **Customer deep dive background sections:** Only updated when materially new info emerges
- **Cross-customer summary:** Updated when shared gaps change or new customers are added
- **Table of Contents structure:** Updated when sections are added or removed

---

## Conventions

### Formatting
- Business-goal-led headings (not feature-led)
- Customer quotes: *"Quote text."* - Speaker Name
- No em dashes in body text
- No horizontal rules between sections
- Tables and bullets for scannable content; paragraphs for narrative

### Customer Categorization
Each customer in the call synthesis table gets one of these categories:
- **Paying customer** - signed and paying
- **Pilot** - active pilot, not yet paying
- **Pipeline** - in pipeline, being pitched
- **Free tier** - on free plan, potential upsell

### Date Ranges
- Each cycle covers exactly 2 weeks
- Date format for section headers: "Month DD - Month DD" (e.g., "Jan 28 - Feb 11")
- Date format for customer table: MM/DD (e.g., 02/10)

---

## Handling Special Cases

### New customers (first call)
- Add to customer table with appropriate category
- If they become a pilot, create a new pilot section with exec summary and deep dive
- Ask PM: "Should we add a pilot section for [customer]?"

### New pilots
- Create exec summary and deep dive following existing pilot format
- Add to cross-customer summary if they share gaps with existing pilots
- Add to Table of Contents

### Ad-hoc requests
Sometimes the bi-weekly includes one-off content (competitive analysis, strategic memos, etc.). These are handled inline during Step 5 (Review) when the PM can request additions.

### Removing stale content
If a customer hasn't been discussed in 2+ cycles, ask PM: "Should we keep [customer] pilot section, or archive it?"

---

## File Naming

- Output files: `YYYY-MM-DD.md` (date of the bi-weekly meeting)
- Location: `product/meetings/team-bi-weekly/docs/YYYY-MM-DD.md`

---

## Google Doc Auto-Push

Step 4 automatically pushes the compiled update to a Google Doc using the Google Workspace MCP (`mcp__google_workspace__*` tools). This eliminates manual copy-paste and ensures the shared doc is always in sync with the source markdown. See `step-4-push-to-gdoc.md` for details.

---

## Reference

See `reference/2026-02-11.md` for the canonical example of what good output looks like. This was the first bi-weekly produced with this workflow and covers:
- OKR tables with workstream status
- 5 customer calls synthesized with thematic analysis
- Cross-customer summary for Meridian and CloudKitchen
- Full exec summaries and deep dives for active pilots
