-- Generation Success Rate Query
-- Calculates daily generation success rate from the project_generations table.
-- Used in the Generation Metrics dashboard (Mode).
--
-- Success = status IN ('completed', 'deployed')
-- Failure = status IN ('failed', 'timeout', 'cancelled')
--
-- Author: Grace Lin, Analytics
-- Last updated: 2026-03-05
--
-- Related metrics: (core platform metric — see CLAUDE.md Core Metrics table)
-- Related schema: schemas/prototyping/project-generations.md

WITH daily_generations AS (
    SELECT
        DATE_TRUNC('day', created_at) AS generation_date,
        COUNT(*) AS total_generations,
        COUNT_IF(status IN ('completed', 'deployed')) AS successful_generations,
        COUNT_IF(status IN ('failed', 'timeout', 'cancelled')) AS failed_generations,
        AVG(generation_time_ms) AS avg_generation_time_ms,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY generation_time_ms) AS p50_generation_time_ms,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY generation_time_ms) AS p95_generation_time_ms
    FROM analytics.example_product.project_generations
    WHERE created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
)

SELECT
    generation_date,
    total_generations,
    successful_generations,
    failed_generations,
    ROUND(successful_generations * 100.0 / NULLIF(total_generations, 0), 2) AS success_rate_pct,
    ROUND(avg_generation_time_ms, 0) AS avg_time_ms,
    ROUND(p50_generation_time_ms, 0) AS p50_time_ms,
    ROUND(p95_generation_time_ms, 0) AS p95_time_ms
FROM daily_generations
ORDER BY generation_date DESC;
