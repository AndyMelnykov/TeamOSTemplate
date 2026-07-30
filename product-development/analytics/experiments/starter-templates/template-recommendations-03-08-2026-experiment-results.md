# Experiment: Personalized Template Recommendations vs Category Browse

**Author:** Casey Nguyen, Analytics
**Date:** 2026-03-08
**Linear / Jira / Asana Ticket:** EXAMPLE_PRODUCT-1035
**Status:** Complete
**Decision:** Ship

## TL;DR

Personalized template recommendations increased the fork rate by **27%** compared to the default category browse experience. Users who saw recommended templates were also more likely to deploy their forked project (44% vs 39% fork-to-deploy conversion). We recommend shipping the recommendations experience to all users.

## Hypothesis

If we show users personalized template recommendations based on their project history and category preferences (instead of the default category browse grid), then the fork rate will increase because users will find relevant templates faster and with less browsing friction.

## Experiment Design

| Parameter | Value |
|-----------|-------|
| **Feature flag** | `marketplace-recommendations` |
| **Start date** | 2026-02-15 |
| **End date** | 2026-03-07 |
| **Duration** | 21 days |
| **Platform** | Web only |
| **Eligible users** | All users who visited the marketplace at least once and had at least one existing project (needed for recommendation signal) |
| **Allocation** | 50/50 random split at user level |
| **Control (A)** | Default marketplace browse: category sidebar + grid sorted by "Popular" |
| **Treatment (B)** | Personalized recommendations: "Recommended for You" row at top of marketplace, followed by category browse below |

### Recommendation Algorithm (Treatment)

The "Recommended for You" row displays up to 8 templates selected by:

1. Matching the category of the user's most recent project (weight: 0.4)
2. Matching categories the user has previously forked from (weight: 0.3)
3. High-rated templates in the user's most-viewed categories (weight: 0.2)
4. Trending templates with high fork velocity in the last 7 days (weight: 0.1)

Templates the user has already forked are excluded.

## Results

### Primary Metric: Fork Rate

| Variant | Users | Marketplace Views | Forks | Fork Rate (forks/views) |
|---------|-------|-------------------|-------|--------------------------|
| Control (A) | 2,341 | 8,712 | 396 | **4.54%** |
| Treatment (B) | 2,387 | 8,894 | 514 | **5.78%** |

**Lift: +27.3%** (95% CI: +18.1% to +37.2%)
**p-value: < 0.001**
**Significant: Yes**

### Secondary Metrics

| Metric | Control (A) | Treatment (B) | Lift | p-value |
|--------|-------------|---------------|------|---------|
| Template detail view rate | 22.4% | 28.1% | +25.4% | < 0.001 |
| Fork-to-deploy conversion | 39.1% | 44.0% | +12.5% | 0.031 |
| Avg templates viewed before fork | 4.7 | 3.2 | -31.9% | < 0.001 |
| Time on marketplace page (median) | 2m 18s | 1m 42s | -26.1% | < 0.001 |
| Return visit rate (7d) | 31.2% | 34.8% | +11.5% | 0.047 |

### Interpretation

- **Fork rate increased by 27%.** This is the headline result. Users who see recommendations fork templates at a significantly higher rate.
- **Users find templates faster.** The average number of templates viewed before forking dropped from 4.7 to 3.2, and median time on the marketplace page decreased by 26%. This indicates that recommendations surface relevant templates more efficiently.
- **Fork-to-deploy conversion also improved.** Users in the treatment group not only forked more, but the templates they forked were more likely to be deployed (44% vs 39%). This suggests that recommendations match users with templates they actually intend to use, not just templates they click on out of curiosity.
- **Return visits increased.** Users who saw recommendations were 11.5% more likely to return to the marketplace within 7 days, suggesting a better overall experience.

### Guardrail Metrics

| Metric | Control (A) | Treatment (B) | Status |
|--------|-------------|---------------|--------|
| Marketplace page load time (p95) | 1.8s | 2.1s | Within threshold (< 3s) |
| Fork error rate | 0.5% | 0.6% | Flat |
| Template report rate | 0.3% | 0.3% | Flat |

The recommendation algorithm adds ~300ms to page load (the recommendation query runs server-side). This is within acceptable bounds but should be optimized before full rollout. No negative impact on error rates or abuse metrics.

## Segmentation

| Segment | Control Fork Rate | Treatment Fork Rate | Lift |
|---------|-------------------|---------------------|------|
| Free tier | 3.8% | 5.1% | +34.2% |
| Pro tier | 5.2% | 6.4% | +23.1% |
| Teams tier | 6.1% | 7.3% | +19.7% |
| New users (< 7 days) | 3.1% | 4.5% | +45.2% |
| Returning users (7+ days) | 5.4% | 6.5% | +20.4% |

Recommendations have the strongest effect on new users and free-tier users, who benefit most from guided discovery. This is a strong signal for improving activation.

## Decision

**Ship the personalized recommendations experience to all users.**

Rationale:
1. The 27% fork rate lift is well above the minimum detectable effect (10%) we set before the experiment.
2. Fork-to-deploy conversion also improved, meaning the lift is not driven by low-quality forks.
3. The effect is positive across all segments, with especially strong impact on new users and free-tier users.
4. No guardrail metrics were breached.

## Follow-Up Actions

1. **Optimize recommendation query performance.** The 300ms added latency should be reduced by pre-computing recommendations and caching them with a 1-hour TTL.
2. **Iterate on the algorithm.** The current weights (0.4/0.3/0.2/0.1) were chosen based on intuition. Run a follow-up experiment to A/B test different weight configurations.
3. **Extend to email.** Test sending a weekly "Recommended Templates" email to users who have not visited the marketplace recently.
4. **Monitor long-term retention.** Track whether the fork rate lift translates to improved D30 retention for the treatment cohort.
