# Custom Domains

**Author:** Morgan Wu, Engineer
**Status:** In Progress
**Last Updated:** 2026-03-22
**Related RFC:** [`engineering/rfcs/deployment/custom-domains-rfc.md`](../../rfcs/deployment/custom-domains-rfc.md)
**Related PRD:** [`product/PRDs/deployment/custom-domains-prd.md`](../../../product/PRDs/deployment/custom-domains-prd.md)
**Related Metrics:** [`product/analytics/metrics/deployment/custom-domains-metrics.md`](../../../analytics/metrics/deployment/custom-domains-metrics.md)
**Related Data Pipeline:** [`data-engineering/plans/deployment/domain-events-pipeline.md`](../../../data-engineering/plans/deployment/domain-events-pipeline.md)

---

## Overview
Let users connect their own domain to a published example_product workflow portal instead of using the default example_productapp.dev subdomain.

## Steps
1. Add domain management API in `src/routes/domains.ts`
   - `POST /api/workflows/:id/domains` — register custom domain
   - `GET /api/workflows/:id/domains` — list connected domains with SSL status
   - `DELETE /api/workflows/:id/domains/:domainId` — remove domain
2. Build DNS verification flow
   - Generate CNAME or A record values for the user to configure
   - Poll DNS propagation status every 30s for up to 48 hours
   - Show step-by-step instructions for common registrars (GoDaddy, Namecheap, Cloudflare)
3. Add automatic SSL provisioning
   - Trigger Let's Encrypt certificate after DNS verification passes
   - Store cert in `domain_certificates` table with expiry tracking
   - Auto-renew 30 days before expiry via cron job
4. Create `DomainSettings` component in `src/components/publish/`
   - Input field for custom domain
   - Status indicators: DNS pending, DNS verified, SSL provisioning, live
   - Remove domain with confirmation dialog
5. Add tests
   - Domain registration creates DNS verification record
   - SSL provisioned after DNS verification
   - Published portal accessible on custom domain
