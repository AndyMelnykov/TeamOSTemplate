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

| Metric | Definition | Target |
|--------|------------|--------|
| **Generation Success Rate (GSR)** | Percentage of generations that produce working, error-free code | > 92% |
| **Time-to-Deploy (TTD)** | Median elapsed time from first generation to production deployment | < 15 min |
| **Project Completion Rate (PCR)** | Percentage of projects that reach at least one deployment | > 60% |
| **User Retention (D7)** | Percentage of new users who return within 7 days | > 45% |
| **Iteration Depth** | Average number of follow-up generations per project | Tracking (higher = engagement) |
| **Deploy Frequency** | Average deploys per active project per week | > 2 |
| **Error Recovery Rate** | Percentage of failed generations that succeed on retry/iteration | > 80% |

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
