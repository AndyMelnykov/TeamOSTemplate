# AI Extraction v3 - Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Riley Patel (Engineer) |
| **Status** | Draft |
| **Last Updated** | 2026-03-18 |
| **Related PRD** | `product/PRDs/ai-gen-v3-prd.md` |

---

## Summary

Migrates the extraction pipeline to the v3 model to improve Extraction Success Rate (ESR) on multi-page, mixed-document-type automation runs.

## Motivation

See `product/PRDs/ai-gen-v3-prd.md` — ESR is below target specifically on less-common document combinations (e.g., scanned purchase orders mixed with native-PDF invoices in the same automation run).

## Proposed Design

- Stand up the v3 extraction model behind the existing extraction-service interface so no downstream caller changes.
- Log automation run outcomes to the `project-generations` table (`analytics/schemas/prototyping/project-generations.md`) with a model-version column so v2 vs v3 ESR can be compared per cohort.
- Roll out by percentage cohort, gated on ESR staying at or above the v2 baseline at each step.

## Alternatives Considered

- Full cutover without a staged rollout: rejected — insufficient signal to catch a regression before it affects all users.

## Rollout Plan

5% -> 25% -> 100% cohort rollout, each stage gated on ESR (`reference/metrics.md`) staying at or above baseline for 3 consecutive days.
