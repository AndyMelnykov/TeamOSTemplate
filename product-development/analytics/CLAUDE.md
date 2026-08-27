# example_product Analytics

Analytics resources for the example_product AI prototyping platform.

## Contents

| Folder/File | Description |
|-------------|-------------|
| `queries/` | SQL query patterns organized by product area |
| `schemas/` | Table documentation for example_product data sources, organized by product area |
| `metrics/` | Metric definitions organized by product area |
| `dashboards.md` | Links to example_product-related dashboards (Sigma, Mode, etc.) |
| `dashboards/` | Dashboard docs organized by product area |
| `experiments/` | Experiment results organized by product area |
| `investigations/` | Ad hoc investigations organized by product area |
| `playbooks/` | Repeatable analysis playbooks (e.g. funnel-analysis.md) |

---

## Data Sources

| Source | Description | Access |
|--------|-------------|--------|
| Snowflake | Primary data warehouse - generation logs, deployment events, project metadata | SQL via Snowflake connector |
| Segment | Event tracking - user actions, generation triggers, UI interactions | Segment workspace |
| Amplitude | Product analytics - funnels, retention, feature adoption | Amplitude dashboard |
| Stripe | Billing and subscription data - plan tiers, revenue, churn | Stripe dashboard + Snowflake sync |

---

## Core Metrics

Canonical metric definitions and targets live in [reference/metrics.md](../../reference/metrics.md), not here.

---

## Common Queries

Queries are stored in `queries/` and named by metric:

| Query File | Description |
|------------|-------------|
| `queries/prototyping/generation-success-rate.sql` | Generation success rate |
| `queries/billing/credit-burn-rate.sql` | Credit burn rate |
| `queries/deployment/domain-ssl-health.sql` | Domain SSL health |
| `queries/home-page/search-usage.sql` | Search usage |
| `queries/prototyping/version-restore-rate.sql` | Version restore rate |
| `queries/starter-templates/template-fork-rate.sql` | Template fork rate |
| `queries/deployment/one-click-deploy-success.sql` | One-click deploy success rate and time-to-deploy |
| `queries/deployment/domain-setup-completion.sql` | Custom domain setup funnel completion rates |

---

## Dashboards

| Dashboard | Tool | Description |
|-----------|------|-------------|
| example_product Health | Sigma | Real-time GSR, TTD, error rates, deploy volume |
| Growth & Retention | Amplitude | Signup funnel, activation, D7/D30 retention |
| Revenue | Sigma | MRR, plan distribution, expansion, churn |
| Generation Quality | Mode | Error taxonomy, framework-level success rates, iteration patterns |
