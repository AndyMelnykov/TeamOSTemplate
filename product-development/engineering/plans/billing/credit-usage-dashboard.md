# Credit usage dashboard

| Field | Value |
|-------|-------|
| **Related PRD** | `product/PRDs/billing/credit-usage-dashboard-prd.md` |
| **Related RFC** | `engineering/rfcs/billing/credit-usage-dashboard-rfc.md` |
| **Related Data Model RFC** | `data-engineering/rfcs/billing/credit-ledger-model-rfc.md` |
| **Related Data Model Plan** | `data-engineering/plans/billing/credit-ledger-model.md` |
| **Analytics Schema** | `product/analytics/schemas/billing/credit_transactions.md` |
| **Metrics** | `product/analytics/metrics/billing/credit-usage-metrics.md` |
| **Dashboards** | `product/analytics/dashboards/billing/credit-usage-dashboards.md` |

## Overview
Show users a breakdown of how they're spending credits (extraction, refinement, publish) so they understand consumption before hitting limits or deciding to upgrade.

## Steps
1. Add `GET /api/billing/usage` endpoint in `src/routes/billing.ts`
   - Query credit transactions grouped by type and day
   - Return current balance, burn rate, projected days remaining
2. Create `UsageDashboard` component in `src/components/billing/`
   - Bar chart showing daily credit usage by category
   - Summary cards: credits used this cycle, remaining, reset date
   - Trend line showing consumption rate
3. Add usage breakdown by workflow
   - `GET /api/billing/usage/by-workflow` returns per-workflow totals
   - Sortable table: workflow name, extractions, refinements, total credits
4. Add low-balance warning banner
   - Show at <20% remaining credits on home page
   - Link to upgrade or purchase more credits
5. Add tests
   - Usage totals match actual credit transactions
   - Breakdown by workflow sums to total
   - Warning banner appears at correct threshold
