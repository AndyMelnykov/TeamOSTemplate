-- Credit Burn Rate by Subscription Tier with Projected Days to Depletion
-- Author: Casey Nguyen
-- Last Updated: 2026-03-22
--
-- Calculates the daily credit burn rate for each user over the trailing 7 days,
-- then aggregates by subscription tier. Includes projected days until credit
-- depletion at the current burn rate.
--
-- Platform: Snowflake
-- Source table: analytics.example_product.credit_transactions
-- Recommended schedule: Daily, 06:00 UTC
--
-- Related metrics: metrics/billing/credit-usage-metrics.md
-- Related schema: schemas/billing/credit_transactions.md

WITH user_daily_usage AS (
    -- Aggregate daily debit totals per user over the trailing 7 days
    SELECT
        ct.user_id,
        ct.subscription_tier,
        DATE(ct.created_at) AS usage_date,
        SUM(ct.amount) AS daily_credits_used
    FROM analytics.example_product.credit_transactions ct
    WHERE ct.type = 'debit'
        AND ct.created_at >= DATEADD('day', -7, CURRENT_DATE())
        AND ct.created_at < CURRENT_DATE()
    GROUP BY ct.user_id, ct.subscription_tier, DATE(ct.created_at)
),

user_burn_rate AS (
    -- Calculate 7-day average daily burn rate per user
    SELECT
        user_id,
        subscription_tier,
        SUM(daily_credits_used) / 7.0 AS avg_daily_burn_rate,
        SUM(daily_credits_used) AS total_7d_usage,
        COUNT(DISTINCT usage_date) AS active_days
    FROM user_daily_usage
    GROUP BY user_id, subscription_tier
),

current_balance AS (
    -- Get each user's most recent balance
    SELECT
        user_id,
        balance_after AS current_balance
    FROM analytics.example_product.credit_transactions
    WHERE (user_id, created_at) IN (
        SELECT user_id, MAX(created_at)
        FROM analytics.example_product.credit_transactions
        GROUP BY user_id
    )
),

user_projections AS (
    -- Combine burn rate with current balance to project depletion
    SELECT
        ubr.user_id,
        ubr.subscription_tier,
        ubr.avg_daily_burn_rate,
        ubr.total_7d_usage,
        ubr.active_days,
        cb.current_balance,
        CASE
            WHEN ubr.avg_daily_burn_rate > 0
                THEN ROUND(cb.current_balance / ubr.avg_daily_burn_rate, 1)
            ELSE NULL
        END AS projected_days_to_depletion,
        CASE
            WHEN ubr.avg_daily_burn_rate > 0
                THEN DATEADD('day',
                    ROUND(cb.current_balance / ubr.avg_daily_burn_rate),
                    CURRENT_DATE()
                )
            ELSE NULL
        END AS projected_depletion_date
    FROM user_burn_rate ubr
    JOIN current_balance cb ON ubr.user_id = cb.user_id
)

-- Final output: aggregated by subscription tier
SELECT
    subscription_tier,
    COUNT(DISTINCT user_id) AS total_users,
    ROUND(AVG(avg_daily_burn_rate), 2) AS avg_burn_rate_per_day,
    ROUND(MEDIAN(avg_daily_burn_rate), 2) AS median_burn_rate_per_day,
    ROUND(AVG(current_balance), 0) AS avg_current_balance,
    ROUND(AVG(projected_days_to_depletion), 1) AS avg_days_to_depletion,
    ROUND(MEDIAN(projected_days_to_depletion), 1) AS median_days_to_depletion,
    COUNT(CASE WHEN projected_days_to_depletion <= 3 THEN 1 END) AS users_depleting_within_3d,
    COUNT(CASE WHEN projected_days_to_depletion <= 7 THEN 1 END) AS users_depleting_within_7d,
    ROUND(
        COUNT(CASE WHEN projected_days_to_depletion <= 7 THEN 1 END)::FLOAT
        / NULLIF(COUNT(DISTINCT user_id), 0) * 100,
        1
    ) AS pct_depleting_within_7d
FROM user_projections
GROUP BY subscription_tier
ORDER BY
    CASE subscription_tier
        WHEN 'free' THEN 1
        WHEN 'pro' THEN 2
        WHEN 'team' THEN 3
        WHEN 'business' THEN 4
        WHEN 'enterprise' THEN 5
    END;
