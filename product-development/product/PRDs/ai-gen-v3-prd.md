# AI Generation v3 - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-18 |
| **Related RFC** | `engineering/rfcs/gen-v3-rfc.md` |

---

## Overview

AI Generation v3 upgrades example_product's core code-generation pipeline to the next-generation model, targeting a material lift in Generation Success Rate (GSR) — see `reference/metrics.md` for the metric definition and current target (> 92%).

## Problem Statement

GSR has plateaued below target on multi-file generations involving less common framework combinations. Support tickets and the `analytics/investigations/` history show generation failures concentrated in these cases, directly suppressing Project Completion Rate (PCR).

## User Stories

- As a user generating a multi-file app, I want a higher first-try success rate, so that I spend fewer iterations recovering from broken generations.

## Requirements

- Migrate the generation pipeline to the v3 model.
- Maintain framework-detection accuracy at or above the current baseline while improving GSR.
- Ship behind a gradual rollout so GSR can be monitored per cohort before full cutover.

## Design

No user-facing UI changes; this is a backend model upgrade. See `engineering/rfcs/gen-v3-rfc.md`.

## Technical Considerations

See `engineering/rfcs/gen-v3-rfc.md` and the `table-schemas` entry in `feature-index.yaml` (`prototyping.ai-generation-v3.table-schemas`) for the generation-event schema this feature depends on.

## Launch Plan

Staged rollout by cohort, monitored against the GSR target in `reference/metrics.md`.
