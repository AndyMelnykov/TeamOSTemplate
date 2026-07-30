# Experiment: Version History Onboarding Tooltip

**Author:** Casey Nguyen, Analytics
**Date:** 2026-03-12
**Linear / Jira / Asana:** EXAMPLE_PRODUCT-1052
**Status:** Complete
**Decision:** Ship

## TL;DR

Showing a tooltip highlighting the version history panel after a user's first AI generation increased version history adoption by 34% compared to no tooltip. The tooltip group had significantly higher panel open rates, first-week restore usage, and no negative impact on generation flow. Decision: ship the tooltip to all users at GA launch.

## Hypothesis

Users are not discovering the version history panel because it is tucked into the editor toolbar with no onboarding affordance. A contextual tooltip shown after the first generation ("Your project version has been saved. Browse version history here.") will increase awareness and drive higher adoption of version history features.

## Setup

| Parameter | Value |
|-----------|-------|
| Experiment type | A/B test |
| Platform | example_product web app |
| Audience | New example_product Pro and Teams users during beta period |
| Allocation | 50/50 random assignment at user level |
| Duration | 2026-03-03 to 2026-03-11 (8 days) |
| Sample size | 1,847 users (924 control, 923 treatment) |
| Feature flag | `version_history_onboarding_tooltip` |

**Control (A):** No tooltip. Version history panel is available in the editor toolbar but no onboarding prompt is shown.

**Treatment (B):** After the user's first successful AI generation, a tooltip appears pointing to the version history icon in the toolbar. Tooltip text: "Your project version has been saved. You can browse and restore previous versions anytime." Tooltip auto-dismisses after 8 seconds or on click.

## Primary Metric

| Metric | Control (A) | Treatment (B) | Lift | p-value | Significant? |
|--------|-------------|---------------|------|---------|--------------|
| Version history panel open rate (7-day) | 18.2% | 24.4% | **+34.1%** | 0.0003 | Yes |

## Secondary Metrics

| Metric | Control (A) | Treatment (B) | Lift | p-value | Significant? |
|--------|-------------|---------------|------|---------|--------------|
| First-session panel open rate | 9.1% | 17.8% | +95.6% | < 0.0001 | Yes |
| Diff view usage (7-day) | 7.3% | 10.1% | +38.4% | 0.02 | Yes |
| At least one restore (7-day) | 5.8% | 8.2% | +41.4% | 0.03 | Yes |
| Time to first panel open (median) | 4.2 days | 0.8 days | -81.0% | < 0.0001 | Yes |
| Generation completion rate | 94.1% | 93.8% | -0.3% | 0.78 | No |
| Avg generations per user (7-day) | 12.4 | 12.7 | +2.4% | 0.51 | No |

## Guardrail Metrics

| Metric | Control (A) | Treatment (B) | Status |
|--------|-------------|---------------|--------|
| Generation completion rate | 94.1% | 93.8% | No degradation |
| Time-to-first-generation | 32s | 33s | No degradation |
| Tooltip dismissal frustration (rapid close < 1s) | N/A | 4.2% | Acceptable |

## Analysis

The tooltip drove a statistically significant 34% lift in the primary metric (7-day panel open rate), from 18.2% to 24.4%. The effect was strongest in the first session, where the panel open rate nearly doubled (9.1% to 17.8%), confirming that the tooltip successfully addressed the discoverability problem.

Downstream engagement also improved: users in the treatment group were 41% more likely to restore a version within their first week, and 38% more likely to use the diff viewer. This suggests the tooltip not only drove awareness but also meaningful feature engagement.

Critically, there was no negative impact on the generation flow. Generation completion rate and average generations per user were statistically indistinguishable between groups. The tooltip did not interrupt or distract users from their primary workflow.

The tooltip dismissal rate within 1 second (a proxy for user annoyance) was 4.2%, which is well below our 10% threshold for tooltip fatigue.

## Segmentation

| Segment | Control open rate | Treatment open rate | Lift |
|---------|-------------------|---------------------|------|
| Free trial users | 14.6% | 20.1% | +37.7% |
| Pro users | 20.8% | 27.2% | +30.8% |
| Teams users | 22.1% | 28.9% | +30.8% |
| Users with 1-3 generations | 11.2% | 18.4% | +64.3% |
| Users with 4+ generations | 23.7% | 29.1% | +22.8% |

The tooltip had the largest relative effect on low-generation users (1-3 generations), who are least likely to discover the panel organically. This is the exact population we most want to reach: users who might abandon after a bad generation because they do not know version history exists.

## Decision

**Ship the tooltip to all users at GA launch.**

The 34% adoption lift with zero negative impact on core workflows makes this a clear win. The tooltip will be included in the default GA experience (no opt-in required) and will trigger once per user after their first successful generation.

## Follow-Up

- Monitor tooltip fatigue over 30 days post-GA. If dismissal rates rise above 10%, revisit the trigger timing.
- Test a variant with a more prominent coach mark (animated highlight) for users who do not open the panel within 3 days.
- Evaluate whether a second tooltip after the first "bad generation" (generation followed by no activity for 2 minutes) could further boost restore usage.
