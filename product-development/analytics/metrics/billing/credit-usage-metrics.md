# Credit Usage Metrics

| Field | Value |
|-------|-------|
| **Owner** | Hannah Stulberg (PM) |
| **Analytics Lead** | Casey Nguyen |
| **Last Updated** | 2026-03-22 |

---

## Primary Metrics

### Credit Utilization Rate

**Definition**: Percentage of allocated credits used within a billing cycle.

```
credit_utilization_rate = (total_credits_debited_in_cycle / cycle_credit_allocation) * 100
```

**Segmentation**: Calculated per user and aggregated by subscription tier (Free, Pro, Team, Business, Enterprise).

**Target**: This is a tracking metric rather than an optimization target. The goal is to understand distribution:
- Users below 30% utilization may be over-provisioned (downgrade risk or engagement problem).
- Users above 80% utilization are candidates for proactive upgrade outreach.
- Users at 100% who did not upgrade are the highest churn risk.

**Current distribution (March 2026)**:
| Tier | Median Utilization | % Users >80% | % Users at 100% |
|------|-------------------|---------------|-----------------|
| Free | 72% | 38% | 22% |
| Pro | 61% | 24% | 11% |
| Team | 54% | 18% | 7% |

**Refresh cadence**: Daily, computed in the `dbt_billing.credit_utilization` model.

---

### Credit-to-Upgrade Rate

**Definition**: Percentage of users who upgrade their subscription within 7 days of their credit balance dropping below 20% of their cycle allocation.

```
credit_to_upgrade_rate = (users_who_upgraded_within_7d_of_low_balance / users_who_hit_low_balance) * 100
```

**Target**: >12% (current baseline: 8%).

**Rationale**: This metric directly measures whether credit usage visibility translates into self-serve upgrades. The 7-day window accounts for the typical decision-making period observed in user behavior data. The 20% threshold aligns with the low-balance warning banner trigger.

**Refresh cadence**: Weekly, computed in the `dbt_billing.credit_upgrade_funnel` model.

---

## Secondary Metrics

### Average Credits per Generation

**Definition**: Mean number of credits consumed per generation event, segmented by generation type (text-to-UI, image-to-UI, iteration).

```
avg_credits_per_generation = SUM(amount) / COUNT(DISTINCT reference_id)
WHERE category = 'generation' AND type = 'debit'
```

**Current values (March 2026)**:
| Generation Type | Avg Credits |
|----------------|-------------|
| Text-to-UI | 12.4 |
| Image-to-UI | 18.7 |
| Iteration | 6.2 |

**Use case**: Informs credit pricing decisions and helps users understand relative costs across generation types.

---

### Credit Depletion Rate by Tier

**Definition**: Percentage of users who reach 0 credits before their billing cycle resets, segmented by subscription tier.

```
depletion_rate = (users_reaching_zero_balance / total_users_in_tier) * 100
```

**Current values (March 2026)**:
| Tier | Depletion Rate |
|------|---------------|
| Free | 22% |
| Pro | 11% |
| Team | 7% |
| Business | 3% |

**Target**: Reduce Free and Pro depletion rates by 30% relative through proactive warnings (not by increasing allocations).

---

### Refund Rate

**Definition**: Percentage of total credit debits that are subsequently refunded within the same billing cycle.

```
refund_rate = (SUM(amount WHERE category = 'refund') / SUM(amount WHERE type = 'debit')) * 100
```

**Current value**: 2.1% (March 2026).

**Target**: <3%. A refund rate above 3% may indicate generation quality issues driving user dissatisfaction and manual refund requests.

---

## Data Sources

| Source | Table / System | Sync Frequency | Notes |
|--------|---------------|----------------|-------|
| Credit transactions | `analytics.example_product.credit_transactions` | 15 min (Fivetran) | Primary ledger. See schema doc. |
| User profiles | `analytics.example_product.dim_users` | 15 min (Fivetran) | Current tier, signup date, email. |
| Subscription plans | `analytics.example_product.dim_subscription_plans` | Daily (dbt seed) | Credit allocations per tier. |
| Stripe events | `analytics.stripe.charges` | 1 hour (Fivetran) | Revenue tie-out and upgrade event detection. |
| Generation events | `analytics.example_product.fact_generations` | 15 min (Fivetran) | Generation type and metadata for per-type credit analysis. |

## Dashboard Links

| Dashboard | Platform | Link |
|-----------|----------|------|
| Credit Usage Health | Sigma | [Credit Usage Health Dashboard](https://app.sigmacomputing.com/example_product/workbook/credit-usage-health) |
| Credit Utilization by Tier | Sigma | [Utilization by Tier](https://app.sigmacomputing.com/example_product/workbook/credit-utilization-tier) |
| Billing Experiments | Amplitude | [Billing Experiments](https://app.amplitude.com/example_product/dashboard/billing-experiments) |
| Revenue Impact | Stripe | [Stripe Billing Dashboard](https://dashboard.stripe.com/billing) |

## Related Queries

| Query | Description |
|-------|-------------|
| [credit-burn-rate.sql](../../queries/billing/credit-burn-rate.sql) | Credit burn rate by tier with depletion projections |

## Related Investigations

| Investigation | Date | Summary |
|--------------|------|---------|
| [2026-03-10-credit-depletion-churn-analysis.md](../../investigations/billing/2026-03-10-credit-depletion-churn-analysis.md) | 2026-03-10 | Credit depletion as churn predictor |
