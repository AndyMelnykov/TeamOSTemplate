# Figma Make — Pricing Analysis

_Last reviewed: 2026-03-23_

![Figma Make pricing page](images/figma-make-pricing.png)

## Pricing Model

Per-seat pricing with seat type differentiation (Full seat, Dev seat, Collab seat). AI credits are included per seat per month. Figma Make is bundled into the Figma subscription -- it is not available as a standalone product. This means existing Figma customers get Make at no incremental cost, which is a significant distribution advantage. Free seats with view and comment access are available on all plans. Figma is also free for students and educators.

## Tiers

| Tier | Price | Key Inclusions | Limits |
|------|-------|----------------|--------|
| Starter (Free) | $0/mo | Unlimited drafts, UI kits and templates, 150 AI credits/day (up to 500/mo) | 500 AI credits/mo |
| Professional | $20/mo (Full), $15/mo (Dev), $5/mo (Collab) | 3,000 AI credits/mo, unlimited files and projects, team-wide design libraries, advanced Dev Mode inspection and MCP Server | Per-seat billing |
| Organization | $55/mo (Full), $25/mo (Dev), $5/mo (Collab) -- billed annually | 3,500 AI credits/mo, unlimited teams, shared libraries and fonts, centralized admin tools | Billed annually |
| Enterprise | $90/mo (Full), $35/mo (Dev), $5/mo (Collab) -- billed annually | 4,250 AI credits/mo, custom team workspaces, design system theming and APIs, SCIM seat management | Billed annually, contact sales |

![Figma Make tier breakdown](images/figma-make-tiers.png)

## Free Tier

Unlimited drafts. UI kits and templates. 150 AI credits per day, up to 500 per month. View and comment access for free collaborators on all plans. The free tier is reasonably generous for individual exploration but constrains serious team usage. The 500 credits/mo cap is the primary upgrade trigger.

## Enterprise

$90/mo per Full seat, $35/mo per Dev seat, $5/mo per Collab seat (all billed annually). Includes:
- 4,250 AI credits/mo per seat
- Custom team workspaces
- Design system theming and APIs
- SCIM seat management
- For businesses designing multiple products or brands needing enterprise-level security and scalable design systems

## Comparison to example_product

Figma Make's bundling into the existing Figma subscription is its biggest competitive advantage -- it's effectively "free" for the millions of teams already paying for Figma. However, Make is design-first (starts from Figma designs, not prompts), generates frontend code only, and lacks deployment or hosting capabilities.

example_product's full-stack generation, deployment pipeline, and prompt-first approach serve a fundamentally different workflow. The seat-type model (Full/Dev/Collab) at different price points is more granular than example_product's pricing structure.

| Dimension | Figma Make | example_product | Notes |
|-----------|------------|-------|-------|
| Entry price | $0 (bundled with Figma) | Comparable free tier | Figma wins on distribution -- already in designer workflows |
| Per-seat cost | $20-$90/mo depending on seat type and tier | Simpler per-seat model | Figma's granular seat types add complexity but can be cheaper for mixed teams |
| Code output | Frontend only (HTML/CSS/React) | Full-stack (frontend + backend + DB + auth) | example_product delivers significantly more value per generation |
| Deployment | None -- export code only | One-click deploy, custom domains, CI/CD | example_product -- Make requires separate hosting solution |
| AI credits | 500-4,250/mo per seat depending on tier | Different model | Hard to compare directly |
| Enterprise features | SCIM, design system APIs | SSO, audit logs, team workspaces, compliance | example_product has broader enterprise feature set |
