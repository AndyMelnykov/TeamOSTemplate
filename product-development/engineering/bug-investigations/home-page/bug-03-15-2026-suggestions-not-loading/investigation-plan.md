# Prompt suggestions returning 500 for users with >50 projects

| Field | Value |
|-------|-------|
| Run Date | 2026-03-15 |
| Author | Jordan Kim, Engineer |
| Status | Complete |
| Playbook | [Home Page Error Triage](https://playbooks.internal/home-page-errors) |
| Google Doc | [Investigation: Suggestions 500s](https://docs.google.com/document/d/1abc-suggestions-500) |
| Related Tickets | EXAMPLE_PRODUCT-1042, EXAMPLE_PRODUCT-1058 |

## Objective
Investigate why the prompt suggestions endpoint returns 500 errors for users with large project histories (>50 projects), causing the home page to render without personalized suggestions.

## Background
Datadog alerts fired on 2026-03-14 showing a spike in 500s on `GET /api/home/suggestions`. Initial triage linked the errors to users with >50 projects. The suggestions feature launched 2 weeks prior and was only load-tested with accounts up to 20 projects.

## Impact Scope
- **Affected users:** ~1,200 users (8% of active base) with >50 projects
- **Severity:** P2 — feature degraded, not broken (fallback renders generic suggestions)
- **Duration:** Ongoing since 2026-03-13, partial mitigation via fallback on 2026-03-14

## Infrastructure
- **Service:** `suggestion-engine` microservice (Node.js, deployed on Vercel serverless)
- **Database:** Supabase PostgreSQL — `projects` and `project_metadata` tables
- **Cache:** Redis (Upstash) — suggestion cache layer
- **Monitoring:** Datadog APM, Supabase query performance dashboard

## Results
- The `SuggestionEngine.getRecentProjectTypes()` method runs an unindexed query on `project_metadata` joined with `projects` for the user's full history
- For users with >50 projects, query time exceeds the 5s Vercel function timeout
- Redis cache is never populated because the initial query fails before caching

## Analysis
1. Checked Datadog traces — all 500s originate from `suggestion-engine` with timeout errors
2. Pulled slow query logs from Supabase — the `project_metadata` join takes 6-12s for users with >50 projects
3. Ruled out Redis — cache misses are a symptom, not a cause (never gets populated)
4. Confirmed the query has no index on `project_metadata.user_id`
5. Tested with a 200-project account in staging — consistently times out at 8s

## Root Cause
Missing index on `project_metadata.user_id`. The suggestion query does a sequential scan across the full `project_metadata` table for the user's projects, which scales linearly with project count. Combined with the 5s serverless timeout, this guarantees failure for users above ~45 projects.

## Recommended Fix
1. Add index on `project_metadata.user_id` — immediate fix, should bring query to <200ms
2. Add `LIMIT 10` to the query — suggestions only need recent projects, not all of them
3. Increase Vercel function timeout to 10s as a safety net
4. Add circuit breaker to fall back to generic suggestions if query exceeds 2s

## Cross-Validation
- Verified fix in staging: query drops from 8s to 120ms with index + LIMIT
- Confirmed via Datadog that 500 rate correlates exactly with users having >50 projects
- Cross-checked with Supabase slow query log timestamps matching Datadog error spikes

## Data Examples

| User ID | Project Count | Query Time (before) | Query Time (after) |
|---------|--------------|--------------------|--------------------|
| usr_a8f2 | 52 | 6.2s | 95ms |
| usr_c3d1 | 87 | 9.1s | 110ms |
| usr_f7e9 | 203 | 12.4s | 180ms |
| usr_b1a5 | 15 | 0.8s | 0.4s |

## Executive Summary
The prompt suggestions feature fails for ~1,200 users with >50 projects due to a missing database index causing query timeouts. Add an index on `project_metadata.user_id` and limit the query to the 10 most recent projects. This is a straightforward fix with no architectural changes needed. Deploy the migration, verify in staging, and monitor Datadog for 500 rate drop to zero.

## Appendix

### Query 1: Identify affected users
```sql
SELECT u.id, u.email, COUNT(p.id) as project_count
FROM users u
JOIN projects p ON p.user_id = u.id
GROUP BY u.id, u.email
HAVING COUNT(p.id) > 50
ORDER BY project_count DESC;
```

### Query 2: Slow query causing timeouts
```sql
-- This is the problematic query (before fix)
SELECT pm.project_type, pm.created_at
FROM project_metadata pm
JOIN projects p ON p.id = pm.project_id
WHERE p.user_id = $1
ORDER BY pm.created_at DESC;
```

### Query 3: Fixed query with index and limit
```sql
-- After adding INDEX on project_metadata(user_id) and LIMIT
SELECT pm.project_type, pm.created_at
FROM project_metadata pm
WHERE pm.user_id = $1
ORDER BY pm.created_at DESC
LIMIT 10;
```
