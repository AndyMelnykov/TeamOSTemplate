# Referral credits not granted after paid conversion

| Field | Value |
|-------|-------|
| Run Date | 2026-02-28 |
| Author | Casey Nguyen, Analytics |
| Status | Complete |
| Playbook | [Referral Program Debugging](https://playbooks.internal/referral-program) |
| Google Doc | [Investigation: Missing Referral Credits](https://docs.google.com/document/d/1jkl-referral-credits) |
| Related Tickets | EXAMPLE_PRODUCT-965, EXAMPLE_PRODUCT-971 |

## Objective
Investigate why referrers are not receiving their 100-credit bonus when referred users convert to paid plans, despite the referral being correctly attributed at signup.

## Background
The referral program ("Share Lovable — 100 credits per paid referral") launched in January 2026. Several users contacted support saying they referred friends who upgraded to paid but never received credits. The referral attribution (signup tracking) is working — the credit grant on conversion is not.

## Impact Scope
- **Affected referrers:** 89 users who should have received credits since 2026-02-01
- **Missing credits:** 8,900 credits (89 × 100) not granted
- **Severity:** P2 — feature broken but no financial loss to users (they just didn't get a bonus)
- **Duration:** Since 2026-02-01 (Stripe webhook endpoint migration)

## Infrastructure
- **Service:** `referral-service` (Supabase Edge Function)
- **Payment processor:** Stripe — webhook for `customer.subscription.created`
- **Database:** Supabase PostgreSQL — `referrals` and `credit_transactions` tables
- **Webhook handler:** `src/routes/webhooks/stripe.ts`

## Results
- Referral records in `referrals` table correctly link referrer to referred user
- Stripe webhooks for `customer.subscription.created` are being received
- The webhook handler calls `referralService.grantCredits()` but the function silently fails
- The Stripe webhook payload changed field names after the February Stripe API version upgrade

## Analysis
1. Checked `referrals` table — all 89 referrals have `status: 'signed_up'`, none updated to `'converted'`
2. Verified Stripe webhook delivery — all `customer.subscription.created` events show 200 response
3. Added logging to `grantCredits()` in staging — found it reads `event.data.object.customer` but the new Stripe API version nests it under `event.data.object.customer_id`
4. The field access returns `undefined`, the function does a no-op lookup and exits without error
5. No error is thrown because the code uses optional chaining (`customer?.id`) which silently returns undefined

## Root Cause
The Stripe API version was upgraded from `2024-12-18.acacia` to `2025-01-27.acacia` on 2026-02-01. The `customer.subscription.created` webhook payload changed `data.object.customer` (string) to `data.object.customer_id` (string). The webhook handler still reads the old field name, gets `undefined`, and silently skips the credit grant.

## Recommended Fix
1. Update `stripe.ts` webhook handler to read `customer_id` (new field) with fallback to `customer` (old field)
2. Pin Stripe API version in webhook endpoint configuration to prevent future silent breaks
3. Add error logging when referral lookup returns no match — this should never silently no-op
4. Run backfill script to grant credits to the 89 affected referrers
5. Add webhook payload validation with Zod schema to catch field changes at deploy time

## Cross-Validation
- Tested with Stripe CLI webhook replay in staging — credits now grant correctly
- Verified all 89 missing referrers have valid referral records that should have converted
- Cross-referenced Stripe dashboard subscription dates with `referrals.created_at` — all match

## Data Examples

| Referrer | Referred User | Signup Date | Paid Date | Credits Granted |
|----------|--------------|-------------|-----------|----------------|
| usr_a1b2 | usr_x9y8 | 2026-02-03 | 2026-02-10 | 0 (should be 100) |
| usr_c3d4 | usr_w7v6 | 2026-02-08 | 2026-02-15 | 0 (should be 100) |
| usr_e5f6 | usr_u5t4 | 2026-02-14 | 2026-02-22 | 0 (should be 100) |

## Executive Summary
Referral credits stopped being granted on 2026-02-01 when the Stripe API version was upgraded. The webhook handler reads a renamed field (`customer` → `customer_id`), gets undefined, and silently skips. Fix the field name, add payload validation, backfill 8,900 credits to 89 referrers, and pin the Stripe API version to prevent recurrence.

## Appendix

### Query 1: Referrals that should have converted but didn't
```sql
SELECT r.referrer_id, r.referred_user_id, r.created_at as signup_date,
       s.created as paid_date, r.status
FROM referrals r
JOIN stripe_subscriptions s ON s.user_id = r.referred_user_id
WHERE r.status = 'signed_up'
  AND s.status = 'active'
  AND s.created > r.created_at
ORDER BY s.created;
```

### Query 2: Verify no credits were granted
```sql
SELECT ct.user_id, ct.amount, ct.type, ct.reason, ct.created_at
FROM credit_transactions ct
WHERE ct.reason = 'referral_bonus'
  AND ct.created_at > '2026-02-01'
ORDER BY ct.created_at;
```

### Query 3: Backfill credits for affected referrers
```sql
INSERT INTO credit_transactions (user_id, amount, type, reason, reference_id, created_at)
SELECT r.referrer_id, 100, 'credit', 'referral_bonus_backfill', r.id, NOW()
FROM referrals r
JOIN stripe_subscriptions s ON s.user_id = r.referred_user_id
WHERE r.status = 'signed_up'
  AND s.status = 'active'
  AND s.created > r.created_at;
```
