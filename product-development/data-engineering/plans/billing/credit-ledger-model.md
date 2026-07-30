# Credit Ledger Data Model - Implementation Plan

| Field | Value |
|-------|-------|
| **Author** | Casey Nguyen (Analytics) |
| **Status** | Draft |
| **Last Updated** | 2026-03-22 |
| **Related RFC** | `data-engineering/rfcs/billing/credit-ledger-model-rfc.md` |

---

## Overview

Build the credit transaction data model in Snowflake to power the Credit Usage Dashboard and billing analytics. This plan covers the full pipeline from Supabase source to analytics-ready tables in Snowflake, including Fivetran configuration, dbt models, data quality tests, and metric models.

## Steps

### 1. Configure Fivetran connector for `credit_transactions`

- Add `credit_transactions` table to the existing Supabase PostgreSQL connector in Fivetran.
- Set sync mode to incremental append using `created_at` as the cursor column.
- Set sync frequency to 15 minutes.
- Disable soft delete (append-only source table).
- Verify initial sync lands correctly in `raw.supabase.credit_transactions`.
- Validate row counts match between Supabase and Snowflake raw layer.

### 2. Create dbt staging model `stg_credit_transactions`

- Create `models/staging/supabase/stg_credit_transactions.sql`.
- Rename columns to snake_case (source uses `camelCase` in some fields).
- Cast `id` to `transaction_id` (VARCHAR(36)).
- Cast `created_at` to `TIMESTAMP_TZ`.
- Cast `amount` to `INTEGER`.
- Add `_dbt_loaded_at` as `CURRENT_TIMESTAMP()`.
- Filter out test and internal accounts using the `dim_users.is_internal` flag.
- Materialize as a view (no need to persist staging data).
- Add source freshness test: warn at 30 minutes, error at 1 hour.

### 3. Create dbt fact model `fact_credit_transactions`

- Create `models/marts/billing/fact_credit_transactions.sql`.
- Materialize as incremental (append-only, using `created_at` as the incremental key).
- Join to a billing cycle spine to derive `billing_cycle_id` and `day_of_cycle`.
- Compute `is_first_depletion` flag: TRUE when `balance_after = 0` and no prior row in the same `billing_cycle_id` has `balance_after = 0`.
- Set clustering key to `(user_id, created_at)`.
- Add schema YAML with column descriptions and dbt tests (see RFC for full test list).

### 4. Create dbt seed `dim_subscription_plans`

- Create `seeds/billing/dim_subscription_plans.csv` with current plan data.
- Columns: `tier`, `display_name`, `monthly_credits`, `price_monthly_usd`, `price_annual_usd`, `max_projects`, `max_team_members`, `overage_enabled`, `overage_rate_usd`, `is_active`, `effective_from`, `effective_to`.
- Populate with current plan values (free, pro, team, business, enterprise).
- Add schema YAML with accepted_values test on `tier`.

### 5. Backfill historical transactions

- Run a one-time full sync of the `credit_transactions` table (not incremental) to capture all historical data from December 2025 onward.
- Validate backfill completeness:
  - Row count in Snowflake matches Supabase.
  - Sum of debit amounts matches Supabase.
  - Spot-check 50 random `balance_after` values against Supabase.
- After validation, switch Fivetran back to incremental mode.

### 6. Build balance integrity check

- Create custom dbt test `tests/billing/test_balance_after_integrity.sql`.
- Test verifies that each `balance_after` equals the previous `balance_after` adjusted by the current transaction amount and type.
- Configure test to run on every dbt build.
- Set up Slack alert to `#data-alerts` on failure.

### 7. Build metric models

#### `credit_utilization` (daily, per user)
- Create `models/marts/billing/credit_utilization.sql`.
- Materialize as incremental (daily grain).
- Calculate: `total_debits_in_cycle / plan_monthly_credits * 100` as `utilization_pct`.
- Join to `dim_subscription_plans` for `monthly_credits`.
- Include `subscription_tier`, `billing_cycle_id`, `utilization_pct`, `credits_remaining`.

#### `credit_burn_rate` (7-day rolling, per user)
- Create `models/marts/billing/credit_burn_rate.sql`.
- Materialize as incremental (daily grain).
- Calculate: `SUM(amount) OVER 7-day window / 7` as `daily_burn_rate`.
- Include `projected_days_remaining` based on current balance divided by burn rate.

#### `credit_upgrade_funnel` (weekly cohort)
- Create `models/marts/billing/credit_upgrade_funnel.sql`.
- Materialize as table (rebuilt weekly).
- Identify users who crossed the <20% balance threshold.
- Track whether they upgraded within 7 days.
- Calculate `credit_to_upgrade_rate` per cohort week and tier.

### 8. Set up freshness monitoring and alerts

- Configure Fivetran sync delay alert: warn at 30 minutes in `#data-alerts`.
- Configure dbt source freshness: warn at 30 minutes, error at 1 hour.
- Add elementary (or custom) row count anomaly detection:
  - Alert if daily inserts are <50% or >200% of the 7-day rolling average.
- Add all alerts to the `#data-alerts` Slack channel.

### 9. Create Sigma dashboard views

- Build the "Credit Usage Health" workbook in Sigma connected to the metric models.
- Views: daily consumption stacked area chart, utilization by tier histogram, at-risk users table, burn rate trends.
- Share with `example_product-product` and `example_product-analytics` groups.
- Document dashboard in `product/analytics/dashboards/billing/credit-usage-dashboards.md`.

### 10. Validate end-to-end pipeline

- Run full dbt build in staging environment.
- Verify all tests pass (0 errors, 0 warnings on error-severity tests).
- Compare metric model outputs against manually computed values for 10 sample users.
- Load test the API-facing queries against the fact table at 2x expected traffic.
- Confirm p95 query latency <200ms for single-user daily usage query.
- Get sign-off from Riley Patel (engineering) that API integration is working correctly.

## Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Supabase `credit_transactions` table exists with production data | Engineering | Complete |
| Fivetran Supabase connector is provisioned | Data Engineering | Complete |
| Snowflake `analytics` database and `example_product` schema exist | Data Engineering | Complete |
| dbt project has `billing` model directory | Data Engineering | To do |
| Sigma workspace access for `example_product-product` group | Data Engineering | Complete |
| Engineering RFC approved | Riley Patel | In review |

## Timeline

| Step | Estimated Duration | Target Completion |
|------|-------------------|-------------------|
| Steps 1-2 (Fivetran + staging model) | 2 days | Week 1 |
| Steps 3-4 (fact model + seed) | 2 days | Week 1 |
| Step 5 (backfill) | 1 day | Week 1 |
| Step 6 (balance integrity) | 1 day | Week 2 |
| Step 7 (metric models) | 3 days | Week 2 |
| Step 8 (monitoring) | 1 day | Week 2 |
| Step 9 (Sigma dashboards) | 2 days | Week 3 |
| Step 10 (validation) | 2 days | Week 3 |
