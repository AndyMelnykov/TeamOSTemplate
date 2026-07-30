# Investigation: Custom Domain Adoption Funnel Drop-off

**Author:** Casey Nguyen, Analytics
**Date:** 2026-03-18
**Linear / Jira / Asana:** EXAMPLE_PRODUCT-1070
**Status:** Complete

---

# Question

Where do users drop off in the custom domain setup flow, and what can we do to improve completion rates?

# Background

Custom domains entered closed beta on 2026-03-04 with 50 Pro and Teams users. After two weeks, the domain setup completion rate (domain added to traffic serving) was 62%, below the 75% target. Product and engineering requested an investigation into where users are abandoning the flow and why.

# Methodology

- Pulled all `custom_domain_events` from Segment for the beta cohort (2026-03-04 to 2026-03-18, n=50 users, 73 domain setup attempts).
- Built a step-by-step funnel: Domain Added -> DNS Instructions Viewed -> DNS Record Configured -> DNS Verified -> SSL Provisioned -> Live.
- Joined with session recordings (Amplitude) to observe user behavior at each step.
- Segmented by registrar (where identifiable from DNS provider metadata) and subscription tier.

# Funnel Results

| Step | Users | Drop-off from previous step |
|------|-------|-----------------------------|
| 1. Domain Added | 73 (100%) | -- |
| 2. DNS Instructions Viewed | 70 (96%) | 4% |
| 3. DNS Record Configured (left example_product to registrar) | 58 (79%) | 17% |
| 4. DNS Verified | 47 (64%) | 19% |
| 5. SSL Provisioned | 46 (63%) | 2% |
| 6. Live (serving traffic) | 45 (62%) | 2% |

# Key Finding

**35% of users drop off at the DNS configuration step** (between viewing instructions and successfully verifying DNS). This is the single largest point of friction in the entire flow.

Breakdown of DNS configuration drop-off:

| Cause | Users affected | % of drop-offs |
|-------|---------------|----------------|
| User viewed instructions but never left example_product (abandoned) | 12 | 43% |
| User left example_product but DNS record was misconfigured (wrong value, wrong record type) | 9 | 32% |
| User configured DNS correctly but did not wait for propagation (assumed it failed) | 5 | 18% |
| User hit registrar-specific confusion (could not find DNS settings page) | 2 | 7% |

# Session Recording Observations

- **Copy-paste friction:** 8 of 12 users who abandoned were observed manually trying to type the CNAME target value (a 40+ character hash). Several made typos and did not realize it.
- **Registrar mismatch:** The beta DNS instructions were generic. Users on GoDaddy and Namecheap spent significant time trying to map generic instructions to their registrar's UI.
- **Propagation anxiety:** 5 users configured DNS correctly but returned to example_product within 2 minutes, saw "Pending DNS," and assumed it was broken. They did not notice the "DNS changes can take up to 48 hours" messaging.

# Segmentation

| Segment | Completion rate | Notes |
|---------|----------------|-------|
| Cloudflare users | 78% | Fastest propagation, most DNS-savvy users |
| GoDaddy users | 54% | Highest drop-off at instruction step |
| Namecheap users | 58% | Confusion around "Advanced DNS" navigation |
| Pro tier | 60% | More likely to be solo developers, less DNS experience |
| Teams tier | 68% | Often had a team member with DNS experience |

# Recommendations

1. **Add a copy-to-clipboard button for the CNAME target value.** This is the single highest-impact fix. Users should never need to manually type a hash string. Estimated impact: eliminates typo-related failures (32% of drop-offs).

2. **Add registrar-specific DNS instructions with tabs for GoDaddy, Namecheap, and Cloudflare.** Include step-by-step instructions with screenshots. Users on these three registrars account for 85% of our beta cohort. Estimated impact: reduces abandonment by ~40%.

3. **Add an inline propagation status indicator with estimated time.** Replace the static "up to 48 hours" text with a live "Checking DNS... last checked 10 seconds ago" message. This reassures users that the system is actively working. Estimated impact: reduces premature abandonment by ~18%.

4. **Send a push notification or email when DNS is verified.** Users who leave example_product to configure DNS may not return promptly. A notification closes the loop. Estimated impact: recovers ~10% of users who configured DNS correctly but did not return.

# Impact Estimate

If recommendations 1-3 are implemented, projected domain setup completion rate increases from 62% to approximately 80%, exceeding the 75% target.

# Next Steps

- Recommendations shared with Morgan Wu (engineering) and Taylor Brooks (design) on 2026-03-18.
- Copy-to-clipboard and registrar tabs are being added in the next sprint (EXAMPLE_PRODUCT-1075, EXAMPLE_PRODUCT-1076).
- Propagation indicator design review scheduled for 2026-03-20.
- Will re-run this funnel analysis two weeks after changes ship.

---

## Related Resources

| Resource | Path |
|----------|------|
| Metrics definition | [custom-domains-metrics.md](../../metrics/deployment/custom-domains-metrics.md) |
| SQL query | [domain-setup-completion.sql](../../queries/deployment/domain-setup-completion.sql) |
| Schema | [domain_certificates.md](../../schemas/deployment/domain_certificates.md) |
| Playbook | [funnel-analysis.md](../../playbooks/funnel-analysis.md) |
