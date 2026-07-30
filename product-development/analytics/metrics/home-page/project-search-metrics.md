# Project Search (Cmd+K) - Metrics Definition

**Feature:** Project Search
**Owner:** Hannah Stulberg, PM
**Analytics Lead:** Casey Nguyen

# Primary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Search usage rate | % of DAU who execute at least one search per day | > 20% | `search_events` table, `daily_active_users` |
| Zero-results rate | % of search queries that return zero results | < 15% | `search_events` WHERE `is_zero_results = TRUE` |
| Click-through rate (CTR) | % of search queries where the user clicks at least one result | > 45% | `search_events` WHERE `clicked_result_id IS NOT NULL` |

# Secondary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Queries per session | Average number of search queries per user session | Tracking (higher = engagement) | `search_events` grouped by `session_id` |
| Time-to-click | Median milliseconds from search execution to result click | < 3000ms | `search_events.time_to_click_ms` |
| Search-to-project-open rate | % of search sessions that result in a project being opened | > 35% | `search_events` joined with `project_open_events` |
| Repeat search rate | % of users who search again within 7 days of first search | > 50% | `search_events` cohort analysis |
| Filter usage rate | % of search queries with at least one filter applied | Tracking | `search_events` WHERE `filters_applied != '{}'` |

# Data Sources

- **`search_events`** -- Primary event table in Snowflake (`analytics.example_product.search_events`), populated via Segment -> Snowpipe pipeline
- **`daily_active_users`** -- DAU table derived from session events, used as denominator for usage rate
- **`project_open_events`** -- Downstream event tracking project opens, joined by `user_id` and time window
- **`users`** -- User profile data for segmentation by tier, signup date, org membership

# Dashboard Links

- [Search Health Dashboard](https://app.sigmacomputing.com/example_product-labs/workbook/search-health) -- Real-time search usage, zero-results rate, latency percentiles (Sigma)
- [Search Experiments](https://analytics.amplitude.com/example_product-labs/dashboard/search-experiments) -- A/B test results and feature flag rollout metrics (Amplitude)
- [Search Funnel](https://app.mode.com/example_product-labs/reports/search-funnel) -- Detailed funnel analysis from modal open to project engagement (Mode)

## Related Queries

| Query | Description |
|-------|-------------|
| [search-usage.sql](../../queries/home-page/search-usage.sql) | Daily search metrics with latency percentiles |

## Related Investigations

| Investigation | Date | Summary |
|--------------|------|---------|
| [2026-03-15-search-zero-results-rate.md](../../investigations/home-page/2026-03-15-search-zero-results-rate.md) | 2026-03-15 | Search zero-results rate investigation |
