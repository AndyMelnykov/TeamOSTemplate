# Credit Ledger Data Model - Data Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Casey Nguyen (Analytics) |
| **Status** | Draft |
| **Last Updated** | 2026-03-22 |

---

## Table of Contents

1. [Summary](#summary)
2. [Motivation](#motivation)
3. [Data Model](#data-model)
4. [Pipeline Architecture](#pipeline-architecture)
5. [Key Queries](#key-queries)
6. [Data Quality](#data-quality)

---

## Summary

This RFC defines the data model for the credit transaction ledger in Snowflake. It covers two core tables -- `fact_credit_transactions` (the immutable event log of all credit movements) and `dim_subscription_plans` (the reference table for plan-level credit allocations and pricing). The pipeline extracts from Supabase PostgreSQL via Fivetran, lands in Snowflake raw, and is transformed through dbt into analytics-ready tables.

## Motivation

The Credit Usage Dashboard (EXAMPLE_PRODUCT-1028) requires reliable, low-latency access to credit transaction data for both real-time API queries and analytical workloads. Today, credit data lives only in the Supabase production database with no analytics replica. This creates two problems:

1. **No analytical access**: Analysts cannot query credit data without risking production database performance. Ad-hoc investigations (like the depletion-churn analysis in EXAMPLE_PRODUCT-1030) require engineering to run queries and export results manually.
2. **No historical aggregations**: The production schema is optimized for transactional writes, not for the aggregated reads that dashboards and metrics require. Building dbt models on top of a replicated copy allows us to pre-compute burn rates, utilization metrics, and projections without impacting production.

## Data Model

### `fact_credit_transactions`

The core fact table. One row per credit transaction event. Append-only -- no updates or deletes.

```sql
CREATE TABLE analytics.example_product.fact_credit_transactions (
    transaction_id      VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id             VARCHAR(36) NOT NULL,
    org_id              VARCHAR(36),
    amount              INTEGER NOT NULL,
    type                VARCHAR(10) NOT NULL,    -- 'debit' or 'credit'
    category            VARCHAR(20) NOT NULL,    -- 'generation', 'edit', 'deploy', 'refund', 'referral', 'bonus'
    reference_id        VARCHAR(36),
    project_id          VARCHAR(36),
    balance_after       INTEGER NOT NULL,
    subscription_tier   VARCHAR(20) NOT NULL,    -- 'free', 'pro', 'team', 'business', 'enterprise'
    created_at          TIMESTAMP_TZ NOT NULL,

    -- dbt-added fields
    _fivetran_synced    TIMESTAMP_TZ NOT NULL,   -- Fivetran sync timestamp
    _dbt_loaded_at      TIMESTAMP_TZ NOT NULL,   -- dbt model run timestamp
    billing_cycle_id    VARCHAR(36),             -- Derived: maps transaction to billing cycle
    day_of_cycle        INTEGER,                 -- Derived: day number within the billing cycle (1-indexed)
    is_first_depletion  BOOLEAN                  -- Derived: TRUE if this is the first transaction where balance_after = 0 in the cycle
);
```

**Clustering key**: `(user_id, created_at)` -- optimized for the primary access pattern of per-user time-range queries.

**Partitioning**: By `created_at` month for efficient time-range pruning in analytical queries.

### `dim_subscription_plans`

Reference table for subscription plan attributes. Maintained as a dbt seed file and updated manually when plans change.

```sql
CREATE TABLE analytics.example_product.dim_subscription_plans (
    tier                VARCHAR(20) NOT NULL PRIMARY KEY,  -- 'free', 'pro', 'team', 'business', 'enterprise'
    display_name        VARCHAR(50) NOT NULL,
    monthly_credits     INTEGER NOT NULL,
    price_monthly_usd   DECIMAL(10, 2) NOT NULL,
    price_annual_usd    DECIMAL(10, 2) NOT NULL,
    max_projects        INTEGER,
    max_team_members    INTEGER,
    overage_enabled     BOOLEAN NOT NULL DEFAULT FALSE,
    overage_rate_usd    DECIMAL(10, 4),           -- Cost per credit above allocation (if overage enabled)
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from      DATE NOT NULL,
    effective_to        DATE,                      -- NULL if currently active

    _dbt_loaded_at      TIMESTAMP_TZ NOT NULL
);
```

**Current plan data (seed values):**

| Tier | Monthly Credits | Monthly Price | Annual Price |
|------|----------------|---------------|--------------|
| free | 500 | $0.00 | $0.00 |
| pro | 2,000 | $20.00 | $192.00 |
| team | 10,000 | $50.00/seat | $480.00/seat |
| business | 50,000 | $200.00 | $1,920.00 |
| enterprise | Custom | Custom | Custom |

## Pipeline Architecture

```
Supabase PostgreSQL (source of truth)
        │
        ▼
   Fivetran Connector
   (postgres → snowflake)
   Sync: every 15 minutes
   Mode: incremental append
   Table: raw.supabase.credit_transactions
        │
        ▼
   Snowflake Raw Layer
   raw.supabase.credit_transactions
        │
        ▼
   dbt Staging Model
   stg_credit_transactions
   - Rename columns to snake_case
   - Cast types
   - Add _dbt_loaded_at
   - Filter test/internal accounts
        │
        ▼
   dbt Fact Model
   fact_credit_transactions
   - Join to billing cycles to derive billing_cycle_id and day_of_cycle
   - Compute is_first_depletion flag
   - Add data quality tests
        │
        ▼
   dbt Metric Models
   - credit_utilization (daily, per user)
   - credit_burn_rate (7-day rolling, per user)
   - credit_upgrade_funnel (weekly cohort)
```

### Fivetran Configuration

| Setting | Value |
|---------|-------|
| Connector | PostgreSQL |
| Source host | Supabase project `example_product-prod` |
| Destination schema | `raw.supabase` |
| Sync frequency | 15 minutes |
| Sync mode | Incremental append (using `created_at` as cursor) |
| Tables synced | `credit_transactions` |
| Soft delete | Disabled (append-only source table) |
| History mode | Disabled (no SCD tracking needed for append-only) |

### dbt Models

| Model | Materialization | Schema | Description |
|-------|----------------|--------|-------------|
| `stg_credit_transactions` | View | `staging` | Cleaned and typed staging model |
| `fact_credit_transactions` | Incremental | `analytics.example_product` | Core fact table with derived fields |
| `dim_subscription_plans` | Table (seed) | `analytics.example_product` | Plan reference data |
| `credit_utilization` | Incremental | `analytics.example_product_metrics` | Daily utilization rate per user |
| `credit_burn_rate` | Incremental | `analytics.example_product_metrics` | 7-day rolling burn rate per user |
| `credit_upgrade_funnel` | Table | `analytics.example_product_metrics` | Weekly cohort funnel: low balance → upgrade |

## Key Queries

### Daily credit usage by category (dashboard API)

```sql
SELECT
    DATE(created_at) AS usage_date,
    category,
    SUM(amount) AS total_credits
FROM analytics.example_product.fact_credit_transactions
WHERE user_id = :user_id
    AND type = 'debit'
    AND created_at >= :start_date
    AND created_at < :end_date
GROUP BY 1, 2
ORDER BY 1;
```

Expected performance: <200ms for a single user with 90 days of data, leveraging the `(user_id, created_at)` clustering key.

### Credit utilization rate by tier (metrics dashboard)

```sql
SELECT
    f.subscription_tier,
    d.monthly_credits AS plan_allocation,
    COUNT(DISTINCT f.user_id) AS total_users,
    AVG(cycle_usage.total_used::FLOAT / d.monthly_credits * 100) AS avg_utilization_pct,
    MEDIAN(cycle_usage.total_used::FLOAT / d.monthly_credits * 100) AS median_utilization_pct
FROM (
    SELECT
        user_id,
        subscription_tier,
        billing_cycle_id,
        SUM(CASE WHEN type = 'debit' THEN amount ELSE 0 END) AS total_used
    FROM analytics.example_product.fact_credit_transactions
    WHERE created_at >= DATEADD('month', -1, CURRENT_DATE())
    GROUP BY 1, 2, 3
) cycle_usage
JOIN analytics.example_product.fact_credit_transactions f
    ON cycle_usage.user_id = f.user_id
JOIN analytics.example_product.dim_subscription_plans d
    ON f.subscription_tier = d.tier
WHERE d.is_active = TRUE
GROUP BY 1, 2
ORDER BY 1;
```

### Users at risk of depletion (operational alert)

```sql
WITH burn_rates AS (
    SELECT
        user_id,
        SUM(amount) / 7.0 AS daily_burn_rate
    FROM analytics.example_product.fact_credit_transactions
    WHERE type = 'debit'
        AND created_at >= DATEADD('day', -7, CURRENT_DATE())
    GROUP BY user_id
),
latest_balance AS (
    SELECT DISTINCT
        user_id,
        LAST_VALUE(balance_after) OVER (
            PARTITION BY user_id ORDER BY created_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS current_balance
    FROM analytics.example_product.fact_credit_transactions
)
SELECT
    lb.user_id,
    lb.current_balance,
    br.daily_burn_rate,
    ROUND(lb.current_balance / NULLIF(br.daily_burn_rate, 0), 1) AS projected_days_remaining
FROM latest_balance lb
JOIN burn_rates br ON lb.user_id = br.user_id
WHERE lb.current_balance > 0
    AND br.daily_burn_rate > 0
    AND (lb.current_balance / br.daily_burn_rate) <= 3
ORDER BY projected_days_remaining ASC;
```

## Data Quality

### dbt Tests

| Test | Table | Column(s) | Severity |
|------|-------|-----------|----------|
| `not_null` | `fact_credit_transactions` | `transaction_id`, `user_id`, `amount`, `type`, `category`, `balance_after`, `created_at` | Error |
| `unique` | `fact_credit_transactions` | `transaction_id` | Error |
| `accepted_values` | `fact_credit_transactions` | `type` (`debit`, `credit`) | Error |
| `accepted_values` | `fact_credit_transactions` | `category` (`generation`, `edit`, `deploy`, `refund`, `referral`, `bonus`) | Error |
| `accepted_values` | `fact_credit_transactions` | `subscription_tier` (`free`, `pro`, `team`, `business`, `enterprise`) | Error |
| `relationships` | `fact_credit_transactions` | `user_id` → `dim_users.user_id` | Warn |
| `relationships` | `fact_credit_transactions` | `project_id` → `dim_projects.project_id` | Warn |
| `positive_values` | `fact_credit_transactions` | `amount` | Error |
| `non_negative` | `fact_credit_transactions` | `balance_after` | Error |

### Balance Integrity Check

A custom dbt test validates that `balance_after` values are consistent:

```sql
-- For each user, verify that balance_after = previous_balance_after - amount (for debits)
-- or balance_after = previous_balance_after + amount (for credits)
SELECT
    transaction_id,
    user_id,
    balance_after AS actual_balance,
    LAG(balance_after) OVER (PARTITION BY user_id ORDER BY created_at) +
        CASE WHEN type = 'credit' THEN amount ELSE -amount END AS expected_balance
FROM analytics.example_product.fact_credit_transactions
HAVING actual_balance != expected_balance
```

If this test returns any rows, an alert fires in `#data-alerts` on Slack and the dbt run is marked as failed.

### Freshness Monitoring

| Check | Threshold | Alert Channel |
|-------|-----------|---------------|
| Fivetran sync delay | >30 minutes | `#data-alerts` |
| dbt model staleness (`fact_credit_transactions`) | >1 hour | `#data-alerts` |
| Row count anomaly (daily inserts < 50% of 7-day avg) | Trigger | `#data-alerts` |
| Row count anomaly (daily inserts > 200% of 7-day avg) | Trigger | `#data-alerts` |
