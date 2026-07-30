# Investigation: Do Users Who Hit 0 Credits Churn More?

| Field | Value |
|-------|-------|
| **Author** | Casey Nguyen (Analytics) |
| **Date** | 2026-03-10 |
| **Linear / Jira / Asana Ticket** | EXAMPLE_PRODUCT-1030 |
| **Status** | Complete |

---

## Question

Is there a statistically significant relationship between credit depletion (reaching a zero credit balance before cycle reset) and user churn? If so, how large is the effect, and does it vary by subscription tier?

## Background

The billing support queue has been dominated by complaints from users who were surprised by hitting their credit limit. PM hypothesized that this surprise depletion experience is a meaningful driver of churn, but we had not previously quantified the relationship. This investigation was requested to put hard numbers behind the hypothesis and inform the priority of the Credit Usage Dashboard feature (EXAMPLE_PRODUCT-1028).

## Methodology

**Cohort definition**: All users with at least one complete billing cycle between January 1, 2026 and February 28, 2026 (N = 14,832).

**Treatment group**: Users whose `balance_after` reached 0 at any point during the billing cycle (i.e., at least one row in `credit_transactions` where `balance_after = 0` and `type = 'debit'`). N = 1,987 (13.4% of the cohort).

**Control group**: Users who completed the billing cycle without reaching 0. N = 12,845.

**Churn definition**: User did not perform any credit-consuming action (generation, edit, or deploy) in the 14 days following their billing cycle reset date AND did not renew their subscription.

**Statistical method**: Chi-squared test for independence, with Bonferroni correction for tier-level subgroup analysis. Effect size measured using relative risk (RR).

## Findings

### Overall

| Metric | Depleted (N=1,987) | Not Depleted (N=12,845) | Relative Risk |
|--------|-------------------|------------------------|---------------|
| 14-day churn rate | 18.2% | 5.7% | **3.19x** |
| p-value | -- | -- | < 0.001 |

**Users who deplete their credits are 3.2x more likely to churn within 14 days than users who do not.**

### By Subscription Tier

| Tier | Depleted Churn Rate | Non-Depleted Churn Rate | Relative Risk | p-value |
|------|-------------------|------------------------|---------------|---------|
| Free | 24.1% | 9.8% | 2.46x | < 0.001 |
| Pro | 15.6% | 4.2% | 3.71x | < 0.001 |
| Team | 10.3% | 3.1% | 3.32x | < 0.01 |

The effect is most pronounced for Pro users, who represent the highest revenue-per-user tier affected. Free users have a higher absolute churn rate in both groups but a lower relative risk, likely because Free users have higher baseline churn regardless of credit usage.

### Time-to-Churn Analysis

Among users who depleted and subsequently churned, the median time from depletion to last activity was **3 days**. This suggests the churn decision happens quickly after the depletion event, reinforcing the importance of pre-depletion warnings rather than post-depletion recovery.

| Days from Depletion to Last Activity | % of Churned Users |
|---------------------------------------|-------------------|
| 0 (same day) | 28% |
| 1-3 days | 35% |
| 4-7 days | 22% |
| 8-14 days | 15% |

### Confounding Factors Considered

- **Usage intensity**: Heavy users are both more likely to deplete and more likely to churn from frustration. We controlled for this by segmenting by usage quartile and found the depletion-churn relationship holds across all quartiles (RR range: 2.4x - 3.8x).
- **Account age**: Newer users might deplete more and churn more. Controlling for cohort month did not meaningfully change the result.
- **Plan fit**: Some users may be on plans that are too small for their usage. This is real, but it is also the mechanism we want to address -- helping users see their usage so they can right-size their plan.

## Recommendations

Based on these findings:

1. **Ship low-balance warnings**: A warning at <20% remaining credits would reach users a median of 5 days before depletion, well within the window where intervention can change behavior. This is the strongest lever we have to reduce surprise depletion.

2. **Implement a grace period**: Rather than a hard stop at 0 credits, allow users to continue with degraded functionality (e.g., lower-quality generations or rate-limited access) for 24-48 hours while they decide whether to upgrade. This converts the "cliff" experience into a "ramp" that preserves the user relationship.

3. **Build the usage dashboard**: Proactive visibility into credit consumption will reduce the number of users who reach depletion in the first place. Users who understand their burn rate can pace usage or upgrade before hitting zero.

4. **Prioritize Pro tier interventions**: The 3.71x relative risk among Pro users, combined with their higher revenue contribution, makes this the highest-ROI segment to target first.

## Data Sources

- `analytics.example_product.credit_transactions` -- credit depletion events
- `analytics.example_product.dim_users` -- subscription tier, account age, churn status
- `analytics.stripe.subscriptions` -- renewal and cancellation events

## Related

- PRD: `product/PRDs/billing/credit-usage-dashboard-prd.md`
- Experiment: `product/analytics/experiments/billing/low-balance-warning-03-05-2026-experiment-results.md`

---

## Related Resources

| Resource | Path |
|----------|------|
| Metrics definition | [credit-usage-metrics.md](../../metrics/billing/credit-usage-metrics.md) |
| SQL query | [credit-burn-rate.sql](../../queries/billing/credit-burn-rate.sql) |
| Schema | [credit_transactions.md](../../schemas/billing/credit_transactions.md) |
