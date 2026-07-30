# Custom Domains - Metrics Definition

**Feature:** Custom Domains
**Owner:** Hannah Stulberg, PM
**Analytics Lead:** Casey Nguyen

# Primary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Domain setup completion rate | % of users who start the custom domain flow (add a domain) and reach `Live` status | > 75% | `custom_domains` table, funnel: `created` -> `dns_verified` -> `ssl_provisioned` -> `live` |
| Time-to-live | Median elapsed time from domain added (`created_at`) to first request served on the custom domain | < 10 min | `custom_domains.created_at` to first `domain_request_events.timestamp` |

# Secondary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| SSL provision success rate | % of DNS-verified domains that successfully receive an SSL certificate on the first attempt | > 99% | `domain_certificates` where `status = 'active'` / total DNS-verified domains |
| Renewal success rate | % of auto-renewal attempts that succeed without manual intervention | > 99.5% | `domain_certificates` where renewal attempted and `status` remained `active` |
| DNS verification success rate | % of added domains that reach `dns_status = 'verified'` within 48 hours | > 80% | `custom_domains` where `dns_status = 'verified'` / total created |
| DNS verification time | Median time from domain added to DNS verified | < 30 min | `custom_domains.created_at` to timestamp of `dns_status = 'verified'` transition |
| Free-to-Pro conversion lift | Relative increase in Free-to-Pro conversion among users who encounter the custom domain upgrade CTA | +15% | `custom_domain_events` joined with `subscriptions` |
| Domain removal rate | % of custom domains removed within 30 days of being added | < 10% | `custom_domains` where deleted within 30 days of `created_at` |

# Data Sources

- **`custom_domains`** -- Primary domain table in Snowflake, populated via backend event logging
- **`domain_certificates`** -- Certificate lifecycle table, tracks issuance, renewal, and expiry
- **`domain_request_events`** -- Edge proxy logs for requests served on custom domains (via Snowpipe)
- **`subscriptions`** -- Stripe subscription data synced daily via Fivetran
- **`custom_domain_events`** -- Segment events for domain add, verify, remove, and upgrade CTA interactions

# Dashboard Links

- [Custom Domains Health Dashboard](https://app.sigmacomputing.com/example_product-labs/workbook/custom-domains-health) -- Real-time SSL status, verification rates, active domain count
- [Custom Domains Feature Board](https://app.mode.com/example_product-labs/reports/custom-domains) -- Weekly metrics review, funnel analysis, conversion impact

## Related Queries

| Query | Description |
|-------|-------------|
| [domain-ssl-health.sql](../../queries/deployment/domain-ssl-health.sql) | SSL cert health and renewal monitoring |
| [domain-setup-completion.sql](../../queries/deployment/domain-setup-completion.sql) | Setup funnel completion rates |

## Related Investigations

| Investigation | Date | Summary |
|--------------|------|---------|
| [2026-03-18-custom-domain-adoption-funnel.md](../../investigations/deployment/2026-03-18-custom-domain-adoption-funnel.md) | 2026-03-18 | Custom domain adoption funnel drop-off analysis |
