# Version Snapshots Pipeline - Implementation Plan

**Related RFC:** [`data-engineering/rfcs/prototyping/version-snapshots-pipeline-rfc.md`](../../rfcs/prototyping/version-snapshots-pipeline-rfc.md)
**Related Feature RFC:** [`engineering/rfcs/prototyping/version-history-rfc.md`](../../../engineering/rfcs/prototyping/version-history-rfc.md)

---

## Overview

Build the data pipeline to ingest version history events from the example_product application database into Snowflake, producing `fact_version_events` and `dim_project_versions` tables for analytics queries, dashboards, and investigations.

## Steps

1. Configure Debezium CDC connector for `project_versions` table
   - Add connector configuration to the Kafka Connect cluster targeting `example_product.public.project_versions`
   - Configure to capture inserts only (versions are immutable, no updates or deletes)
   - Set `snapshot.mode=initial` to backfill existing versions from the dogfood and beta periods
   - Validate events are landing in Kafka topic `example_product.public.project_versions`

2. Create raw landing table in Snowflake
   - Create `raw.example_product.project_versions_raw` table matching the CDC event schema
   - Configure Snowpipe to auto-ingest from the Kafka topic via the S3 staging layer
   - Validate end-to-end latency: target < 5 minutes from PostgreSQL insert to raw table availability
   - Add monitoring alert if latency exceeds 15 minutes

3. Build dbt staging model
   - Create `stg_example_product__project_versions` model in `models/staging/example_product/`
   - Cast types, rename columns to analytics conventions, deduplicate on `version_id`
   - Add `dbt_valid_from` and `dbt_loaded_at` metadata columns
   - Add schema test: `version_id` is unique and not null
   - Add schema test: `action` is one of (`auto_snapshot`, `manual_save`, `restore`)

4. Build `fact_version_events` dbt model
   - Create `fact_version_events` model in `models/marts/example_product/`
   - Join staging model with `dim_users` to get `org_id` and `subscription_tier` at event time
   - Join with `fact_generation_events` on `project_id` and `created_at` proximity to resolve `generation_id`
   - Materialize as incremental model partitioned on `event_timestamp`
   - Add data quality test: for every `restore` action, `source_version_id` is not null
   - Add data quality test: `version_number` is monotonically increasing per `project_id`

5. Build `dim_project_versions` dbt model
   - Create `dim_project_versions` model in `models/marts/example_product/`
   - Join fact table with `dim_projects` (project name, framework, created_at) and `dim_users` (email) and `dim_orgs` (org name)
   - Compute `is_latest_version` using `ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY version_number DESC) = 1`
   - Compute `versions_in_project` using `COUNT(*) OVER (PARTITION BY project_id)`
   - For restores, resolve `source_version_number` by joining back on `source_version_id`
   - Materialize as table (full refresh daily, incremental is complex due to `is_latest_version` updates)

6. Add data quality checks and alerting
   - Add dbt source freshness check: `raw.example_product.project_versions_raw` loaded within last 30 minutes
   - Add row count comparison between raw and fact tables (alert on > 1% discrepancy)
   - Add Slack alert to #example_product-eng for any data quality test failures
   - Add Sigma alert on the Version History Health dashboard for restore success rate drops

7. Connect dashboards and enable self-service
   - Grant `SELECT` on `fact_version_events` and `dim_project_versions` to the `analytics_readonly` role
   - Update Mode connection to include the new tables
   - Verify Version History Feature Board queries run correctly against the new tables
   - Verify Version History Health dashboard in Sigma connects and refreshes
   - Document table schemas in `product/analytics/schemas/prototyping/project_versions.md` (already done)

8. Backfill validation
   - After initial CDC snapshot completes, compare row counts between PostgreSQL `project_versions` and `fact_version_events`
   - Spot-check 50 random versions: verify all columns match between source and destination
   - Validate that beta-period restore events have correct `source_version_id` linkage
   - Sign off with Casey Nguyen (analytics) that queries return expected results for the beta period
