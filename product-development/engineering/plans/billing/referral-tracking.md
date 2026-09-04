# Referral tracking

## Overview
Give users visibility into their referral status — who signed up, who converted to paid, and how many credits they've earned from the 100-credits-per-referral program.

## Steps
1. Add `GET /api/referrals` endpoint in `src/routes/referrals.ts`
   - Return list of referrals with status (signed up / active / paid)
   - Include total credits earned and pending credits
2. Create `ReferralDashboard` component in `src/components/billing/`
   - Summary: total referrals, converted, credits earned
   - Table: referred email (masked), signup date, status, credit amount
   - Shareable referral link with copy button
3. Add referral attribution tracking
   - Store referral_code in `referrals` table on signup
   - Listen for Stripe webhook on first paid subscription → credit referrer
   - Idempotent credit grant to prevent double-counting
4. Add share integrations
   - Generate OG-tagged referral URL for social sharing
   - "Share example_product" button in sidebar triggers share sheet (copy link, Twitter, email)
5. Add tests
   - Referral code correctly attributes signups
   - Credits granted once on paid conversion only
   - Dashboard totals match transaction history
