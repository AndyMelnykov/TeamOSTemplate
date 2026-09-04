# Restoring old version drops saved clause/field blocks

| Field | Value |
|-------|-------|
| Run Date | 2026-03-18 |
| Author | Morgan Wu, Engineer |
| Status | In Progress |
| Playbook | [Data Integrity Triage](https://playbooks.internal/data-integrity) |
| Google Doc | [Investigation: Version Restore Data Loss](https://docs.google.com/document/d/1mno-version-restore) |
| Related Tickets | EXAMPLE_PRODUCT-1071, EXAMPLE_PRODUCT-1075, EXAMPLE_PRODUCT-1082 |

## Objective
Investigate why restoring a previous workflow version removes clause/field blocks that were saved to the user's reusable block library, even though the library is supposed to be independent of workflow versions.

## Background
Version history launched in v2.5.0 (2026-03-10). Within a week, 3 users reported that restoring an old version deleted blocks they'd saved to their personal clause/field block library. The block library stores blocks separately from workflows, but the restore operation appears to be overwriting the library entries.

## Impact Scope
- **Affected users:** 14 users who performed a version restore on workflows containing saved blocks
- **Blocks lost:** 37 clause/field blocks across those users permanently deleted
- **Severity:** P1 — data loss, user-created content destroyed
- **Duration:** Since 2026-03-10 (version history launch)

## Infrastructure
- **Service:** `workflow-service` (Node.js on Vercel serverless)
- **Database:** Supabase PostgreSQL — `workflow_versions`, `workflows`, `saved_blocks` tables
- **Storage:** Supabase Storage — `block-assets` bucket
- **Feature flag:** `version_history_enabled` (rolled out 100% on 2026-03-10)

## Results
- The restore function (`WorkflowService.restoreVersion()`) overwrites the entire `workflow_state` JSON column
- `workflow_state` contains a `blocks` array that was originally just inline clause/field blocks
- When the block library feature launched, saved blocks were added to this same `blocks` array with a `saved: true` flag
- Restoring an old version replaces the array with the snapshot, which doesn't include blocks saved after that version

## Analysis
1. Read `restoreVersion()` in `src/services/workflow_service.ts` — it does a full replacement of `workflow_state`
2. Checked the `saved_blocks` table — blocks are stored there AND referenced in `workflow_state.blocks`
3. Found that `saveBlock()` writes to both `saved_blocks` table and appends to `workflow_state.blocks`
4. Restoring a version overwrites `workflow_state`, removing the reference — and then a cleanup job deletes orphaned `saved_blocks` entries
5. The orphan cleanup job (`cleanOrphanedBlocks`) runs every hour and deletes `saved_blocks` rows with no matching `workflow_state` reference

## Root Cause
Dual-write architecture conflict. Blocks are stored in both `saved_blocks` table and embedded in `workflow_state.blocks`. When a version restore overwrites `workflow_state`, the saved block references are lost. The orphan cleanup cron job then deletes the `saved_blocks` rows because they no longer have a workflow reference, causing permanent data loss.

## Recommended Fix
1. **Immediate:** Disable the orphan cleanup cron job to prevent further data loss
2. **Short-term:** Update `restoreVersion()` to preserve entries in `workflow_state.blocks` where `saved: true`
3. **Long-term:** Remove block references from `workflow_state` entirely — `saved_blocks` table should be the single source of truth
4. **Data recovery:** Restore deleted blocks from Supabase point-in-time backup for the 14 affected users

## Cross-Validation
- Reproduced in staging: save block → create new version → restore old version → block disappears after cleanup job runs
- Confirmed `saved_blocks` rows are deleted by the cleanup job via database audit logs
- Verified point-in-time backup contains the deleted blocks for recovery

## Data Examples

| User ID | Blocks Before Restore | Blocks After Restore | Lost |
|---------|--------------------------|-------------------------|------|
| usr_d4e5 | 8 | 5 | 3 |
| usr_g7h8 | 12 | 6 | 6 |
| usr_j1k2 | 5 | 2 | 3 |

## Executive Summary
Version restore causes permanent data loss by overwriting workflow state that contains clause/field block library references. An orphan cleanup job then deletes the now-unreferenced saved blocks. Immediately disable the cleanup job, patch restore to preserve saved blocks, and recover lost data from backups for 14 affected users (37 blocks). The root cause is a dual-write architecture that should be refactored to use `saved_blocks` as the single source of truth.

## Appendix

### Query 1: Users affected by block loss after restore
```sql
SELECT wv.user_id, wv.workflow_id, wv.restored_at,
       COUNT(sb.id) as blocks_deleted
FROM workflow_versions wv
JOIN audit_log al ON al.entity_type = 'saved_block'
  AND al.action = 'delete'
  AND al.created_at BETWEEN wv.restored_at AND wv.restored_at + INTERVAL '2 hours'
  AND al.user_id = wv.user_id
JOIN saved_blocks sb ON sb.id = al.entity_id
WHERE wv.restored_at > '2026-03-10'
GROUP BY wv.user_id, wv.workflow_id, wv.restored_at
ORDER BY blocks_deleted DESC;
```

### Query 2: Orphaned block cleanup job activity
```sql
SELECT DATE(run_at) as date, deleted_count
FROM cron_job_runs
WHERE job_name = 'cleanOrphanedBlocks'
  AND run_at > '2026-03-10'
ORDER BY run_at;
```
