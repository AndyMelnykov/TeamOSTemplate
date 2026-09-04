# DESCRIBE TABLE: `analytics.example_product.credit_transactions`

Credit transaction ledger recording every credit movement in the example_product platform. Credits are consumed as pages/documents are processed through automation runs and published portals. Each row represents a single debit or credit event. This is an append-only table -- corrections are modeled as new rows with category `refund`.

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `transaction_id` | `VARCHAR(36)` | NOT NULL | Primary key. UUID v4 generated at insert time. |
| `user_id` | `VARCHAR(36)` | NOT NULL | Foreign key to `dim_users.user_id`. The user whose balance was affected. |
| `org_id` | `VARCHAR(36)` | NULL | Foreign key to `dim_organizations.org_id`. Populated for users on Teams plans. NULL for individual Pro users. |
| `amount` | `INTEGER` | NOT NULL | Number of credits involved in the transaction. Always positive -- direction is indicated by the `type` column. |
| `type` | `VARCHAR(10)` | NOT NULL | Direction of the transaction. Values: `debit` (credits consumed), `credit` (credits added). |
| `category` | `VARCHAR(20)` | NOT NULL | Classification of the transaction. Values: `automation_run` (pages processed during extraction), `edit` (refinement to an existing workflow), `publish` (publishing a workflow to a live portal), `refund`, `referral`, `bonus`. |
| `reference_id` | `VARCHAR(36)` | NULL | Foreign key to the originating entity (e.g., `workflow_automation_runs.generation_id`, `publish_events.deploy_id`). NULL for bonus and referral credits. |
| `project_id` | `VARCHAR(36)` | NULL | Foreign key to `dim_workflows.project_id`. The workflow this transaction is tied to (also referred to as `workflow_id`). NULL for transactions not tied to a workflow (e.g., referral bonuses, plan credits). |
| `balance_after` | `INTEGER` | NOT NULL | User's credit balance immediately after this transaction was applied. Denormalized for fast balance lookups. |
| `subscription_tier` | `VARCHAR(20)` | NOT NULL | User's subscription tier at the time of the transaction. Values: `free`, `pro`, `teams`, `enterprise`. Captured at write time so historical analysis reflects the tier when the event occurred, not the current tier. |
| `created_at` | `TIMESTAMP_TZ` | NOT NULL | Timestamp when the transaction was recorded. Sourced from the application server clock at insert time. |

## Indexes

| Index Name | Columns | Type | Notes |
|------------|---------|------|-------|
| `pk_credit_transactions` | `transaction_id` | Primary key | Unique, clustered. |
| `idx_ct_user_created` | `user_id`, `created_at` | Composite | Powers the daily usage query for the dashboard. Most common access pattern. |
| `idx_ct_user_category` | `user_id`, `category` | Composite | Supports filtering by transaction category. |
| `idx_ct_project` | `project_id` | Single column | Supports per-workflow usage breakdowns. |
| `idx_ct_org_created` | `org_id`, `created_at` | Composite | Powers team/org-level usage queries. |
| `idx_ct_created` | `created_at` | Single column | Supports time-range scans for analytics pipelines and backfills. |

## Common Joins

| Join Target | Join Key | Use Case |
|-------------|----------|----------|
| `dim_users` | `user_id = dim_users.user_id` | Enrich with user email, name, signup date, current plan. |
| `dim_organizations` | `org_id = dim_organizations.org_id` | Enrich with org name, plan type, seat count for team-level reporting. |
| `dim_workflows` | `project_id = dim_workflows.project_id` | Enrich with workflow name, created date, workflow type for per-workflow breakdowns. |
| `workflow_automation_runs` | `reference_id = workflow_automation_runs.generation_id` | Link credit debits to specific automation run events for cost-per-page analysis. |
| `publish_events` | `reference_id = publish_events.deploy_id` | Link credit debits to publish events for publish cost analysis. |
| `dim_subscription_plans` | `subscription_tier = dim_subscription_plans.tier` | Look up plan credit allocation, price, and features for utilization rate calculations. |

## Notes

- **Naming note**: `project_id` here is referenced as `workflow_id`, and the joined `workflow_automation_runs`/`publish_events` tables are referenced by their legacy names `project_generations`/`deploy_events` in some older docs. All refer to the same underlying entities.
- **Source system**: Supabase PostgreSQL (`public.credit_transactions`), replicated to Snowflake via Fivetran with a sync interval of 15 minutes.
- **Grain**: One row per credit transaction event. A single user action (e.g., an automation run processing a document) produces exactly one debit row.
- **Volume**: Approximately 2.4M rows as of March 2026, growing at roughly 120K rows/week.
- **Retention**: No retention policy. All historical transactions are retained indefinitely for auditing and trend analysis.
- **`balance_after` integrity**: The `balance_after` column is maintained within a database transaction in the source system. If discrepancies are detected during Fivetran sync, a data quality alert fires in the `#data-alerts` Slack channel.
- **`subscription_tier` is snapshot**: This column captures the tier at transaction time. For current-tier analysis, join to `dim_users` instead.
- **Backfill**: Historical transactions prior to the ledger migration (December 2025) were backfilled from Stripe payment events and may have `reference_id` set to NULL.
