# Credit Usage Dashboard - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-22 |
| **Related RFC** | `engineering/rfcs/billing/credit-usage-dashboard-rfc.md` |
| **Related Plan** | `engineering/plans/billing/credit-usage-dashboard.md` |

---

## Overview

The Credit Usage Dashboard gives example_product users real-time visibility into how they consume credits across generations, edits, and deploys. It surfaces daily usage breakdowns, burn rate, projected depletion dates, and per-project spending so users can manage their credits proactively rather than being surprised by a hard stop at the limit.

## Problem Statement

example_product users currently have no way to see how they are spending credits. The only signal they receive is a hard block when they hit zero. This creates three compounding problems:

1. **Unexpected interruptions**: Users are blocked mid-workflow with no warning. They cannot plan around their credit budget because there is nothing to plan with.
2. **Opaque consumption**: Users do not know which activities or projects consume the most credits. A user running dozens of generation iterations on one project has no idea that project is responsible for 60% of their spend.
3. **Uninformed upgrade decisions**: Without usage data, users cannot evaluate whether upgrading makes financial sense. They either churn because they feel nickel-and-dimed, or they stay on a plan that does not match their actual usage patterns.

This lack of visibility erodes trust. Users feel the credit system is a black box designed to extract money rather than a transparent resource they can manage.

## Business Opportunity

Solving credit visibility has direct impact on two business metrics:

- **Reduce churn from surprise limit hits**: Users who deplete credits without warning are 3.2x more likely to churn within 14 days (see investigation: `product/analytics/investigations/billing/2026-03-10-credit-depletion-churn-analysis.md`). A dashboard with proactive warnings can meaningfully reduce this churn vector. Our experiment with a low-balance warning banner alone reduced churn-from-depletion by 22%.
- **Drive upgrades through self-serve data**: When users can see their usage patterns, they can self-identify as candidates for a higher tier. This shifts the upgrade motion from sales-driven to product-led. We expect this to increase the credit-to-upgrade conversion rate (users who upgrade within 7 days of reaching <20% balance) from the current 8% to over 12%.

Conservative modeling suggests that reducing credit-related churn by 15% and increasing the upgrade rate by 4 percentage points would generate an incremental $180K ARR within the first two quarters.

## Why Now

- **Credit complaints are the top support topic**: Billing-related tickets averaged 47 per week in Q1 2026, with "I didn't know I was out of credits" as the most common theme. This is consuming support bandwidth that should be going to product issues.
- **Competitor parity**: Both Vercel v0 and Replit now surface usage dashboards. Our absence here is increasingly visible in competitive deals and review site comparisons.
- **Data infrastructure is ready**: The credit transaction ledger was migrated to Supabase in Q4 2025 and is now replicated to Snowflake via Fivetran. The data exists; we just need to surface it.

## Customer Requests

> "I burned through my credits in 3 days and had no idea. I was iterating on a landing page and each generation apparently costs different amounts? There's no way to see any of this."
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

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Billing-related support tickets per week | 47 | <25 | 8 weeks post-launch |
| Churn rate among users who deplete credits | 18% (14-day) | <12% | 12 weeks post-launch |
| Credit-to-upgrade conversion rate (upgrade within 7d of <20% balance) | 8% | >12% | 12 weeks post-launch |
| Dashboard weekly active usage | -- | >40% of Pro/Team users | 8 weeks post-launch |
| Low-balance banner click-through rate | -- | >5% | 4 weeks post-launch |

### Non-Goals

- This project does not change credit pricing, allocation amounts, or billing cycle mechanics.
- This project does not add the ability to purchase additional credits mid-cycle (that is a separate initiative tracked in EXAMPLE_PRODUCT-1105).
- This project does not build an admin/team-level usage view for Team plan admins (planned for Phase 2).

## User Stories

### As a Pro user, I want to see how many credits I have used and how many remain so that I can pace my usage through the billing cycle.

**Acceptance criteria:**
- Dashboard shows total credits used this cycle, remaining balance, and cycle reset date.
- Data refreshes within 60 seconds of a credit-consuming action.

### As a Pro user, I want to see a daily breakdown of my credit usage by category so that I understand which activities consume the most credits.

**Acceptance criteria:**
- Bar chart displays daily usage segmented by generation, edit, and deploy.
- User can hover over any bar segment to see the exact credit count.
- User can filter the chart by date range (7 days, 30 days, this cycle, custom).

### As a user with multiple projects, I want to see credit usage broken down by project so that I can identify which projects are most expensive.

**Acceptance criteria:**
- Table lists each project with columns: generations, edits, deploys, total credits, last activity.
- Table is sortable by any column.
- Clicking a project name navigates to the project detail page.

### As a user approaching my credit limit, I want to receive a warning before I hit zero so that I can take action.

**Acceptance criteria:**
- Warning banner appears when remaining credits fall below 20% of the cycle allocation.
- Banner is shown on the home page and the usage dashboard.
- Banner includes the remaining credit count, percentage, and cycle reset date.
- Banner includes a CTA to upgrade the plan.
- Banner can be dismissed for 24 hours.

### As a user who ran out of credits, I want to understand what happened so that I can avoid it next time.

**Acceptance criteria:**
- Dashboard shows the projected depletion date based on the 7-day burn rate.
- If the user has already depleted, the dashboard shows when depletion occurred and which category drove the final consumption.

## Requirements

### Must Have (P0)

| ID | Requirement |
|----|-------------|
| R1 | Display current credit balance, total used this cycle, and cycle reset date |
| R2 | Show daily usage bar chart broken down by category (generation, edit, deploy) |
| R3 | Calculate and display burn rate (7-day rolling average credits per day) |
| R4 | Show projected depletion date based on current burn rate |
| R5 | Show per-project credit breakdown in a sortable table |
| R6 | Low-balance warning banner at <20% remaining credits |
| R7 | Date range filter (7d, 30d, this cycle, custom) |

### Should Have (P1)

| ID | Requirement |
|----|-------------|
| R8 | Category filter (multi-select: generation, edit, deploy) |
| R9 | Project filter (searchable dropdown) |
| R10 | Shareable/bookmarkable URLs with filter state in query parameters |
| R11 | Comparison to previous cycle (% change on summary cards) |
| R12 | Export usage data as CSV |

### Nice to Have (P2)

| ID | Requirement |
|----|-------------|
| R13 | Email notification at 20% and 5% remaining credits |
| R14 | Slack notification integration for low balance |
| R15 | Budget alerts: user-defined credit threshold notifications |

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

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Should the low-balance threshold be configurable per user, or fixed at 20%? | Hannah Stulberg | Open |
| 2 | Do we show refund and referral credits in the dashboard, or only consumption? | Hannah Stulberg | Open |
| 3 | What is the right default date range for the chart -- 7 days or 30 days? | Hannah Stulberg | Open -- pending analytics on typical billing cycle length |
| 4 | Should we show cost in dollars alongside credits for users on usage-based plans? | Hannah Stulberg | Open -- requires pricing team input |
| 5 | How do we handle users on legacy plans that do not have credit-based billing? | Riley Patel | Open |
