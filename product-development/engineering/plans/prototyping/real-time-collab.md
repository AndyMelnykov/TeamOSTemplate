# Real-time collaboration

## Overview
Enable multiplayer editing so team members can work on the same workflow simultaneously with live presence indicators and conflict-free updates.

## Steps
1. Set up WebSocket collaboration server
   - Add `yjs` for CRDT-based document sync
   - Authenticate connections using existing session token
   - Room per workflow, auto-join on workflow open
2. Add presence indicators in `src/components/builder/`
   - Show collaborator avatars in top bar with colored borders
   - Display colored cursors/selections in the field-mapping view
   - "Currently viewing" indicator on the workflow canvas
3. Add real-time sync for extraction test runs
   - When one user runs a test extraction on a sample document, others see a "processing..." indicator
   - Extracted fields and confidence scores stream to all connected clients simultaneously
   - Lock the test-run control for others during an active extraction
4. Add conflict resolution
   - CRDT handles concurrent field-mapping edits automatically
   - Workflow canvas changes use last-write-wins with undo support
   - Show toast when another user's edit affects your current view
5. Add tests
   - Two clients see each other's edits in real time
   - Presence shows correct collaborator count
   - Concurrent edits merge without data loss
