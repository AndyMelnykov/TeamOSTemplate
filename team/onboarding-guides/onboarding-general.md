# Onboarding: General

This guide covers setup and orientation common to all new example_product team members. Role-specific guides are linked at the bottom.

## Setup

### Shared Tools (everyone gets these)

| Tool | Purpose | Access |
|------|---------|--------|
| GitHub | Code, PRs, CI/CD | `example_product-labs` org invite |
| Linear / Jira / Asana | Issue tracking, sprints | `example_product` team invite |
| Slack | Communication | example_product Labs workspace invite |
| Google Workspace | Docs, email, calendar | Auto-provisioned |
| Figma | Design files, prototypes (view access) | `example_product Labs` workspace invite |

### Function-Specific Tools

See your role-specific onboarding guide for additional tools.

### Repos

| Repo | Description |
|------|-------------|
| `example_product-app` | Main application (frontend + backend API) |
| `example_product-ai` | AI generation pipeline and model serving |
| `example_product-infra` | Terraform, Kubernetes configs, CI/CD |
| `example_product-docs` | Public documentation site |
| `example_product-product` | This repo - product docs, PRDs, strategy |

### Environment Setup

1. Get laptop provisioned and accounts set up (IT will walk you through this)
2. Accept invitations to GitHub (`example_product-labs` org), Linear / Jira / Asana (`example_product` team), Slack, and Google Workspace
3. Set up local development environment (follow `CONTRIBUTING.md` in the main repo)
4. Complete a test generation on staging and deploy it

## Key Documents

- [Platform Overview](../product/product-context/example_product-platform-overview.md) - what example_product does
- [Business Info](../product/strategy/business-context/example_product-business-info.md) - company context

## Slack Channels

| Channel | Purpose |
|---------|---------|
| `#example_product-general` | Team-wide announcements and discussion |
| `#example_product-eng` | Engineering discussion, architecture decisions |
| `#example_product-eng-standup` | Daily async standup posts |
| `#example_product-product` | Product discussions, customer feedback, roadmap |
| `#example_product-incidents` | Production incidents and on-call alerts |
| `#example_product-deploys` | Automated deploy notifications |

## People to Meet

Your manager will pair you with an onboarding buddy on your first day.

| Person | Role |
|--------|------|
| Jordan Reeves | Product questions |
| Alex Chen | Product questions |
| Sam Torres | Engineering architecture |
| Priya Patel | Engineering architecture |
| Emily Zhao | Design system |
| Grace Lin | Data and analytics |

## Org Chart

See your manager for current org chart and reporting structure. Cross-functional partners vary by role - check your role-specific guide.

## First Tasks

- [ ] Accept all tool invitations and verify access
- [ ] Join all Slack channels listed above
- [ ] Read the three Key Documents
- [ ] Meet your onboarding buddy
- [ ] Attend your first standup and sprint planning (async standup daily, sync planning biweekly)
- [ ] Ship a small starter task (your manager will assign one in Linear / Jira / Asana)

## Role-Specific Guides

- [Product](onboarding-product.md)
- [Engineering](onboarding-engineering.md)
- [Design](onboarding-design.md)
- [Analytics](onboarding-analytics.md)
- [Data Engineering](onboarding-data-engineering.md)
