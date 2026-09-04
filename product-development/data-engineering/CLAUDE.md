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
| Billing | `billing/` | Billing ledger data model (pages/automation runs consumed against plan credits) |
| Deployment | `deployment/` | Domain events pipeline (custom portal domain lifecycle) |
| Home Page | `home-page/` | Search events pipeline (search across workflows, templates, automation runs) |
| Prototyping | `prototyping/` | Version snapshots pipeline (workflow/template version history) |
| Starter Templates | `starter-templates/` | Marketplace analytics pipeline (contract/invoice/intake-form template marketplace) |

## Naming Conventions

- **Plans:** `{pipeline-name}.md` (e.g., `credit-ledger-model.md`)
- **RFCs:** `{pipeline-name}-rfc.md` (e.g., `credit-ledger-model-rfc.md`)
