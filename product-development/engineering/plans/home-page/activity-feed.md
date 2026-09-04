# Activity feed

## Overview
Surface a timeline of recent extractions, publishes, and collaborator activity below My Workflows so users can quickly resume work or see what teammates changed.

## Steps
1. Add `GET /api/home/activity` endpoint in `src/routes/home.ts`
   - Aggregate recent events: workflow edits, publishes, shares, comments, completed signatures
   - Return last 20 events, paginated
   - Filter to workflows the user owns or is shared on
2. Create `ActivityFeed` component in `src/components/home/`
   - Each item shows: avatar, action description, workflow name, timestamp
   - Click navigates to the relevant workflow or publish
   - Relative timestamps ("2 hours ago")
3. Add activity event recording
   - Emit events from the workflow builder, publish pipeline, and share flow
   - Write to `activity_events` table with user_id, workflow_id, event_type, metadata
4. Add "Shared with me" filter toggle
   - Default shows all, toggle filters to only shared workflow activity
5. Add tests
   - Feed shows events across owned and shared workflows
   - Pagination loads more items
   - Events record correctly from each source
