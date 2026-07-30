# Engineering

Engineering plans, RFCs, and bug investigations for example_product. All organized by product area.

## Folders

| Folder | What's Here |
|--------|-------------|
| `plans/` | Implementation plans for upcoming features |
| `rfcs/` | Technical design proposals and architecture decisions |
| `bug-investigations/` | Dated investigation plans for production bugs |

## Product Areas

All three folders share the same product-area structure:

| Product Area | Subfolder | What's Here |
|-------------|-----------|-------------|
| Billing | `billing/` | Credit usage, referral tracking, seat management, credit bugs |
| Deployment | `deployment/` | Custom domains, preview environments, SSL, deploy bugs |
| Home Page | `home-page/` | Activity feed, project search, prompt suggestions |
| Prototyping | `prototyping/` | Component library, real-time collab, version history |
| Starter Templates | `starter-templates/` | Community marketplace, template customizer |

## Naming Conventions

- **Plans:** `{feature-name}.md` (e.g., `credit-usage-dashboard.md`)
- **RFCs:** `{feature-name}-rfc.md` (e.g., `credit-usage-dashboard-rfc.md`)
- **Bug investigations:** `bug-{date}-{description}/investigation-plan.md` (e.g., `bug-03-12-2026-credit-double-charge/investigation-plan.md`)
