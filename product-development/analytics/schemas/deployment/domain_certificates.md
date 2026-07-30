# Schema: `analytics.example_product.domain_certificates`

Certificate lifecycle tracking for custom domains connected to example_product projects. One row per certificate issued.

**Database:** `ANALYTICS`
**Schema:** `EXAMPLE_PRODUCT`
**Table:** `DOMAIN_CERTIFICATES`
**Refresh:** Streaming (near real-time via Snowpipe)
**Retention:** 2 years

# Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | VARCHAR(36) | No | Unique identifier for the certificate record (UUID) |
| `domain_id` | VARCHAR(36) | No | Foreign key to `custom_domains.id` |
| `provider` | VARCHAR(50) | No | Certificate authority provider (e.g., `letsencrypt`) |
| `issued_at` | TIMESTAMP_NTZ | Yes | When the certificate was issued (null if pending or failed) |
| `expires_at` | TIMESTAMP_NTZ | Yes | When the certificate expires (null if not yet issued) |
| `auto_renew` | BOOLEAN | No | Whether automatic renewal is enabled (default `true`) |
| `last_renewal_attempt` | TIMESTAMP_NTZ | Yes | Timestamp of the most recent renewal attempt (null if never attempted) |
| `status` | VARCHAR(20) | No | Certificate status: `pending`, `active`, `expired`, `revoked`, `failed` |
| `created_at` | TIMESTAMP_NTZ | No | When the certificate record was created (UTC) |
| `updated_at` | TIMESTAMP_NTZ | No | Last status update timestamp (UTC) |

# Indexes & Clustering

- Clustered on `(created_at, domain_id)`
- Commonly filtered on `status`, `expires_at`, `auto_renew`

# Common Joins

- `custom_domains` on `domain_id` -- Domain metadata, DNS status, project association
- `projects` on `custom_domains.project_id` -- Project metadata
- `users` on `custom_domains.user_id` -- User profile and account details

# Notes

- `issued_at` and `expires_at` are null for certificates in `pending` or `failed` status.
- `last_renewal_attempt` is null until the first renewal is attempted; it updates on every renewal attempt regardless of outcome.
- Let's Encrypt certificates have a 90-day validity period. The renewal cron targets certificates expiring within 30 days.
- When a domain is removed, the certificate `status` is set to `revoked` rather than deleting the row, preserving audit history.
