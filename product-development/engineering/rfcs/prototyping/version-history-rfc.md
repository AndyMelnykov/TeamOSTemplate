# RFC: Version History

**Author:** Morgan Wu, Engineer
**Status:** Draft
**Last Updated:** 2026-03-22
**Related PRD:** [`product/PRDs/prototyping/version-history-prd.md`](../../../product/PRDs/prototyping/version-history-prd.md)
**Related Plan:** [`engineering/plans/prototyping/version-history.md`](../../plans/prototyping/version-history.md)

---

## Table of Contents

1. [Summary](#summary)
2. [Motivation](#motivation)
3. [Proposed Design](#proposed-design)
   - [Phase 1: Database](#phase-1-database)
   - [Phase 2: API](#phase-2-api)
   - [Phase 3: Frontend](#phase-3-frontend)
4. [Key Queries](#key-queries)
5. [Security Considerations](#security-considerations)
6. [Rollout Plan](#rollout-plan)

---

## Summary

Let users browse and restore previous workflow versions with diff views. Every AI-assisted refinement creates a versioned snapshot of the full workflow definition (extraction rules, field mappings, routing steps, and branding). Users can scroll through their version timeline, compare any two versions side-by-side, and restore a previous version non-destructively (restoring creates a new version rather than overwriting history).

## Motivation

Today, example_product users have no reliable way to undo or roll back when an AI-assisted refinement takes a workflow's extraction rules or routing logic in the wrong direction. The only recovery option is a single-step undo that reverts the most recent change, which is inadequate when users want to go back multiple steps or compare how the workflow evolved across several refinements.

This leads to real pain:

- **Lost work:** Users who iterate multiple times on field mappings or approval routing and then realize an earlier version was better have no way to recover it. Customer verbatims consistently cite this as a top frustration.
- **Experimentation anxiety:** Users hesitate to try bold instructions (e.g., "route anything over $10K to legal for review") because they fear losing a good working configuration. This suppresses engagement and limits the value of AI-assisted refinement.
- **Abandonment after a bad extraction run:** Internal analytics show that 18% of users who experience a bad automation run abandon the workflow entirely rather than trying to fix it. Version history provides a safety net that keeps users in the flow.
- **Competitive gap:** PandaDoc shipped version history in Q1 2026. We are losing evaluation deals where this feature is a checkbox item.

## Proposed Design

### Phase 1: Database

Create the `workflow_versions` table to store immutable snapshots of workflow state.

```sql
CREATE TABLE workflow_versions (
    version_id       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id      UUID         NOT NULL REFERENCES workflows(workflow_id),
    user_id          UUID         NOT NULL REFERENCES users(user_id),
    version_number   INTEGER      NOT NULL,
    instruction_trigger TEXT,
    definition_hash  VARCHAR(64)  NOT NULL,
    snapshot_data    JSONB        NOT NULL,
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_workflow_version UNIQUE (workflow_id, version_number)
);

CREATE INDEX idx_workflow_versions_workflow_id ON workflow_versions (workflow_id, version_number DESC);
CREATE INDEX idx_workflow_versions_user_id ON workflow_versions (user_id, created_at DESC);
```

**Column details:**

| Column | Description |
|--------|-------------|
| `version_id` | Unique identifier for this version snapshot |
| `workflow_id` | The workflow this version belongs to |
| `user_id` | The user who triggered the refinement or manual save that created this version |
| `version_number` | Monotonically increasing integer per workflow, starting at 1 |
| `instruction_trigger` | The natural-language instruction that triggered this refinement (null for manual saves) |
| `definition_hash` | SHA-256 hash of the serialized workflow definition, used for fast equality checks and deduplication |
| `snapshot_data` | Full workflow state as JSONB: extraction rules, field mappings, routing steps, signature configuration, branding |
| `created_at` | Timestamp of version creation |

**Snapshot data structure:**

```json
{
  "extraction_rules": {
    "vendor_name": { "field_type": "text", "source": "header block", "confidence_threshold": 0.85 },
    "total_amount": { "field_type": "currency", "source": "line-item table", "confidence_threshold": 0.9 }
  },
  "routing": {
    "steps": [
      { "step": "manager_approval", "condition": "total_amount > 10000" },
      { "step": "legal_review", "condition": "clause_detected == 'indemnification'" }
    ]
  },
  "metadata": {
    "automation_run_id": "uuid",
    "extraction_model_version": "example_product-extract-3.2"
  }
}
```

### Phase 2: API

#### `GET /api/workflows/:id/versions`

Returns the paginated version list for a workflow, ordered by version number descending.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 25 | Results per page (max 100) |
| `from_date` | ISO 8601 | - | Filter versions created on or after this date |
| `to_date` | ISO 8601 | - | Filter versions created on or before this date |
| `search` | string | - | Search instruction_trigger text |

**Success response (200):**

```json
{
  "versions": [
    {
      "version_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "version_number": 12,
      "instruction_trigger": "Route anything over $10,000 to legal for review",
      "definition_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "field_count": 8,
      "created_at": "2026-03-22T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 25,
    "total_count": 47,
    "total_pages": 2
  }
}
```

**Failure responses:**

| Status | Body | Condition |
|--------|------|-----------|
| 401 | `{ "error": "unauthorized", "message": "Authentication required" }` | Missing or invalid auth token |
| 403 | `{ "error": "forbidden", "message": "You do not have access to this workflow" }` | User is not a member of the workflow |
| 404 | `{ "error": "not_found", "message": "Workflow not found" }` | Invalid workflow ID |

---

#### `POST /api/workflows/:id/versions/:versionId/restore`

Restores a previous version by creating a new version with the snapshot data from the specified version. This is non-destructive: the current state is preserved as a version before the restore is applied.

**Request body:**

```json
{
  "confirm": true
}
```

**Success response (201):**

```json
{
  "restored_version": {
    "version_id": "f7e8d9c0-b1a2-3456-cdef-890123456789",
    "version_number": 13,
    "instruction_trigger": null,
    "source_version_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "source_version_number": 5,
    "created_at": "2026-03-22T15:00:00Z"
  },
  "message": "Workflow restored to version 5. Your previous state has been saved as version 12."
}
```

**Failure responses:**

| Status | Body | Condition |
|--------|------|-----------|
| 400 | `{ "error": "bad_request", "message": "Confirmation required. Set confirm: true to proceed." }` | Missing or false `confirm` field |
| 401 | `{ "error": "unauthorized", "message": "Authentication required" }` | Missing or invalid auth token |
| 403 | `{ "error": "forbidden", "message": "You do not have access to this workflow" }` | User is not a member or lacks edit permission |
| 404 | `{ "error": "not_found", "message": "Version not found" }` | Invalid version ID |
| 409 | `{ "error": "conflict", "message": "Another restore is in progress for this workflow" }` | Concurrent restore attempt |

---

#### `GET /api/workflows/:id/versions/:v1/diff/:v2`

Returns a structured diff between two versions, showing added, removed, and modified extraction rules, field mappings, and routing steps.

**Success response (200):**

```json
{
  "v1": {
    "version_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "version_number": 5
  },
  "v2": {
    "version_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "version_number": 12
  },
  "summary": {
    "fields_added": 2,
    "fields_removed": 0,
    "fields_modified": 3,
    "routing_steps_added": 1,
    "routing_steps_removed": 0
  },
  "diffs": [
    {
      "section": "routing",
      "status": "modified",
      "changes": [
        {
          "path": "routing.steps",
          "old_value": [{ "step": "manager_approval", "condition": "total_amount > 5000" }],
          "new_value": [
            { "step": "manager_approval", "condition": "total_amount > 5000" },
            { "step": "legal_review", "condition": "clause_detected == 'indemnification'" }
          ]
        }
      ]
    },
    {
      "section": "extraction_rules.legal_review_flag",
      "status": "added",
      "changes": []
    }
  ]
}
```

**Failure responses:**

| Status | Body | Condition |
|--------|------|-----------|
| 401 | `{ "error": "unauthorized", "message": "Authentication required" }` | Missing or invalid auth token |
| 403 | `{ "error": "forbidden", "message": "You do not have access to this workflow" }` | User is not a member of the workflow |
| 404 | `{ "error": "not_found", "message": "One or both versions not found" }` | Invalid version IDs |
| 422 | `{ "error": "unprocessable", "message": "Cannot diff versions from different workflows" }` | Version IDs belong to different workflows |

### Phase 3: Frontend

#### VersionHistory slide-out panel

The `VersionHistory` component lives in `src/components/builder/VersionHistory.tsx` and renders as a slide-out panel triggered from the workflow builder toolbar. The panel occupies the right 400px of the viewport and pushes the builder canvas left rather than overlaying it.

**Panel contents:**

- **Header:** "Version History" title with close button and version count badge
- **Filters bar:** Date range picker (from/to) and a search input for filtering by instruction text
- **Version list:** Scrollable list of version cards, each showing:
  - Version number (e.g., "v12")
  - Instruction snippet (truncated to 80 characters)
  - Relative timestamp ("2 hours ago")
  - Change summary ("+3 fields, ~2 routing steps modified")
  - "Compare" checkbox for selecting versions to diff
  - "Restore" button (secondary style)

**Interaction behavior:**

- Clicking a version card expands it to show the full instruction and a read-only preview of the workflow (extraction rules, routing) at that version
- Selecting exactly two "Compare" checkboxes opens the diff viewer
- Scrolling to the bottom of the list triggers pagination (loads next 25 versions)

#### Diff viewer (side-by-side)

The diff viewer opens as a full-width overlay within the workflow builder. It renders a side-by-side comparison of extraction rules, field mappings, and routing steps.

- Left pane: earlier version (labeled "v5 - March 18, 2:30 PM")
- Right pane: later version (labeled "v12 - March 22, 3:00 PM")
- Section sidebar on the left showing changed sections (Extraction Rules, Routing, Signature, Branding) with status icons (added/removed/modified)
- Clicking a section in the sidebar navigates the diff view to that section
- Additions highlighted in green, deletions highlighted in red
- "Close diff" button returns to the version list panel

#### Restore confirmation dialog

When a user clicks "Restore" on a version, a modal dialog appears:

- **Title:** "Restore to version {N}?"
- **Body:** "Your current workflow configuration will be saved as a new version before restoring. You can always return to it later."
- **Primary action:** "Restore" (blue button)
- **Secondary action:** "Cancel" (text button)
- On confirm, calls the restore API, closes the dialog, refreshes the version list, and shows a toast: "Restored to version {N}"

## Key Queries

**Fetch version list for a workflow:**

```sql
SELECT version_id, version_number, instruction_trigger, definition_hash, created_at
FROM workflow_versions
WHERE workflow_id = :workflow_id
ORDER BY version_number DESC
LIMIT :per_page OFFSET :offset;
```

**Get latest version number for incrementing:**

```sql
SELECT COALESCE(MAX(version_number), 0) + 1 AS next_version
FROM workflow_versions
WHERE workflow_id = :workflow_id;
```

**Fetch two versions for diffing:**

```sql
SELECT version_id, version_number, snapshot_data, created_at
FROM workflow_versions
WHERE workflow_id = :workflow_id
  AND version_id IN (:v1_id, :v2_id);
```

**Count versions per workflow (for pagination):**

```sql
SELECT COUNT(*) AS total_versions
FROM workflow_versions
WHERE workflow_id = :workflow_id;
```

## Security Considerations

- **Authorization:** All version endpoints enforce workflow membership checks. Users can only access versions for workflows they are a member of. The restore endpoint additionally requires edit permission (viewers cannot restore).
- **Data isolation:** Queries always filter by `workflow_id` to prevent cross-workflow data leakage. The diff endpoint validates both versions belong to the same workflow.
- **Snapshot size limits:** Snapshot data is capped at 50 MB per version. Workflows exceeding this limit (typically ones with very large clause/field libraries) will receive a 413 error and should use the incremental snapshot path (future work).
- **Rate limiting:** The restore endpoint is rate-limited to 10 requests per minute per user to prevent abuse and accidental rapid-fire restores.
- **Audit trail:** All restore operations are logged to the `audit_events` table with the acting user, source version, and timestamp.
- **Data retention:** Versions are retained for the lifetime of the workflow. When a workflow is deleted, all associated versions are cascade-deleted after a 30-day soft-delete grace period.

## Rollout Plan

| Phase | Scope | Flag | Timeline |
|-------|-------|------|----------|
| 1 - Internal dogfood | example_product Labs internal workflows only | `version_history_internal` | Week 1 |
| 2 - Beta | example_product Pro and Teams customers, opt-in | `version_history_beta` | Weeks 2-3 |
| 3 - GA | All users, enabled by default | `version_history_ga` | Week 4 |

**Phase 1 goals:** Validate snapshot creation reliability, measure storage impact, gather UX feedback from internal team.

**Phase 2 goals:** Monitor restore success rate (target >99%), collect feedback on diff viewer usability, verify no performance degradation on workflows with 100+ versions.

**Phase 3 goals:** Full launch with onboarding tooltip, track adoption metrics (see version history metrics doc), monitor for any edge cases at scale.

**Rollback plan:** Each phase gate is controlled by a feature flag. If issues arise, the flag can be disabled without a deploy. Existing snapshots are retained even if the feature is disabled.
