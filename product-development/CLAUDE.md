# Product Development

All product development artifacts for example_product - product, engineering, analytics, data engineering, and design.

## Doc Index

| Path | Description |
|------|-------------|
| [product/CLAUDE.md](product/CLAUDE.md) | PRDs, strategy, customers, competitive research, launch emails, sales enablement, workstreams |
| [engineering/CLAUDE.md](engineering/CLAUDE.md) | Engineering plans, RFCs, bug investigations - organized by product area |
| [analytics/CLAUDE.md](analytics/CLAUDE.md) | Metrics glossary, SQL queries, table schemas, dashboards, experiments, investigations |
| [data-engineering/CLAUDE.md](data-engineering/CLAUDE.md) | Data pipeline plans and RFCs - organized by product area |
| [design/CLAUDE.md](design/CLAUDE.md) | Design docs (stub - design artifacts live in Figma, linked from PRDs) |
| `feature-index.yaml` | Master feature index - every feature mapped to its PRDs, RFCs, plans, schemas, experiments, tickets |
| `analytics/data-catalog.yaml` | Data warehouse table registry - descriptions, owners, refresh cadence, upstream sources |
| [product/customers/CLAUDE.md](product/customers/CLAUDE.md) | Customer accounts routing table - named accounts, segments, data source pointers |

## `feature-index.yaml` optional keys

Beyond the artifact pointers already in use (`prd:`, `eng-rfc:`, etc.), any entry may carry:

| Key | Purpose |
|-----|---------|
| `opportunity:` / `hypothesis:` | Pointers to the discovery artifacts that justify the feature — see [reference/discovery-artifact-types.md](../reference/discovery-artifact-types.md) |
| `read_first:` | Paths an agent should open before anything else in this entry |
| `do_not_load_by_default:` | Paths that exist but shouldn't be pulled in without a specific reason (e.g. an archived experiment) |
