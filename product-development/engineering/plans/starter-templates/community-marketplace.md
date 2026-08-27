---
**Related RFC:** [`engineering/rfcs/starter-templates/community-marketplace-rfc.md`](../../rfcs/starter-templates/community-marketplace-rfc.md)
**Related PRD:** [`product/PRDs/starter-templates/community-marketplace-prd.md`](../../../product/PRDs/starter-templates/community-marketplace-prd.md)
**Related Analytics Plan:** [`data-engineering/plans/starter-templates/marketplace-analytics.md`](../../../data-engineering/plans/starter-templates/marketplace-analytics.md)
**Metrics:** [`product/analytics/metrics/starter-templates/marketplace-metrics.md`](../../../analytics/metrics/starter-templates/marketplace-metrics.md)
**Schemas:** [`published_templates`](../../../analytics/schemas/starter-templates/published_templates.md) | [`template_forks`](../../../analytics/schemas/starter-templates/template_forks.md)
**Dashboards:** [`product/analytics/dashboards/starter-templates/marketplace-dashboards.md`](../../../analytics/dashboards/starter-templates/marketplace-dashboards.md)
---

# Community marketplace

## Overview
Let users publish their projects as templates and discover templates created by others, with ratings and usage stats to surface the best ones.

## Steps
1. Add "Publish as template" flow
   - Button in project settings → opens publish dialog
   - User adds title, description, category, preview screenshots
   - Submitted to `published_templates` table with status: pending review
2. Add marketplace API endpoints in `src/routes/marketplace.ts`
   - `GET /api/marketplace` — browse with category filters, sort by popular/new
   - `GET /api/marketplace/:id` — template detail with preview and stats
   - `POST /api/marketplace/:id/use` — fork template into user's projects
3. Create `MarketplaceBrowser` component in `src/components/templates/`
   - Grid layout with template cards: preview image, title, author, use count
   - Category sidebar: SaaS, portfolio, e-commerce, internal tool, landing page
   - Search bar with full-text search across titles and descriptions
4. Add ratings and usage tracking
   - 5-star rating after using a template for >10 minutes
   - Track fork count and display on template cards
5. Add tests
   - Publish flow creates pending template
   - Browse returns filtered and sorted results
   - Fork creates independent copy in user's projects
