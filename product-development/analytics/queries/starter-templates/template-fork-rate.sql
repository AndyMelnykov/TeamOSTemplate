-- Template Fork Rate Queries
-- Calculates daily fork rate, top templates by forks, and fork-to-deploy conversion
-- for the Community Marketplace feature.
--
-- Used in the Community Marketplace Dashboard (Sigma).
--
-- Author: Casey Nguyen, Analytics
-- Last updated: 2026-03-22
--
-- Related metrics: metrics/starter-templates/marketplace-metrics.md
-- Related schema: schemas/starter-templates/template_forks.md

-- =============================================================================
-- Query 1: Daily fork rate (last 30 days)
-- =============================================================================

WITH daily_forks AS (
    SELECT
        DATE_TRUNC('day', tf.created_at) AS fork_date,
        COUNT(*) AS total_forks,
        COUNT(DISTINCT tf.user_id) AS unique_forkers,
        COUNT(DISTINCT tf.template_id) AS unique_templates_forked
    FROM analytics.example_product.template_forks tf
    WHERE tf.created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
),
daily_marketplace_views AS (
    SELECT
        DATE_TRUNC('day', event_timestamp) AS view_date,
        COUNT(*) AS marketplace_page_views
    FROM analytics.example_product.segment_events
    WHERE event_name = 'marketplace.viewed'
      AND event_timestamp >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
)

SELECT
    df.fork_date,
    df.total_forks,
    df.unique_forkers,
    df.unique_templates_forked,
    dmv.marketplace_page_views,
    ROUND(df.total_forks * 100.0 / NULLIF(dmv.marketplace_page_views, 0), 2) AS fork_rate_pct
FROM daily_forks df
LEFT JOIN daily_marketplace_views dmv ON dmv.view_date = df.fork_date
ORDER BY df.fork_date DESC;


-- =============================================================================
-- Query 2: Top templates by fork count (last 30 days)
-- =============================================================================

SELECT
    pt.template_id,
    pt.title,
    pt.category,
    pt.avg_rating,
    pt.author_id,
    u.username AS author_username,
    COUNT(tf.fork_id) AS forks_last_30d,
    pt.fork_count AS forks_all_time,
    pt.rating_count
FROM analytics.example_product.published_templates pt
JOIN analytics.example_product.template_forks tf
    ON tf.template_id = pt.template_id
    AND tf.created_at >= DATEADD('day', -30, CURRENT_DATE())
JOIN analytics.example_product.users u
    ON u.user_id = pt.author_id
WHERE pt.status = 'approved'
GROUP BY 1, 2, 3, 4, 5, 6, 8, 9
ORDER BY forks_last_30d DESC
LIMIT 25;


-- =============================================================================
-- Query 3: Fork-to-deploy conversion (last 30 days)
-- =============================================================================
-- Measures what percentage of forked templates result in a successful deployment.
-- Compares against blank-project deploy rate as a baseline.

WITH forked_projects AS (
    SELECT
        tf.fork_id,
        tf.template_id,
        tf.user_id,
        tf.project_id,
        tf.customizations_applied,
        tf.created_at AS fork_created_at,
        pt.category AS template_category
    FROM analytics.example_product.template_forks tf
    JOIN analytics.example_product.published_templates pt
        ON pt.template_id = tf.template_id
    WHERE tf.created_at >= DATEADD('day', -30, CURRENT_DATE())
),
fork_deploy_status AS (
    SELECT
        fp.fork_id,
        fp.template_id,
        fp.template_category,
        fp.customizations_applied,
        MAX(CASE WHEN de.status = 'completed' THEN 1 ELSE 0 END) AS was_deployed,
        MIN(de.created_at) AS first_deploy_at,
        DATEDIFF('minute', fp.fork_created_at, MIN(de.created_at)) AS minutes_to_first_deploy
    FROM forked_projects fp
    LEFT JOIN analytics.example_product.deploy_events de
        ON de.project_id = fp.project_id
    GROUP BY 1, 2, 3, 4, fp.fork_created_at
)

SELECT
    -- Overall conversion
    COUNT(*) AS total_forks,
    SUM(was_deployed) AS forks_deployed,
    ROUND(SUM(was_deployed) * 100.0 / NULLIF(COUNT(*), 0), 2) AS fork_to_deploy_pct,

    -- By customization status
    SUM(CASE WHEN customizations_applied THEN 1 ELSE 0 END) AS forks_with_customizations,
    SUM(CASE WHEN customizations_applied AND was_deployed = 1 THEN 1 ELSE 0 END) AS customized_and_deployed,
    ROUND(
        SUM(CASE WHEN customizations_applied AND was_deployed = 1 THEN 1 ELSE 0 END) * 100.0
        / NULLIF(SUM(CASE WHEN customizations_applied THEN 1 ELSE 0 END), 0),
    2) AS customized_deploy_pct,

    -- Time to deploy
    ROUND(AVG(CASE WHEN was_deployed = 1 THEN minutes_to_first_deploy END), 1) AS avg_minutes_to_deploy,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN was_deployed = 1 THEN minutes_to_first_deploy END), 1) AS p50_minutes_to_deploy
FROM fork_deploy_status;


-- =============================================================================
-- Query 4: Fork-to-deploy conversion by template category
-- =============================================================================

WITH forked_projects AS (
    SELECT
        tf.fork_id,
        tf.project_id,
        pt.category AS template_category,
        tf.created_at AS fork_created_at
    FROM analytics.example_product.template_forks tf
    JOIN analytics.example_product.published_templates pt
        ON pt.template_id = tf.template_id
    WHERE tf.created_at >= DATEADD('day', -30, CURRENT_DATE())
),
fork_deploy_status AS (
    SELECT
        fp.fork_id,
        fp.template_category,
        MAX(CASE WHEN de.status = 'completed' THEN 1 ELSE 0 END) AS was_deployed
    FROM forked_projects fp
    LEFT JOIN analytics.example_product.deploy_events de
        ON de.project_id = fp.project_id
    GROUP BY 1, 2
)

SELECT
    template_category,
    COUNT(*) AS total_forks,
    SUM(was_deployed) AS forks_deployed,
    ROUND(SUM(was_deployed) * 100.0 / NULLIF(COUNT(*), 0), 2) AS fork_to_deploy_pct
FROM fork_deploy_status
GROUP BY 1
ORDER BY fork_to_deploy_pct DESC;
