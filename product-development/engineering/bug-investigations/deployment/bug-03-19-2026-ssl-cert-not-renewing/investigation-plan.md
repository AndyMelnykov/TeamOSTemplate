# Auto-renew failing silently for custom domain certs

| Field | Value |
|-------|-------|
| Run Date | 2026-03-19 |
| Author | Morgan Wu, Engineer |
| Status | In Progress |
| Playbook | [SSL/TLS Incident Response](https://playbooks.internal/ssl-incidents) |
| Google Doc | [Investigation: SSL Renewal Failures](https://docs.google.com/document/d/1yza-ssl-renewal) |
| Related Tickets | EXAMPLE_PRODUCT-1065, EXAMPLE_PRODUCT-1068, EXAMPLE_PRODUCT-1078 |

## Objective
Investigate why Let's Encrypt SSL certificates for custom domains are not auto-renewing, causing deployed sites to show browser security warnings when certs expire.

## Background
Custom domains launched in v2.5.0 with automatic SSL provisioning via Let's Encrypt. The first batch of certificates (provisioned 2026-02-17) are approaching their 90-day expiry. The auto-renew cron job runs daily but is not renewing expiring certificates. Two users have already reported browser security warnings.

## Impact Scope
- **Affected users:** 31 users with custom domains provisioned before 2026-03-01 (certs expiring in next 2 weeks)
- **Immediately impacted:** 2 users whose certs already expired (sites showing security warnings)
- **Severity:** P1 — deployed production sites inaccessible or showing security warnings
- **Duration:** Discovered 2026-03-19, certificates started failing to renew ~30 days ago

## Infrastructure
- **Service:** `cert-manager` cron job (Vercel Cron, runs daily at 2am UTC)
- **Certificate authority:** Let's Encrypt (via `acme-client` npm package)
- **DNS verification:** Cloudflare API for DNS-01 challenge
- **Database:** Supabase PostgreSQL — `domain_certificates` table
- **Secrets:** Let's Encrypt account key stored in Vercel environment variables

## Results
- The `cert-manager` cron job runs daily but completes in <1s (should take 30-60s per renewal)
- Cron job logs show "No certificates due for renewal" even though 31 certs expire within 30 days
- The renewal query filters on `expires_at < NOW() + INTERVAL '30 days'` but the `expires_at` column stores a Unix timestamp (integer) not a PostgreSQL timestamp
- The comparison always evaluates to false because it's comparing an integer to a timestamp

## Analysis
1. Checked Vercel Cron logs — job runs on schedule, exits in <1s with "0 certificates renewed"
2. Queried `domain_certificates` directly — found 31 rows with `expires_at` values like `1747526400` (Unix epoch)
3. The renewal query uses `WHERE expires_at < NOW() + INTERVAL '30 days'` — this compares integer to timestamp
4. PostgreSQL doesn't error on this comparison but it evaluates incorrectly, always returning 0 rows
5. The initial provisioning code stores `expires_at` as Unix timestamp from the ACME response, but the renewal query assumes it's a PostgreSQL `timestamptz`

## Root Cause
Type mismatch between stored data and query. The certificate provisioning code stores `expires_at` as a Unix epoch integer (from the Let's Encrypt ACME response), but the renewal cron job's query compares it against `NOW() + INTERVAL '30 days'` which is a PostgreSQL timestamp. The comparison silently returns no results instead of erroring, so the cron job thinks no certificates need renewal.

## Recommended Fix
1. **Immediate:** Manually renew the 2 expired certificates via CLI
2. **Fix the query:** Convert the comparison: `WHERE to_timestamp(expires_at) < NOW() + INTERVAL '30 days'`
3. **Migration:** Alter `expires_at` column from `bigint` to `timestamptz` and convert existing values
4. **Add monitoring:** Alert if the cron job completes in <5s (indicates it's not doing any work)
5. **Add cert expiry dashboard:** surface certs expiring in <14 days in admin view

## Cross-Validation
- Ran the corrected query in staging — correctly identifies 31 certificates due for renewal
- Manually triggered renewal for a test domain in staging — certificate renewed successfully
- Verified Let's Encrypt account key is valid and rate limits are not exceeded

## Data Examples

| Domain | Provisioned | Expires (Unix) | Expires (Human) | Days Until Expiry |
|--------|------------|----------------|-----------------|-------------------|
| app.customerdomain.com | 2026-02-17 | 1747526400 | 2026-05-18 | 60 |
| dashboard.startup.io | 2026-02-20 | 1747785600 | 2026-05-21 | 63 |
| www.mybrand.com | 2026-02-15 | 1747353600 | 2026-05-16 | 58 |
| portal.agency.co | 2026-02-10 | 1746921600 | 2026-05-11 | 53 |

## Executive Summary
SSL auto-renewal is silently broken because certificate expiry dates are stored as Unix timestamps (integers) but the renewal query compares them against PostgreSQL timestamps. The comparison never matches, so no certs get renewed. Two user sites are already showing security warnings. Immediately renew expired certs manually, fix the query's type comparison, and migrate the column to `timestamptz`. Add monitoring to catch silent cron job failures.

## Appendix

### Query 1: Certificates due for renewal (broken version)
```sql
-- This returns 0 rows due to type mismatch
SELECT domain, expires_at
FROM domain_certificates
WHERE expires_at < NOW() + INTERVAL '30 days'
  AND status = 'active';
```

### Query 2: Certificates due for renewal (fixed version)
```sql
-- Correct comparison using to_timestamp()
SELECT domain, to_timestamp(expires_at) as expires_at_ts,
       EXTRACT(DAY FROM to_timestamp(expires_at) - NOW()) as days_remaining
FROM domain_certificates
WHERE to_timestamp(expires_at) < NOW() + INTERVAL '30 days'
  AND status = 'active'
ORDER BY expires_at ASC;
```

### Query 3: Cron job execution history
```sql
SELECT run_id, started_at, completed_at,
       EXTRACT(EPOCH FROM completed_at - started_at) as duration_seconds,
       certificates_renewed
FROM cron_job_runs
WHERE job_name = 'cert-manager'
ORDER BY started_at DESC
LIMIT 30;
```
