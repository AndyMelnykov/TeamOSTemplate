# Schema: `analytics.example_product.published_templates`

Dimension table tracking all templates published to the Community Marketplace. One row per published template submission. Includes both approved and rejected templates for funnel analysis.

**Database:** `ANALYTICS`
**Schema:** `EXAMPLE_PRODUCT`
**Table:** `PUBLISHED_TEMPLATES`
**Refresh:** Streaming (near real-time via Snowpipe)
**Retention:** Indefinite

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `template_id` | VARCHAR(36) | No | Unique identifier for the published template (UUID) |
| `source_project_id` | VARCHAR(36) | No | Project that was published as a template |
| `author_id` | VARCHAR(36) | No | User who published the template |
| `title` | VARCHAR(200) | No | Display title for the template |
| `description` | TEXT | No | Author-provided description of the template |
| `category` | VARCHAR(50) | No | Template category: `saas`, `portfolio`, `e-commerce`, `landing-page`, `internal-tool` |
| `preview_images` | VARIANT | No | JSON array of preview image objects (`url`, `alt`, `order`) |
| `status` | VARCHAR(20) | No | Review status: `pending`, `approved`, `rejected` |
| `fork_count` | INTEGER | No | Total number of times this template has been forked |
| `avg_rating` | FLOAT | Yes | Average user rating (1.0 - 5.0), null if no ratings |
| `rating_count` | INTEGER | No | Total number of ratings received |
| `author_subscription_tier` | VARCHAR(20) | No | Author's subscription tier at time of publish: `free`, `pro`, `teams`, `enterprise` |
| `review_completed_at` | TIMESTAMP_NTZ | Yes | When the template was approved or rejected (null if still pending) |
| `created_at` | TIMESTAMP_NTZ | No | When the template was submitted (UTC) |
| `updated_at` | TIMESTAMP_NTZ | No | Last update timestamp (UTC) |

## Indexes & Clustering

- Clustered on `(created_at, category)`
- Commonly filtered on `status`, `category`, `author_id`

## Common Joins

- `users` on `author_id` - Author profile, account age, subscription details
- `projects` on `source_project_id` - Source project metadata, generation history
- `template_forks` on `template_id` - Fork events and downstream project outcomes
- `template_ratings` on `template_id` - Individual rating records

## Notes

- `fork_count` is a denormalized counter updated in near real-time; for exact counts, aggregate from `template_forks`
- `avg_rating` is null until the template receives its first rating
- `preview_images` uses Snowflake VARIANT type; parse with `PARSE_JSON()` or `LATERAL FLATTEN()`
- Templates with status `rejected` are retained for review process analytics but excluded from marketplace-facing queries
