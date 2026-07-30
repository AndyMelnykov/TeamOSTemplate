# Forked template missing image assets from original

| Field | Value |
|-------|-------|
| Run Date | 2026-03-01 |
| Author | Riley Patel, Engineer |
| Status | Complete |
| Playbook | [Asset Pipeline Debugging](https://playbooks.internal/asset-pipeline) |
| Google Doc | [Investigation: Fork Missing Assets](https://docs.google.com/document/d/1vwx-fork-assets) |
| Related Tickets | EXAMPLE_PRODUCT-978, EXAMPLE_PRODUCT-983 |

## Objective
Investigate why forking a community template into a new project results in missing images — broken image placeholders appear where the original template had working images.

## Background
The community marketplace launched in v2.4.0. Users forking templates reported broken images within their new projects. The original templates display images correctly. The issue appears to affect templates that use uploaded images rather than external URLs.

## Impact Scope
- **Affected users:** ~180 users who forked templates with uploaded images since marketplace launch
- **Templates affected:** 23 of 67 published templates (those with uploaded assets)
- **Severity:** P2 — forked projects have broken images, requiring manual re-upload
- **Duration:** Since 2026-02-20 (marketplace launch)

## Infrastructure
- **Service:** `template-service` (Supabase Edge Function)
- **Storage:** Supabase Storage — `project-assets` bucket (source) and per-project folders
- **Database:** Supabase PostgreSQL — `published_templates`, `projects`, `project_assets` tables
- **CDN:** Supabase Storage CDN with signed URLs

## Results
- Template assets are stored in the original author's project folder: `project-assets/{author_project_id}/`
- The fork operation copies project code and config but does NOT copy files from Supabase Storage
- The forked project's code references the original asset paths, which are access-controlled to the original author
- Signed URLs expire after 1 hour, so forked images break immediately for the new user

## Analysis
1. Compared forked project's asset references with storage contents — no files exist in the forked project's storage folder
2. Checked `forkTemplate()` in `src/services/template_service.ts` — it copies `project_state` JSON but has no storage copy step
3. Asset URLs in `project_state` are absolute paths to the author's storage folder
4. Verified that Supabase Storage RLS policies restrict access to the project owner
5. Even if paths were public, they point to the wrong folder — the fork needs its own copies

## Root Cause
The `forkTemplate()` function copies the project state (code, config, component tree) but does not copy the associated files from Supabase Storage. Image references in the forked project still point to the original author's storage folder, which is access-restricted. The fork operation was built for code-only templates and never accounted for uploaded assets.

## Recommended Fix
1. Add asset copy step to `forkTemplate()`:
   - List all files in source project's storage folder
   - Copy each file to the new project's folder in `project-assets/{new_project_id}/`
   - Rewrite asset URLs in `project_state` to point to the new paths
2. Add `asset_count` field to `published_templates` to show users how many assets will be copied
3. Show a progress indicator during fork if >5 assets need copying
4. Backfill: offer affected users a "re-fork" button that copies assets from the original

## Cross-Validation
- Reproduced in staging: fork template with 3 uploaded images → all 3 show as broken
- Applied fix in staging: assets copied to new folder, URLs rewritten → all images load
- Verified storage RLS policies correctly block cross-user access (confirming this isn't just a permissions fix)

## Data Examples

| Template | Assets | Forks | Forks with Broken Images |
|----------|--------|-------|-------------------------|
| SaaS Dashboard Pro | 8 | 34 | 34 (100%) |
| Portfolio Starter | 5 | 29 | 29 (100%) |
| E-commerce Kit | 12 | 18 | 18 (100%) |
| Blog Starter | 0 | 45 | 0 (0%) |

## Executive Summary
Forking a template doesn't copy uploaded image assets from Supabase Storage — it only copies the project code, which still references the original author's access-restricted files. Add a storage copy step to `forkTemplate()` that duplicates assets to the new project's folder and rewrites URLs. This affects 180 users across 23 templates. Templates without uploaded images (external URLs only) are unaffected.

## Appendix

### Query 1: Templates with uploaded assets
```sql
SELECT pt.id, pt.title, pt.author_id,
       COUNT(pa.id) as asset_count
FROM published_templates pt
LEFT JOIN project_assets pa ON pa.project_id = pt.source_project_id
  AND pa.asset_type = 'uploaded'
GROUP BY pt.id, pt.title, pt.author_id
HAVING COUNT(pa.id) > 0
ORDER BY asset_count DESC;
```

### Query 2: Forks with broken asset references
```sql
SELECT p.id as forked_project_id, p.user_id, p.forked_from_template_id,
       COUNT(pa.id) as missing_assets
FROM projects p
JOIN published_templates pt ON pt.id = p.forked_from_template_id
JOIN project_assets pa ON pa.project_id = pt.source_project_id
  AND pa.asset_type = 'uploaded'
LEFT JOIN project_assets pa_fork ON pa_fork.project_id = p.id
  AND pa_fork.filename = pa.filename
WHERE pa_fork.id IS NULL
  AND p.created_at > '2026-02-20'
GROUP BY p.id, p.user_id, p.forked_from_template_id
ORDER BY missing_assets DESC;
```
