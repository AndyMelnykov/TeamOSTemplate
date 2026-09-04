# Schema: `analytics.example_product.workflow_automation_runs`

Event-level table capturing every AI automation run (document extraction attempt) on the example_product platform. One row per automation run request.

**Database:** `ANALYTICS`
**Schema:** `EXAMPLE_PRODUCT`
**Table:** `WORKFLOW_AUTOMATION_RUNS`
**Refresh:** Streaming (near real-time via Snowpipe)
**Retention:** 2 years

# Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `generation_id` | VARCHAR(36) | No | Unique identifier for the automation run (UUID). Also referred to as `automation_run_id` in newer docs and narrative writeups. |
| `project_id` | VARCHAR(36) | No | Workflow this automation run belongs to (also referred to as `workflow_id`) |
| `user_id` | VARCHAR(36) | No | User who triggered the automation run |
| `org_id` | VARCHAR(36) | Yes | Organization ID (null for free-tier users) |
| `prompt_text` | TEXT | No | The user's input instruction describing what fields/clauses to extract or how to route the document |
| `prompt_token_count` | INTEGER | No | Token count of the input instruction |
| `status` | VARCHAR(20) | No | Automation run outcome: `completed`, `published`, `failed`, `timeout`, `cancelled` |
| `error_code` | VARCHAR(50) | Yes | Error code if status is `failed` or `timeout` |
| `generation_time_ms` | INTEGER | Yes | Wall-clock time from request to completion in milliseconds |
| `model_version` | VARCHAR(50) | No | AI extraction model version used (e.g., `example_product-extract-3.2`) |
| `output_type` | VARCHAR(20) | No | Type of document processed: `contract`, `invoice`, `intake_form`, `purchase_order` |
| `output_file_count` | INTEGER | Yes | Number of extracted fields/clauses produced |
| `output_token_count` | INTEGER | Yes | Token count of the extracted structured output |
| `deploy_attempted` | BOOLEAN | No | Whether the user attempted to publish this automation run's workflow (also referred to as `publish_attempted`) |
| `subscription_tier` | VARCHAR(20) | No | User's tier at time of automation run: `free`, `pro`, `teams`, `enterprise` |
| `created_at` | TIMESTAMP_NTZ | No | When the automation run was initiated (UTC) |
| `updated_at` | TIMESTAMP_NTZ | No | Last status update timestamp (UTC) |

# Indexes & Clustering

- Clustered on `(created_at, user_id)`
- Commonly filtered on `status`, `model_version`, `subscription_tier`

# Common Joins

- `users` on `user_id` - User profile and account details
- `workflows` on `project_id` (`workflow_id`) - Workflow metadata
- `publish_events` on `generation_id` (`automation_run_id`) - Publish outcomes
- `subscriptions` on `user_id` - Billing and plan information

# Notes

- **Naming note**: this table's legacy name is `project_generations` (matching this doc's filename); it is referenced as `workflow_automation_runs` in current dashboards, investigations, and experiment writeups. Both names point at the same underlying table.
- `generation_time_ms` is null for `cancelled` automation runs (user cancelled before completion)
- `error_code` values are documented in the [Error Code Reference](../../metrics/prototyping/error-codes.md)
