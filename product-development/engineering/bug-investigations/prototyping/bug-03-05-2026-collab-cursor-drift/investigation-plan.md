# Collaborator cursors showing wrong position after AI field insertion

| Field | Value |
|-------|-------|
| Run Date | 2026-03-05 |
| Author | Jordan Kim, Engineer |
| Status | Complete |
| Playbook | [Real-time Collaboration Debugging](https://playbooks.internal/collab-debug) |
| Google Doc | [Investigation: Cursor Drift](https://docs.google.com/document/d/1pqr-cursor-drift) |
| Related Tickets | EXAMPLE_PRODUCT-998, EXAMPLE_PRODUCT-1005 |

## Objective
Investigate why collaborator presence cursors jump to incorrect positions on the workflow builder canvas after an AI-suggested field/clause insertion completes, making it appear that other users are editing a different part of the workflow.

## Background
Since launching real-time collaboration (v2.3.0), we've received reports that cursor positions become unreliable after AI field insertions. User A sees User B's cursor near the "Routing" step when User B is actually editing a field mapping near the "Signature" step. The issue only occurs after the AI auto-inserts suggested fields/clauses into the canvas, not manual drag-and-drop edits.

## Impact Scope
- **Affected users:** All users of real-time collaboration (~200 active co-editing pairs)
- **Severity:** P3 — UX confusion, no data loss or functional impact
- **Duration:** Since v2.3.0 launch (2026-02-20)

## Infrastructure
- **Service:** `collab-server` (WebSocket server on Railway)
- **CRDT library:** Yjs (v13.6.x)
- **Canvas:** Workflow builder built on `react-flow` with a custom Yjs binding for the node/edge graph
- **Presence:** Yjs awareness protocol for cursor sharing

## Results
- AI field insertions add nodes to the canvas via direct `reactFlowInstance.addNodes()` calls rather than through Yjs operations
- The Yjs document updates after the insertion via a reconciliation step
- During reconciliation, node canvas coordinates shift (auto-layout repositions downstream steps) but awareness cursor positions are not recalculated
- Other clients render stale cursor coordinates until the next manual drag by that user

## Analysis
1. Added debug logging to awareness updates — confirmed cursor positions don't update after an AI field insertion
2. Traced the insertion path: AI suggestion accepted → `reactFlowInstance.addNodes()` → canvas state update → Yjs sync
3. Found that `addNodes()` updates the canvas state but the Yjs awareness `cursor` field still references pre-insertion coordinates
4. Manual drags work because the Yjs-react-flow binding hooks into `onNodesChange` events and updates awareness on every change
5. AI insertions bypass the binding's change hook because they call `addNodes()` directly instead of going through a tracked node-change event

## Root Cause
AI-suggested fields/clauses are inserted via a direct `reactFlowInstance.addNodes()` call, which does not go through the Yjs collaboration binding's `onNodesChange` observer. The binding normally intercepts canvas change events to update awareness cursor coordinates, but the direct insertion bypasses this. Cursor positions become stale by the canvas offset introduced when auto-layout repositions steps to make room for the new field.

## Recommended Fix
1. Route AI field insertions through the same `onNodesChange` pipeline as manual drags, or emit a synthetic change event after `addNodes()`
2. After AI insertion, explicitly call `awareness.setLocalStateField('cursor', updatedPosition)` to broadcast corrected coordinates
3. Add an `onYjsSync` callback that forces cursor re-broadcast after any large canvas change (>3 nodes affected by auto-layout)

## Cross-Validation
- Reproduced consistently in staging with a 2-user session: accept an AI field suggestion → cursor drifts by the auto-layout offset
- Confirmed manual drags correctly update cursors (goes through the tracked `onNodesChange` path)
- Verified fix in staging: routing through the change pipeline keeps cursors accurate

## Data Examples

| Scenario | User B Actual Canvas Y | User A Sees User B At | Drift |
|----------|-------------------|----------------------|-------|
| 4-field AI insert above cursor, auto-layout shifts down | 640 | 320 | -320px |
| 1-field AI insert below cursor | 160 | 160 | 0 (correct) |
| 8-field AI insert (bulk clause suggestion) at cursor | 960 | 240 | -720px |

## Executive Summary
Collaborator cursors drift after AI field insertions because new fields/clauses are added to the workflow canvas via a direct `addNodes()` call instead of through the Yjs collaboration binding's tracked change pipeline. The Yjs awareness protocol never gets updated coordinates. Fix by routing AI insertions through the same change pipeline as manual drags, which automatically handles cursor rebroadcast. This is a straightforward plumbing change with no architectural risk.

## Appendix

### Query 1: Collaboration sessions with AI field-insertion events
```sql
SELECT cs.session_id, cs.workflow_id, COUNT(DISTINCT cs.user_id) as collaborators,
       COUNT(fse.id) as field_insertions_during_session
FROM collab_sessions cs
LEFT JOIN field_suggestion_events fse ON fse.workflow_id = cs.workflow_id
  AND fse.created_at BETWEEN cs.started_at AND COALESCE(cs.ended_at, NOW())
WHERE cs.started_at > '2026-02-20'
GROUP BY cs.session_id, cs.workflow_id
HAVING COUNT(DISTINCT cs.user_id) > 1 AND COUNT(fse.id) > 0
ORDER BY field_insertions_during_session DESC;
```

### Query 2: Awareness update frequency during field insertion
```sql
SELECT DATE_TRUNC('minute', timestamp) as minute,
       COUNT(*) FILTER (WHERE event_type = 'awareness_update') as cursor_updates,
       COUNT(*) FILTER (WHERE event_type = 'field_insertion_complete') as insertions
FROM collab_events
WHERE session_id = $1
GROUP BY minute
ORDER BY minute;
```
