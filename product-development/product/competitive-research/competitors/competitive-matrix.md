# Competitive Feature Matrix

Last updated: 2026-03-22

## How to Read This Matrix

- **Yes** - Feature fully available
- **Partial** - Feature exists but with significant limitations
- **No** - Feature not available

## Generation Quality

| Feature | example_product | Lovable | Google Stitch | v0 | Replit | Figma Make | Bolt |
|---------|-------|---------|---------------|-----|--------|------------|------|
| UI component quality | Yes | Yes | Partial | Yes | Partial | Yes | Yes |
| Responsive design | Yes | Yes | Partial | Yes | Partial | Yes | Yes |
| Design system adherence | Yes | Yes | Partial | Partial | No | Yes | Partial |
| Code maintainability | Yes | Partial | Partial | Yes | Partial | Partial | Partial |
| Iteration without full regen | Yes | Partial | Partial | Partial | Yes | No | Yes |
| Multi-page app generation | Yes | Yes | Partial | No | Yes | No | Yes |
| State management quality | Yes | Partial | Partial | Partial | Yes | No | Partial |

## Deployment

| Feature | example_product | Lovable | Google Stitch | v0 | Replit | Figma Make | Bolt |
|---------|-------|---------|---------------|-----|--------|------------|------|
| One-click deploy | Yes | Yes | Partial | Partial | Yes | No | Yes |
| Custom domain support | Yes | Yes | No | No | Yes | No | Partial |
| CI/CD pipeline | Yes | No | Partial | Partial | Partial | No | No |
| Environment management | Yes | Partial | Partial | No | Yes | No | Partial |
| Hosting included | Yes | Yes | Yes | Partial | Yes | No | Yes |
| Export to own infra | Yes | Partial | No | Yes | Yes | Partial | Partial |

## Collaboration

| Feature | example_product | Lovable | Google Stitch | v0 | Replit | Figma Make | Bolt |
|---------|-------|---------|---------------|-----|--------|------------|------|
| Real-time multiplayer editing | Yes | No | Partial | No | Yes | Yes | No |
| Team workspaces | Yes | Partial | Yes | Partial | Yes | Yes | Partial |
| Version history | Yes | Partial | Partial | Yes | Yes | Partial | Partial |
| Commenting / review | Yes | No | Partial | Partial | Partial | Yes | No |
| Role-based permissions | Yes | Partial | Yes | No | Partial | Yes | No |
| Share preview links | Yes | Yes | Yes | Yes | Yes | Partial | Yes |

## Enterprise Features

| Feature | example_product | Lovable | Google Stitch | v0 | Replit | Figma Make | Bolt |
|---------|-------|---------|---------------|-----|--------|------------|------|
| SSO / SAML | Yes | No | Yes | No | Partial | Yes | No |
| Audit logging | Yes | No | Yes | No | Partial | Partial | No |
| SOC 2 compliance | Yes | No | Yes | No | Yes | Yes | No |
| Data residency controls | Partial | No | Yes | No | No | Partial | No |
| Admin console | Yes | No | Yes | No | Partial | Yes | No |
| SLA guarantees | Yes | No | Yes | No | Partial | Yes | No |
| On-prem / private cloud | Partial | No | Partial | No | No | No | No |

## Pricing

| Feature | example_product | Lovable | Google Stitch | v0 | Replit | Figma Make | Bolt |
|---------|-------|---------|---------------|-----|--------|------------|------|
| Free tier | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Per-seat pricing | Yes | Yes | No | Yes | Yes | Yes | Yes |
| Usage-based pricing | Yes | Yes | No | Yes | Yes | No | Yes |
| Enterprise custom pricing | Yes | No | Yes | No | Yes | Yes | No |
| Starting price point | $20/mo | $20/mo | Free (beta) | $20/mo | $25/mo | Included w/ Figma | $20/mo |

## Integrations

| Feature | example_product | Lovable | Google Stitch | v0 | Replit | Figma Make | Bolt |
|---------|-------|---------|---------------|-----|--------|------------|------|
| Git (GitHub/GitLab) | Yes | Partial | Partial | Yes | Yes | No | Partial |
| Database connectors | Yes | Partial | Partial | No | Yes | No | Partial |
| Auth providers | Yes | Partial | Yes | No | Partial | No | Partial |
| API integrations | Yes | Partial | Partial | Partial | Yes | No | Partial |
| Design tool import | Yes | Partial | No | Partial | No | Yes | No |
| Cloud provider support | Yes | No | Yes | Partial | Partial | No | No |

## Customization

| Feature | example_product | Lovable | Google Stitch | v0 | Replit | Figma Make | Bolt |
|---------|-------|---------|---------------|-----|--------|------------|------|
| Tech stack selection | Yes | Partial | Partial | No | Yes | No | Partial |
| Architecture patterns | Yes | No | Partial | No | Partial | No | No |
| Custom component library | Yes | Partial | No | Partial | Partial | Yes | No |
| Theme / design token support | Yes | Partial | Partial | Partial | No | Yes | Partial |
| Code style / linting config | Yes | No | No | Partial | Yes | No | No |
| Plugin / extension system | Partial | No | No | No | Partial | Yes | No |

## Summary Scorecard

| Category | example_product | Lovable | Google Stitch | v0 | Replit | Figma Make | Bolt |
|----------|-------|---------|---------------|-----|--------|------------|------|
| Generation Quality | 5 | 4 | 3 | 4 | 3 | 2 | 4 |
| Deployment | 5 | 4 | 2 | 2 | 4 | 1 | 4 |
| Collaboration | 5 | 2 | 4 | 2 | 4 | 4 | 2 |
| Enterprise Features | 5 | 1 | 5 | 1 | 3 | 4 | 1 |
| Pricing | 4 | 4 | 4 | 3 | 4 | 3 | 4 |
| Integrations | 5 | 2 | 3 | 2 | 4 | 2 | 2 |
| Customization | 5 | 2 | 2 | 2 | 3 | 3 | 2 |

Scoring: 1 (weak) to 5 (best-in-class). Scores populated after individual teardowns are complete.

## Next Steps

1. Complete individual competitor teardowns in `teardowns/{competitor}/`
2. Fill in matrix cells from teardown findings
3. Populate summary scorecard
4. Identify top 3 competitive gaps for roadmap prioritization
