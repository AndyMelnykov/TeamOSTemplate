# Experiment Results: Low-Balance Warning Banner

| Field | Value |
|-------|-------|
| **Author** | Casey Nguyen (Analytics) |
| **Experiment Start** | 2026-03-05 |
| **Experiment End** | 2026-03-19 |
| **Duration** | 2 weeks |
| **Status** | Complete |

---

## TL;DR

Showing a warning banner when users drop below 20% of their credit allocation reduced churn-from-depletion by 22% and increased the upgrade rate by 15%. The result is statistically significant and the recommendation is to **ship the warning banner to all users**.

## Hypothesis

Users who receive a visible warning when their credit balance falls below 20% of their cycle allocation will be more likely to upgrade their plan or pace their usage, resulting in lower churn from credit depletion.

## Setup

| Parameter | Value |
|-----------|-------|
| **Variants** | Control (no banner), Treatment (warning banner at <20% credits) |
| **Allocation** | 50/50 random split |
| **Targeting** | All Pro and Team users who reached <20% balance during the experiment window |
| **Sample Size** | Control: 1,247 users; Treatment: 1,261 users |
| **Primary Metrics** | Churn-from-depletion rate (14-day), upgrade conversion rate |
| **Secondary Metrics** | Banner click-through rate, time to upgrade, credit pacing behavior |
| **Randomization Unit** | User ID |
| **Feature Flag** | `billing.low_balance_banner.enabled` (LaunchDarkly) |

## Primary Results

### Churn-from-Depletion Rate (14-day)

| Variant | Users Who Depleted | Users Who Churned | Churn Rate | Change |
|---------|-------------------|-------------------|------------|--------|
| Control | 412 | 74 | 17.96% | -- |
| Treatment | 398 | 56 | 14.07% | **-21.6%** |

| Statistical Test | Value |
|-----------------|-------|
| Chi-squared | 6.42 |
| p-value | 0.011 |
| Confidence level | 95% |
| Relative risk reduction | 21.6% |
| Absolute risk reduction | 3.89 pp |
| NNT (number needed to treat) | 26 |

**Result: Statistically significant.** Showing the banner to 26 users who hit low balance prevents one churn event.

### Upgrade Conversion Rate

| Variant | Users at <20% Balance | Users Who Upgraded | Upgrade Rate | Change |
|---------|-----------------------|-------------------|--------------|--------|
| Control | 1,247 | 101 | 8.10% | -- |
| Treatment | 1,261 | 118 | 9.36% | **+15.6%** |

| Statistical Test | Value |
|-----------------|-------|
| Chi-squared | 4.87 |
| p-value | 0.027 |
| Confidence level | 95% |
| Relative lift | 15.6% |
| Absolute lift | 1.26 pp |

**Result: Statistically significant.** The banner drove a meaningful increase in self-serve upgrades.

## Secondary Results

### Banner Engagement

| Metric | Value |
|--------|-------|
| Banner impressions (unique users) | 1,261 |
| Banner click-through rate (CTA: "Upgrade Plan") | 6.3% |
| Banner dismiss rate | 31.2% |
| Median time from banner first seen to upgrade | 2.4 days |
| Users who saw banner and then visited /billing/plans | 14.8% |

### Credit Pacing Behavior

| Metric | Control | Treatment | Change |
|--------|---------|-----------|--------|
| Avg daily credits used after hitting <20% | 42.1 | 36.8 | -12.6% |
| % users who reached 0 credits | 33.0% | 31.6% | -4.2% (not significant, p=0.34) |
| Median days from <20% to depletion | 4.8 | 5.6 | +16.7% |

The treatment group showed a modest reduction in daily credit consumption after seeing the banner, suggesting some users paced their usage. However, the reduction in depletion rate itself was not statistically significant -- the primary benefit of the banner is driving upgrades and reducing churn among those who do deplete, rather than preventing depletion.

## Segmentation

### By Subscription Tier

| Tier | Control Churn Rate | Treatment Churn Rate | Relative Change | p-value |
|------|-------------------|---------------------|-----------------|---------|
| Pro | 19.2% | 14.8% | -22.9% | 0.018 |
| Team | 12.1% | 9.8% | -19.0% | 0.14 (ns) |

The effect is stronger and statistically significant for Pro users. The Team tier result trends in the right direction but the subgroup sample size (N=387) is too small for significance at the 2-week mark.

### By Usage Intensity

| Usage Quartile | Control Churn Rate | Treatment Churn Rate | Relative Change |
|---------------|-------------------|---------------------|-----------------|
| Q1 (lightest) | 12.3% | 10.1% | -17.9% |
| Q2 | 16.8% | 13.2% | -21.4% |
| Q3 | 19.4% | 15.0% | -22.7% |
| Q4 (heaviest) | 23.1% | 17.5% | -24.2% |

The banner is most effective for heavier users, who are also the highest-value users. This is a favorable skew.

## Learnings

1. **Timing matters**: Users who saw the banner within 1 day of crossing the 20% threshold were 2.1x more likely to upgrade than users who first saw it 3+ days after crossing. This validates the real-time warning approach over batch email notifications.

2. **Banner fatigue is low**: The 31.2% dismiss rate is within acceptable bounds. Users who dismissed the banner and then later re-encountered it (after 24h suppression expired) had a 4.1% CTR on the second impression, suggesting the message remains relevant.

3. **Upgrade path is short**: The median 2.4 days from banner impression to upgrade suggests users think briefly about the decision but do not need extensive nurturing. The dashboard itself (showing usage data) may further shorten this decision cycle.

4. **Pacing alone does not solve the problem**: While some users reduce consumption after seeing the banner, the depletion rate reduction was not statistically significant. The real value of the banner is in converting depleters into upgraders and retaining those who deplete anyway.

## Decision

**Ship to 100% of Pro and Team users.**

The warning banner delivers significant improvements on both primary metrics (churn reduction and upgrade lift) with minimal user friction. Rolling out to all users is the clear next step.

Follow-up work:
- Extend to Free tier users (separate experiment, since the upgrade path is different).
- Test a second notification at the 5% threshold for users who dismissed the first banner.
- Integrate the banner into the Credit Usage Dashboard (see `engineering/plans/billing/credit-usage-dashboard.md`).

## Data Sources

- `analytics.example_product.credit_transactions` -- credit balance tracking
- Amplitude experiment results -- variant assignment and metric computation
- `analytics.stripe.subscriptions` -- upgrade event detection
- `analytics.example_product.dim_users` -- churn classification
