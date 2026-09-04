# Domain Events Pipeline - Implementation Plan

**Author:** Casey Nguyen, Analytics Engineer
**Last Updated:** 2026-03-22
**Related RFC:** [`data-engineering/rfcs/deployment/domain-events-pipeline-rfc.md`](../../rfcs/deployment/domain-events-pipeline-rfc.md)
**Related Engineering RFC:** [`engineering/rfcs/deployment/custom-domains-rfc.md`](../../../engineering/rfcs/deployment/custom-domains-rfc.md)

---

## Overview

Build the analytics data pipeline for the custom domains feature: ingest domain lifecycle events from Segment, model them in dbt, and serve them via `fact_domain_events` and `dim_custom_domains` tables in Snowflake.

## Steps

### 1. Instrument Segment tracking calls in backend services

**Owner:** Morgan Wu (Engineering), with Casey Nguyen reviewing event schema

- Add `analytics.track()` calls for all domain lifecycle events in:
  - `src/routes/domains.ts` -- `domain.added`, `domain.removed`
  - `src/workers/dnsVerification.ts` -- `domain.dns_check`, `domain.dns_verified`, `domain.dns_failed`
  - `src/services/sslProvisioning.ts` -- `domain.ssl_requested`, `domain.ssl_provisioned`, `domain.ssl_failed`, `domain.ssl_renewed`, `domain.ssl_expired`
- Each event must include: `domain_id`, `workflow_id`, `user_id`, `domain`, `event_type`, and event-specific metadata per the RFC schema.
- Add the `domain.first_request` event via edge proxy access log -> Snowpipe (already configured for publish events; extend the existing pipe).
- **Validation:** Confirm events appear in `raw.segment.tracks` in Snowflake within 5 minutes of triggering. Check field names, types, and nullability.

### 2. Add Fivetran incremental sync for `custom_domains` and `domain_certificates`

**Owner:** Casey Nguyen

- Add `custom_domains` and `domain_certificates` tables to the existing Fivetran Postgres connector.
- Configure 15-minute sync interval (matching other application tables).
- Verify row counts match production after initial sync.
- Confirm `updated_at` column is used as the replication key for incremental syncs.

### 3. Build dbt staging model

**Owner:** Casey Nguyen

- Create `models/staging/segment/stg_domain_events.sql`:
  - Filter `raw.segment.tracks` for `event` LIKE `'domain.%'`.
  - Deduplicate on `message_id` using `QUALIFY ROW_NUMBER()`.
  - Parse `properties` VARIANT column into typed columns matching `fact_domain_events` schema.
  - Apply 2-hour lookback window for late-arriving events.
- Create `models/staging/application/stg_custom_domains.sql` and `stg_domain_certificates.sql` from Fivetran synced tables.
- Add `schema.yml` with column descriptions, `not_null` and `accepted_values` tests.

### 4. Build `fact_domain_events` model

**Owner:** Casey Nguyen

- Create `models/marts/deployment/fact_domain_events.sql`:
  - Join `stg_domain_events` with `stg_custom_domains` to enrich with `subscription_tier` and `org_id`.
  - Compute `dns_status_before` / `dns_status_after` and `ssl_status_before` / `ssl_status_after` using `LAG()` window functions partitioned by `domain_id`.
  - Materialize as incremental table with `event_timestamp` as the unique key.
- Add dbt tests: `unique` on `event_id`, `relationships` to `dim_custom_domains`, `not_null` on required fields.
- Add source freshness test: warn after 1 hour, error after 2 hours.

### 5. Build `dim_custom_domains` SCD Type 2 model

**Owner:** Casey Nguyen

- Create `models/marts/deployment/dim_custom_domains.sql`:
  - Use dbt `snapshot` (or custom SCD2 logic) on `stg_custom_domains` joined with `stg_domain_certificates`.
  - Track changes on: `dns_status`, `ssl_status`, `certificate_status`, `subscription_tier`, `is_active`.
  - Generate surrogate `domain_key` via `AUTOINCREMENT`.
  - Set `is_current = TRUE` for the latest version of each domain.
- Add dbt tests: `unique` on `domain_key`, at most one `is_current = TRUE` per `domain_id`.

### 6. Backfill historical events

**Owner:** Casey Nguyen

- After initial dbt models are deployed, run a one-time backfill:
  - Replay domain events from `raw.segment.tracks` going back to the beta launch date (2026-03-04).
  - For domains that existed before event tracking was instrumented, seed initial state from the Fivetran sync.
- Validate backfilled data against known beta metrics (73 domain setup attempts, 45 reaching live status).

### 7. Connect dashboards

**Owner:** Casey Nguyen

- Update the Custom Domains Health Dashboard (Sigma) to query `fact_domain_events` and `dim_custom_domains` instead of production DB.
- Update the SSL Certificate Ops dashboard (Datadog) with Snowflake data source for historical trending.
- Verify all dashboard metrics match production database spot checks.

### 8. Documentation and handoff

**Owner:** Casey Nguyen

- Add `fact_domain_events` and `dim_custom_domains` to the schema registry (`product/analytics/schemas/deployment/`).
- Update `product/analytics/CLAUDE.md` data sources table with new tables.
- Document common query patterns in `product/analytics/queries/deployment/`.
- Remove direct production DB query access for domain analytics.
- Hand off to analytics team with a walkthrough session.

## Timeline

| Week | Milestone |
|------|-----------|
| Week 1 | Steps 1-2: Instrument events, configure Fivetran sync |
| Week 2 | Steps 3-4: Staging models and fact table |
| Week 3 | Steps 5-6: Dimension table and backfill |
| Week 4 | Steps 7-8: Dashboards, documentation, handoff |

## Dependencies

- Custom domains feature must be deployed (at least to beta) for events to flow.
- Engineering team (Morgan Wu) must ship Segment tracking calls before the pipeline can ingest data.
- Existing Fivetran Postgres connector must have capacity for two additional tables.
- dbt Cloud scheduler must have an available slot for the hourly run.

## Risks

| Risk | Mitigation |
|------|------------|
| Late or missing Segment events | 2-hour lookback window; source freshness alerts |
| Fivetran sync lag during high-volume periods | Monitor sync duration; alert if > 30 minutes |
| SCD2 dimension grows large over time | Partition by `valid_from`; archive rows older than 1 year |
| Event schema changes without pipeline update | dbt schema tests will fail loudly; add to PR review checklist |
