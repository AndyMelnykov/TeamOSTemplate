# Custom Domains PRD

**Author:** Hannah Stulberg, PM
**Status:** Draft
**Last Updated:** 2026-03-22
**Related RFC:** [`engineering/rfcs/deployment/custom-domains-rfc.md`](../../../engineering/rfcs/deployment/custom-domains-rfc.md)
**Related Plan:** [`engineering/plans/deployment/custom-domains.md`](../../../engineering/plans/deployment/custom-domains.md)

---

# Business Opportunity

Custom domains transform example_product from a workflow-building tool into a production document platform. Today, every published workflow's portal lives on a `*.example_productapp.dev` subdomain, which signals "demo" to anyone who sees the URL. For users publishing client-facing contracts, vendor onboarding forms, or applicant intake portals, a branded domain is non-negotiable.

**Professional presentation drives paid conversion.** Users on the Free tier build and test workflows internally. The moment they want to send something externally -- to a client, a vendor, an applicant -- they need a real URL. Custom domains are a natural upgrade trigger to example_product Pro.

**Table stakes for business users.** In every Enterprise and Teams sales conversation, custom domains come up in the first call. Procurement and legal teams will not approve a platform where customer-facing contracts or intake forms are served from a third-party subdomain. Without custom domains, example_product is excluded from production use cases entirely.

| Conversion lever | Impact |
|-----------------|--------|
| Free-to-Pro upgrade trigger | Users who publish are 3.2x more likely to upgrade; custom domains add a second conversion moment |
| Teams/Enterprise deal velocity | Removes a top-3 procurement blocker, reducing average sales cycle by an estimated 2 weeks |
| Retention | Users with custom domains have a projected 25% lower churn rate (based on competitive benchmarking with DocuSign/PandaDoc data) |

# Why Now

Custom domains is the **number one requested publishing feature** across all feedback channels:

- **Feature request volume:** 47 unique requests in the last 90 days (EXAMPLE_PRODUCT-980, EXAMPLE_PRODUCT-1012, EXAMPLE_PRODUCT-1044 and related threads).
- **Customer calls:** Mentioned unprompted in 8 of the last 12 Enterprise prospect calls.
- **Competitive pressure:** DocuSign, PandaDoc, Dropbox Sign, and Conga all offer custom domains on their lowest paid tiers. PandaDoc launched custom-domain branded portals in February 2026. example_product is now the only major AI document automation platform without it.
- **Revenue at risk:** Three active pipeline deals totaling ~$180K ARR have flagged custom domains as a requirement for signing.

# Customer Requests

| Source | Customer/Segment | Verbatim |
|--------|-----------------|----------|
| Feature request (EXAMPLE_PRODUCT-980) | Pro user, freelance ops consultant | "I love building workflows in example_product but I can't send clients a example_productapp.dev link. They'd never take it seriously." |
| Sales call, 2026-03-05 | Enterprise prospect, fintech | "We need our compliance portal on our own domain. If example_product can't do that, we'll have to look at alternatives." |
| Support ticket | Teams user, agency | "We're building client onboarding workflows in example_product. Each one needs to live on the client's domain. This is a dealbreaker for us." |
| NPS comment | Pro user, startup founder | "example_product is amazing for building workflows. The second I want to go live with real vendors, I have to bolt on a real domain myself. Fix this and I'll never leave." |
| Customer call, 2026-02-28 | Enterprise pilot, healthcare | "Our legal team won't approve anything that doesn't run on our corporate domain. Period." |

# Goals

| Goal | Metric | Target |
|------|--------|--------|
| Enable professional publishing | Domain setup completion rate | > 75% of users who start the flow complete it |
| Fast time-to-live | Time from domain added to serving traffic | < 10 minutes (median) |
| Reliable SSL | SSL provision success rate | > 99% |
| Drive upgrades | Free-to-Pro conversion lift among publishers | +15% relative increase |
| Reduce churn | 90-day retention for users with custom domains vs. without | +10pp |

# User Stories

## Freelance Ops Consultant (Pro)

**As a** freelance ops consultant building client intake and approval workflows in example_product, **I want to** connect my client's domain to the published workflow portal **so that** the deliverable looks professional and the client sees their own brand in the URL.

**Acceptance criteria:**
- I can add a custom domain from the workflow's publishing settings.
- I see clear DNS configuration instructions for my registrar.
- The domain is live with HTTPS within minutes of DNS propagation.
- I can remove the domain when the engagement is complete.

## Startup Founder (Pro)

**As a** startup founder who built my vendor onboarding workflow in example_product, **I want to** launch it on my own domain **so that** vendors and partners see a legitimate portal, not a demo link.

**Acceptance criteria:**
- I can add my startup's domain (e.g., `portal.mystartup.com`) to my example_product workflow.
- SSL is provisioned automatically -- I don't need to manage certificates.
- The domain stays live and certificates auto-renew without my intervention.

## Agency Lead (Teams)

**As an** agency lead managing multiple client document workflows, **I want to** connect a different custom domain to each workflow **so that** each client gets a branded portal without leaving example_product.

**Acceptance criteria:**
- Each workflow in my Teams workspace can have its own custom domain.
- I can see the status of all domains across workflows in one place.
- My team members can manage domains for workflows they have access to.

## Enterprise Admin (Enterprise)

**As an** IT administrator at an enterprise customer, **I want to** publish example_product-built intake and approval portals on our corporate domain **so that** they comply with our security and branding policies.

**Acceptance criteria:**
- Domains are verified through DNS to prove ownership.
- SSL certificates are issued from a trusted CA (Let's Encrypt).
- I can remove a domain and its certificate is revoked immediately.
- Audit logs capture domain add/remove/verify events.

# Requirements

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Users can add a custom domain to a published workflow from the publishing settings page | P0 |
| FR-2 | System generates CNAME target and verification token upon domain registration | P0 |
| FR-3 | DNS verification runs automatically via polling (every 30s, up to 48 hours) | P0 |
| FR-4 | Users can manually trigger DNS verification check | P1 |
| FR-5 | SSL certificate is provisioned automatically via Let's Encrypt after DNS verification | P0 |
| FR-6 | Certificates auto-renew 30 days before expiry | P0 |
| FR-7 | Users see step-by-step DNS instructions for GoDaddy, Namecheap, and Cloudflare | P0 |
| FR-8 | Status indicators show DNS pending, DNS verified, SSL provisioning, and live states | P0 |
| FR-9 | Users can remove a custom domain with a confirmation dialog | P0 |
| FR-10 | Domain removal revokes the SSL certificate and clears routing | P0 |
| FR-11 | Free-tier users see an upgrade prompt when attempting to add a domain | P1 |
| FR-12 | Plan limits enforced: Pro (3 domains), Teams (10 domains), Enterprise (unlimited) | P0 |
| FR-13 | Domain add/remove/verify events are captured in audit logs | P1 |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | DNS verification polling does not exceed 1 query per domain per 30 seconds | P0 |
| NFR-2 | SSL provisioning completes within 60 seconds of DNS verification (p95) | P0 |
| NFR-3 | Edge routing adds < 5ms latency to requests on custom domains | P0 |
| NFR-4 | Certificate private keys are encrypted at rest (AES-256-GCM) | P0 |
| NFR-5 | Domain addition rate-limited to 10 per project per hour | P1 |
| NFR-6 | System supports 10,000+ concurrent custom domains | P1 |

# Launch Plan

## Phase 1: Internal Dogfood (Week 1-2)

- Deploy behind `custom-domains` feature flag.
- example_product team tests with internal workflows and personal domains.
- Validate end-to-end flow: add domain, configure DNS, verify, SSL provision, serve traffic, remove.
- Fix any issues found before external exposure.

## Phase 2: Closed Beta (Week 3-4)

- Invite 50 Pro and Teams users who submitted feature requests.
- Track domain setup completion rate, time-to-live, and SSL success rate against targets.
- Gather qualitative feedback on DNS instructions (are they clear? do users need more registrar guides?).
- Iterate on UX based on where users drop off.

## Phase 3: General Availability (Week 5-6)

- Enable for all Pro, Teams, and Enterprise tiers.
- Publish help center article with video walkthrough.
- Add "Custom Domains" to the publishing settings page for all eligible users.
- Display upgrade CTA for Free-tier users.
- Announce in product changelog, in-app notification, and email to Pro/Teams users.
- Run targeted email to Enterprise pipeline deals that flagged custom domains.

## Success Criteria for GA

- Domain setup completion rate > 75%.
- Median time-to-live < 10 minutes.
- SSL provision success rate > 99%.
- Zero P0/P1 bugs from beta.
- Help center article published with registrar guides for GoDaddy, Namecheap, and Cloudflare.
