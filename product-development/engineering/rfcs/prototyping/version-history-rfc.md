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

Let users browse and restore previous project versions with diff views. Every AI generation creates a versioned snapshot of the full project state. Users can scroll through their version timeline, compare any two versions side-by-side, and restore a previous version non-destructively (restoring creates a new version rather than overwriting history).

## Motivation

Today, example_product users have no reliable way to undo or roll back when an AI generation takes a project in the wrong direction. The only recovery option is a single-step undo that reverts the most recent change, which is inadequate when users want to go back multiple steps or compare how the project evolved across several generations.

This leads to real pain:

- **Lost work:** Users who iterate multiple times and then realize an earlier version was better have no way to recover it. Customer verbatims consistently cite this as a top frustration.
- **Experimentation anxiety:** Users hesitate to try bold prompts because they fear losing a good working state. This suppresses engagement and limits the value of AI-assisted iteration.
- **Abandonment after bad generations:** Internal analytics show that 18% of users who experience a bad generation abandon the project entirely rather than trying to fix it. Version history provides a safety net that keeps users in the flow.
- **Competitive gap:** Lovable shipped version history in Q1 2026. We are losing evaluation deals where this feature is a checkbox item.

## Proposed Design

### Phase 1: Database

Create the `project_versions` table to store immutable snapshots of project state.

```sql
CREATE TABLE project_versions (
    version_id       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id       UUID         NOT NULL REFERENCES projects(project_id),
    user_id          UUID         NOT NULL REFERENCES users(user_id),
    version_number   INTEGER      NOT NULL,
    prompt_trigger   TEXT,
    file_tree_hash   VARCHAR(64)  NOT NULL,
    snapshot_data    JSONB        NOT NULL,
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_project_version UNIQUE (project_id, version_number)
);

CREATE INDEX idx_project_versions_project_id ON project_versions (project_id, version_number DESC);
CREATE INDEX idx_project_versions_user_id ON project_versions (user_id, created_at DESC);
```

**Column details:**

| Column | Description |
|--------|-------------|
| `version_id` | Unique identifier for this version snapshot |
| `project_id` | The project this version belongs to |
| `user_id` | The user who triggered the generation or manual save that created this version |
| `version_number` | Monotonically increasing integer per project, starting at 1 |
| `prompt_trigger` | The prompt text that triggered this generation (null for manual saves) |
| `file_tree_hash` | SHA-256 hash of the serialized file tree, used for fast equality checks and deduplication |
| `snapshot_data` | Full project state as JSONB: file contents, configuration, metadata |
| `created_at` | Timestamp of version creation |

**Snapshot data structure:**

```json
{
  "files": {
    "src/App.tsx": { "content": "...", "hash": "abc123" },
    "src/index.css": { "content": "...", "hash": "def456" }
  },
  "config": {
    "framework": "react",
    "dependencies": { "react": "^18.2.0" }
  },
  "metadata": {
    "generation_id": "uuid",
    "model_version": "example_product-gen-3.2"
  }
}
```

### Phase 2: API

#### `GET /api/projects/:id/versions`

Returns the paginated version list for a project, ordered by version number descending.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 25 | Results per page (max 100) |
| `from_date` | ISO 8601 | - | Filter versions created on or after this date |
| `to_date` | ISO 8601 | - | Filter versions created on or before this date |
| `search` | string | - | Search prompt_trigger text |

**Success response (200):**

```json
{
  "versions": [
    {
      "version_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "version_number": 12,
      "prompt_trigger": "Add a dark mode toggle to the header",
      "file_tree_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "file_count": 8,
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
| 403 | `{ "error": "forbidden", "message": "You do not have access to this project" }` | User is not a member of the project |
| 404 | `{ "error": "not_found", "message": "Project not found" }` | Invalid project ID |

---

#### `POST /api/projects/:id/versions/:versionId/restore`

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
    "prompt_trigger": null,
    "source_version_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "source_version_number": 5,
    "created_at": "2026-03-22T15:00:00Z"
  },
  "message": "Project restored to version 5. Your previous state has been saved as version 12."
}
```

**Failure responses:**

| Status | Body | Condition |
|--------|------|-----------|
| 400 | `{ "error": "bad_request", "message": "Confirmation required. Set confirm: true to proceed." }` | Missing or false `confirm` field |
| 401 | `{ "error": "unauthorized", "message": "Authentication required" }` | Missing or invalid auth token |
| 403 | `{ "error": "forbidden", "message": "You do not have access to this project" }` | User is not a member or lacks edit permission |
| 404 | `{ "error": "not_found", "message": "Version not found" }` | Invalid version ID |
| 409 | `{ "error": "conflict", "message": "Another restore is in progress for this project" }` | Concurrent restore attempt |

---

#### `GET /api/projects/:id/versions/:v1/diff/:v2`

Returns a structured diff between two versions, showing added, removed, and modified files with line-level changes.

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
    "files_added": 2,
    "files_removed": 0,
    "files_modified": 3,
    "total_additions": 87,
    "total_deletions": 14
  },
  "diffs": [
    {
      "file_path": "src/App.tsx",
      "status": "modified",
      "additions": 24,
      "deletions": 8,
      "hunks": [
        {
          "old_start": 10,
          "old_lines": 12,
          "new_start": 10,
          "new_lines": 28,
          "content": "@@ -10,12 +10,28 @@\n-import { Header } from './Header';\n+import { Header } from './Header';\n+import { ThemeToggle } from './ThemeToggle';\n ..."
        }
      ]
    },
    {
      "file_path": "src/ThemeToggle.tsx",
      "status": "added",
      "additions": 45,
      "deletions": 0,
      "hunks": []
    }
  ]
}
```

**Failure responses:**

| Status | Body | Condition |
|--------|------|-----------|
| 401 | `{ "error": "unauthorized", "message": "Authentication required" }` | Missing or invalid auth token |
| 403 | `{ "error": "forbidden", "message": "You do not have access to this project" }` | User is not a member of the project |
| 404 | `{ "error": "not_found", "message": "One or both versions not found" }` | Invalid version IDs |
| 422 | `{ "error": "unprocessable", "message": "Cannot diff versions from different projects" }` | Version IDs belong to different projects |

### Phase 3: Frontend

#### VersionHistory slide-out panel

The `VersionHistory` component lives in `src/components/editor/VersionHistory.tsx` and renders as a slide-out panel triggered from the editor toolbar. The panel occupies the right 400px of the viewport and pushes the editor content left rather than overlaying it.

**Panel contents:**

- **Header:** "Version History" title with close button and version count badge
- **Filters bar:** Date range picker (from/to) and a search input for filtering by prompt text
- **Version list:** Scrollable list of version cards, each showing:
  - Version number (e.g., "v12")
  - Prompt snippet (truncated to 80 characters)
  - Relative timestamp ("2 hours ago")
  - File change summary ("+3 files, ~2 modified")
  - "Compare" checkbox for selecting versions to diff
  - "Restore" button (secondary style)

**Interaction behavior:**

- Clicking a version card expands it to show the full prompt and a read-only preview of the project at that version
- Selecting exactly two "Compare" checkboxes opens the diff viewer
- Scrolling to the bottom of the list triggers pagination (loads next 25 versions)

#### Diff viewer (side-by-side)

The diff viewer opens as a full-width overlay within the editor area. It renders a side-by-side comparison using a Monaco-based diff editor.

- Left pane: earlier version (labeled "v5 - March 18, 2:30 PM")
- Right pane: later version (labeled "v12 - March 22, 3:00 PM")
- File tree sidebar on the left showing changed files with status icons (added/removed/modified)
- Clicking a file in the sidebar navigates the diff view to that file
- Additions highlighted in green, deletions highlighted in red
- "Close diff" button returns to the version list panel

#### Restore confirmation dialog

When a user clicks "Restore" on a version, a modal dialog appears:

- **Title:** "Restore to version {N}?"
- **Body:** "Your current project state will be saved as a new version before restoring. You can always return to it later."
- **Primary action:** "Restore" (blue button)
- **Secondary action:** "Cancel" (text button)
- On confirm, calls the restore API, closes the dialog, refreshes the version list, and shows a toast: "Restored to version {N}"

## Key Queries

**Fetch version list for a project:**

```sql
SELECT version_id, version_number, prompt_trigger, file_tree_hash, created_at
FROM project_versions
WHERE project_id = :project_id
ORDER BY version_number DESC
LIMIT :per_page OFFSET :offset;
```

**Get latest version number for incrementing:**

```sql
SELECT COALESCE(MAX(version_number), 0) + 1 AS next_version
FROM project_versions
WHERE project_id = :project_id;
```

**Fetch two versions for diffing:**

```sql
SELECT version_id, version_number, snapshot_data, created_at
FROM project_versions
WHERE project_id = :project_id
  AND version_id IN (:v1_id, :v2_id);
```

**Count versions per project (for pagination):**

```sql
SELECT COUNT(*) AS total_versions
FROM project_versions
WHERE project_id = :project_id;
```

## Security Considerations

- **Authorization:** All version endpoints enforce project membership checks. Users can only access versions for projects they are a member of. The restore endpoint additionally requires edit permission (viewers cannot restore).
- **Data isolation:** Queries always filter by `project_id` to prevent cross-project data leakage. The diff endpoint validates both versions belong to the same project.
- **Snapshot size limits:** Snapshot data is capped at 50 MB per version. Projects exceeding this limit will receive a 413 error and should use the incremental snapshot path (future work).
- **Rate limiting:** The restore endpoint is rate-limited to 10 requests per minute per user to prevent abuse and accidental rapid-fire restores.
- **Audit trail:** All restore operations are logged to the `audit_events` table with the acting user, source version, and timestamp.
- **Data retention:** Versions are retained for the lifetime of the project. When a project is deleted, all associated versions are cascade-deleted after a 30-day soft-delete grace period.

## Rollout Plan

| Phase | Scope | Flag | Timeline |
|-------|-------|------|----------|
| 1 - Internal dogfood | example_product Labs internal projects only | `version_history_internal` | Week 1 |
| 2 - Beta | example_product Pro and Teams customers, opt-in | `version_history_beta` | Weeks 2-3 |
| 3 - GA | All users, enabled by default | `version_history_ga` | Week 4 |

**Phase 1 goals:** Validate snapshot creation reliability, measure storage impact, gather UX feedback from internal team.

**Phase 2 goals:** Monitor restore success rate (target >99%), collect feedback on diff viewer usability, verify no performance degradation on projects with 100+ versions.

**Phase 3 goals:** Full launch with onboarding tooltip, track adoption metrics (see version history metrics doc), monitor for any edge cases at scale.

**Rollback plan:** Each phase gate is controlled by a feature flag. If issues arise, the flag can be disabled without a deploy. Existing snapshots are retained even if the feature is disabled.
