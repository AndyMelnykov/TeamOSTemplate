-- Version Restore Rate and Versions Per Project
-- Calculates daily version restore rate (restores / active projects)
-- and average versions per project.
-- Used in the Version History Feature Board (Mode).
--
-- Author: Casey Nguyen, Analytics
-- Last updated: 2026-03-22
--
-- Related metrics: metrics/prototyping/version-history-metrics.md
-- Related schema: schemas/prototyping/project_versions.md

-- Daily restore rate: restores / active projects with at least one version
WITH daily_restores AS (
    SELECT
        DATE_TRUNC('day', created_at) AS event_date,
        COUNT(DISTINCT CASE WHEN action = 'restore' THEN project_id END) AS projects_with_restore,
        COUNT(CASE WHEN action = 'restore' THEN 1 END) AS total_restores
    FROM analytics.example_product.project_versions
    WHERE created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
),

daily_active_projects AS (
    SELECT
        DATE_TRUNC('day', created_at) AS event_date,
        COUNT(DISTINCT project_id) AS active_projects
    FROM analytics.example_product.project_versions
    WHERE created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
),

-- Average versions per project (rolling 30-day window)
versions_per_project AS (
    SELECT
        project_id,
        COUNT(*) AS version_count
    FROM analytics.example_product.project_versions
    WHERE created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
)

SELECT
    dap.event_date,
    dap.active_projects,
    COALESCE(dr.total_restores, 0) AS total_restores,
    COALESCE(dr.projects_with_restore, 0) AS projects_with_restore,
    ROUND(
        COALESCE(dr.projects_with_restore, 0) * 100.0
        / NULLIF(dap.active_projects, 0),
        2
    ) AS restore_rate_pct,
    ROUND(AVG(vpp.version_count), 2) AS avg_versions_per_project
FROM daily_active_projects dap
LEFT JOIN daily_restores dr
    ON dap.event_date = dr.event_date
CROSS JOIN versions_per_project vpp
GROUP BY
    dap.event_date,
    dap.active_projects,
    dr.total_restores,
    dr.projects_with_restore
ORDER BY dap.event_date DESC;
