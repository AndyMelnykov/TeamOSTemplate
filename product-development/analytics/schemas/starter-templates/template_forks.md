# Schema: `analytics.example_product.template_forks`

Event-level table capturing every template fork action in the document template marketplace. One row per fork event (a user creating a new workflow from a published template).

**Database:** `ANALYTICS`
**Schema:** `EXAMPLE_PRODUCT`
**Table:** `TEMPLATE_FORKS`
**Refresh:** Streaming (near real-time via Snowpipe)
**Retention:** 2 years

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `fork_id` | VARCHAR(36) | No | Unique identifier for the fork event (UUID) |
| `template_id` | VARCHAR(36) | No | Published template that was forked |
| `user_id` | VARCHAR(36) | No | User who forked the template |
| `project_id` | VARCHAR(36) | No | New workflow created from the fork (also referred to as `workflow_id`) |
| `customizations_applied` | BOOLEAN | No | Whether the user made edits (field mappings, routing, branding) to the forked workflow within the first session |
| `created_at` | TIMESTAMP_NTZ | No | When the fork occurred (UTC) |

## Indexes & Clustering

- Clustered on `(created_at, template_id)`
- Commonly filtered on `template_id`, `user_id`

## Common Joins

- `published_templates` on `template_id` - Template metadata (category, author, rating)
- `users` on `user_id` - User profile, subscription tier, account age
- `workflows` on `project_id` (`workflow_id`) - Forked workflow metadata and downstream events
- `publish_events` on `project_id` (`workflow_id`) - Whether the forked workflow was eventually published
- `workflow_automation_runs` on `project_id` (`workflow_id`) - Automation run activity in the forked workflow

## Notes

- **Naming note**: `project_id` in this table is referenced as `workflow_id` in current dashboards, investigations, and experiment writeups; both names point at the same column.
- `customizations_applied` is set to `true` if the user triggers at least one automation run or manual edit within the first 30 minutes after forking
- A single user can fork the same template multiple times (each creates a new workflow), so `(template_id, user_id)` is not unique
- To calculate fork-to-publish conversion, join with `publish_events` on `project_id` (`workflow_id`) and check for `status = 'completed'`
