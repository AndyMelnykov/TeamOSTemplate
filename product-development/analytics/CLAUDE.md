# example_product Analytics

Analytics resources for the example_product AI-powered document automation platform.

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
| `metric-watch.yaml` | Metrics the sweep watches: id, unit, cadence, target source, snapshot file and rules |
| `snapshots/` | One CSV of measured values per watched metric (`<metric_id>.csv`) |

---

## Analytics → signals

Analytics feeds the product loop the way customer calls do: a watched metric that misses its target or moves sharply, a completed A/B experiment and a completed investigation each become a row in `product-development/signals/signals.csv`. This repo holds no warehouse credentials, so there are two halves.

| Half | What it does | How it runs |
|------|--------------|-------------|
| **Capture** | Appends measured values to `snapshots/<metric_id>.csv` (`period,segment,value,captured_at,captured_by`). A correction is a new row with a later `captured_at`; the latest per `(period, segment)` wins. | `/analytics-snapshot`: an analyst types the value from the dashboard, or a warehouse adapter named in [`docs/agents/capabilities.md`](../../docs/agents/capabilities.md) runs the metric's query. |
| **Sweep** | Reads `metric-watch.yaml`, the snapshots and every `Status: Complete` report under `experiments/` and `investigations/`, and adds signals through `scripts/signals/signals.py`. Re-running on unchanged inputs adds nothing. | `/analytics-sweep` on demand; `.github/workflows/analytics-sweep.yml` every Monday 07:00 UTC. |

**Cadences.** `weekly` metrics use periods like `2026-W44`, `monthly` ones `2026-11`. Only the latest period per segment is evaluated.

**Rules** (in `metric-watch.yaml`): `below-target` compares the latest value with the target (from `reference/metrics.md`, or the `target` given for a metric defined under `metrics/`); `change` fires when the latest period moved by at least `threshold_pct` against the previous one, in the given `direction`.

**Signals written.** Metric hits and investigations: `source_type: analytics` (investigations also tagged `investigation`); experiments: `source_type: experiment`. `source_ref` is the snapshot or report path. Rows seeded with `captured_by: example-data` are sample data and their `detail` says so.

**Checks.** `analytics-watch-invalid` flags a malformed watch entry, a bad snapshot row or a missing snapshot file; `analytics-unswept-reports` flags a `Complete` report no signal cites. To watch a new metric, add it to `metric-watch.yaml` and create its snapshot file. Watched metrics also count as instrumented for the hypothesis A/B-test recommendation.

---

## Data Sources

| Source | Description | Access |
|--------|-------------|--------|
| Snowflake | Primary data warehouse - automation run logs, publish events, workflow metadata | SQL via Snowflake connector |
| Segment | Event tracking - user actions, automation run triggers, UI interactions | Segment workspace |
| Amplitude | Product analytics - funnels, retention, feature adoption | Amplitude dashboard |
| Stripe | Billing and subscription data - plan tiers, revenue, churn | Stripe dashboard + Snowflake sync |

---

## Core Metrics

Canonical metric definitions and targets live in [reference/metrics.md](../../reference/metrics.md), not here.

---

## Common Queries

Queries are stored in `queries/` and named by metric. Table names below match the schema doc filenames (see `schemas/` and `data-catalog.yaml` for the current-vs-legacy naming note, e.g. `project_generations` / `workflow_automation_runs`, `deploy_events` / `publish_events`).

| Query File | Description |
|------------|-------------|
| `queries/prototyping/generation-success-rate.sql` | Extraction success rate |
| `queries/billing/credit-burn-rate.sql` | Credit burn rate |
| `queries/deployment/domain-ssl-health.sql` | Custom portal domain SSL health |
| `queries/home-page/search-usage.sql` | Search usage |
| `queries/prototyping/version-restore-rate.sql` | Version restore rate |
| `queries/starter-templates/template-fork-rate.sql` | Template fork rate |
| `queries/deployment/one-click-deploy-success.sql` | One-click publish success rate and time-to-publish |
| `queries/deployment/domain-setup-completion.sql` | Custom portal domain setup funnel completion rates |

---

## Dashboards

| Dashboard | Tool | Description |
|-----------|------|-------------|
| example_product Health | Sigma | Real-time ESR, TTP, error rates, publish volume |
| Growth & Retention | Amplitude | Signup funnel, activation, D7/D30 retention |
| Revenue | Sigma | MRR, plan distribution, expansion, churn |
| Extraction Quality | Mode | Error taxonomy, document-type-level success rates, refinement patterns |
