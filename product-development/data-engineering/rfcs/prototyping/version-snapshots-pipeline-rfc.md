# RFC: Version Snapshots Data Pipeline

**Author:** Casey Nguyen, Analytics & Morgan Wu, Engineering
**Status:** Draft
**Last Updated:** 2026-03-22
**Related RFC:** [`engineering/rfcs/prototyping/version-history-rfc.md`](../../../engineering/rfcs/prototyping/version-history-rfc.md)
**Related Plan:** [`data-engineering/plans/prototyping/version-snapshots-pipeline.md`](../../plans/prototyping/version-snapshots-pipeline.md)

---

## Summary

Build the data pipeline to ingest version history events from the example_product application database into Snowflake, producing a fact table (`fact_version_events`) for analytics queries and a dimension table (`dim_project_versions`) for enriched reporting. This pipeline supports the metrics, dashboards, and investigations defined in the version history analytics docs.

## Motivation

The version history feature generates two categories of data that the analytics team needs:

1. **Event-level data:** Every version creation (auto-snapshot, manual save, restore) needs to be queryable in Snowflake for metrics like restore rate, versions per project, and restore-to-continue rate.
2. **Enriched dimension data:** For dashboards and investigations, we need version data joined with project metadata, user attributes, and subscription tier at the time of the event.

Without a dedicated pipeline, the analytics team would need to query the production database directly or build ad-hoc ETL, both of which are unsustainable and error-prone.

## Proposed Design

### Source

Version events originate from the `project_versions` table in the example_product application PostgreSQL database. Each insert to this table triggers a Debezium CDC event that lands in Kafka topic `example_product.public.project_versions`.

### Pipeline Architecture

```
PostgreSQL (project_versions)
  --> Debezium CDC
    --> Kafka (example_product.public.project_versions)
      --> Snowpipe (near real-time)
        --> raw.example_product.project_versions_raw
          --> dbt transform
            --> analytics.example_product.fact_version_events
            --> analytics.example_product.dim_project_versions
```

### Fact Table: `fact_version_events`

Grain: one row per version event. This is the primary table for metrics queries.

```sql
CREATE TABLE analytics.example_product.fact_version_events (
    event_id            VARCHAR(36)     NOT NULL,
    version_id          VARCHAR(36)     NOT NULL,
    project_id          VARCHAR(36)     NOT NULL,
    user_id             VARCHAR(36)     NOT NULL,
    org_id              VARCHAR(36),
    version_number      INTEGER         NOT NULL,
    action              VARCHAR(20)     NOT NULL,
    source_version_id   VARCHAR(36),
    prompt_trigger      TEXT,
    file_count          INTEGER         NOT NULL,
    total_size_bytes    BIGINT          NOT NULL,
    generation_id       VARCHAR(36),
    subscription_tier   VARCHAR(20)     NOT NULL,
    event_timestamp     TIMESTAMP_NTZ   NOT NULL,
    loaded_at           TIMESTAMP_NTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_fact_version_events PRIMARY KEY (event_id)
);
```

**Column details:**

| Column | Description |
|--------|-------------|
| `event_id` | Unique identifier for this pipeline event (UUID, generated at ingestion) |
| `version_id` | Maps to `project_versions.version_id` in the source system |
| `project_id` | Project this version belongs to |
| `user_id` | User who triggered the version creation |
| `org_id` | Organization ID (null for free-tier users) |
| `version_number` | Sequential version number within the project |
| `action` | Event type: `auto_snapshot`, `manual_save`, `restore` |
| `source_version_id` | For restores, the version that was restored from |
| `prompt_trigger` | The prompt text that triggered the generation (null for manual saves and restores) |
| `file_count` | Number of files in the project at this version |
| `total_size_bytes` | Total size of the snapshot in bytes |
| `generation_id` | The generation that triggered this version (null for manual saves) |
| `subscription_tier` | User's subscription tier at time of event: `free`, `pro`, `teams`, `enterprise` |
| `event_timestamp` | When the version was created in the source system (UTC) |
| `loaded_at` | When this row was loaded into Snowflake |

**Clustering:** `(event_timestamp, project_id)`

### Dimension Table: `dim_project_versions`

Grain: one row per project-version combination. Enriched with project and user attributes for dashboard joins.

```sql
CREATE TABLE analytics.example_product.dim_project_versions (
    version_id              VARCHAR(36)     NOT NULL,
    project_id              VARCHAR(36)     NOT NULL,
    project_name            VARCHAR(255),
    project_framework       VARCHAR(50),
    project_created_at      TIMESTAMP_NTZ,
    user_id                 VARCHAR(36)     NOT NULL,
    user_email              VARCHAR(255),
    org_id                  VARCHAR(36),
    org_name                VARCHAR(255),
    subscription_tier       VARCHAR(20)     NOT NULL,
    version_number          INTEGER         NOT NULL,
    action                  VARCHAR(20)     NOT NULL,
    source_version_id       VARCHAR(36),
    source_version_number   INTEGER,
    prompt_trigger          TEXT,
    file_count              INTEGER         NOT NULL,
    total_size_bytes        BIGINT          NOT NULL,
    is_latest_version       BOOLEAN         NOT NULL,
    versions_in_project     INTEGER         NOT NULL,
    created_at              TIMESTAMP_NTZ   NOT NULL,
    updated_at              TIMESTAMP_NTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_dim_project_versions PRIMARY KEY (version_id)
);
```

**Column details:**

| Column | Description |
|--------|-------------|
| `version_id` | Unique identifier for this version |
| `project_id` | Project this version belongs to |
| `project_name` | Name of the project (from `dim_projects`) |
| `project_framework` | Framework detected for the project (react, nextjs, vue, etc.) |
| `project_created_at` | When the project was first created |
| `user_id` | User who created this version |
| `user_email` | User's email address (from `dim_users`) |
| `org_id` | Organization ID (null for individual users) |
| `org_name` | Organization name (from `dim_orgs`) |
| `subscription_tier` | User's tier at time of version creation |
| `version_number` | Sequential version number within the project |
| `action` | Event type: `auto_snapshot`, `manual_save`, `restore` |
| `source_version_id` | For restores, the version restored from |
| `source_version_number` | For restores, the version number restored from (denormalized for readability) |
| `prompt_trigger` | The prompt that triggered the generation |
| `file_count` | Number of files at this version |
| `total_size_bytes` | Snapshot size in bytes |
| `is_latest_version` | Whether this is the most recent version for the project |
| `versions_in_project` | Total number of versions in the project at the time of this snapshot |
| `created_at` | When this version was created in the source system |
| `updated_at` | When this dimension row was last refreshed |

**Clustering:** `(created_at, project_id)`

## Data Quality Checks

| Check | Query Logic | Alert Threshold |
|-------|-------------|-----------------|
| No missing version events | Compare count of `project_versions` in PostgreSQL vs `fact_version_events` in Snowflake for the last hour | Difference > 0 for more than 15 minutes |
| Version number monotonicity | For each project, verify `version_number` is strictly increasing by `created_at` | Any violation triggers alert |
| Action value validation | All `action` values are in (`auto_snapshot`, `manual_save`, `restore`) | Any unexpected value triggers alert |
| Restore source integrity | Every `restore` event has a non-null `source_version_id` that exists in the table | Any violation triggers alert |
| Latency SLA | Time from PostgreSQL insert to Snowflake availability | > 5 minutes triggers warning, > 15 minutes triggers alert |

## Security Considerations

- `prompt_trigger` may contain sensitive user input. The pipeline does not filter or redact prompt content. Access to the analytics tables is controlled by Snowflake RBAC (analytics team and authorized dashboards only).
- `user_email` in the dimension table is PII. The `dim_project_versions` table inherits the same access controls as `dim_users`.
- CDC events in Kafka are encrypted in transit (TLS) and at rest (broker-level encryption).

## Rollout Plan

| Phase | Scope | Timeline |
|-------|-------|----------|
| 1 | Deploy raw table and Snowpipe ingestion, validate data completeness | Week 1 |
| 2 | Deploy dbt models for `fact_version_events` and `dim_project_versions`, run data quality checks | Week 2 |
| 3 | Connect dashboards and enable analytics team self-service queries | Week 3 |
