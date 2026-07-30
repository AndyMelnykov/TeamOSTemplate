# Project card thumbnails showing outdated screenshots

| Field | Value |
|-------|-------|
| Run Date | 2026-03-08 |
| Author | Sam Chen, Engineer |
| Status | Complete |
| Playbook | [Asset Pipeline Debugging](https://playbooks.internal/asset-pipeline) |
| Google Doc | [Investigation: Stale Thumbnails](https://docs.google.com/document/d/1def-stale-thumbnails) |
| Related Tickets | EXAMPLE_PRODUCT-987, EXAMPLE_PRODUCT-1003 |

## Objective
Investigate why project card thumbnails on the home page show outdated screenshots that don't reflect recent edits, even after multiple generations.

## Background
Users reported via support (5 tickets in one week) that their project thumbnails on the home page look nothing like the current state of their project. The thumbnail generation pipeline was last updated in January 2026 when we switched screenshot providers.

## Impact Scope
- **Affected users:** ~3,400 users (22% of active base) — any user who edited a project after 2026-02-15
- **Severity:** P3 — cosmetic issue, no data loss or functional impact
- **Duration:** Since 2026-02-15 (screenshot provider migration), discovered 2026-03-05

## Infrastructure
- **Service:** `thumbnail-worker` (background job on Vercel cron)
- **Storage:** Supabase Storage bucket `project-thumbnails`
- **CDN:** Vercel Edge Network with aggressive caching (Cache-Control: max-age=86400)
- **Screenshot provider:** Screenshotone API (migrated from Urlbox in Feb 2026)

## Results
- Thumbnails are generated correctly by the new provider
- The generated screenshots are uploaded to Supabase Storage with the correct file names
- However, the CDN serves stale cached versions because the cache key hasn't changed
- The old provider used versioned URLs (`?v=timestamp`), the new one uses the same static URL

## Analysis
1. Confirmed new screenshots are generated — checked Supabase Storage directly, files are current
2. Compared CDN response headers — `x-vercel-cache: HIT` with `age: 604800` (7 days stale)
3. Found the migration PR (#482) — removed the `?v=` query param when switching providers
4. The old URL pattern was `/thumbnails/{project_id}.png?v={updated_at}`, new pattern is `/thumbnails/{project_id}.png`
5. Without the version param, CDN has no reason to refetch

## Root Cause
During the Screenshotone migration (PR #482), the URL versioning query parameter (`?v={updated_at}`) was removed. The CDN caches thumbnails for 24 hours by default, but without URL busting, even users who wait 24 hours may get a stale edge cache from a different PoP.

## Recommended Fix
1. Restore cache-busting query param: append `?v={project.updated_at}` to thumbnail URLs
2. Purge existing CDN cache for the `project-thumbnails` path
3. Reduce `max-age` to 3600 (1 hour) for thumbnail assets specifically
4. Add `stale-while-revalidate=86400` so users see something while refreshing

## Cross-Validation
- Manually busted cache for 3 test projects — all showed updated thumbnails immediately
- Verified Supabase Storage has correct current screenshots for sampled projects
- Confirmed CDN purge API works for the thumbnail path prefix

## Data Examples

| Project ID | Last Edit | Thumbnail Date | Stale By |
|-----------|-----------|---------------|----------|
| prj_x8a2 | 2026-03-07 | 2026-02-16 | 19 days |
| prj_k3f1 | 2026-03-05 | 2026-02-20 | 13 days |
| prj_m9c7 | 2026-03-08 | 2026-02-15 | 21 days |

## Executive Summary
Project thumbnails appear stale because a cache-busting query parameter was dropped during the screenshot provider migration in February. The CDN serves old cached versions indefinitely. Restore the `?v={updated_at}` param on thumbnail URLs, purge the CDN cache, and reduce cache TTL to 1 hour. No backend or database changes needed — this is a frontend URL fix plus a one-time cache purge.

## Appendix

### Query 1: Projects with stale thumbnails
```sql
SELECT p.id, p.name, p.updated_at, pt.generated_at,
       EXTRACT(DAY FROM p.updated_at - pt.generated_at) as stale_days
FROM projects p
JOIN project_thumbnails pt ON pt.project_id = p.id
WHERE p.updated_at > pt.generated_at
  AND p.updated_at > '2026-02-15'
ORDER BY stale_days DESC
LIMIT 50;
```

### Query 2: Thumbnail generation success rate since migration
```sql
SELECT DATE(created_at) as date,
       COUNT(*) as total_jobs,
       COUNT(*) FILTER (WHERE status = 'success') as success,
       COUNT(*) FILTER (WHERE status = 'failed') as failed
FROM thumbnail_jobs
WHERE created_at > '2026-02-15'
GROUP BY DATE(created_at)
ORDER BY date;
```
