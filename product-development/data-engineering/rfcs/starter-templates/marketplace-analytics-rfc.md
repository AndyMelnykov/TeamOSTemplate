# RFC: Community Marketplace Analytics Data Models

**Author:** Casey Nguyen, Analytics Engineer
**Status:** Draft
**Last Updated:** 2026-03-22
**Related Feature RFC:** [`engineering/rfcs/starter-templates/community-marketplace-rfc.md`](../../../engineering/rfcs/starter-templates/community-marketplace-rfc.md)
**Related Plan:** [`data-engineering/plans/starter-templates/marketplace-analytics.md`](../../plans/starter-templates/marketplace-analytics.md)

---

## Summary

This RFC defines the analytics data models for the Community Marketplace feature. We need two new tables in the Snowflake analytics warehouse: `fact_template_forks` for tracking fork events and `dim_published_templates` for template metadata. These models support the marketplace metrics defined in the product analytics spec and power the Community Marketplace Dashboard in Sigma.

## Motivation

The Community Marketplace introduces two new entity types (published templates and template forks) that do not exist in our current analytics schema. The product team needs to measure template publish rate, fork rate, fork-to-deploy conversion, and average rating. The existing `project_generations` and `deploy_events` tables do not capture the template-to-project relationship, so new models are required.

## Data Flow

```
Application DB (Postgres)
    ├── published_templates  ──→  Snowpipe  ──→  raw.example_product.published_templates
    └── template_forks       ──→  Snowpipe  ──→  raw.example_product.template_forks
                                                        │
                                                   dbt transforms
                                                        │
                                               ┌────────┴────────┐
                                               │                 │
                                   dim_published_templates   fact_template_forks
                                   (analytics.example_product.dim_     (analytics.example_product.fact_
                                    published_templates)       template_forks)
```

Raw data lands in the `raw.example_product` schema via Snowpipe (near real-time). dbt models transform and enrich the data into the `analytics.example_product` schema on an hourly schedule.

## Schema Design

### `fact_template_forks`

Fact table capturing every template fork event. Grain: one row per fork.

```sql
CREATE TABLE analytics.example_product.fact_template_forks (
    fork_id                 VARCHAR(36)     NOT NULL PRIMARY KEY,
    template_id             VARCHAR(36)     NOT NULL,
    user_id                 VARCHAR(36)     NOT NULL,
    project_id              VARCHAR(36)     NOT NULL,
    author_id               VARCHAR(36)     NOT NULL,
    template_category       VARCHAR(50)     NOT NULL,
    user_subscription_tier  VARCHAR(20)     NOT NULL,
    customizations_applied  BOOLEAN         NOT NULL DEFAULT FALSE,
    was_deployed            BOOLEAN         NOT NULL DEFAULT FALSE,
    minutes_to_first_deploy INTEGER         NULL,
    fork_created_at         TIMESTAMP_NTZ   NOT NULL,
    first_deploy_at         TIMESTAMP_NTZ   NULL,
    _loaded_at              TIMESTAMP_NTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
```

**Column Notes:**

| Column | Description |
|--------|-------------|
| `fork_id` | Primary key, UUID from the application database |
| `template_id` | Foreign key to `dim_published_templates` |
| `user_id` | User who performed the fork |
| `project_id` | New project created by the fork; joins to `project_generations` and `deploy_events` |
| `author_id` | Author of the template (denormalized from `dim_published_templates` for query convenience) |
| `template_category` | Category of the template at fork time (denormalized) |
| `user_subscription_tier` | User's subscription tier at fork time: `free`, `pro`, `teams`, `enterprise` |
| `customizations_applied` | Whether the user edited the forked project within 30 minutes |
| `was_deployed` | Whether the forked project has been deployed (updated by downstream dbt model) |
| `minutes_to_first_deploy` | Time from fork to first successful deploy, null if not deployed |
| `fork_created_at` | Timestamp of the fork event |
| `first_deploy_at` | Timestamp of the first successful deploy, null if not deployed |
| `_loaded_at` | dbt model load timestamp |

**Clustering:** `(fork_created_at, template_category)`

**dbt model:** `models/marts/example_product/fact_template_forks.sql`

**Refresh:** Hourly via dbt Cloud job `example_product_marketplace_models`

**Upstream dependencies:**
- `raw.example_product.template_forks` (Snowpipe)
- `raw.example_product.published_templates` (Snowpipe, for denormalized fields)
- `analytics.example_product.deploy_events` (for `was_deployed` and `first_deploy_at`)
- `analytics.example_product.users` (for `user_subscription_tier`)

### `dim_published_templates`

Dimension table for published template metadata. Grain: one row per published template. Slowly changing dimension (Type 1 -- overwrites on update).

```sql
CREATE TABLE analytics.example_product.dim_published_templates (
    template_id             VARCHAR(36)     NOT NULL PRIMARY KEY,
    source_project_id       VARCHAR(36)     NOT NULL,
    author_id               VARCHAR(36)     NOT NULL,
    author_username         VARCHAR(100)    NOT NULL,
    title                   VARCHAR(200)    NOT NULL,
    description             TEXT            NOT NULL,
    category                VARCHAR(50)     NOT NULL,
    status                  VARCHAR(20)     NOT NULL,
    fork_count              INTEGER         NOT NULL DEFAULT 0,
    avg_rating              FLOAT           NULL,
    rating_count            INTEGER         NOT NULL DEFAULT 0,
    author_subscription_tier VARCHAR(20)    NOT NULL,
    is_approved             BOOLEAN         NOT NULL DEFAULT FALSE,
    review_hours            FLOAT           NULL,
    published_at            TIMESTAMP_NTZ   NOT NULL,
    approved_at             TIMESTAMP_NTZ   NULL,
    updated_at              TIMESTAMP_NTZ   NOT NULL,
    _loaded_at              TIMESTAMP_NTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
```

**Column Notes:**

| Column | Description |
|--------|-------------|
| `template_id` | Primary key, UUID from the application database |
| `source_project_id` | Original project that was published as a template |
| `author_id` | User who published the template |
| `author_username` | Denormalized username for dashboard display |
| `title` | Template display title |
| `description` | Template description text |
| `category` | Template category: `saas`, `portfolio`, `e-commerce`, `landing-page`, `internal-tool` |
| `status` | Review status: `pending`, `approved`, `rejected` |
| `fork_count` | Total fork count (denormalized counter) |
| `avg_rating` | Average rating, null if no ratings yet |
| `rating_count` | Number of ratings received |
| `author_subscription_tier` | Author's subscription tier at time of publish |
| `is_approved` | Boolean convenience column: `status = 'approved'` |
| `review_hours` | Hours between submission and approval/rejection, null if still pending |
| `published_at` | When the template was submitted |
| `approved_at` | When the template was approved, null if pending or rejected |
| `updated_at` | Last update from the application database |
| `_loaded_at` | dbt model load timestamp |

**Clustering:** `(published_at, category)`

**dbt model:** `models/marts/example_product/dim_published_templates.sql`

**Refresh:** Hourly via dbt Cloud job `example_product_marketplace_models`

**Upstream dependencies:**
- `raw.example_product.published_templates` (Snowpipe)
- `analytics.example_product.users` (for `author_username` and `author_subscription_tier`)

## Testing

### dbt Tests

```yaml
# models/marts/example_product/schema.yml
models:
  - name: fact_template_forks
    columns:
      - name: fork_id
        tests:
          - unique
          - not_null
      - name: template_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_published_templates')
              field: template_id
      - name: user_id
        tests:
          - not_null
      - name: project_id
        tests:
          - not_null
          - unique
      - name: template_category
        tests:
          - accepted_values:
              values: ['saas', 'portfolio', 'e-commerce', 'landing-page', 'internal-tool']

  - name: dim_published_templates
    columns:
      - name: template_id
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'approved', 'rejected']
      - name: category
        tests:
          - accepted_values:
              values: ['saas', 'portfolio', 'e-commerce', 'landing-page', 'internal-tool']
      - name: avg_rating
        tests:
          - dbt_utils.accepted_range:
              min_value: 1.0
              max_value: 5.0
              where: "avg_rating IS NOT NULL"
```

### Data Quality Checks

- `fork_count` on `dim_published_templates` should equal `COUNT(*)` from `fact_template_forks` for each template (reconciliation query run daily)
- `was_deployed` on `fact_template_forks` should be consistent with `deploy_events` (reconciliation query run daily)
- No orphan forks: every `template_id` in `fact_template_forks` must exist in `dim_published_templates`

## Rollout

1. **Week 1:** Create raw tables and Snowpipe ingestion for `published_templates` and `template_forks`
2. **Week 1:** Write and test dbt models for `dim_published_templates` and `fact_template_forks`
3. **Week 2:** Deploy dbt models to production, add to `example_product_marketplace_models` dbt Cloud job (hourly)
4. **Week 2:** Build Sigma dashboard views on top of the new models
5. **Week 3:** Add data quality alerts (Snowflake alerts for row count anomalies, freshness checks)
6. **Ongoing:** Monitor and tune clustering keys based on actual query patterns
