# Onboarding: Data Engineering

Data engineering-specific setup and orientation for data engineers joining example_product.

## Setup

### Shared Tools (everyone gets these)

See [General Onboarding](onboarding-general.md#shared-tools-everyone-gets-these).

### Function-Specific Tools

| Tool | Purpose | Access |
|------|---------|--------|
| Snowflake | Data warehouse | Request access from Grace Lin |
| dbt | Data transformations and modeling | Access via `example_product-data` repo |
| Fivetran | Data ingestion pipelines | Admin access from Grace Lin |
| Airflow | Pipeline orchestration | Access via `example_product-data` repo |
| AWS Console | S3, Lambda, data infrastructure | Request from Sam Torres |

### Repos

| Repo | Why |
|------|-----|
| `example_product-data` | dbt models, Airflow DAGs, pipeline configs |
| `example_product-infra` | Terraform for data infrastructure |
| `example_product-product` | Analytics schemas, metric definitions |

### Environment Setup

1. Complete [General Onboarding](onboarding-general.md) setup first
2. Clone `example_product-data` and follow its `CONTRIBUTING.md` for local setup
3. Get Snowflake access and connect your SQL client
4. Get Fivetran access and review current connector configurations
5. Set up local dbt and run a test build against the dev schema
6. Review Airflow DAGs and understand the current pipeline schedule

## Key Documents

- [Analytics CLAUDE.md](../product/analytics/CLAUDE.md) - metrics glossary, data sources, schema docs
- [Analytics Schemas](../product/analytics/) - table definitions and column descriptions
- [Product CLAUDE.md](../product/CLAUDE.md) - product context for understanding what data matters

## Slack Channels

| Channel | Purpose |
|---------|---------|
| `#example_product-eng` | Engineering discussion, relevant for pipeline dependencies |
| `#example_product-general` | Team-wide announcements |
| `#example_product-incidents` | Incidents that may affect data pipelines |
| `#example_product-deploys` | Deploy notifications that may trigger pipeline runs |

## People to Meet

| Person | Why |
|--------|-----|
| Grace Lin | Data lead - pipeline architecture, access, priorities |
| Casey Nguyen | Analytics - downstream consumer of your pipelines |
| Sam Torres | Engineering architecture - upstream data sources |
| Morgan Wu | Infrastructure - shared infra and deployment |

## Org Chart

Data engineering works closely with Analytics (downstream consumers) and Engineering (upstream data sources). Data lead: Grace Lin. Primary analytics partner: Casey Nguyen. Infrastructure partner: Morgan Wu.

## First Tasks

- [ ] Get Snowflake, Fivetran, and dbt access configured
- [ ] Run a local dbt build against the dev schema
- [ ] Review the current Airflow DAG schedule and pipeline dependencies
- [ ] Trace one data pipeline end-to-end (source → ingestion → transformation → dashboard)
- [ ] Meet with Grace for architecture walkthrough and current priorities
- [ ] Pick up a small pipeline task from Linear / Jira / Asana (your manager will assign one)
