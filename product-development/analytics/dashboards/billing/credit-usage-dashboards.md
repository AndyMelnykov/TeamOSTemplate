# Credit Usage Dashboards

| Field | Value |
|-------|-------|
| **Owner** | Hannah Stulberg (PM) |
| **Analytics Lead** | Casey Nguyen |
| **Last Updated** | 2026-03-22 |

---

## Dashboard Index

### Credit Usage Health (Sigma)

**Link**: [Credit Usage Health Dashboard](https://app.sigmacomputing.com/example_product/workbook/credit-usage-health)

**Purpose**: Primary operational dashboard for monitoring credit consumption patterns across the example_product user base. Used by PM and analytics to track utilization rates, identify users at risk of depletion, and validate the impact of billing features.

**Key views**:
- Daily credit consumption by category (generation, edit, deploy) -- stacked area chart
- Credit utilization distribution by subscription tier -- histogram
- Users approaching depletion (<20% balance) -- filterable table with projected depletion date
- Burn rate trends -- 7-day rolling average, segmented by tier
- Refund volume and rate -- daily trend line

**Refresh**: Every 15 minutes (aligned with Fivetran sync cadence).

**Filters**: Date range, subscription tier, category, org (for team plans).

---

### Billing Experiments (Amplitude)

**Link**: [Billing Experiments Dashboard](https://app.amplitude.com/example_product/dashboard/billing-experiments)

**Purpose**: Tracks active and completed experiments related to billing features. Used to monitor experiment health (sample size, statistical significance) and measure impact on conversion and retention metrics.

**Key views**:
- Active experiments with variant allocation and sample sizes
- Low-balance warning banner experiment: churn-from-depletion rate by variant
- Low-balance warning banner experiment: upgrade conversion rate by variant
- Funnel: credit depletion -> warning seen -> upgrade page visited -> upgrade completed
- Retention curves by experiment variant (7d, 14d, 30d)

**Refresh**: Hourly.

**Filters**: Experiment name, date range, subscription tier, platform (web/mobile).

---

### Revenue Impact (Stripe Dashboard)

**Link**: [Stripe Billing Dashboard](https://dashboard.stripe.com/billing)

**Purpose**: Source-of-truth for revenue metrics tied to billing changes. Used by PM, finance, and leadership to track the dollar impact of credit-related features on MRR, upgrade volume, and churn.

**Key views**:
- MRR by subscription tier -- trend line
- Upgrade and downgrade volume -- daily counts
- Churn rate by tier -- monthly cohort view
- Revenue from credit overage charges -- if/when usage-based pricing is enabled
- Invoice and payment failure rates

**Refresh**: Real-time (Stripe native).

**Filters**: Date range, subscription tier, payment status.

---

## Access

All dashboards are accessible to members of the `example_product-product` and `example_product-analytics` groups. To request access, contact Casey Nguyen or post in #example_product-data.
