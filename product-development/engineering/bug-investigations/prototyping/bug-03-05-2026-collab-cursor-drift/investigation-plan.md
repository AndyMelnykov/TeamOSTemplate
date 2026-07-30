# Collaborator cursors showing wrong position after AI generation

| Field | Value |
|-------|-------|
| Run Date | 2026-03-05 |
| Author | Jordan Kim, Engineer |
| Status | Complete |
| Playbook | [Real-time Collaboration Debugging](https://playbooks.internal/collab-debug) |
| Google Doc | [Investigation: Cursor Drift](https://docs.google.com/document/d/1pqr-cursor-drift) |
| Related Tickets | EXAMPLE_PRODUCT-998, EXAMPLE_PRODUCT-1005 |

## Objective
Investigate why collaborator presence cursors jump to incorrect positions in the code editor after an AI generation completes, making it appear that other users are editing different parts of the file.

## Background
Since launching real-time collaboration (v2.3.0), we've received reports that cursor positions become unreliable after AI generations. User A sees User B's cursor at line 50 when User B is actually at line 120. The issue only occurs after AI-generated code insertions, not manual edits.

## Impact Scope
- **Affected users:** All users of real-time collaboration (~200 active collaborating pairs)
- **Severity:** P3 — UX confusion, no data loss or functional impact
- **Duration:** Since v2.3.0 launch (2026-02-20)

## Infrastructure
- **Service:** `collab-server` (WebSocket server on Railway)
- **CRDT library:** Yjs (v13.6.x)
- **Editor:** CodeMirror 6 with `y-codemirror.next` binding
- **Presence:** Yjs awareness protocol for cursor sharing

## Results
- AI generations insert code via direct DOM/state manipulation rather than through Yjs operations
- The Yjs document updates after the insertion via a reconciliation step
- During reconciliation, character offsets shift but awareness cursor positions are not recalculated
- Other clients render stale cursor positions until the next manual edit by that user

## Analysis
1. Added debug logging to awareness updates — confirmed cursor positions don't update after AI generation
2. Traced the generation insertion path: AI output → `editor.dispatch()` → state update → Yjs sync
3. Found that `editor.dispatch()` updates the CodeMirror state but the Yjs awareness `cursor` field still references pre-insertion offsets
4. Manual edits work because the `y-codemirror` plugin hooks into CodeMirror transactions and updates awareness
5. AI insertions bypass the plugin's transaction hook because they use `replaceRange` directly

## Root Cause
AI-generated code is inserted via `editor.view.dispatch()` with a direct `replaceRange`, which does not go through the Yjs collaboration plugin's transaction observer. The plugin normally intercepts CodeMirror transactions to update awareness cursor positions, but direct dispatches bypass this. Cursor positions become stale by the number of characters/lines inserted by the AI.

## Recommended Fix
1. Route AI insertions through the Yjs document instead of direct CodeMirror dispatch
2. After AI insertion, explicitly call `awareness.setLocalStateField('cursor', updatedPosition)` to broadcast corrected positions
3. Add a `onYjsSync` callback that forces cursor re-broadcast after any large document change (>100 chars)

## Cross-Validation
- Reproduced consistently in staging with 2-user session: generate code → cursor drifts by exactly the number of inserted lines
- Confirmed manual edits correctly update cursors (goes through Yjs transaction path)
- Verified fix in staging: routing through Yjs document keeps cursors accurate

## Data Examples

| Scenario | User B Actual Line | User A Sees User B At | Drift |
|----------|-------------------|----------------------|-------|
| 20-line AI insert above cursor | 45 | 25 | -20 lines |
| 5-line AI insert below cursor | 10 | 10 | 0 (correct) |
| 50-line AI replace at cursor | 80 | 30 | -50 lines |

## Executive Summary
Collaborator cursors drift after AI generations because code is inserted via direct CodeMirror dispatch instead of through the Yjs collaboration layer. The Yjs awareness protocol never gets updated positions. Fix by routing AI insertions through the Yjs document, which automatically handles cursor rebroadcast. This is a straightforward plumbing change with no architectural risk.

## Appendix

### Query 1: Collaboration sessions with generation events
```sql
SELECT cs.session_id, cs.project_id, COUNT(DISTINCT cs.user_id) as collaborators,
       COUNT(gj.id) as generations_during_session
FROM collab_sessions cs
LEFT JOIN generation_jobs gj ON gj.project_id = cs.project_id
  AND gj.created_at BETWEEN cs.started_at AND COALESCE(cs.ended_at, NOW())
WHERE cs.started_at > '2026-02-20'
GROUP BY cs.session_id, cs.project_id
HAVING COUNT(DISTINCT cs.user_id) > 1 AND COUNT(gj.id) > 0
ORDER BY generations_during_session DESC;
```

### Query 2: Awareness update frequency during generation
```sql
SELECT DATE_TRUNC('minute', timestamp) as minute,
       COUNT(*) FILTER (WHERE event_type = 'awareness_update') as cursor_updates,
       COUNT(*) FILTER (WHERE event_type = 'generation_complete') as generations
FROM collab_events
WHERE session_id = $1
GROUP BY minute
ORDER BY minute;
```
