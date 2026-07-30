-- Search Usage Metrics
-- Calculates daily search usage rate, zero-results rate, and average results
-- per query from the search_events table.
-- Used in the Search Health dashboard (Sigma).
--
-- Usage rate = distinct searchers / DAU
-- Zero-results rate = searches with 0 results / total searches
-- Avg results = mean result_count across all searches
--
-- Author: Casey Nguyen, Analytics
-- Last updated: 2026-03-22
--
-- Related metrics: metrics/home-page/project-search-metrics.md
-- Related schema: schemas/home-page/search_events.md

WITH daily_searches AS (
    SELECT
        DATE_TRUNC('day', created_at) AS search_date,
        COUNT(*) AS total_searches,
        COUNT(DISTINCT user_id) AS distinct_searchers,
        COUNT_IF(is_zero_results = TRUE) AS zero_result_searches,
        COUNT_IF(clicked_result_id IS NOT NULL) AS searches_with_click,
        AVG(result_count) AS avg_results_per_query,
        AVG(search_latency_ms) AS avg_latency_ms,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY search_latency_ms) AS p95_latency_ms
    FROM analytics.example_product.search_events
    WHERE created_at >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
),

daily_active AS (
    SELECT
        DATE_TRUNC('day', event_date) AS active_date,
        COUNT(DISTINCT user_id) AS dau
    FROM analytics.example_product.daily_active_users
    WHERE event_date >= DATEADD('day', -30, CURRENT_DATE())
    GROUP BY 1
)

SELECT
    ds.search_date,
    ds.total_searches,
    ds.distinct_searchers,
    da.dau,
    ROUND(ds.distinct_searchers * 100.0 / NULLIF(da.dau, 0), 2) AS search_usage_rate_pct,
    ds.zero_result_searches,
    ROUND(ds.zero_result_searches * 100.0 / NULLIF(ds.total_searches, 0), 2) AS zero_results_rate_pct,
    ds.searches_with_click,
    ROUND(ds.searches_with_click * 100.0 / NULLIF(ds.total_searches, 0), 2) AS click_through_rate_pct,
    ROUND(ds.avg_results_per_query, 1) AS avg_results_per_query,
    ROUND(ds.avg_latency_ms, 0) AS avg_latency_ms,
    ROUND(ds.p95_latency_ms, 0) AS p95_latency_ms
FROM daily_searches ds
LEFT JOIN daily_active da
    ON ds.search_date = da.active_date
ORDER BY ds.search_date DESC;
