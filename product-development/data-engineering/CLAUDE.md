# Data Engineering

Data pipeline plans and RFCs for example_product. Organized by product area.

## Folders

| Folder | What's Here |
|--------|-------------|
| `plans/` | Data pipeline implementation plans |
| `rfcs/` | Data pipeline design proposals |

## Product Areas

Both folders share the same product-area structure:

| Product Area | Subfolder | What's Here |
|-------------|-----------|-------------|
| Billing | `billing/` | Credit ledger data model |
| Deployment | `deployment/` | Domain events pipeline |
| Home Page | `home-page/` | Search events pipeline |
| Prototyping | `prototyping/` | Version snapshots pipeline |
| Starter Templates | `starter-templates/` | Marketplace analytics pipeline |

## Naming Conventions

- **Plans:** `{pipeline-name}.md` (e.g., `credit-ledger-model.md`)
- **RFCs:** `{pipeline-name}-rfc.md` (e.g., `credit-ledger-model-rfc.md`)
