# Restoring old version drops custom components

| Field | Value |
|-------|-------|
| Run Date | 2026-03-18 |
| Author | Morgan Wu, Engineer |
| Status | In Progress |
| Playbook | [Data Integrity Triage](https://playbooks.internal/data-integrity) |
| Google Doc | [Investigation: Version Restore Data Loss](https://docs.google.com/document/d/1mno-version-restore) |
| Related Tickets | EXAMPLE_PRODUCT-1071, EXAMPLE_PRODUCT-1075, EXAMPLE_PRODUCT-1082 |

## Objective
Investigate why restoring a previous project version removes custom components that were saved to the user's component library, even though the library is supposed to be independent of project versions.

## Background
Version history launched in v2.5.0 (2026-03-10). Within a week, 3 users reported that restoring an old version deleted components they'd saved to their personal library. The component library stores components separately from projects, but the restore operation appears to be overwriting the library entries.

## Impact Scope
- **Affected users:** 14 users who performed a version restore on projects containing saved components
- **Components lost:** 37 components across those users permanently deleted
- **Severity:** P1 — data loss, user-created content destroyed
- **Duration:** Since 2026-03-10 (version history launch)

## Infrastructure
- **Service:** `project-service` (Node.js on Vercel serverless)
- **Database:** Supabase PostgreSQL — `project_versions`, `projects`, `saved_components` tables
- **Storage:** Supabase Storage — `component-assets` bucket
- **Feature flag:** `version_history_enabled` (rolled out 100% on 2026-03-10)

## Results
- The restore function (`ProjectService.restoreVersion()`) overwrites the entire `project_state` JSON column
- `project_state` contains a `components` array that was originally just inline components
- When the component library feature launched, saved components were added to this same `components` array with a `saved: true` flag
- Restoring an old version replaces the array with the snapshot, which doesn't include components saved after that version

## Analysis
1. Read `restoreVersion()` in `src/services/project_service.ts` — it does a full replacement of `project_state`
2. Checked the `saved_components` table — components are stored there AND referenced in `project_state.components`
3. Found that `saveComponent()` writes to both `saved_components` table and appends to `project_state.components`
4. Restoring a version overwrites `project_state`, removing the reference — and then a cleanup job deletes orphaned `saved_components` entries
5. The orphan cleanup job (`cleanOrphanedComponents`) runs every hour and deletes `saved_components` rows with no matching `project_state` reference

## Root Cause
Dual-write architecture conflict. Components are stored in both `saved_components` table and embedded in `project_state.components`. When a version restore overwrites `project_state`, the saved component references are lost. The orphan cleanup cron job then deletes the `saved_components` rows because they no longer have a project reference, causing permanent data loss.

## Recommended Fix
1. **Immediate:** Disable the orphan cleanup cron job to prevent further data loss
2. **Short-term:** Update `restoreVersion()` to preserve entries in `project_state.components` where `saved: true`
3. **Long-term:** Remove component references from `project_state` entirely — `saved_components` table should be the single source of truth
4. **Data recovery:** Restore deleted components from Supabase point-in-time backup for the 14 affected users

## Cross-Validation
- Reproduced in staging: save component → create new version → restore old version → component disappears after cleanup job runs
- Confirmed `saved_components` rows are deleted by the cleanup job via database audit logs
- Verified point-in-time backup contains the deleted components for recovery

## Data Examples

| User ID | Components Before Restore | Components After Restore | Lost |
|---------|--------------------------|-------------------------|------|
| usr_d4e5 | 8 | 5 | 3 |
| usr_g7h8 | 12 | 6 | 6 |
| usr_j1k2 | 5 | 2 | 3 |

## Executive Summary
Version restore causes permanent data loss by overwriting project state that contains component library references. An orphan cleanup job then deletes the now-unreferenced saved components. Immediately disable the cleanup job, patch restore to preserve saved components, and recover lost data from backups for 14 affected users (37 components). The root cause is a dual-write architecture that should be refactored to use `saved_components` as the single source of truth.

## Appendix

### Query 1: Users affected by component loss after restore
```sql
SELECT pv.user_id, pv.project_id, pv.restored_at,
       COUNT(sc.id) as components_deleted
FROM project_versions pv
JOIN audit_log al ON al.entity_type = 'saved_component'
  AND al.action = 'delete'
  AND al.created_at BETWEEN pv.restored_at AND pv.restored_at + INTERVAL '2 hours'
  AND al.user_id = pv.user_id
JOIN saved_components sc ON sc.id = al.entity_id
WHERE pv.restored_at > '2026-03-10'
GROUP BY pv.user_id, pv.project_id, pv.restored_at
ORDER BY components_deleted DESC;
```

### Query 2: Orphaned component cleanup job activity
```sql
SELECT DATE(run_at) as date, deleted_count
FROM cron_job_runs
WHERE job_name = 'cleanOrphanedComponents'
  AND run_at > '2026-03-10'
ORDER BY run_at;
```
