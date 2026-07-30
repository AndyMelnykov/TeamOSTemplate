# Schema: `analytics.example_product.template_forks`

Event-level table capturing every template fork action in the Community Marketplace. One row per fork event (a user creating a new project from a published template).

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
| `project_id` | VARCHAR(36) | No | New project created from the fork |
| `customizations_applied` | BOOLEAN | No | Whether the user made edits to the forked project within the first session |
| `created_at` | TIMESTAMP_NTZ | No | When the fork occurred (UTC) |

## Indexes & Clustering

- Clustered on `(created_at, template_id)`
- Commonly filtered on `template_id`, `user_id`

## Common Joins

- `published_templates` on `template_id` - Template metadata (category, author, rating)
- `users` on `user_id` - User profile, subscription tier, account age
- `projects` on `project_id` - Forked project metadata and downstream events
- `deploy_events` on `project_id` - Whether the forked project was eventually deployed
- `project_generations` on `project_id` - Generation activity in the forked project

## Notes

- `customizations_applied` is set to `true` if the user triggers at least one generation or manual edit within the first 30 minutes after forking
- A single user can fork the same template multiple times (each creates a new project), so `(template_id, user_id)` is not unique
- To calculate fork-to-deploy conversion, join with `deploy_events` on `project_id` and check for `status = 'completed'`
