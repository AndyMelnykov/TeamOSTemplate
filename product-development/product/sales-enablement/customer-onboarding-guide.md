# example_product - Customer Onboarding Guide

*Last updated: March 15, 2026*
*Owner: Hannah Stulberg (PM), Morgan Wu (Solutions Engineering)*

# Overview

This guide defines the standard onboarding process for new example_product customers. The goal is to take a customer from signed contract to productive usage within 14 business days. The process is divided into four phases, each with defined owners, deliverables, and success criteria.

**Target timeline:** 14 business days from contract signature to go-live
**Current average:** 11 business days
**Customer satisfaction (onboarding NPS):** 64

---

# Phase 1: Setup (Days 1-2)

**Owner:** Solutions Engineering
**Goal:** Customer has a working example_product environment with admin access

## Checklist

- [ ] Org workspace created in example_product (`https://app.example_productlabs.dev/org/{customer-slug}`)
- [ ] Admin account provisioned for primary contact
- [ ] Billing configured (Stripe subscription active, invoice sent)
- [ ] Team seats allocated per contract (Starter: 5, Growth: 25, Enterprise: unlimited)
- [ ] SSO configured (Enterprise tier only, requires customer's IdP metadata)
- [ ] Welcome email sent with login credentials and quickstart link
- [ ] Dedicated Slack Connect channel created (Growth + Enterprise tiers)
- [ ] Customer added to example_product status page notifications
- [ ] Salesforce record updated with onboarding start date

## Setup Email Template

Subject: Welcome to example_product - your workspace is ready

```
Hi {{first_name}},

Your example_product workspace is live! Here's everything you need to get started:

- Workspace URL: https://app.example_productlabs.dev/org/{{org-slug}}
- Your login: {{email}} (password reset link below)
- Quickstart guide: https://docs.example_productlabs.dev/quickstart
- Team seat invitations: you can invite up to {{seat_count}} team members

[Set Your Password]

Your onboarding engineer {{se_name}} will reach out within 24 hours to
schedule your configuration session.

Welcome aboard,
The example_product Team
```

## Success Criteria

- Customer can log in and access their workspace
- At least one additional team member has been invited
- No open setup tickets

---

# Phase 2: Configuration (Days 3-5)

**Owner:** Solutions Engineering + Customer
**Goal:** example_product is configured for the customer's tech stack and development patterns

## Checklist

- [ ] Configuration session scheduled (60 min video call)
- [ ] Customer's tech stack documented (framework, styling, state management, testing)
- [ ] `.example_product/architecture.yaml` created with customer's patterns
- [ ] Default project template configured with:
  - [ ] Framework preference (React, Next.js, Vue, etc.)
  - [ ] Styling system (Tailwind, CSS Modules, styled-components, etc.)
  - [ ] TypeScript strictness level
  - [ ] Component naming conventions
  - [ ] Directory structure preferences
- [ ] Custom prompt library seeded with 3-5 starter prompts relevant to their use cases
- [ ] Cloud provider credentials connected (if deploying - AWS, GCP, or Vercel)
- [ ] Git integration configured (GitHub, GitLab, or Bitbucket)
- [ ] Walkthrough of project settings and generation options completed

## Configuration Session Agenda

| Time | Topic | Who |
|------|-------|-----|
| 0:00 - 0:10 | Introductions and onboarding overview | SE |
| 0:10 - 0:25 | Tech stack discussion and architecture.yaml setup | SE + Customer |
| 0:25 - 0:40 | First generation demo using their stack preferences | SE |
| 0:40 - 0:50 | Integrations setup (Git, cloud, CI/CD) | SE + Customer |
| 0:50 - 1:00 | Q&A and next steps | All |

## Success Criteria

- `architecture.yaml` committed and producing correctly-configured output
- Customer has run at least 3 test generations with satisfactory results
- Git integration is connected and exporting works

---

# Phase 3: Training (Days 6-10)

**Owner:** Solutions Engineering + PM
**Goal:** Customer's team is proficient in using example_product for their core use cases

## Checklist

- [ ] Team training session scheduled (90 min, all developers who will use example_product)
- [ ] Training session delivered covering:
  - [ ] Prompt engineering best practices for code generation
  - [ ] Using architecture hints and constraints effectively
  - [ ] Project templates and configuration inheritance
  - [ ] Code export and integration with existing codebase
  - [ ] Deployment workflow (if One-Click Deploy is enabled)
  - [ ] Iterative refinement - editing and re-generating specific components
  - [ ] Troubleshooting common generation issues
- [ ] Hands-on workshop completed (each attendee builds a small project)
- [ ] FAQ document customized for the customer's use cases and shared
- [ ] Office hours schedule shared (Growth: weekly 30-min slot, Enterprise: dedicated SE)
- [ ] Self-serve documentation links sent:
  - Docs: https://docs.example_productlabs.dev
  - Community: https://community.example_productlabs.dev
  - Video tutorials: https://example_productlabs.dev/tutorials
  - Changelog: https://example_productlabs.dev/changelog

## Training Session Agenda

| Time | Topic | Format |
|------|-------|--------|
| 0:00 - 0:15 | example_product overview and key concepts | Presentation |
| 0:15 - 0:35 | Prompt engineering masterclass | Demo + discussion |
| 0:35 - 0:50 | Advanced features (architecture hints, templates, iteration) | Demo |
| 0:50 - 1:20 | Hands-on workshop - build a project from scratch | Individual exercise |
| 1:20 - 1:30 | Q&A and ongoing support resources | Open discussion |

## Success Criteria

- 80%+ of licensed seats have logged in and run at least one generation
- Customer rates training session 4+ out of 5
- No open "how do I..." support tickets from trained users

---

# Phase 4: Go-Live (Days 11-14)

**Owner:** PM + Solutions Engineering
**Goal:** Customer is independently productive and has a success plan for the first 90 days

## Checklist

- [ ] First real project completed in example_product (not a training exercise)
- [ ] Project exported or deployed to customer's environment
- [ ] 90-day success plan created with customer, including:
  - [ ] Target number of projects to build
  - [ ] Target number of active users
  - [ ] Specific use cases to tackle first
  - [ ] Milestone check-in dates (Day 30, Day 60, Day 90)
- [ ] QBR cadence established (quarterly for Growth, monthly for Enterprise)
- [ ] Feedback survey sent (onboarding NPS)
- [ ] Internal handoff completed:
  - [ ] Onboarding summary written and saved to customer file
  - [ ] Salesforce updated with go-live date and health status
  - [ ] Account transitioned from SE to ongoing CSM support (Enterprise)
  - [ ] Any open feature requests logged in [feature requests tracker](../customers/feature-requests/feature-requests.md)

## 90-Day Success Plan Template

| Milestone | Target | Measure |
|-----------|--------|---------|
| Day 30 | 3+ projects created, 60%+ seat utilization | Usage dashboard |
| Day 60 | 1+ project deployed to production, team generating independently | Customer check-in |
| Day 90 | Expansion discussion, identify additional teams/use cases | QBR |

## Success Criteria

- Customer has completed at least 1 real project
- Onboarding NPS score >= 7
- No open P0 or P1 support tickets
- 90-day success plan agreed upon with customer stakeholder

---

# Escalation Process

| Issue | Escalation Path | SLA |
|-------|----------------|-----|
| Login or access problems | Solutions Engineering on-call | 4 hours |
| Generation quality issues | Engineering (via #example_product-eng-support) | 24 hours |
| Configuration help | Assigned SE | 24 hours |
| Billing or contract questions | RevOps (billing@example_productlabs.dev) | 48 hours |
| Customer unhappy with onboarding | PM (Hannah Stulberg) | Same day |

# Resources

- Onboarding deck template: [Google Slides](https://docs.google.com/presentation/d/example_product-onboarding-deck)
- Configuration session recording (example): [Loom](https://loom.com/example_product-config-session-example)
- Training session recording (example): [Loom](https://loom.com/example_product-training-session-example)
- Onboarding NPS survey: [Typeform](https://example_productlabs.typeform.com/onboarding-nps)
