# One-Click Publish - Metrics Definition

**Feature:** One-Click Publish
**Owner:** Jordan Reeves, PM
**Analytics Lead:** Grace Lin

# Primary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Publish success rate | % of publish attempts that complete without error | > 95% | `publish_events` table (legacy name: `deploy_events`) |
| Time-to-publish | Median seconds from "Publish" click to live portal URL | < 45s | `publish_events.duration_ms` |

# Secondary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Publish-to-paid conversion | % of free users who upgrade within 7 days of first publish | > 8% | `publish_events` joined with `subscriptions` |
| Repeat publishes (7d) | % of publishers who publish again within 7 days | > 40% | `publish_events` |
| Publish error rate by type | Breakdown of publish failures by error category | Tracking only | `publish_events` where status = 'failed' |

# Data Sources

- **`publish_events`** - Primary event table in Snowflake, populated via backend event logging (legacy name: `deploy_events`)
- **`subscriptions`** - Stripe subscription data synced daily via Fivetran
- **`workflow_automation_runs`** - Upstream automation run data linked by `project_id`/`workflow_id` (legacy name: `project_generations`)

# Dashboard Links

- [Publish Pipeline Dashboard](https://app.datadoghq.com/example_product-labs/dashboard/deploy-pipeline) - Real-time monitoring
- [One-Click Publish Feature Board](https://app.mode.com/example_product-labs/reports/one-click-deploy) - Weekly metrics review

## Related Queries

| Query | Description |
|-------|-------------|
| [one-click-deploy-success.sql](../../queries/deployment/one-click-deploy-success.sql) | Publish success rate, TTP, conversion |
