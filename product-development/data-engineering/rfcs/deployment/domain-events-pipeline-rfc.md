# RFC: Domain Events Pipeline

**Author:** Casey Nguyen, Analytics Engineer
**Status:** Draft
**Last Updated:** 2026-03-22
**Related RFC:** [`engineering/rfcs/deployment/custom-domains-rfc.md`](../../../engineering/rfcs/deployment/custom-domains-rfc.md)
**Related Plan:** [`data-engineering/plans/deployment/domain-events-pipeline.md`](../../plans/deployment/domain-events-pipeline.md)

---

# Summary

Build a data pipeline to capture custom domain lifecycle events (add, verify, provision, remove) into a `fact_domain_events` table in Snowflake. Maintain a `dim_custom_domains` slowly changing dimension for current domain state. These tables power the Custom Domains Health Dashboard, adoption funnel analysis, and SSL operations monitoring.

# Motivation

The custom domains feature generates events across multiple backend services: the domain management API, the DNS verification worker, the SSL provisioning service, and the edge proxy. Today these events are scattered across application logs and Segment tracks with no unified analytical model. Without a structured pipeline:

- Funnel analysis requires ad hoc joins across 4+ raw tables.
- SSL health monitoring relies on querying the production database directly.
- There is no historical record of domain state transitions (only current state in the application DB).
- The analytics team cannot self-serve domain metrics without engineering support.

# Proposed Design

## Source Systems

| Source | Events | Transport |
|--------|--------|-----------|
| Domain Management API | `domain.added`, `domain.removed` | Segment track calls |
| DNS Verification Worker | `domain.dns_check`, `domain.dns_verified`, `domain.dns_failed` | Segment track calls |
| SSL Provisioning Service | `domain.ssl_requested`, `domain.ssl_provisioned`, `domain.ssl_failed`, `domain.ssl_renewed`, `domain.ssl_expired` | Segment track calls |
| Edge Proxy | `domain.first_request` | Snowpipe from access logs |
| Application DB | `custom_domains`, `domain_certificates` tables | Fivetran incremental sync (every 15 min) |

## Pipeline Architecture

1. **Segment -> Snowflake:** All domain events land in `raw.segment.tracks` via the existing Segment-Snowflake connector. No new connector needed.
2. **Staging:** A dbt staging model (`stg_domain_events`) filters, deduplicates, and normalizes domain events from `raw.segment.tracks`.
3. **Fact table:** `fact_domain_events` is built from `stg_domain_events` with enrichment from the application DB sync (user tier, project metadata).
4. **Dimension table:** `dim_custom_domains` is a Type 2 SCD built from the Fivetran sync of `custom_domains` and `domain_certificates`, capturing every state change with `valid_from` / `valid_to` timestamps.
5. **dbt runs:** Hourly via the existing dbt Cloud scheduler.

# Database Schema

## `fact_domain_events`

```sql
CREATE TABLE analytics.example_product.fact_domain_events (
    event_id            VARCHAR(36)     NOT NULL,
    event_type          VARCHAR(50)     NOT NULL,
    domain_id           VARCHAR(36)     NOT NULL,
    project_id          VARCHAR(36)     NOT NULL,
    user_id             VARCHAR(36)     NOT NULL,
    org_id              VARCHAR(36),
    domain              VARCHAR(253)    NOT NULL,
    subscription_tier   VARCHAR(20)     NOT NULL,
    dns_status_before   VARCHAR(20),
    dns_status_after    VARCHAR(20),
    ssl_status_before   VARCHAR(20),
    ssl_status_after    VARCHAR(20),
    error_code          VARCHAR(100),
    error_message       TEXT,
    duration_ms         INTEGER,
    metadata            VARIANT,
    event_timestamp     TIMESTAMP_NTZ   NOT NULL,
    loaded_at           TIMESTAMP_NTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
```

**Event types:**

| `event_type` | Description | Key `metadata` fields |
|--------------|-------------|----------------------|
| `domain.added` | User added a custom domain | `registrar_hint` (if detectable) |
| `domain.removed` | User removed a custom domain | `reason` (user_initiated, admin, health_check) |
| `domain.dns_check` | Periodic DNS verification poll | `attempt_number`, `cname_resolved` |
| `domain.dns_verified` | DNS CNAME record verified successfully | `propagation_time_ms` |
| `domain.dns_failed` | DNS verification timed out after 48 hours | `total_attempts` |
| `domain.ssl_requested` | ACME certificate request initiated | `provider` |
| `domain.ssl_provisioned` | Certificate issued successfully | `provider`, `expires_at`, `provision_time_ms` |
| `domain.ssl_failed` | ACME challenge failed | `error_code`, `attempt_number` |
| `domain.ssl_renewed` | Certificate renewed successfully | `old_expires_at`, `new_expires_at` |
| `domain.ssl_expired` | Certificate expired without renewal | `last_renewal_attempt` |
| `domain.first_request` | First HTTP request served on custom domain | `user_agent`, `country` |

## `dim_custom_domains`

```sql
CREATE TABLE analytics.example_product.dim_custom_domains (
    domain_key          INTEGER         NOT NULL AUTOINCREMENT,
    domain_id           VARCHAR(36)     NOT NULL,
    project_id          VARCHAR(36)     NOT NULL,
    user_id             VARCHAR(36)     NOT NULL,
    org_id              VARCHAR(36),
    domain              VARCHAR(253)    NOT NULL,
    dns_status          VARCHAR(20)     NOT NULL,
    ssl_status          VARCHAR(20)     NOT NULL,
    cname_target        VARCHAR(253)    NOT NULL,
    certificate_id      VARCHAR(36),
    certificate_status  VARCHAR(20),
    certificate_provider VARCHAR(50),
    certificate_expires_at TIMESTAMP_NTZ,
    auto_renew          BOOLEAN,
    subscription_tier   VARCHAR(20)     NOT NULL,
    is_active           BOOLEAN         NOT NULL,
    valid_from          TIMESTAMP_NTZ   NOT NULL,
    valid_to            TIMESTAMP_NTZ,
    is_current          BOOLEAN         NOT NULL DEFAULT TRUE,
    loaded_at           TIMESTAMP_NTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
```

**SCD Type 2 behavior:**
- When any tracked column changes (dns_status, ssl_status, certificate_status, subscription_tier, is_active), the current row is closed (`valid_to` = change timestamp, `is_current` = FALSE) and a new row is opened.
- `is_active` is set to FALSE when a domain is removed, preserving the full history.
- `domain_key` is a surrogate key for joining with `fact_domain_events` in dimensional queries.

# Data Quality

- **Deduplication:** Events are deduplicated on `event_id` (Segment `messageId`). The staging model uses `QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY loaded_at) = 1`.
- **Late-arriving events:** The pipeline uses a 2-hour lookback window on each run to catch late Segment events.
- **Schema tests:** dbt tests enforce `not_null` on `event_id`, `domain_id`, `event_timestamp`; `accepted_values` on `event_type` and status fields; `relationships` between `domain_id` and `dim_custom_domains`.
- **Freshness:** dbt source freshness check alerts if `fact_domain_events` is more than 2 hours stale.

# Rollout

1. **Week 1:** Ship Segment tracking calls in the domain management API, DNS worker, and SSL service. Validate events land in `raw.segment.tracks`.
2. **Week 2:** Deploy dbt staging model and `fact_domain_events`. Backfill from raw events. Run data quality tests.
3. **Week 3:** Deploy `dim_custom_domains` SCD. Connect to Sigma dashboards. Validate against production database state.
4. **Week 4:** Hand off to analytics team. Document in schema registry. Remove direct production DB queries.
