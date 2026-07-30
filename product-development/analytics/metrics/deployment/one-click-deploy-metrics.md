# One-Click Deploy - Metrics Definition

**Feature:** One-Click Deploy
**Owner:** Jordan Reeves, PM
**Analytics Lead:** Grace Lin

# Primary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Deploy success rate | % of deploy attempts that complete without error | > 95% | `deploy_events` table |
| Time-to-deploy | Median seconds from "Deploy" click to live URL | < 45s | `deploy_events.duration_ms` |

# Secondary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Deploy-to-paid conversion | % of free users who upgrade within 7 days of first deploy | > 8% | `deploy_events` joined with `subscriptions` |
| Repeat deploys (7d) | % of deployers who deploy again within 7 days | > 40% | `deploy_events` |
| Deploy error rate by type | Breakdown of deploy failures by error category | Tracking only | `deploy_events` where status = 'failed' |

# Data Sources

- **`deploy_events`** - Primary event table in Snowflake, populated via backend event logging
- **`subscriptions`** - Stripe subscription data synced daily via Fivetran
- **`project_generations`** - Upstream generation data linked by `project_id`

# Dashboard Links

- [Deploy Pipeline Dashboard](https://app.datadoghq.com/example_product-labs/dashboard/deploy-pipeline) - Real-time monitoring
- [One-Click Deploy Feature Board](https://app.mode.com/example_product-labs/reports/one-click-deploy) - Weekly metrics review

## Related Queries

| Query | Description |
|-------|-------------|
| [one-click-deploy-success.sql](../../queries/deployment/one-click-deploy-success.sql) | Deploy success rate, TTD, conversion |
