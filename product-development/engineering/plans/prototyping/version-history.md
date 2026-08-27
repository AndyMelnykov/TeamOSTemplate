---
**Related PRD:** [`product/PRDs/prototyping/version-history-prd.md`](../../../product/PRDs/prototyping/version-history-prd.md)
**Related RFC:** [`engineering/rfcs/prototyping/version-history-rfc.md`](../../rfcs/prototyping/version-history-rfc.md)
**Related Data Pipeline:** [`data-engineering/plans/prototyping/version-snapshots-pipeline.md`](../../../data-engineering/plans/prototyping/version-snapshots-pipeline.md)
**Analytics Schema:** [`product/analytics/schemas/prototyping/project_versions.md`](../../../analytics/schemas/prototyping/project_versions.md)
**Metrics:** [`product/analytics/metrics/prototyping/version-history-metrics.md`](../../../analytics/metrics/prototyping/version-history-metrics.md)
---

# Version history

## Overview
Let users browse and restore previous versions of a project so they can safely experiment and roll back when the AI takes a wrong turn.

## Steps
1. Add version snapshot on each generation
   - After each successful AI generation, snapshot full project state to `project_versions` table
   - Store: version number, timestamp, prompt that triggered it, file tree hash
2. Add `GET /api/projects/:id/versions` endpoint in `src/routes/projects.ts`
   - Return version list with timestamps, prompts, and diff summaries
3. Create `VersionHistory` panel in `src/components/editor/`
   - Slide-out panel listing versions chronologically
   - Each entry shows: version number, prompt snippet, timestamp
   - Click to preview that version's output in a read-only view
4. Add restore flow
   - "Restore this version" button creates a new version from the old snapshot
   - Non-destructive — current state becomes just another version in history
5. Add version diff view
   - Side-by-side comparison of any two versions
   - Highlight added/removed/changed elements
6. Add tests
   - Snapshot created after each generation
   - Restore creates new version, doesn't overwrite history
   - Diff correctly highlights changes
