# Credit Usage Dashboard - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Shipped |
| **Last Updated** | 2026-03-22 |
| **Related RFC** | `engineering/rfcs/billing/credit-usage-dashboard-rfc.md` |
| **Related Plan** | `engineering/plans/billing/credit-usage-dashboard.md` |
| **Hypothesis** | none — shipped before the hypothesis stage existed; the case is the churn investigation and low-balance banner experiment cited in Sources |
| **Execution Path** | engineering-mediated |

---

## Overview

The Credit Usage Dashboard gives example_product users real-time visibility into how they consume credits across extraction, routing, and signature activity. It surfaces daily usage breakdowns, burn rate, projected depletion dates, and per-workflow spending so users can manage their credits proactively rather than being surprised by a hard stop at the limit.

## Problem Statement

example_product users currently have no way to see how they are spending credits. The only signal they receive is a hard block when they hit zero. This creates three compounding problems:

1. **Unexpected interruptions**: Users are blocked mid-workflow with no warning. They cannot plan around their credit budget because there is nothing to plan with.
2. **Opaque consumption**: Users do not know which activities or workflows consume the most credits. A user running dozens of pages through extraction on one workflow has no idea that workflow is responsible for 60% of their spend.
3. **Uninformed upgrade decisions**: Without usage data, users cannot evaluate whether upgrading makes financial sense. They either churn because they feel nickel-and-dimed, or they stay on a plan that does not match their actual usage patterns.

This lack of visibility erodes trust. Users feel the credit system is a black box designed to extract money rather than a transparent resource they can manage.

## Business Opportunity

Solving credit visibility has direct impact on two business metrics:

- **Reduce churn from surprise limit hits**: Users who deplete credits without warning are 3.2x more likely to churn within 14 days (see investigation: `product/analytics/investigations/billing/2026-03-10-credit-depletion-churn-analysis.md`). A dashboard with proactive warnings can meaningfully reduce this churn vector. Our experiment with a low-balance warning banner alone reduced churn-from-depletion by 22%.
- **Drive upgrades through self-serve data**: When users can see their usage patterns, they can self-identify as candidates for a higher tier. This shifts the upgrade motion from sales-driven to product-led. We expect this to increase the credit-to-upgrade conversion rate (users who upgrade within 7 days of reaching <20% balance) from the current 8% to over 12%.

Conservative modeling suggests that reducing credit-related churn by 15% and increasing the upgrade rate by 4 percentage points would generate an incremental $180K ARR within the first two quarters.

## Why Now

- **Credit complaints are the top support topic**: Billing-related tickets averaged 47 per week in Q1 2026, with "I didn't know I was out of credits" as the most common theme. This is consuming support bandwidth that should be going to product issues.
- **Competitor parity**: Both PandaDoc and Dropbox Sign now surface usage dashboards. Our absence here is increasingly visible in competitive deals and review site comparisons.
- **Data infrastructure is ready**: The credit transaction ledger was migrated to Supabase in Q4 2025 and is now replicated to Snowflake via Fivetran. The data exists; we just need to surface it.

## Customer Requests

> "I burned through my credits in 3 days and had no idea. I was processing a batch of vendor contracts and each extraction apparently costs different amounts? There's no way to see any of this."
> -- Sara M., Pro user, support ticket EXAMPLE_PRODUCT-892

> "We have 5 people on our team plan and I have zero visibility into who's using what. I got a Stripe charge for overages I didn't even know we incurred. I need a dashboard yesterday."
> -- David K., Team plan admin, customer call 2026-02-14

> "I'd happily upgrade to Business if I could see that I'm actually using enough to justify it. Right now I have no idea if I'm at 50% utilization or 95%. Show me the data and I'll make the decision myself."
> -- Priya R., Pro user, NPS survey response

## Goals & Success Metrics

### Goals

1. Give every example_product user clear, real-time visibility into their credit consumption.
2. Reduce surprise credit depletion events by warning users before they hit zero.
3. Create a self-serve upgrade path driven by usage data rather than sales outreach.

### Success Metrics

| Metric | Baseline | Target | Timeline | Source |
|--------|----------|--------|----------|--------|
| Billing-related support tickets per week | 47 | <25 | 8 weeks post-launch | Not yet documented (Open Question 6) |
| Churn rate among users who deplete credits | 18% (14-day) | <12% | 12 weeks post-launch | Credit Usage Health dashboard (Sigma); method in the churn investigation (see Sources) |
| Credit-to-upgrade conversion rate (upgrade within 7d of <20% balance) | 8% | >12% | 12 weeks post-launch | Billing Experiments dashboard (Amplitude), depletion-to-upgrade funnel |
| Dashboard weekly active usage | -- | >40% of Pro/Team users | 8 weeks post-launch | Not yet documented (Open Question 6) |
| Low-balance banner click-through rate | -- | >5% | 4 weeks post-launch | Billing Experiments dashboard (Amplitude), warning-seen to upgrade-page funnel step |

### Non-Goals

- This project does not change credit pricing, allocation amounts, or billing cycle mechanics.
- This project does not add the ability to purchase additional credits mid-cycle (that is a separate initiative tracked in EXAMPLE_PRODUCT-1105).
- This project does not build an admin/team-level usage view for Team plan admins (planned for Phase 2).

## User Stories

### Story 1: As a Pro user, I want to see how many credits I have used and how many remain so that I can pace my usage through the billing cycle.

**Acceptance criteria:**
- Dashboard shows total credits used this cycle, remaining balance, and cycle reset date.
- Data refreshes within 60 seconds of a credit-consuming action.

### Story 2: As a Pro user, I want to see a daily breakdown of my credit usage by category so that I understand which activities consume the most credits.

**Acceptance criteria:**
- Bar chart displays daily usage segmented by extraction, routing, and signature.
- User can hover over any bar segment to see the exact credit count.
- User can filter the chart by date range (7 days, 30 days, this cycle, custom).

### Story 3: As a user with multiple workflows, I want to see credit usage broken down by workflow so that I can identify which workflows are most expensive.

**Acceptance criteria:**
- Table lists each workflow with columns: pages extracted, routing steps, signatures, total credits, last activity.
- Table is sortable by any column.
- Clicking a workflow name navigates to the workflow detail page.

### Story 4: As a user approaching my credit limit, I want to receive a warning before I hit zero so that I can take action.

**Acceptance criteria:**
- Warning banner appears when remaining credits fall below 20% of the cycle allocation.
- Banner is shown on the home page and the usage dashboard.
- Banner includes the remaining credit count, percentage, and cycle reset date.
- Banner includes a CTA to upgrade the plan.
- Banner can be dismissed for 24 hours.

### Story 5: As a user who ran out of credits, I want to understand what happened so that I can avoid it next time.

**Acceptance criteria:**
- Dashboard shows the projected depletion date based on the 7-day burn rate.
- If the user has already depleted, the dashboard shows when depletion occurred and which category drove the final consumption.

## Requirements

### Must Have (P0)

| ID | Requirement |
|----|-------------|
| P0-1 | Display current credit balance, total used this cycle, and cycle reset date |
| P0-2 | Show daily usage bar chart broken down by category (extraction, routing, signature) |
| P0-3 | Calculate and display burn rate (7-day rolling average credits per day) |
| P0-4 | Show projected depletion date based on current burn rate |
| P0-5 | Show per-workflow credit breakdown in a sortable table |
| P0-6 | Low-balance warning banner at <20% remaining credits |
| P0-7 | Date range filter (7d, 30d, this cycle, custom) |

### Should Have (P1)

| ID | Requirement |
|----|-------------|
| P1-1 | Category filter (multi-select: extraction, routing, signature) |
| P1-2 | Workflow filter (searchable dropdown) |
| P1-3 | Shareable/bookmarkable URLs with filter state in query parameters |
| P1-4 | Comparison to previous cycle (% change on summary cards) |
| P1-5 | Export usage data as CSV |

### Nice to Have (P2)

| ID | Requirement |
|----|-------------|
| P2-1 | Email notification at 20% and 5% remaining credits |
| P2-2 | Slack notification integration for low balance |
| P2-3 | Budget alerts: user-defined credit threshold notifications |

## Acceptance Criteria

| ID | Given | When | Then | Covers | Verify by |
|----|-------|------|------|--------|-----------|
| AC-1 | A user has used credits this cycle | They open the usage dashboard | It shows total credits used this cycle, the remaining balance and the cycle reset date | P0-1, Story 1 | automated-test |
| AC-2 | A user is on the usage dashboard | They perform a credit-consuming action | The dashboard data reflects it within 60 seconds | P0-1, Story 1 | automated-test |
| AC-3 | A user has usage in extraction, routing and signature | They open the usage dashboard | A daily bar chart shows usage segmented by extraction, routing and signature | P0-2, Story 2 | automated-test |
| AC-4 | The daily bar chart is displayed | They hover over a bar segment | The exact credit count for that segment is shown | P0-2, Story 2 | manual-qa |
| AC-5 | The daily bar chart is displayed | They choose 7 days, 30 days, this cycle or a custom range | The chart shows only usage in that range | P0-7, Story 2 | automated-test |
| AC-6 | A user has usage across several workflows | They open the usage dashboard | A table lists each workflow with pages extracted, routing steps, signatures, total credits and last activity | P0-5, Story 3 | automated-test |
| AC-7 | The workflow table is displayed | They select a column header | The table is sorted by that column | P0-5, Story 3 | automated-test |
| AC-8 | The workflow table is displayed | They select a workflow name | They land on that workflow's detail page | P0-5, Story 3 | automated-test |
| AC-9 | A user's remaining credits are below 20% of the cycle allocation | They open the home page or the usage dashboard | A warning banner shows the remaining credit count, the percentage, the cycle reset date and an upgrade CTA | P0-6, Story 4 | automated-test |
| AC-10 | The low-balance banner is displayed | They dismiss it | It does not reappear for 24 hours | P0-6, Story 4 | automated-test |
| AC-11 | A user's remaining credits are 20% or more of the cycle allocation | They open the home page or the usage dashboard | No low-balance banner is shown | P0-6, Story 4 | automated-test |
| AC-12 | A user has at least 7 days of usage | They open the usage dashboard | It shows the 7-day rolling average burn rate and a projected depletion date based on it | P0-3, P0-4, Story 5 | automated-test |
| AC-13 | A user has already depleted their credits | They open the usage dashboard | It shows when depletion occurred and which category drove the final consumption | P0-4, Story 5 | automated-test |
| AC-14 | The dashboard has been live for 4 weeks | Banner click-throughs are counted against banner views | The low-balance banner click-through rate is above 5% (metric: "Low-balance banner click-through rate" in Goals & Success Metrics) | P0-6, Story 4 | analytics |
| AC-15 | The dashboard has been live for 8 weeks | Weekly dashboard visitors are counted against Pro and Team users | Weekly active usage is above 40% of Pro and Team users (metric: "Dashboard weekly active usage" in Goals & Success Metrics) | P0-1, Story 1 | analytics |

## Design

- Figma file: `https://figma.com/file/example_product-credit-dashboard` (listed in `product-development/feature-index.yaml`).
- The dashboard is a page at `/billing/usage` with summary cards, a filter bar, the daily usage chart and the per-workflow table; the low-balance banner also appears on the home page. Component-level detail is in the [RFC](../../../engineering/rfcs/billing/credit-usage-dashboard-rfc.md).

## Technical Considerations

- The credit transaction ledger lives in Supabase and is replicated to Snowflake via Fivetran; see the [credit_transactions schema](../../../analytics/schemas/billing/credit_transactions.md).
- Architecture, API and rollout: [RFC](../../../engineering/rfcs/billing/credit-usage-dashboard-rfc.md) and [plan](../../../engineering/plans/billing/credit-usage-dashboard.md).
- Rollout is gated by a LaunchDarkly feature flag (see Launch Plan).

## Launch Plan

### Phase 1: Internal Dogfood (Week 5)
- Enable for all internal example_product team members.
- Collect feedback via a dedicated Slack channel (#example_product-billing-beta).
- Fix any P0/P1 bugs identified.

### Phase 2: Beta (Week 6)
- Roll out to 10% of Pro users via LaunchDarkly feature flag.
- Monitor error rates, latency, and dashboard engagement.
- Gate: error rate <0.1%, p95 response time <500ms.

### Phase 3: General Availability (Week 7)
- Enable for all users.
- Add dashboard link to the main navigation under "Billing."
- Publish help center article explaining the dashboard.
- Send announcement email to Pro and Team users.
- Brief support team on new dashboard and updated troubleshooting flows.

### Post-Launch
- Monitor success metrics weekly for 12 weeks.
- Conduct qualitative interviews with 5 users at Week 4 and Week 8 post-launch.
- Prioritize Phase 2 features (team admin view, email notifications) based on adoption data.

## Sources

- [Credit depletion churn investigation](../../../analytics/investigations/billing/2026-03-10-credit-depletion-churn-analysis.md) — the 3.2x churn claim in Business Opportunity and the 18% baseline in Success Metrics
- [Low-balance warning banner experiment](../../../analytics/experiments/billing/low-balance-warning-03-05-2026-experiment-results.md) — the 22% churn-from-depletion reduction cited in Business Opportunity
- [Credit usage dashboards](../../../analytics/dashboards/billing/credit-usage-dashboards.md) — where the Success Metrics `Source` entries are measured
- [credit_transactions schema](../../../analytics/schemas/billing/credit_transactions.md) — the ledger cited in Why Now and Technical Considerations

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Should the low-balance threshold be configurable per user, or fixed at 20%? | Hannah Stulberg | Open |
| 2 | Do we show refund and referral credits in the dashboard, or only consumption? | Hannah Stulberg | Open |
| 3 | What is the right default date range for the chart -- 7 days or 30 days? | Hannah Stulberg | Open -- pending analytics on typical billing cycle length |
| 4 | Should we show cost in dollars alongside credits for users on usage-based plans? | Hannah Stulberg | Open -- requires pricing team input |
| 5 | How do we handle users on legacy plans that do not have credit-based billing? | Riley Patel | Open |
| 6 | Where are "billing-related support tickets per week" and "dashboard weekly active usage" measured? Neither has a documented dashboard, query or event. | Hannah Stulberg | Open |
| 7 | The PRD names the categories extraction, routing and signature; the RFC names extraction, refinement and publish. Which is correct? | Hannah Stulberg | Open |
