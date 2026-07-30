# Search Events Data Pipeline

## Overview

Build the search events data pipeline to move Project Search (Cmd+K) interaction data from Segment to Snowflake. The pipeline supports the search usage rate, zero-results rate, and click-through rate metrics defined in the PRD. End state: `fact_search_events` and `dim_search_results` tables refreshed within 2 minutes of event emission, with dbt transformations running every 15 minutes.

**Related RFC:** `data-engineering/rfcs/home-page/search-events-pipeline-rfc.md`
**Related Product RFC:** `engineering/rfcs/home-page/project-search-rfc.md`
**Related PRD:** `product/PRDs/home-page/project-search-prd.md`

## Steps

1. Create Snowflake tables and staging infrastructure
   - Create `analytics.example_product.raw_search_events` staging table with VARIANT column for raw JSON
   - Create `analytics.example_product.fact_search_events` fact table per RFC schema
   - Create `analytics.example_product.dim_search_results` dimension table per RFC schema
   - Create the S3 external stage `analytics.example_product.segment_s3_stage` pointing to `s3://segment-example_product-events/search/`
   - Grant appropriate roles: `ANALYTICS_LOADER` for Snowpipe writes, `ANALYTICS_READER` for dbt and BI tools
   - Verify table creation with `DESCRIBE TABLE` and confirm clustering keys

2. Configure Segment tracking events
   - Add `Search Executed` track call in `src/components/search/SearchModal.tsx` with all required properties (event_id, query_text, query_length, result_count, result_count_projects, result_count_templates, result_count_actions, filters_applied, search_latency_ms, is_zero_results, search_results array)
   - Add `Search Result Clicked` track call with properties (event_id, clicked_result_id, clicked_result_type, clicked_position, time_to_click_ms)
   - Configure Segment S3 destination to route search events to `s3://segment-example_product-events/search/` prefix with date partitioning
   - Validate events are flowing to S3 using Segment debugger and S3 console
   - Confirm JSON structure matches expected schema

3. Set up Snowpipe auto-ingest
   - Create SQS queue for S3 event notifications on the `search/` prefix
   - Create Snowpipe `analytics.example_product.pipe_search_events` with AUTO_INGEST = TRUE
   - Configure the S3 bucket notification to send PUT events to the SQS queue
   - Test end-to-end: emit a test event from staging, verify it appears in `raw_search_events` within 2 minutes
   - Monitor Snowpipe status with `SELECT SYSTEM$PIPE_STATUS('analytics.example_product.pipe_search_events')`

4. Build dbt models
   - Create `models/staging/stg_search_events.sql`: parse raw JSON, deduplicate by event_id, join Search Executed with Search Result Clicked events, enrich with subscription_tier from users table
   - Create `models/marts/fact_search_events.sql`: incremental model with merge strategy on event_id, derive is_zero_results, cast and rename columns to match fact table schema
   - Create `models/marts/dim_search_results.sql`: flatten search_results array from raw events, one row per result per search, flag was_clicked based on click events
   - Add `schema.yml` with column descriptions and dbt tests: unique(event_id), not_null(user_id, event_id, created_at), accepted_values(subscription_tier, ['free', 'pro', 'teams', 'enterprise']), relationships(event_id references fact_search_events)
   - Add source freshness check: warn after 15 minutes, error after 30 minutes
   - Add the models to the existing 15-minute incremental dbt Cloud job selector

5. Add data quality tests and monitoring
   - Add row count anomaly detection: alert if daily row count drops > 50% day-over-day
   - Add freshness monitoring: alert if `raw_search_events` has no new rows for 30+ minutes
   - Add duplicate detection: daily check that event_id is unique in fact table
   - Add enum validation: subscription_tier and clicked_result_type match expected values
   - Configure Slack alerts to `#example_product-data-alerts` for pipeline failures and quality check violations
   - Run full pipeline in staging environment with synthetic data before enabling in production
   - Document runbook for common failure modes (Snowpipe lag, S3 delivery delay, dbt model failure)
