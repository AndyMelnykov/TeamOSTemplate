# Community Marketplace Analytics - Implementation Plan

**Feature:** Community Marketplace Analytics Pipeline
**Owner:** Casey Nguyen, Analytics
**Related RFC:** [`data-engineering/rfcs/starter-templates/marketplace-analytics-rfc.md`](../../rfcs/starter-templates/marketplace-analytics-rfc.md)
**Related Feature RFC:** [`engineering/rfcs/starter-templates/community-marketplace-rfc.md`](../../../engineering/rfcs/starter-templates/community-marketplace-rfc.md)
**Last Updated:** 2026-03-22

---

## Overview

Build the analytics data pipeline for the Community Marketplace feature. This includes raw data ingestion via Snowpipe, dbt transformation models, Sigma dashboards, and data quality monitoring. The pipeline must be ready before the marketplace internal beta launch.

## Steps

### 1. Set up Snowpipe ingestion for raw tables

- Create `raw.example_product.published_templates` table in Snowflake matching the application DB schema
- Create `raw.example_product.template_forks` table in Snowflake matching the application DB schema
- Configure Snowpipe to stream CDC events from the application database into both raw tables
- Validate data lands within 60 seconds of application writes
- Add Snowpipe error alerting to the `#example_product-eng` Slack channel

### 2. Write dbt staging models

- Create `models/staging/example_product/stg_example_product__published_templates.sql` to clean and type-cast raw published templates
- Create `models/staging/example_product/stg_example_product__template_forks.sql` to clean and type-cast raw fork events
- Add `schema.yml` with column-level tests (not_null, unique, accepted_values)
- Run `dbt test` locally and verify all tests pass

### 3. Write dbt mart models

- Create `models/marts/example_product/dim_published_templates.sql` with the following enrichments:
  - Join `users` for `author_username` and `author_subscription_tier`
  - Compute `is_approved` boolean from status
  - Compute `review_hours` as `DATEDIFF('hour', published_at, approved_at)`
- Create `models/marts/example_product/fact_template_forks.sql` with the following enrichments:
  - Denormalize `author_id` and `template_category` from `dim_published_templates`
  - Join `users` for `user_subscription_tier`
  - Join `deploy_events` to compute `was_deployed`, `first_deploy_at`, and `minutes_to_first_deploy`
- Add `schema.yml` with relationship tests, range tests, and reconciliation tests

### 4. Deploy dbt models to production

- Add both models to the `example_product_marketplace_models` dbt Cloud job
- Set schedule to hourly
- Run initial full refresh and validate row counts against raw tables
- Verify clustering keys are applied: `(fork_created_at, template_category)` for fact, `(published_at, category)` for dim

### 5. Build Sigma dashboards

- Create "Community Marketplace Overview" dashboard with the following views:
  - Weekly publish rate (line chart)
  - Weekly fork rate (line chart)
  - Fork-to-deploy conversion (line chart with 40% target line)
  - Average template rating (line chart with 4.0 target line)
  - Review queue turnaround (bar chart, median hours)
- Create "Top Templates Leaderboard" dashboard:
  - Ranked table: template title, category, author, fork count, avg rating, deploy conversion
  - Filterable by category and date range
- Create "Publisher Analytics" dashboard:
  - Submissions per week, approval rate, top contributors
- Create "Review Queue Operations" dashboard:
  - Pending count, median review time, approval/rejection breakdown
- Share all dashboards with the `example_product-product` and `example_product-eng` Sigma teams

### 6. Set up data quality monitoring

- Add Snowflake alert: `fact_template_forks` row count drops to 0 for 2+ hours during business hours
- Add Snowflake alert: `dim_published_templates` freshness exceeds 3 hours
- Add daily reconciliation query: `fork_count` on dim matches `COUNT(*)` from fact
- Add daily reconciliation query: `was_deployed` on fact matches `deploy_events` status
- Route all alerts to `#example_product-eng` Slack channel

### 7. Backfill historical data from internal template library

- Write a one-time backfill script to populate `dim_published_templates` with the 12 existing internal templates
- Backfill `fact_template_forks` with historical fork events from the internal template system (January 2026 onward)
- Validate backfilled data appears correctly in Sigma dashboards
- Document the backfill in the dbt project README

### 8. Add Segment event tracking

- Work with the frontend team to add Segment events for:
  - `marketplace.viewed` - user opens the marketplace page
  - `marketplace.template_clicked` - user clicks a template card
  - `marketplace.search` - user performs a search (include search query)
  - `marketplace.filter_applied` - user applies a category filter
  - `marketplace.sort_changed` - user changes sort order
- Verify events appear in Segment debugger and flow into Snowflake via the existing Segment-to-Snowflake pipeline

## Timeline

| Week | Milestone |
|------|-----------|
| Week 1 | Steps 1-2: Snowpipe ingestion and staging models |
| Week 2 | Steps 3-4: Mart models deployed to production |
| Week 3 | Steps 5-6: Sigma dashboards and data quality alerts |
| Week 4 | Steps 7-8: Backfill and Segment event tracking |

## Dependencies

- Engineering team must deploy the `published_templates` and `template_forks` application DB tables (from the feature RFC) before Snowpipe can be configured
- Frontend team must instrument Segment events (Step 8) after the marketplace UI is built
- Sigma team workspace access for dashboard creation (already provisioned)

## Risks

| Risk | Mitigation |
|------|------------|
| Snowpipe latency exceeds 60s during high-volume fork events | Pre-test with load simulation; scale Snowpipe warehouse if needed |
| `was_deployed` on fact table goes stale if deploy events arrive late | Set dbt incremental model to look back 7 days on each run |
| Backfill script introduces duplicates | Add `MERGE` logic with `fork_id` deduplication |
