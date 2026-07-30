-- Domain SSL Health Dashboard Query
-- Snowflake SQL for monitoring certificate health, renewal success, and provisioning performance.
-- Used by: Custom Domains Health Dashboard (Sigma)
-- Owner: Casey Nguyen, Analytics
--
-- Related metrics: metrics/deployment/custom-domains-metrics.md
-- Related schema: schemas/deployment/domain_certificates.md

-- =============================================================================
-- 1. Certificates expiring in the next 30 days
-- =============================================================================
WITH expiring_certs AS (
    SELECT
        dc.id                   AS certificate_id,
        cd.domain               AS domain,
        cd.project_id           AS project_id,
        u.email                 AS owner_email,
        dc.provider             AS provider,
        dc.issued_at            AS issued_at,
        dc.expires_at           AS expires_at,
        dc.auto_renew           AS auto_renew,
        dc.last_renewal_attempt AS last_renewal_attempt,
        dc.status               AS cert_status,
        DATEDIFF('day', CURRENT_TIMESTAMP(), dc.expires_at) AS days_until_expiry
    FROM analytics.example_product.domain_certificates dc
    JOIN analytics.example_product.custom_domains cd ON cd.id = dc.domain_id
    JOIN analytics.example_product.users u ON u.id = cd.user_id
    WHERE dc.status = 'active'
      AND dc.expires_at <= DATEADD('day', 30, CURRENT_TIMESTAMP())
      AND dc.expires_at > CURRENT_TIMESTAMP()
    ORDER BY dc.expires_at ASC
),

-- =============================================================================
-- 2. Renewal success rate (last 90 days)
-- =============================================================================
renewal_stats AS (
    SELECT
        COUNT(*) AS total_renewal_attempts,
        SUM(CASE WHEN dc.status = 'active' THEN 1 ELSE 0 END) AS successful_renewals,
        SUM(CASE WHEN dc.status = 'failed' THEN 1 ELSE 0 END) AS failed_renewals,
        ROUND(
            SUM(CASE WHEN dc.status = 'active' THEN 1 ELSE 0 END) * 100.0
            / NULLIF(COUNT(*), 0),
            2
        ) AS renewal_success_rate_pct
    FROM analytics.example_product.domain_certificates dc
    WHERE dc.last_renewal_attempt >= DATEADD('day', -90, CURRENT_TIMESTAMP())
      AND dc.last_renewal_attempt IS NOT NULL
),

-- =============================================================================
-- 3. Average time-to-provision (SSL provisioning duration)
--    Measured as time from domain DNS verification to certificate issuance
-- =============================================================================
provision_times AS (
    SELECT
        AVG(DATEDIFF('second', cd.updated_at, dc.issued_at))   AS avg_provision_seconds,
        MEDIAN(DATEDIFF('second', cd.updated_at, dc.issued_at)) AS median_provision_seconds,
        PERCENTILE_CONT(0.95) WITHIN GROUP (
            ORDER BY DATEDIFF('second', cd.updated_at, dc.issued_at)
        ) AS p95_provision_seconds,
        COUNT(*) AS total_provisions
    FROM analytics.example_product.domain_certificates dc
    JOIN analytics.example_product.custom_domains cd ON cd.id = dc.domain_id
    WHERE dc.issued_at IS NOT NULL
      AND cd.dns_status = 'verified'
      AND dc.issued_at >= DATEADD('day', -90, CURRENT_TIMESTAMP())
)

-- =============================================================================
-- Final output: combine all three sections
-- =============================================================================
SELECT
    '--- Certificates Expiring Within 30 Days ---' AS section,
    ec.certificate_id,
    ec.domain,
    ec.project_id,
    ec.owner_email,
    ec.expires_at,
    ec.days_until_expiry,
    ec.auto_renew,
    ec.last_renewal_attempt,
    ec.cert_status,
    NULL AS renewal_success_rate_pct,
    NULL AS avg_provision_seconds,
    NULL AS median_provision_seconds,
    NULL AS p95_provision_seconds
FROM expiring_certs ec

UNION ALL

SELECT
    '--- Renewal Success Rate (90d) ---' AS section,
    NULL, NULL, NULL, NULL, NULL,
    rs.total_renewal_attempts,
    NULL,
    NULL,
    NULL,
    rs.renewal_success_rate_pct,
    NULL,
    NULL,
    NULL
FROM renewal_stats rs

UNION ALL

SELECT
    '--- Avg Time-to-Provision (90d) ---' AS section,
    NULL, NULL, NULL, NULL, NULL,
    pt.total_provisions,
    NULL,
    NULL,
    NULL,
    NULL,
    pt.avg_provision_seconds,
    pt.median_provision_seconds,
    pt.p95_provision_seconds
FROM provision_times pt
;
