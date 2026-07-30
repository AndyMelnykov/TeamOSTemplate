-- One-Click Deploy Success Rate, Time-to-Deploy, and Conversion Impact
-- Author: Casey Nguyen
-- Last Updated: 2026-03-22
--
-- Related metrics: metrics/deployment/one-click-deploy-metrics.md
-- Related schema: schemas/deployment/ (deploy_events table - not yet documented)
--
-- Platform: Snowflake
-- Source tables: analytics.example_product.deploy_events, analytics.example_product.subscriptions
-- Recommended schedule: Daily, 06:00 UTC

-- =============================================================================
-- 1. Daily deploy success rate and time-to-deploy
-- =============================================================================
WITH daily_deploys AS (
    SELECT
        DATE_TRUNC('day', de.created_at) AS deploy_date,
        COUNT(*) AS total_deploy_attempts,
        COUNT_IF(de.status = 'completed') AS successful_deploys,
        COUNT_IF(de.status = 'failed') AS failed_deploys,
        COUNT_IF(de.status = 'timeout') AS timed_out_deploys,

        -- Time-to-deploy: median duration from click to live URL
        MEDIAN(
            CASE WHEN de.status = 'completed' THEN de.duration_ms END
        ) AS median_deploy_duration_ms,
        AVG(
            CASE WHEN de.status = 'completed' THEN de.duration_ms END
        ) AS avg_deploy_duration_ms,
        PERCENTILE_CONT(0.95) WITHIN GROUP (
            ORDER BY CASE WHEN de.status = 'completed' THEN de.duration_ms END
        ) AS p95_deploy_duration_ms
    FROM analytics.example_product.deploy_events de
    WHERE de.created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
),

-- =============================================================================
-- 2. Time-to-deploy from first generation to production deploy
--    Measures the full journey, not just the deploy step itself
-- =============================================================================
project_first_generation AS (
    -- Earliest generation per project (start of the user journey)
    SELECT
        project_id,
        MIN(created_at) AS first_generation_at
    FROM analytics.example_product.project_generations
    WHERE created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY project_id
),

first_production_deploy AS (
    -- First successful production deploy per project
    SELECT
        de.project_id,
        MIN(de.created_at) AS first_deploy_at
    FROM analytics.example_product.deploy_events de
    WHERE de.status = 'completed'
      AND de.deploy_target = 'production'
      AND de.created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY de.project_id
),

generation_to_deploy AS (
    SELECT
        DATE_TRUNC('day', fpd.first_deploy_at) AS deploy_date,
        MEDIAN(
            DATEDIFF('second', pfg.first_generation_at, fpd.first_deploy_at)
        ) AS median_generation_to_deploy_seconds,
        AVG(
            DATEDIFF('second', pfg.first_generation_at, fpd.first_deploy_at)
        ) AS avg_generation_to_deploy_seconds,
        COUNT(*) AS projects_deployed
    FROM first_production_deploy fpd
    JOIN project_first_generation pfg
        ON pfg.project_id = fpd.project_id
    GROUP BY 1
),

-- =============================================================================
-- 3. Deploy-to-paid conversion
--    Free users who upgrade within 7 days of their first deploy
-- =============================================================================
first_deploys AS (
    -- First successful deploy per free-tier user
    SELECT
        de.user_id,
        MIN(de.created_at) AS first_deploy_at
    FROM analytics.example_product.deploy_events de
    JOIN analytics.example_product.subscriptions s
        ON s.user_id = de.user_id
        AND s.tier = 'free'
        AND s.status = 'active'
    WHERE de.status = 'completed'
      AND de.created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY de.user_id
),

deploy_upgrades AS (
    SELECT
        DATE_TRUNC('day', fd.first_deploy_at) AS deploy_date,
        COUNT(DISTINCT fd.user_id) AS free_users_who_deployed,
        COUNT(DISTINCT CASE
            WHEN s.upgraded_at IS NOT NULL
                AND s.upgraded_at BETWEEN fd.first_deploy_at
                    AND DATEADD('day', 7, fd.first_deploy_at)
            THEN fd.user_id
        END) AS users_upgraded_within_7d
    FROM first_deploys fd
    LEFT JOIN analytics.example_product.subscriptions s
        ON s.user_id = fd.user_id
        AND s.tier != 'free'
    GROUP BY 1
)

-- =============================================================================
-- Final output: combine daily success rate, TTD, and conversion
-- =============================================================================
SELECT
    dd.deploy_date,

    -- Deploy success rate
    dd.total_deploy_attempts,
    dd.successful_deploys,
    dd.failed_deploys,
    dd.timed_out_deploys,
    ROUND(
        dd.successful_deploys * 100.0 / NULLIF(dd.total_deploy_attempts, 0), 2
    ) AS deploy_success_rate_pct,

    -- Time-to-deploy (deploy step only)
    ROUND(dd.median_deploy_duration_ms, 0) AS median_deploy_ms,
    ROUND(dd.avg_deploy_duration_ms, 0) AS avg_deploy_ms,
    ROUND(dd.p95_deploy_duration_ms, 0) AS p95_deploy_ms,

    -- Time-to-deploy (generation to production)
    ROUND(g2d.median_generation_to_deploy_seconds, 0) AS median_gen_to_deploy_seconds,
    ROUND(g2d.avg_generation_to_deploy_seconds, 0) AS avg_gen_to_deploy_seconds,
    g2d.projects_deployed,

    -- Deploy-to-paid conversion
    du.free_users_who_deployed,
    du.users_upgraded_within_7d,
    ROUND(
        du.users_upgraded_within_7d * 100.0
        / NULLIF(du.free_users_who_deployed, 0), 2
    ) AS deploy_to_paid_conversion_pct

FROM daily_deploys dd
LEFT JOIN generation_to_deploy g2d
    ON g2d.deploy_date = dd.deploy_date
LEFT JOIN deploy_upgrades du
    ON du.deploy_date = dd.deploy_date
ORDER BY dd.deploy_date DESC;
