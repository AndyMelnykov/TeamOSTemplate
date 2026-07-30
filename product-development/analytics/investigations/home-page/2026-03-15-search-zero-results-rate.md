# Investigation: High Zero-Results Rate in Project Search

| Field | Value |
|-------|-------|
| Run Date | 2026-03-15 |
| Author | Casey Nguyen, Analytics |
| Status | Complete |
| Related Tickets | EXAMPLE_PRODUCT-1055 |
| Dashboard | [Search Health](https://app.sigmacomputing.com/example_product-labs/workbook/search-health) |

---

## Objective

Investigate why the zero-results rate for Project Search (Cmd+K) is elevated at 23%, well above the 15% target established in the PRD. Identify the root causes driving empty search results and recommend actionable improvements to the search system.

## Methodology

1. Pulled all search events from the beta rollout period (2026-03-01 through 2026-03-14) -- 12,847 total search queries from 1,923 unique users.
2. Segmented zero-result queries by query text patterns, user tier, and session context.
3. Manually categorized a random sample of 200 zero-result queries into root cause buckets.
4. Cross-referenced zero-result queries against existing project names, template titles, and action descriptions to identify near-misses.
5. Analyzed click-through behavior on sessions that included both zero-result and successful searches to understand recovery patterns.

## Key Findings

### Finding 1: 23% of all searches return zero results

During the beta period, 2,955 out of 12,847 searches returned no results. This breaks down as follows:

| Root Cause | % of Zero-Result Queries | Example Queries |
|------------|-------------------------|-----------------|
| Misspellings / typos | 38% | "dashbaord", "landign page", "ecomerce" |
| Component-level searches | 24% | "navbar", "sidebar", "login form", "pricing table" |
| Framework or library names | 15% | "next.js", "tailwind", "shadcn", "prisma" |
| Overly specific phrases | 12% | "my project from tuesday", "the one with the blue header" |
| Non-existent content | 11% | "mobile app", "flutter template", "iOS" |

### Finding 2: Misspellings account for the largest share

38% of zero-result searches are near-misses caused by typos. The current search implementation uses PostgreSQL `plainto_tsquery` which requires exact token matches. Common misspellings:

| Misspelled Query | Intended Match | Frequency |
|-----------------|----------------|-----------|
| "dashbaord" | "dashboard" | 87 |
| "landign" | "landing" | 52 |
| "ecomerce" / "ecommrce" | "e-commerce" | 41 |
| "portfoilo" | "portfolio" | 29 |
| "admni" | "admin" | 23 |

### Finding 3: Component-level searches reveal an indexing gap

24% of zero-result searches are for UI component names ("navbar", "sidebar", "login form", "pricing table"). These searches fail because the search index only covers project names, descriptions, and template titles. It does not index the individual components or page elements within projects or templates.

| Component Query | Frequency | Templates That Should Match |
|----------------|-----------|---------------------------|
| "navbar" | 64 | SaaS Dashboard, Landing Page, Portfolio |
| "login form" | 48 | SaaS Dashboard, Admin Panel |
| "pricing table" | 37 | Landing Page, SaaS Marketing |
| "sidebar" | 31 | Admin Panel, Dashboard Starter |
| "chart" / "charts" | 28 | Analytics Dashboard, SaaS Dashboard |

### Finding 4: Zero-results sessions have lower retention

Users who encounter a zero-result search in their first session are 34% less likely to return within 7 days compared to users whose first search returned results (D7 retention: 31% vs 47%).

### Finding 5: Recovery behavior is promising

62% of users who hit a zero-result search immediately try a different query. Of those who retry, 71% find results on their second attempt. This suggests users are motivated to search but the system is failing to meet their intent on the first try.

## Data Summary

| Metric | Value |
|--------|-------|
| Total searches (beta period) | 12,847 |
| Unique searchers | 1,923 |
| Zero-result searches | 2,955 (23.0%) |
| Zero-result unique users | 847 (44.0% of searchers) |
| Avg queries per zero-result session | 2.4 |
| Recovery rate (successful retry) | 44% (71% of the 62% who retry) |

## Recommendations

### R1: Add fuzzy matching (Priority: P0)

Implement PostgreSQL `pg_trgm` trigram matching as a fallback when `plainto_tsquery` returns zero results. This would catch misspellings with edit distance <= 2, addressing 38% of zero-result queries. Estimated impact: reduces zero-results rate from 23% to ~15%.

**Implementation:** Add a `title_trigram` GIN index on `search_index.title` using `gin_trgm_ops`. When the primary tsquery returns zero results, fall back to `similarity(title, :query) > 0.3` ordered by similarity score.

### R2: Index component and element names (Priority: P1)

Expand the `search_index` to include component-level content from templates. Add a `components` text field to the search index populated from template metadata. This addresses 24% of zero-result queries.

**Implementation:** Add a new field to the `search_index.metadata` JSONB column containing an array of component names extracted from each template's manifest. Include these in the `search_vector` with weight 'C'.

### R3: Add "did you mean" suggestions (Priority: P2)

When a search returns zero results, show a "Did you mean: [suggestion]?" prompt based on trigram similarity to existing indexed content. This improves the recovery experience even for queries that fuzzy matching alone cannot resolve.

### R4: Track zero-result queries for template gap analysis (Priority: P1)

Pipe zero-result queries that fall into the "non-existent content" bucket (11%) into a weekly report for the product team. Queries like "mobile app", "flutter template", and "iOS" signal demand for content types example_product does not yet support.

---

## Appendix

### Query A: Zero-results rate by day

```sql
SELECT
    DATE_TRUNC('day', created_at) AS search_date,
    COUNT(*) AS total_searches,
    COUNT_IF(is_zero_results = TRUE) AS zero_result_searches,
    ROUND(COUNT_IF(is_zero_results = TRUE) * 100.0 / COUNT(*), 2) AS zero_results_rate_pct
FROM analytics.example_product.search_events
WHERE created_at BETWEEN '2026-03-01' AND '2026-03-15'
GROUP BY 1
ORDER BY 1;
```

### Query B: Top zero-result query patterns

```sql
WITH zero_result_queries AS (
    SELECT
        LOWER(TRIM(query_text)) AS normalized_query,
        COUNT(*) AS frequency,
        COUNT(DISTINCT user_id) AS unique_users
    FROM analytics.example_product.search_events
    WHERE created_at BETWEEN '2026-03-01' AND '2026-03-15'
      AND is_zero_results = TRUE
    GROUP BY 1
)

SELECT
    normalized_query,
    frequency,
    unique_users,
    ROUND(frequency * 100.0 / SUM(frequency) OVER (), 2) AS pct_of_zero_results
FROM zero_result_queries
ORDER BY frequency DESC
LIMIT 50;
```

---

## Related Resources

| Resource | Path |
|----------|------|
| Metrics definition | [project-search-metrics.md](../../metrics/home-page/project-search-metrics.md) |
| SQL query | [search-usage.sql](../../queries/home-page/search-usage.sql) |
| Schema | [search_events.md](../../schemas/home-page/search_events.md) |
