# AI Generation v3 - Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Riley Patel (Engineer) |
| **Status** | Draft |
| **Last Updated** | 2026-03-18 |
| **Related PRD** | `product/PRDs/ai-gen-v3-prd.md` |

---

## Summary

Migrates the generation pipeline to the v3 model to improve Generation Success Rate (GSR) on multi-file, mixed-framework generations.

## Motivation

See `product/PRDs/ai-gen-v3-prd.md` — GSR is below target specifically on less-common framework combinations.

## Proposed Design

- Stand up the v3 model behind the existing generation-service interface so no downstream caller changes.
- Log generation outcomes to the `project-generations` table (`analytics/schemas/prototyping/project-generations.md`) with a model-version column so v2 vs v3 GSR can be compared per cohort.
- Roll out by percentage cohort, gated on GSR staying at or above the v2 baseline at each step.

## Alternatives Considered

- Full cutover without a staged rollout: rejected — insufficient signal to catch a regression before it affects all users.

## Rollout Plan

5% -> 25% -> 100% cohort rollout, each stage gated on GSR (`reference/metrics.md`) staying at or above baseline for 3 consecutive days.
