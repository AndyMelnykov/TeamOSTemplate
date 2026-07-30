# Customer Insights

Customer feedback, account context, and call notes for example_product's named accounts.

## Segments

| Segment | Description |
|---------|-------------|
| Enterprise | Managed accounts with complex needs (SSO, compliance, dedicated support) |
| Growth | Mid-market accounts with expansion potential |
| Self-serve | Long-tail, no individual account management |

Only named/managed accounts get folders. Self-serve customers are tracked through aggregate analytics.

## Named Accounts

| Account | Segment | Folder |
|---------|---------|--------|
| Acme Corp | Growth | [accounts/acme-corp/](accounts/acme-corp/CLAUDE.md) |
| Meridian Health | Enterprise | [accounts/meridian-health/](accounts/meridian-health/CLAUDE.md) |
| Crestview Financial | Enterprise | [accounts/crestview-financial/](accounts/crestview-financial/CLAUDE.md) |
| Stackline | Growth | [accounts/stackline/](accounts/stackline/CLAUDE.md) |
| Axiom Logistics | Enterprise | [accounts/axiom-logistics/](accounts/axiom-logistics/CLAUDE.md) |
| Helix Robotics | Growth | [accounts/helix-robotics/](accounts/helix-robotics/CLAUDE.md) |
| Volta Energy | Growth | [accounts/volta-energy/](accounts/volta-energy/CLAUDE.md) |
| NovaBridge | Growth | [accounts/novabridge/](accounts/novabridge/CLAUDE.md) |
| Pinnacle Media | Growth | [accounts/pinnacle-media/](accounts/pinnacle-media/CLAUDE.md) |

## Finding Customer Data

| Looking for... | Where to find it |
|----------------|-----------------|
| Account context, goals, risks | `accounts/{customer}/account-context.md` |
| Call summaries | `accounts/{customer}/calls/summaries/` |
| Call transcripts | `accounts/{customer}/calls/transcripts/` |
| Analytics (metrics, queries, schemas, dashboards) | `../../analytics/CLAUDE.md` (organized by product area, not by customer) |
| Feature requests for a customer | Linear / Jira / Asana: filter by customer label |
| Escalations | Linear / Jira / Asana: filter by `type:escalation` + customer label |

## Processing Customer Calls

When processing a new customer call:
1. Save summary to `accounts/{customer}/calls/summaries/{date}.md`
2. Save transcript to `accounts/{customer}/calls/transcripts/{date}.md`
3. Update `accounts/{customer}/account-context.md` with new insights
4. Log feature requests in Linear / Jira / Asana with the customer label
