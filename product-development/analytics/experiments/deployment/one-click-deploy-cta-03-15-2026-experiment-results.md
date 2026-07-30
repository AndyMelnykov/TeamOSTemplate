# Experiment: "Deploy to your domain" CTA vs. Generic "Deploy" Button

**Author:** Casey Nguyen, Analytics
**Date:** 2026-03-15
**Linear / Jira / Asana:** EXAMPLE_PRODUCT-1058
**Status:** Complete

---

# TL;DR

Replacing the generic "Deploy" button with a domain-specific "Deploy to your domain" CTA increased custom domain setup initiation by **41%** among Pro and Teams users. The variant also lifted overall deploy clicks by 12%. Decision: **Ship the variant to all eligible users.**

# Hypothesis

Users who see a CTA that explicitly mentions deploying to their own domain will be more likely to (a) click the deploy button and (b) proceed through the custom domain setup flow. The generic "Deploy" button does not communicate that custom domains are available, so users may not discover the feature until they dig into deployment settings.

# Setup

| Parameter | Value |
|-----------|-------|
| Experiment type | A/B test |
| Audience | Pro and Teams users with at least one deployed project, no custom domain configured |
| Sample size | 1,200 users (600 control, 600 variant) |
| Duration | 2026-03-01 to 2026-03-14 (14 days) |
| Allocation | 50/50 random split, stratified by tier (Pro/Teams) |
| Primary metric | Custom domain setup initiation rate (% of users who add at least one custom domain) |
| Secondary metrics | Deploy button click rate, domain setup completion rate, Free-to-Pro upgrade rate (spillover) |
| Powered to detect | 10% relative lift at 80% power, alpha = 0.05 |

# Variants

| Variant | Description |
|---------|-------------|
| **Control** | Standard "Deploy" button in the project header. Deployment settings page shows custom domains section below the fold. |
| **Treatment** | "Deploy to your domain" button in the project header with a small globe icon. On click, opens deployment settings page scrolled to the custom domains section with a highlighted callout: "Connect your own domain for a professional URL." |

# Results

| Metric | Control | Treatment | Lift | p-value | Significant? |
|--------|---------|-----------|------|---------|--------------|
| Custom domain setup initiation rate | 8.2% | 11.5% | **+41%** | 0.003 | Yes |
| Deploy button click rate | 34.1% | 38.2% | +12% | 0.02 | Yes |
| Domain setup completion rate (of those who started) | 64% | 67% | +5% | 0.31 | No |
| Time-to-first-domain-add (median, among initiators) | 4.2 days after deploy | 1.1 days after deploy | -74% | 0.001 | Yes |

# Segmentation

| Segment | Control initiation rate | Treatment initiation rate | Lift |
|---------|------------------------|--------------------------|------|
| Pro users | 6.8% | 10.1% | +49% |
| Teams users | 11.3% | 14.2% | +26% |
| Users with 1 deploy | 5.1% | 8.9% | +75% |
| Users with 3+ deploys | 12.4% | 14.8% | +19% |

The largest lift was among Pro users and users with only one prior deploy -- exactly the segment most likely to be unaware of the custom domain feature.

# Analysis

- The treatment CTA made custom domains discoverable at the moment of highest intent (deploying a project). This explains the 41% lift in domain setup initiation.
- The 12% lift in overall deploy clicks suggests the domain-specific CTA also increases deployment motivation, even for users who do not go on to add a custom domain.
- Domain setup completion rate was not significantly different between groups, indicating the CTA affects discovery and initiation but not the DNS configuration flow itself (which is addressed separately in EXAMPLE_PRODUCT-1070).
- Time-to-first-domain-add dropped from 4.2 days to 1.1 days, meaning users in the treatment group discovered custom domains almost immediately rather than stumbling on it later.

# Decision

**Ship the treatment variant ("Deploy to your domain" CTA) to all Pro and Teams users.**

Rationale:
- Statistically significant 41% lift in the primary metric with a p-value of 0.003.
- No negative impact on any secondary metric.
- Positive spillover on overall deploy click rate.
- Implementation cost is minimal (copy change + scroll anchor + callout component).

# Follow-up

- Monitor domain setup initiation rate for 30 days post-rollout to confirm the lift holds at scale.
- Evaluate whether the CTA should also be shown to Free-tier users as an upgrade prompt (separate experiment, EXAMPLE_PRODUCT-1082).
- Combine with the DNS instruction improvements (EXAMPLE_PRODUCT-1075, EXAMPLE_PRODUCT-1076) to improve end-to-end completion.
