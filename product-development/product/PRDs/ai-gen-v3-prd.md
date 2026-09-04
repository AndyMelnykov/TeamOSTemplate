# AI Extraction v3 - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-18 |
| **Related RFC** | `engineering/rfcs/gen-v3-rfc.md` |

---

## Overview

AI Extraction v3 upgrades example_product's core document-extraction pipeline to the next-generation model, targeting a material lift in Extraction Success Rate (ESR) — see `reference/metrics.md` for the metric definition and current target (> 92%).

## Problem Statement

ESR has plateaued below target on multi-field extractions involving less common document formats and layouts (scanned PDFs with tables, multi-page contracts with inconsistent clause ordering). Support tickets and the `analytics/investigations/` history show extraction failures concentrated in these cases, directly suppressing Workflow Completion Rate (WCR).

## User Stories

- As a user processing a multi-page document, I want a higher first-try extraction success rate, so that I spend fewer refinements correcting misextracted fields.

## Requirements

- Migrate the extraction pipeline to the v3 model.
- Maintain document-type detection accuracy at or above the current baseline while improving ESR.
- Ship behind a gradual rollout so ESR can be monitored per cohort before full cutover.

## Design

No user-facing UI changes; this is a backend model upgrade. See `engineering/rfcs/gen-v3-rfc.md`.

## Technical Considerations

See `engineering/rfcs/gen-v3-rfc.md` and the `table-schemas` entry in `feature-index.yaml` (`prototyping.ai-generation-v3.table-schemas`) for the automation-run event schema this feature depends on.

## Launch Plan

Staged rollout by cohort, monitored against the ESR target in `reference/metrics.md`.
