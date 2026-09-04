# Credits deducted twice on automation run timeout/retry

| Field | Value |
|-------|-------|
| Run Date | 2026-03-12 |
| Author | Riley Patel, Engineer |
| Status | Complete |
| Playbook | [Billing Incident Response](https://playbooks.internal/billing-incidents) |
| Google Doc | [Investigation: Double Credit Charge](https://docs.google.com/document/d/1ghi-double-charge) |
| Related Tickets | EXAMPLE_PRODUCT-1025, EXAMPLE_PRODUCT-1031, EXAMPLE_PRODUCT-1033 |

## Objective
Investigate reports of users being charged credits twice for a single document automation run when the extraction request times out and the client retries automatically.

## Background
Support received 12 tickets in 3 days from users reporting unexpected credit depletion. Pattern analysis showed all affected users experienced at least one automation run timeout during the reporting period. The automation run retry logic was added in v2.4.0 to improve reliability when processing large or scanned uploads.

## Impact Scope
- **Affected users:** ~340 users who experienced automation run timeouts since v2.4.0 (2026-03-01)
- **Credits over-deducted:** ~4,800 credits total across affected users
- **Severity:** P1 — financial impact, users charged for work not delivered
- **Duration:** 2026-03-01 to 2026-03-12 (11 days)

## Infrastructure
- **Service:** `automation-run-service` (Node.js on Vercel serverless)
- **Billing service:** `credit-ledger` microservice (Supabase Edge Function)
- **Database:** Supabase PostgreSQL — `credit_transactions` and `automation_run_jobs` tables
- **Queue:** Inngest for async automation run job processing (upload → extract → route)
- **Client:** React frontend (workflow builder) with axios retry interceptor

## Results
- The axios retry interceptor on the client fires a new `POST /api/automation-runs` on timeout
- The original request is still processing server-side (Vercel hasn't killed it yet — large scanned PDFs can take a while to OCR)
- Both requests reach `credit-ledger` and deduct credits independently
- The automation run deduplication check uses `automation_run_id`, but retries generate a new ID on the client

## Analysis
1. Traced Datadog requests — found paired requests 30-60s apart with same user, same uploaded document, different `automation_run_id`
2. Checked `credit_transactions` — both requests created separate debit entries
3. Reviewed client retry logic (PR #501) — axios interceptor generates a fresh `automation_run_id` per attempt
4. Checked server-side — no idempotency key or dedup mechanism on the billing endpoint
5. Confirmed the original extraction run often completes successfully after the timeout, so the user gets billed twice but only sees one completed run

## Root Cause
The client-side retry interceptor generates a new `automation_run_id` for each attempt, bypassing the server's deduplication check which relies on `automation_run_id` uniqueness. When the original request completes after the timeout, both the original and retry are billed independently. There is no idempotency key tying retries to the original request.

## Recommended Fix
1. Generate a `request_idempotency_key` on the client before the first attempt, reuse across retries
2. Add idempotency check in `credit-ledger`: if a debit with the same key exists within 5 minutes, skip
3. Refund over-charged credits for the 340 affected users (automated script)
4. Add server-side abort: if an automation run is already in progress for the same document + user, return the existing job ID instead of starting a new one

## Cross-Validation
- Matched double-charge events in `credit_transactions` with timeout logs in Datadog (100% correlation)
- Verified fix in staging: retry with same idempotency key correctly deduplicates
- Confirmed refund calculation matches support ticket reports for 5 sampled users

## Data Examples

| User ID | Date | Credits Charged | Expected | Over-charge |
|---------|------|----------------|----------|-------------|
| usr_p4k2 | 2026-03-10 | 40 | 20 | 20 |
| usr_h7m1 | 2026-03-08 | 60 | 20 | 40 |
| usr_r2n8 | 2026-03-11 | 40 | 20 | 20 |
| usr_w5j3 | 2026-03-09 | 80 | 40 | 40 |

## Executive Summary
Users are double-charged when automation run requests time out and retry. The client retry logic creates a new automation run ID per attempt, so the server treats retries as separate billable requests. Fix by adding an idempotency key that persists across retries, and refund ~4,800 over-charged credits to 340 affected users. This is a P1 billing issue — ship the fix immediately and run the refund script.

## Appendix

### Query 1: Find double-charged users
```sql
SELECT ct.user_id, COUNT(*) as charge_count, SUM(ct.amount) as total_charged
FROM credit_transactions ct
JOIN automation_run_jobs arj ON arj.id = ct.reference_id
WHERE ct.type = 'debit'
  AND ct.created_at > '2026-03-01'
GROUP BY ct.user_id, arj.document_hash, DATE_TRUNC('minute', ct.created_at)
HAVING COUNT(*) > 1
ORDER BY total_charged DESC;
```

### Query 2: Calculate refund amounts per user
```sql
WITH duplicates AS (
  SELECT ct.user_id, ct.amount,
         ROW_NUMBER() OVER (PARTITION BY ct.user_id, arj.document_hash, DATE_TRUNC('minute', ct.created_at) ORDER BY ct.created_at) as rn
  FROM credit_transactions ct
  JOIN automation_run_jobs arj ON arj.id = ct.reference_id
  WHERE ct.type = 'debit' AND ct.created_at > '2026-03-01'
)
SELECT user_id, SUM(amount) as refund_amount
FROM duplicates
WHERE rn > 1
GROUP BY user_id
ORDER BY refund_amount DESC;
```

### Query 3: Verify retry pattern in automation run jobs
```sql
SELECT arj.user_id, arj.document_hash, arj.created_at, arj.status, arj.automation_run_id
FROM automation_run_jobs arj
WHERE arj.user_id = $1
  AND arj.created_at > '2026-03-01'
ORDER BY arj.created_at;
```
