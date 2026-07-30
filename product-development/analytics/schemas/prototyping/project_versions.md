# Schema: `analytics.example_product.project_versions`

Event-level table capturing every version snapshot created on the example_product platform. One row per version event (automatic snapshot, manual save, or restore).

**Database:** `ANALYTICS`
**Schema:** `EXAMPLE_PRODUCT`
**Table:** `PROJECT_VERSIONS`
**Refresh:** Streaming (near real-time via Snowpipe)
**Retention:** 2 years

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `version_id` | VARCHAR(36) | No | Unique identifier for the version event (UUID) |
| `project_id` | VARCHAR(36) | No | Project this version belongs to |
| `user_id` | VARCHAR(36) | No | User who triggered the version creation |
| `version_number` | INTEGER | No | Monotonically increasing version number within the project, starting at 1 |
| `prompt_trigger` | TEXT | Yes | The prompt text that triggered the generation leading to this version (null for manual saves and restores) |
| `action` | VARCHAR(20) | No | Type of event that created this version: `auto_snapshot`, `manual_save`, `restore` |
| `source_version_id` | VARCHAR(36) | Yes | For `restore` actions, the version_id that was restored from (null for `auto_snapshot` and `manual_save`) |
| `file_count` | INTEGER | No | Number of files in the project at this version |
| `total_size_bytes` | BIGINT | No | Total size of all files in the snapshot in bytes |
| `created_at` | TIMESTAMP_NTZ | No | When the version was created (UTC) |

## Indexes & Clustering

- Clustered on `(created_at, project_id)`
- Commonly filtered on `action`, `project_id`, `user_id`

## Common Joins

- `projects` on `project_id` - Project metadata (name, framework, creation date)
- `users` on `user_id` - User profile and account details
- `project_generations` on `project_id` and `created_at` correlation - Link version to the generation that triggered it
- `subscriptions` on `user_id` - Billing and plan information
- Self-join on `source_version_id` = `version_id` - Link restore events to their source version

## Notes

- `action = 'auto_snapshot'` is created automatically after every successful AI generation
- `action = 'manual_save'` is created when a user explicitly saves a version from the editor
- `action = 'restore'` is created when a user restores a previous version; `source_version_id` points to the version that was restored
- `prompt_trigger` is null for `manual_save` and `restore` actions
- `source_version_id` is null for `auto_snapshot` and `manual_save` actions
- `total_size_bytes` represents the full snapshot size, not the incremental delta from the previous version
