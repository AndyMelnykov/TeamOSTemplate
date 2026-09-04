# Competitive Feature Matrix

Last updated: 2026-03-22

## How to Read This Matrix

- **Yes** - Feature fully available
- **Partial** - Feature exists but with significant limitations
- **No** - Feature not available

## Extraction Quality

| Feature | example_product | PandaDoc | Conga | Dropbox Sign | Ironclad | Adobe Acrobat Sign | DocuSign |
|---------|-------|---------|---------------|-----|--------|------------|------|
| OCR / scanned document support | Yes | Partial | Yes | No | Partial | Yes | Partial |
| Field-level extraction accuracy | Yes | Partial | Yes | No | Yes | Partial | Partial |
| Clause / contract-language detection | Yes | Partial | Partial | No | Yes | No | Partial |
| Extraction confidence scoring | Yes | No | Partial | No | Partial | No | No |
| Refinement without full re-upload | Yes | Partial | Partial | No | Yes | No | Partial |
| Multi-format ingestion (PDF/scan/DOCX) | Yes | Yes | Partial | No | Yes | Yes | Yes |
| Table / line-item extraction | Yes | Partial | Yes | No | Partial | No | Partial |

## Publishing

| Feature | example_product | PandaDoc | Conga | Dropbox Sign | Ironclad | Adobe Acrobat Sign | DocuSign |
|---------|-------|---------|---------------|-----|--------|------------|------|
| One-click publish | Yes | Yes | Partial | Yes | Yes | Partial | Yes |
| Custom domain support | Yes | Yes | No | No | Yes | No | Partial |
| CI/CD-style staged rollout | Yes | No | Partial | No | Partial | No | No |
| Environment management (staging/preview) | Yes | Partial | Partial | No | Yes | No | Partial |
| Hosting included | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Export to own infra | Yes | Partial | No | No | Yes | Partial | Partial |

## Collaboration

| Feature | example_product | PandaDoc | Conga | Dropbox Sign | Ironclad | Adobe Acrobat Sign | DocuSign |
|---------|-------|---------|---------------|-----|--------|------------|------|
| Real-time multiplayer editing | Yes | No | Partial | No | Yes | No | No |
| Team workspaces | Yes | Partial | Yes | Partial | Yes | Yes | Partial |
| Version history | Yes | Partial | Partial | No | Yes | Partial | Partial |
| Commenting / review | Yes | Partial | Partial | No | Yes | Partial | No |
| Role-based permissions | Yes | Partial | Yes | No | Yes | Yes | Partial |
| Share preview links | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

## Enterprise Features

| Feature | example_product | PandaDoc | Conga | Dropbox Sign | Ironclad | Adobe Acrobat Sign | DocuSign |
|---------|-------|---------|---------------|-----|--------|------------|------|
| SSO / SAML | Yes | No | Yes | No | Yes | Yes | Partial |
| Audit logging | Yes | No | Yes | No | Yes | Partial | Partial |
| SOC 2 compliance | Yes | Partial | Yes | Yes | Yes | Yes | Yes |
| Data residency controls | Partial | No | Yes | No | Partial | Partial | Partial |
| Admin console | Yes | Partial | Yes | No | Yes | Yes | Yes |
| SLA guarantees | Yes | No | Yes | No | Yes | Yes | Yes |
| On-prem / private cloud | Partial | No | Partial | No | No | No | No |

## Pricing

| Feature | example_product | PandaDoc | Conga | Dropbox Sign | Ironclad | Adobe Acrobat Sign | DocuSign |
|---------|-------|---------|---------------|-----|--------|------------|------|
| Free tier | Yes | Yes | No | Yes | No | No | Yes |
| Per-seat pricing | Yes | Yes | No | Yes | Yes | Yes | Yes |
| Usage-based pricing | Yes | Partial | No | Yes | No | Partial | Yes |
| Enterprise custom pricing | Yes | Yes | Yes | No | Yes | Yes | Yes |
| Starting price point | $29/mo | $19/mo | Custom only | $20/mo | Custom only | $19.99/mo | $25/mo |

## Integrations

| Feature | example_product | PandaDoc | Conga | Dropbox Sign | Ironclad | Adobe Acrobat Sign | DocuSign |
|---------|-------|---------|---------------|-----|--------|------------|------|
| CRM connectors | Yes | Yes | Yes | Partial | Yes | Partial | Yes |
| Storage connectors (Drive/Box/Dropbox) | Yes | Yes | Partial | Yes | Partial | Yes | Yes |
| Identity providers | Yes | Partial | Yes | Partial | Yes | Yes | Yes |
| API access | Yes | Yes | Partial | Yes | Yes | Yes | Yes |
| Payment collection | Yes | Yes | No | No | No | No | Partial |
| ERP connectors | Yes | No | Yes | No | Partial | No | Partial |

## Customization

| Feature | example_product | PandaDoc | Conga | Dropbox Sign | Ironclad | Adobe Acrobat Sign | DocuSign |
|---------|-------|---------|---------------|-----|--------|------------|------|
| Extraction rule configuration | Yes | Partial | Partial | No | Yes | No | Partial |
| Approval routing patterns | Yes | Partial | Yes | No | Yes | Partial | Partial |
| Custom clause/field block library | Yes | Partial | No | No | Yes | No | Partial |
| Branding / white-label | Yes | Partial | Partial | Partial | Partial | Yes | Partial |
| Validation rule / logic config | Yes | No | Partial | No | Yes | No | No |
| Plugin / extension system | Partial | No | Partial | No | Partial | Yes | Partial |

## Summary Scorecard

| Category | example_product | PandaDoc | Conga | Dropbox Sign | Ironclad | Adobe Acrobat Sign | DocuSign |
|----------|-------|---------|---------------|-----|--------|------------|------|
| Extraction Quality | 5 | 3 | 4 | 1 | 4 | 2 | 3 |
| Publishing | 5 | 3 | 2 | 3 | 4 | 2 | 3 |
| Collaboration | 5 | 2 | 4 | 1 | 5 | 3 | 2 |
| Enterprise Features | 5 | 1 | 5 | 1 | 4 | 4 | 4 |
| Pricing | 4 | 4 | 2 | 4 | 3 | 3 | 4 |
| Integrations | 5 | 4 | 3 | 3 | 4 | 3 | 4 |
| Customization | 5 | 2 | 3 | 1 | 4 | 2 | 2 |

Scoring: 1 (weak) to 5 (best-in-class). Scores populated after individual teardowns are complete.

## Next Steps

1. Complete individual competitor teardowns in `teardowns/{competitor}/`
2. Fill in matrix cells from teardown findings
3. Populate summary scorecard
4. Identify top 3 competitive gaps for roadmap prioritization
