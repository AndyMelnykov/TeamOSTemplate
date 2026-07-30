# Community Marketplace PRD

**Author:** Hannah Stulberg, PM
**Status:** Draft
**Last Updated:** 2026-03-22
**Related RFC:** [`engineering/rfcs/starter-templates/community-marketplace-rfc.md`](../../../engineering/rfcs/starter-templates/community-marketplace-rfc.md)
**Related Plan:** [`engineering/plans/starter-templates/community-marketplace.md`](../../../engineering/plans/starter-templates/community-marketplace.md)

---

## Business Opportunity

The Community Marketplace transforms the example_product template library from a static, internally managed asset into a user-generated content platform with compounding network effects.

**Network effects flywheel:**

1. Users publish high-quality templates from their successful projects.
2. New users discover and fork these templates, reducing time-to-value and increasing activation rates.
3. Forked projects get deployed, creating more successful projects that can be published as templates.
4. Each new template increases the value of the marketplace for all users, driving organic growth and retention.

**Revenue impact:**

- Templates published by Pro and Teams users showcase what is possible on example_product, serving as organic marketing for paid tiers.
- Users who fork templates and deploy them are prime upgrade candidates. Template forkers convert to paid at an estimated 2x the rate of users who start from blank projects.
- A thriving marketplace differentiates example_product from competitors (Lovable, v0, Replit) that lack community-driven template ecosystems.

## Why Now

1. **Template catalog is small.** example_product currently has 12 internally created templates. Competitors like Lovable offer 30+ and v0 is expanding rapidly. We cannot scale internal template creation fast enough to keep up.
2. **Users are asking for this.** 34% of feature requests in Q1 2026 referenced template sharing or discovery. In 6 of the last 10 customer calls, users asked some version of "Can I share my project as a template?"
3. **Deployment maturity.** With one-click deploy now stable, users are completing projects at a higher rate, creating a pool of deploy-worthy projects that would make excellent templates.
4. **Competitive moat.** A community marketplace is a defensible asset. Every published template increases switching costs. Moving first on this builds a content advantage that compounds over time.

## Customer Requests

| Source | Request | Date |
|--------|---------|------|
| Customer call - Acme Corp | "We built a great internal tool dashboard and our team wants to share it as a starting point for other departments." | 2026-02-28 |
| Customer call - DevStudio | "I'd love to browse what other people have built and start from their work instead of from scratch." | 2026-03-01 |
| Feature request (Canny) | "Marketplace for user templates with ratings - I want to find the best SaaS dashboard template without trying 5 different ones." | 2026-02-15 |
| Feature request (Canny) | "Let me publish my portfolio template. I've gotten compliments on it and want others to use it." | 2026-02-20 |
| Support ticket | "Is there a way to share my project setup with my team so they can clone it? I keep rebuilding the same base." | 2026-03-05 |
| NPS verbatim | "example_product would be 10x better if I could browse templates from other users, not just the default ones." | 2026-03-10 |

## Goals

### Primary Goals

1. **Grow the template catalog to 100+ community templates within 90 days of launch.** The marketplace must reach a critical mass of content to be useful. Internal seeding plus organic publishing should hit this target.
2. **Increase template fork-to-deploy conversion to 40%+.** Community templates should be high enough quality that users who fork them actually ship.
3. **Improve new user activation by 15%.** Users who start from a template should activate (reach first deploy) at a meaningfully higher rate than users who start from blank projects.

### Secondary Goals

4. Establish a content review process that approves templates within 24 hours without sacrificing quality.
5. Achieve an average template rating of 4.0+ across the marketplace, indicating genuine quality.
6. Drive 10% of monthly active users to publish at least one template within 6 months.

## User Stories

### Template Publisher

- As a example_product user who has built a successful project, I want to publish it as a template so that others can benefit from my work and I can build a reputation in the community.
- As a template publisher, I want to see how many people have forked and rated my template so that I understand its impact and can improve it.
- As a template publisher, I want to add a title, description, category, and preview screenshots so that potential users can evaluate my template before forking.

### Template Consumer

- As a new example_product user, I want to browse community templates by category so that I can find a relevant starting point instead of building from scratch.
- As a user looking for a template, I want to search by keyword and filter by category so that I can quickly find what I need.
- As a user evaluating templates, I want to see ratings, fork counts, and preview images so that I can choose the highest-quality option.
- As a user who forked a template, I want to rate it after trying it so that I can help future users make better choices.

### Template Reviewer (Internal)

- As a example_product team member, I want to review submitted templates before they appear in the marketplace so that we maintain quality and prevent abuse.
- As a reviewer, I want to approve or reject templates with a single click and optional note so that the review process is fast and authors get feedback.

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Users can publish a project as a template with title, description, category, and up to 5 preview images | P0 |
| FR-2 | Published templates enter a pending review state before appearing in the marketplace | P0 |
| FR-3 | Users can browse the marketplace with a grid view of template cards | P0 |
| FR-4 | Users can filter templates by category: SaaS, Portfolio, E-commerce, Landing Page, Internal Tool | P0 |
| FR-5 | Users can sort templates by: Popular (fork count), New (date), Top Rated (avg rating) | P0 |
| FR-6 | Users can search templates by keyword across titles and descriptions | P0 |
| FR-7 | Users can fork a template into their own projects, creating an independent copy | P0 |
| FR-8 | Users can rate templates on a 1-5 star scale after forking and using them for >10 minutes | P1 |
| FR-9 | Template cards display preview image, title, author, category, fork count, and average rating | P0 |
| FR-10 | Admin review queue allows team members to approve or reject pending templates | P0 |
| FR-11 | Users can report templates for inappropriate content | P1 |
| FR-12 | Templates with 3+ reports are automatically hidden pending re-review | P1 |
| FR-13 | Only users with at least one deployed project and accounts older than 7 days can publish | P1 |
| FR-14 | Marketplace link is added to the main navigation | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Marketplace page loads in under 2 seconds (p95) | P0 |
| NFR-2 | Fork operation completes in under 5 seconds | P0 |
| NFR-3 | Full-text search returns results in under 500ms | P1 |
| NFR-4 | Review queue processes templates within 24 hours of submission | P0 |
| NFR-5 | Rate limiting: max 5 template publishes per day, max 10 forks per hour per user | P1 |
| NFR-6 | Marketplace supports 10,000+ published templates without performance degradation | P1 |

## Launch Plan

### Phase 1: Internal Beta (Week 9 after dev start)

- Enable behind `marketplace-beta` feature flag for internal team and 20 invited beta users
- Seed with 15-20 high-quality templates converted from the internal template library
- Validate review queue workflow, fork reliability, and page performance
- Collect qualitative feedback on publishing and browsing UX

### Phase 2: Limited GA (Week 10)

- Enable for all example_product Pro and example_product Teams users
- In-app announcement banner and email notification to eligible users
- Monitor key metrics: publish rate, fork rate, review queue throughput, abuse reports
- Iterate on UX based on beta feedback

### Phase 3: Full GA (Week 12)

- Enable for all users including free tier
- Add marketplace to main navigation and homepage
- Launch "Template of the Week" editorial spotlight
- PR and social media push highlighting top community templates
- Track impact on new user activation and fork-to-deploy conversion

### Success Criteria for GA

- 100+ approved community templates
- Fork-to-deploy conversion >= 40%
- Average template rating >= 4.0
- Review queue SLA met (24-hour turnaround) for 95%+ of submissions
- No major abuse incidents requiring marketplace takedown

## Open Questions

1. Should template publishers receive any form of credit or recognition beyond their name on the card? (e.g., "Featured Creator" badge, profile page with all their templates)
2. Should we allow template versioning, where publishers can update their template and forkers get notified?
3. What is the right policy for templates that include third-party API keys or service integrations -- should these be stripped on publish?
4. Should free-tier users be limited in how many templates they can fork per month?
