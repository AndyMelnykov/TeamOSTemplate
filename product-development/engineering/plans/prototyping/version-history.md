---
**Related PRD:** [`product/PRDs/prototyping/version-history-prd.md`](../../../product/PRDs/prototyping/version-history-prd.md)
**Related RFC:** [`engineering/rfcs/prototyping/version-history-rfc.md`](../../rfcs/prototyping/version-history-rfc.md)
**Related Data Pipeline:** [`data-engineering/plans/prototyping/version-snapshots-pipeline.md`](../../../data-engineering/plans/prototyping/version-snapshots-pipeline.md)
**Analytics Schema:** [`product/analytics/schemas/prototyping/project_versions.md`](../../../analytics/schemas/prototyping/project_versions.md)
**Metrics:** [`product/analytics/metrics/prototyping/version-history-metrics.md`](../../../analytics/metrics/prototyping/version-history-metrics.md)
---

# Version history

## Overview
Let users browse and restore previous versions of a workflow so they can safely experiment with extraction rules and routing logic, and roll back when an AI-assisted refinement takes a wrong turn.

## Steps
1. Add version snapshot on each refinement
   - After each successful AI-assisted refinement, snapshot the full workflow definition to `workflow_versions` table
   - Store: version number, timestamp, instruction that triggered it, definition hash
2. Add `GET /api/workflows/:id/versions` endpoint in `src/routes/workflows.ts`
   - Return version list with timestamps, instructions, and diff summaries
3. Create `VersionHistory` panel in `src/components/builder/`
   - Slide-out panel listing versions chronologically
   - Each entry shows: version number, instruction snippet, timestamp
   - Click to preview that version's extraction rules and routing in a read-only view
4. Add restore flow
   - "Restore this version" button creates a new version from the old snapshot
   - Non-destructive — current state becomes just another version in history
5. Add version diff view
   - Side-by-side comparison of any two versions' extraction rules and routing steps
   - Highlight added/removed/changed fields and steps
6. Add tests
   - Snapshot created after each refinement
   - Restore creates new version, doesn't overwrite history
   - Diff correctly highlights changes
