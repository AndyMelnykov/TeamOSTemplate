# Forked template missing branding assets from original

| Field | Value |
|-------|-------|
| Run Date | 2026-03-01 |
| Author | Riley Patel, Engineer |
| Status | Complete |
| Playbook | [Asset Pipeline Debugging](https://playbooks.internal/asset-pipeline) |
| Google Doc | [Investigation: Fork Missing Assets](https://docs.google.com/document/d/1vwx-fork-assets) |
| Related Tickets | EXAMPLE_PRODUCT-978, EXAMPLE_PRODUCT-983 |

## Objective
Investigate why forking a community template into a new workflow results in missing branding assets — broken logo/letterhead placeholders appear where the original template had working images.

## Background
The community marketplace launched in v2.4.0. Users forking templates (e.g. a vendor-onboarding or NDA template shared by another team) reported broken logos and letterhead images within their new workflow's portal. The original templates display images correctly. The issue appears to affect templates that use uploaded branding assets rather than externally hosted image URLs.

## Impact Scope
- **Affected users:** ~180 users who forked templates with uploaded branding assets since marketplace launch
- **Templates affected:** 23 of 67 published templates (those with uploaded assets)
- **Severity:** P2 — forked workflows have broken branding, requiring manual re-upload
- **Duration:** Since 2026-02-20 (marketplace launch)

## Infrastructure
- **Service:** `template-service` (Supabase Edge Function)
- **Storage:** Supabase Storage — `workflow-assets` bucket (source) and per-workflow folders
- **Database:** Supabase PostgreSQL — `published_templates`, `workflows`, `workflow_assets` tables
- **CDN:** Supabase Storage CDN with signed URLs

## Results
- Template assets are stored in the original author's workflow folder: `workflow-assets/{author_workflow_id}/`
- The fork operation copies workflow config (fields, routing, signature steps) but does NOT copy files from Supabase Storage
- The forked workflow's config references the original asset paths, which are access-controlled to the original author
- Signed URLs expire after 1 hour, so forked branding assets break immediately for the new user

## Analysis
1. Compared forked workflow's asset references with storage contents — no files exist in the forked workflow's storage folder
2. Checked `forkTemplate()` in `src/services/template_service.ts` — it copies `workflow_state` JSON but has no storage copy step
3. Asset URLs in `workflow_state` are absolute paths to the author's storage folder
4. Verified that Supabase Storage RLS policies restrict access to the workflow owner
5. Even if paths were public, they point to the wrong folder — the fork needs its own copies

## Root Cause
The `forkTemplate()` function copies the workflow state (fields, routing rules, signature configuration) but does not copy the associated files from Supabase Storage. Branding asset references (logo, letterhead) in the forked workflow still point to the original author's storage folder, which is access-restricted. The fork operation was built for logic-only templates and never accounted for uploaded branding assets.

## Recommended Fix
1. Add asset copy step to `forkTemplate()`:
   - List all files in source workflow's storage folder
   - Copy each file to the new workflow's folder in `workflow-assets/{new_workflow_id}/`
   - Rewrite asset URLs in `workflow_state` to point to the new paths
2. Add `asset_count` field to `published_templates` to show users how many branding assets will be copied
3. Show a progress indicator during fork if >5 assets need copying
4. Backfill: offer affected users a "re-fork" button that copies assets from the original

## Cross-Validation
- Reproduced in staging: fork template with 3 uploaded branding assets → all 3 show as broken
- Applied fix in staging: assets copied to new folder, URLs rewritten → all images load
- Verified storage RLS policies correctly block cross-user access (confirming this isn't just a permissions fix)

## Data Examples

| Template | Assets | Forks | Forks with Broken Branding |
|----------|--------|-------|-------------------------|
| Vendor Onboarding Pro | 8 | 34 | 34 (100%) |
| Sales Contract Starter | 5 | 29 | 29 (100%) |
| Invoice Automation Kit | 12 | 18 | 18 (100%) |
| Basic NDA | 0 | 45 | 0 (0%) |

## Executive Summary
Forking a template doesn't copy uploaded branding assets from Supabase Storage — it only copies the workflow config, which still references the original author's access-restricted files. Add a storage copy step to `forkTemplate()` that duplicates assets to the new workflow's folder and rewrites URLs. This affects 180 users across 23 templates. Templates without uploaded branding assets (external URLs only) are unaffected.

## Appendix

### Query 1: Templates with uploaded assets
```sql
SELECT pt.id, pt.title, pt.author_id,
       COUNT(wa.id) as asset_count
FROM published_templates pt
LEFT JOIN workflow_assets wa ON wa.workflow_id = pt.source_workflow_id
  AND wa.asset_type = 'uploaded'
GROUP BY pt.id, pt.title, pt.author_id
HAVING COUNT(wa.id) > 0
ORDER BY asset_count DESC;
```

### Query 2: Forks with broken asset references
```sql
SELECT w.id as forked_workflow_id, w.user_id, w.forked_from_template_id,
       COUNT(wa.id) as missing_assets
FROM workflows w
JOIN published_templates pt ON pt.id = w.forked_from_template_id
JOIN workflow_assets wa ON wa.workflow_id = pt.source_workflow_id
  AND wa.asset_type = 'uploaded'
LEFT JOIN workflow_assets wa_fork ON wa_fork.workflow_id = w.id
  AND wa_fork.filename = wa.filename
WHERE wa_fork.id IS NULL
  AND w.created_at > '2026-02-20'
GROUP BY w.id, w.user_id, w.forked_from_template_id
ORDER BY missing_assets DESC;
```
