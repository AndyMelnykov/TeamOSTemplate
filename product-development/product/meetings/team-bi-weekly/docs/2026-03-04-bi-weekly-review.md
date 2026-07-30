# Bi-Weekly Product Review — March 4, 2026

**Date:** Tuesday, March 4, 2026
**Time:** 2:00 - 3:00 PM PT
**Attendees:** Alex Chen, Jordan Reeves, Sam Torres, Priya Patel, Marcus Webb, Grace Lin, Emily Zhao

## Agenda

| Time | Topic | Lead | Goal |
|------|-------|------|------|
| 2:00 - 2:15 | Workstream updates | All | Status check |
| 2:15 - 2:30 | One-Click Deploy beta readiness | Jordan | Go/no-go decision on March 24 target |
| 2:30 - 2:40 | Generation latency regression | Priya | Decide on mitigation approach |
| 2:40 - 2:50 | Enterprise pipeline review | Alex | Align on next steps for active prospects |
| 2:50 - 3:00 | Open discussion | All | — |

## Pre-reads

- [One-Click Deploy plan](../../../engineering/plans/deployment/custom-domains.md)
- [Generation latency Datadog dashboard](https://app.datadoghq.com/example_product-labs/dashboard/gen-latency)
- [Meridian Health account context](../../customers/accounts/meridian-health/account-context.md)

## Discussion: One-Click Deploy Beta Readiness

**Context:** Beta target is March 24. Deploy infrastructure is live on staging with Vercel and Netlify. Preview UI is functional and the internal team has been testing.

**Open items to resolve:**
- [ ] Error handling for failed deploys — how much edge case coverage do we need for beta vs GA?
- [ ] Help article and in-app tooltip copy — who owns, and can we hit March 24 without it?
- [ ] Monitoring dashboards — Grace, are deploy success rate dashboards ready?

**Proposed decision:** Proceed with March 24 if error handling and copy can be done by then. Otherwise push one week.

## Discussion: Generation Latency Regression

**Context:** example_product-gen-3.2 is at 50% rollout. Quality scores up 12% on eval suite, but P95 latency regressed from 7.5s to 11s. Streaming helps perceived performance but raw numbers need to come down.

**Options to discuss:**
1. Roll back to example_product-gen-3.1 for latency-sensitive users
2. Optimize inference pipeline (Priya estimates 2-3 weeks)
3. Accept higher latency, rely on streaming to mask it

**Question for the group:** What's our P95 latency ceiling? Is 8s acceptable for beta?

## Discussion: Enterprise Pipeline

**Context:** Meridian Health pilot agreement expected. NovaTech in legal review. Potential third prospect in financial services.

**Questions:**
- SOC 2 audit timeline — still on track for April?
- Any blockers from the product side for either prospect?

## Notes

_To be filled during the meeting._
