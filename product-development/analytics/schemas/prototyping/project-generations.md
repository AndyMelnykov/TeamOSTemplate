# Schema: `analytics.example_product.project_generations`

Event-level table capturing every AI generation attempt on the example_product platform. One row per generation request.

**Database:** `ANALYTICS`
**Schema:** `EXAMPLE_PRODUCT`
**Table:** `PROJECT_GENERATIONS`
**Refresh:** Streaming (near real-time via Snowpipe)
**Retention:** 2 years

# Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `generation_id` | VARCHAR(36) | No | Unique identifier for the generation (UUID) |
| `project_id` | VARCHAR(36) | No | Project this generation belongs to |
| `user_id` | VARCHAR(36) | No | User who triggered the generation |
| `org_id` | VARCHAR(36) | Yes | Organization ID (null for free-tier users) |
| `prompt_text` | TEXT | No | The user's input prompt |
| `prompt_token_count` | INTEGER | No | Token count of the input prompt |
| `status` | VARCHAR(20) | No | Generation outcome: `completed`, `deployed`, `failed`, `timeout`, `cancelled` |
| `error_code` | VARCHAR(50) | Yes | Error code if status is `failed` or `timeout` |
| `generation_time_ms` | INTEGER | Yes | Wall-clock time from request to completion in milliseconds |
| `model_version` | VARCHAR(50) | No | AI model version used (e.g., `example_product-gen-3.2`) |
| `output_type` | VARCHAR(20) | No | Type of output: `web_app`, `api`, `component`, `full_stack` |
| `output_file_count` | INTEGER | Yes | Number of files generated |
| `output_token_count` | INTEGER | Yes | Token count of the generated output |
| `deploy_attempted` | BOOLEAN | No | Whether the user attempted to deploy this generation |
| `subscription_tier` | VARCHAR(20) | No | User's tier at time of generation: `free`, `pro`, `teams`, `enterprise` |
| `created_at` | TIMESTAMP_NTZ | No | When the generation was initiated (UTC) |
| `updated_at` | TIMESTAMP_NTZ | No | Last status update timestamp (UTC) |

# Indexes & Clustering

- Clustered on `(created_at, user_id)`
- Commonly filtered on `status`, `model_version`, `subscription_tier`

# Common Joins

- `users` on `user_id` - User profile and account details
- `projects` on `project_id` - Project metadata
- `deploy_events` on `generation_id` - Deployment outcomes
- `subscriptions` on `user_id` - Billing and plan information

# Notes

- `generation_time_ms` is null for `cancelled` generations (user cancelled before completion)
- `error_code` values are documented in the [Error Code Reference](../metrics/error-codes.md)
