# RFC: Version Snapshots Data Pipeline

**Author:** Casey Nguyen, Analytics & Morgan Wu, Engineering
**Status:** Draft
**Last Updated:** 2026-03-22
**Related RFC:** [`engineering/rfcs/prototyping/version-history-rfc.md`](../../../engineering/rfcs/prototyping/version-history-rfc.md)
**Related Plan:** [`data-engineering/plans/prototyping/version-snapshots-pipeline.md`](../../plans/prototyping/version-snapshots-pipeline.md)

---

## Summary

Build the data pipeline to ingest version history events from the example_product application database into Snowflake, producing a fact table (`fact_version_events`) for analytics queries and a dimension table (`dim_workflow_versions`) for enriched reporting. This pipeline supports the metrics, dashboards, and investigations defined in the version history analytics docs.

## Motivation

The version history feature generates two categories of data that the analytics team needs:

1. **Event-level data:** Every version creation (auto-snapshot, manual save, restore) needs to be queryable in Snowflake for metrics like restore rate, versions per workflow, and restore-to-continue rate.
2. **Enriched dimension data:** For dashboards and investigations, we need version data joined with workflow metadata, user attributes, and subscription tier at the time of the event.

Without a dedicated pipeline, the analytics team would need to query the production database directly or build ad-hoc ETL, both of which are unsustainable and error-prone.

## Proposed Design

### Source

Version events originate from the `workflow_versions` table in the example_product application PostgreSQL database. Each insert to this table triggers a Debezium CDC event that lands in Kafka topic `example_product.public.workflow_versions`.

### Pipeline Architecture

```
PostgreSQL (workflow_versions)
  --> Debezium CDC
    --> Kafka (example_product.public.workflow_versions)
      --> Snowpipe (near real-time)
        --> raw.example_product.workflow_versions_raw
          --> dbt transform
            --> analytics.example_product.fact_version_events
            --> analytics.example_product.dim_workflow_versions
```

### Fact Table: `fact_version_events`

Grain: one row per version event. This is the primary table for metrics queries.

```sql
CREATE TABLE analytics.example_product.fact_version_events (
    event_id            VARCHAR(36)     NOT NULL,
    version_id          VARCHAR(36)     NOT NULL,
    workflow_id         VARCHAR(36)     NOT NULL,
    user_id             VARCHAR(36)     NOT NULL,
    org_id              VARCHAR(36),
    version_number      INTEGER         NOT NULL,
    action              VARCHAR(20)     NOT NULL,
    source_version_id   VARCHAR(36),
    instruction_trigger TEXT,
    file_count          INTEGER         NOT NULL,
    total_size_bytes    BIGINT          NOT NULL,
    automation_run_id   VARCHAR(36),
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
| `version_id` | Maps to `workflow_versions.version_id` in the source system |
| `workflow_id` | Workflow this version belongs to |
| `user_id` | User who triggered the version creation |
| `org_id` | Organization ID (null for free-tier users) |
| `version_number` | Sequential version number within the workflow |
| `action` | Event type: `auto_snapshot`, `manual_save`, `restore` |
| `source_version_id` | For restores, the version that was restored from |
| `instruction_trigger` | The natural-language instruction that triggered the automation run (null for manual saves and restores) |
| `file_count` | Number of files in the workflow at this version |
| `total_size_bytes` | Total size of the snapshot in bytes |
| `automation_run_id` | The automation run that triggered this version (null for manual saves) |
| `subscription_tier` | User's subscription tier at time of event: `free`, `pro`, `teams`, `enterprise` |
| `event_timestamp` | When the version was created in the source system (UTC) |
| `loaded_at` | When this row was loaded into Snowflake |

**Clustering:** `(event_timestamp, workflow_id)`

### Dimension Table: `dim_workflow_versions`

Grain: one row per workflow-version combination. Enriched with workflow and user attributes for dashboard joins.

```sql
CREATE TABLE analytics.example_product.dim_workflow_versions (
    version_id              VARCHAR(36)     NOT NULL,
    workflow_id             VARCHAR(36)     NOT NULL,
    workflow_name            VARCHAR(255),
    workflow_category        VARCHAR(50),
    workflow_created_at      TIMESTAMP_NTZ,
    user_id                 VARCHAR(36)     NOT NULL,
    user_email               VARCHAR(255),
    org_id                  VARCHAR(36),
    org_name                VARCHAR(255),
    subscription_tier       VARCHAR(20)     NOT NULL,
    version_number          INTEGER         NOT NULL,
    action                  VARCHAR(20)     NOT NULL,
    source_version_id       VARCHAR(36),
    source_version_number   INTEGER,
    instruction_trigger      TEXT,
    file_count              INTEGER         NOT NULL,
    total_size_bytes        BIGINT          NOT NULL,
    is_latest_version       BOOLEAN         NOT NULL,
    versions_in_workflow     INTEGER         NOT NULL,
    created_at              TIMESTAMP_NTZ   NOT NULL,
    updated_at              TIMESTAMP_NTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_dim_workflow_versions PRIMARY KEY (version_id)
);
```

**Column details:**

| Column | Description |
|--------|-------------|
| `version_id` | Unique identifier for this version |
| `workflow_id` | Workflow this version belongs to |
| `workflow_name` | Name of the workflow (from `dim_workflows`) |
| `workflow_category` | Document type the workflow automates (contract, invoice, intake-form, purchase-order, nda, etc.) |
| `workflow_created_at` | When the workflow was first created |
| `user_id` | User who created this version |
| `user_email` | User's email address (from `dim_users`) |
| `org_id` | Organization ID (null for individual users) |
| `org_name` | Organization name (from `dim_orgs`) |
| `subscription_tier` | User's tier at time of version creation |
| `version_number` | Sequential version number within the workflow |
| `action` | Event type: `auto_snapshot`, `manual_save`, `restore` |
| `source_version_id` | For restores, the version restored from |
| `source_version_number` | For restores, the version number restored from (denormalized for readability) |
| `instruction_trigger` | The natural-language instruction that triggered the automation run |
| `file_count` | Number of files at this version |
| `total_size_bytes` | Snapshot size in bytes |
| `is_latest_version` | Whether this is the most recent version for the workflow |
| `versions_in_workflow` | Total number of versions in the workflow at the time of this snapshot |
| `created_at` | When this version was created in the source system |
| `updated_at` | When this dimension row was last refreshed |

**Clustering:** `(created_at, workflow_id)`

## Data Quality Checks

| Check | Query Logic | Alert Threshold |
|-------|-------------|-----------------|
| No missing version events | Compare count of `workflow_versions` in PostgreSQL vs `fact_version_events` in Snowflake for the last hour | Difference > 0 for more than 15 minutes |
| Version number monotonicity | For each workflow, verify `version_number` is strictly increasing by `created_at` | Any violation triggers alert |
| Action value validation | All `action` values are in (`auto_snapshot`, `manual_save`, `restore`) | Any unexpected value triggers alert |
| Restore source integrity | Every `restore` event has a non-null `source_version_id` that exists in the table | Any violation triggers alert |
| Latency SLA | Time from PostgreSQL insert to Snowflake availability | > 5 minutes triggers warning, > 15 minutes triggers alert |

## Security Considerations

- `instruction_trigger` may contain sensitive user input, including excerpts of the extraction or routing instructions a customer wrote for a workflow. The pipeline does not filter or redact instruction content. Access to the analytics tables is controlled by Snowflake RBAC (analytics team and authorized dashboards only).
- `user_email` in the dimension table is PII. The `dim_workflow_versions` table inherits the same access controls as `dim_users`.
- CDC events in Kafka are encrypted in transit (TLS) and at rest (broker-level encryption).

## Rollout Plan

| Phase | Scope | Timeline |
|-------|-------|----------|
| 1 | Deploy raw table and Snowpipe ingestion, validate data completeness | Week 1 |
| 2 | Deploy dbt models for `fact_version_events` and `dim_workflow_versions`, run data quality checks | Week 2 |
| 3 | Connect dashboards and enable analytics team self-service queries | Week 3 |
