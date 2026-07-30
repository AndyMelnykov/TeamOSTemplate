-- Custom Domain Setup Funnel Completion Rates
-- Author: Casey Nguyen
-- Last Updated: 2026-03-22
--
-- Related metrics: metrics/deployment/custom-domains-metrics.md
-- Related investigation: investigations/deployment/2026-03-18-custom-domain-adoption-funnel.md
-- Related schema: schemas/deployment/domain_certificates.md
--
-- Platform: Snowflake
-- Source tables: analytics.example_product.custom_domains, analytics.example_product.custom_domain_events, analytics.example_product.domain_certificates
-- Recommended schedule: Daily, 06:00 UTC

-- =============================================================================
-- 1. Step funnel: created -> dns_verified -> ssl_provisioned -> live
--    With step-by-step conversion rates
-- =============================================================================
WITH domain_funnel_events AS (
    -- Collect the timestamp of each funnel step per domain
    SELECT
        cd.id AS domain_id,
        cd.user_id,
        cd.domain,
        cd.project_id,
        cd.created_at AS step_created_at,

        -- DNS verification timestamp
        MIN(CASE
            WHEN cde.event_type = 'dns_verified' THEN cde.created_at
        END) AS step_dns_verified_at,

        -- SSL provisioned timestamp (certificate issued)
        MIN(CASE
            WHEN cde.event_type = 'ssl_provisioned' THEN cde.created_at
        END) AS step_ssl_provisioned_at,

        -- Domain went live timestamp
        MIN(CASE
            WHEN cde.event_type = 'live' THEN cde.created_at
        END) AS step_live_at

    FROM analytics.example_product.custom_domains cd
    LEFT JOIN analytics.example_product.custom_domain_events cde
        ON cde.domain_id = cd.id
    WHERE cd.created_at >= DATEADD('day', -90, CURRENT_DATE())
    GROUP BY cd.id, cd.user_id, cd.domain, cd.project_id, cd.created_at
),

-- =============================================================================
-- 2. Subscription tier for each domain owner
-- =============================================================================
user_tiers AS (
    SELECT DISTINCT
        user_id,
        tier AS subscription_tier
    FROM analytics.example_product.subscriptions
    WHERE status = 'active'
),

-- =============================================================================
-- 3. Enrich funnel with tier and compute step flags
-- =============================================================================
funnel_with_tier AS (
    SELECT
        dfe.domain_id,
        dfe.user_id,
        dfe.domain,
        dfe.project_id,
        COALESCE(ut.subscription_tier, 'unknown') AS subscription_tier,
        dfe.step_created_at,
        dfe.step_dns_verified_at,
        dfe.step_ssl_provisioned_at,
        dfe.step_live_at,

        -- Step completion flags
        1 AS reached_created,
        CASE WHEN dfe.step_dns_verified_at IS NOT NULL THEN 1 ELSE 0 END AS reached_dns_verified,
        CASE WHEN dfe.step_ssl_provisioned_at IS NOT NULL THEN 1 ELSE 0 END AS reached_ssl_provisioned,
        CASE WHEN dfe.step_live_at IS NOT NULL THEN 1 ELSE 0 END AS reached_live,

        -- Time between steps (in seconds)
        DATEDIFF('second', dfe.step_created_at, dfe.step_dns_verified_at) AS seconds_created_to_dns,
        DATEDIFF('second', dfe.step_dns_verified_at, dfe.step_ssl_provisioned_at) AS seconds_dns_to_ssl,
        DATEDIFF('second', dfe.step_ssl_provisioned_at, dfe.step_live_at) AS seconds_ssl_to_live,
        DATEDIFF('second', dfe.step_created_at, dfe.step_live_at) AS seconds_created_to_live

    FROM domain_funnel_events dfe
    LEFT JOIN user_tiers ut
        ON ut.user_id = dfe.user_id
)

-- =============================================================================
-- 4. Final output: funnel metrics by subscription tier
-- =============================================================================
SELECT
    subscription_tier,

    -- Step counts
    COUNT(*) AS domains_created,
    SUM(reached_dns_verified) AS domains_dns_verified,
    SUM(reached_ssl_provisioned) AS domains_ssl_provisioned,
    SUM(reached_live) AS domains_live,

    -- Step-by-step conversion rates
    ROUND(
        SUM(reached_dns_verified) * 100.0 / NULLIF(COUNT(*), 0), 2
    ) AS created_to_dns_pct,
    ROUND(
        SUM(reached_ssl_provisioned) * 100.0 / NULLIF(SUM(reached_dns_verified), 0), 2
    ) AS dns_to_ssl_pct,
    ROUND(
        SUM(reached_live) * 100.0 / NULLIF(SUM(reached_ssl_provisioned), 0), 2
    ) AS ssl_to_live_pct,

    -- Overall funnel completion rate
    ROUND(
        SUM(reached_live) * 100.0 / NULLIF(COUNT(*), 0), 2
    ) AS overall_completion_rate_pct,

    -- Median time between steps (in seconds)
    MEDIAN(seconds_created_to_dns) AS median_seconds_created_to_dns,
    MEDIAN(seconds_dns_to_ssl) AS median_seconds_dns_to_ssl,
    MEDIAN(seconds_ssl_to_live) AS median_seconds_ssl_to_live,
    MEDIAN(seconds_created_to_live) AS median_seconds_created_to_live

FROM funnel_with_tier
GROUP BY subscription_tier
ORDER BY
    CASE subscription_tier
        WHEN 'free' THEN 1
        WHEN 'pro' THEN 2
        WHEN 'team' THEN 3
        WHEN 'business' THEN 4
        WHEN 'enterprise' THEN 5
        ELSE 6
    END;
