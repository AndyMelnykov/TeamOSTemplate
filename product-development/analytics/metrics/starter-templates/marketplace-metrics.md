# Community Marketplace - Metrics Definition

**Feature:** Community Marketplace (Starter Templates)
**Owner:** Hannah Stulberg, PM
**Analytics Lead:** Casey Nguyen

## Primary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Template publish rate | Number of new templates submitted per week | > 15/week by month 3 | `published_templates` table |
| Fork rate | Number of template forks per week | > 100/week by month 3 | `template_forks` table |
| Fork-to-deploy conversion | % of forked templates where the resulting project reaches at least one successful deployment | > 40% | `template_forks` joined with `deploy_events` |
| Average template rating | Mean rating across all rated templates in the marketplace | > 4.0 | `published_templates.avg_rating` |

## Secondary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Review queue turnaround | Median time from template submission to approval/rejection | < 24 hours | `published_templates` (created_at vs review_completed_at) |
| Publish-to-approved conversion | % of submitted templates that are approved (not rejected) | > 80% | `published_templates` where status IN ('approved', 'rejected') |
| Fork-to-customization rate | % of forks where the user applies customizations in the first session | > 60% | `template_forks.customizations_applied` |
| Repeat publisher rate | % of publishers who publish more than one template within 30 days | Tracking | `published_templates` grouped by author_id |
| Template discovery rate | % of marketplace page views that result in at least one template detail view | > 35% | Segment events: `marketplace.viewed`, `marketplace.template_clicked` |
| Rating participation rate | % of users who forked a template and subsequently rated it | > 15% | `template_forks` joined with `template_ratings` |

## Guardrail Metrics

| Metric | Definition | Threshold | Source |
|--------|-----------|-----------|--------|
| Abuse report rate | % of approved templates that receive abuse reports | < 2% | `template_reports` table |
| Marketplace page load time (p95) | 95th percentile page load for the marketplace browse page | < 2s | Datadog RUM |
| Fork error rate | % of fork attempts that fail | < 1% | `template_forks` joined with error logs |

## Data Sources

- **`published_templates`** - Template metadata and review status in Snowflake, populated via backend event logging
- **`template_forks`** - Fork events in Snowflake, populated via Snowpipe
- **`template_ratings`** - Individual rating records in Snowflake
- **`deploy_events`** - Deployment outcomes, joined by `project_id` to connect forks to deploys
- **Segment** - Frontend interaction events (marketplace views, clicks, searches)
- **Datadog RUM** - Page load performance and client-side errors

## Dashboard Links

- [Community Marketplace Dashboard](https://app.sigma.com/example_product-labs/dashboard/community-marketplace) - Weekly metrics review
- [Marketplace Health Monitor](https://app.datadoghq.com/example_product-labs/dashboard/marketplace-health) - Real-time performance and error monitoring

## Related Queries

| Query | Description |
|-------|-------------|
| [template-fork-rate.sql](../../queries/starter-templates/template-fork-rate.sql) | Template fork rate, top templates, conversion |

## Related Investigations

| Investigation | Date | Summary |
|--------------|------|---------|
| [2026-03-08-template-fork-to-deploy-conversion.md](../../investigations/starter-templates/2026-03-08-template-fork-to-deploy-conversion.md) | 2026-03-08 | Template fork-to-deploy conversion analysis |
