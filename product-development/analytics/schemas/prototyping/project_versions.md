# Schema: `analytics.example_product.workflow_versions`

Event-level table capturing every version snapshot created for a workflow (or the template it was built from) on the example_product platform. One row per version event (automatic snapshot, manual save, or restore).

**Database:** `ANALYTICS`
**Schema:** `EXAMPLE_PRODUCT`
**Table:** `WORKFLOW_VERSIONS`
**Refresh:** Streaming (near real-time via Snowpipe)
**Retention:** 2 years

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `version_id` | VARCHAR(36) | No | Unique identifier for the version event (UUID) |
| `project_id` | VARCHAR(36) | No | Workflow this version belongs to (also referred to as `workflow_id`) |
| `user_id` | VARCHAR(36) | No | User who triggered the version creation |
| `version_number` | INTEGER | No | Monotonically increasing version number within the workflow, starting at 1 |
| `prompt_trigger` | TEXT | Yes | The instruction text (extraction rules or routing logic) that triggered the automation run leading to this version (null for manual saves and restores) |
| `action` | VARCHAR(20) | No | Type of event that created this version: `auto_snapshot`, `manual_save`, `restore` |
| `source_version_id` | VARCHAR(36) | Yes | For `restore` actions, the version_id that was restored from (null for `auto_snapshot` and `manual_save`) |
| `file_count` | INTEGER | No | Number of extraction/routing configuration files in the workflow at this version |
| `total_size_bytes` | BIGINT | No | Total size of all configuration files in the snapshot in bytes |
| `created_at` | TIMESTAMP_NTZ | No | When the version was created (UTC) |

## Indexes & Clustering

- Clustered on `(created_at, project_id)`
- Commonly filtered on `action`, `project_id`, `user_id`

## Common Joins

- `workflows` on `project_id` (`workflow_id`) - Workflow metadata (name, feature area, creation date)
- `users` on `user_id` - User profile and account details
- `workflow_automation_runs` on `project_id` and `created_at` correlation - Link version to the automation run that triggered it
- `subscriptions` on `user_id` - Billing and plan information
- Self-join on `source_version_id` = `version_id` - Link restore events to their source version

## Notes

- **Naming note**: this table's legacy name is `project_versions` (matching this doc's filename); it is referenced as `workflow_versions` in current dashboards, investigations, and experiment writeups. Both names point at the same underlying table.
- `action = 'auto_snapshot'` is created automatically after every successful automation run (AI extraction)
- `action = 'manual_save'` is created when a user explicitly saves a version from the workflow builder
- `action = 'restore'` is created when a user restores a previous version; `source_version_id` points to the version that was restored
- `prompt_trigger` is null for `manual_save` and `restore` actions
- `source_version_id` is null for `auto_snapshot` and `manual_save` actions
- `total_size_bytes` represents the full snapshot size, not the incremental delta from the previous version
