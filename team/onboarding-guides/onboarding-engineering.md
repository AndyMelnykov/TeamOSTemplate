# Onboarding: Engineering

Engineering-specific setup and orientation for developers joining example_product.

## Setup

### Shared Tools (everyone gets these)

See [General Onboarding](onboarding-general.md#shared-tools-everyone-gets-these).

### Function-Specific Tools

| Tool | Purpose | Access |
|------|---------|--------|
| Datadog | Monitoring, alerting, APM | Request access from Sam Torres |
| PagerDuty | On-call rotation and incident management | Added by EM after first month |
| Vercel | Frontend deployments | `example_product-labs` org |
| AWS Console | Infrastructure (read access initially) | Request from Sam Torres |

### Repos

| Repo | Why |
|------|-----|
| `example_product-app` | Main application - frontend (React/Next.js) + backend API |
| `example_product-ai` | AI generation pipeline and model serving |
| `example_product-infra` | Terraform, Kubernetes configs, CI/CD pipelines |
| `example_product-docs` | Public documentation site |
| `example_product-product` | PRDs and specs for feature context |

### Environment Setup

1. Complete [General Onboarding](onboarding-general.md) setup first
2. Clone `example_product-app`, `example_product-ai`, and `example_product-infra`
3. Follow `CONTRIBUTING.md` in `example_product-app` for local dev setup
4. Run the test suite locally and verify it passes
5. Complete a test generation on staging and deploy it
6. Set up Datadog and bookmark the [example_product service dashboard](https://app.datadoghq.com)

## Key Documents

- [Frontend CLAUDE.md](../frontend/CLAUDE.md) - dev conventions, design system, React patterns
- [Engineering TDDs](../engineering/tdds/) - technical design documents
- [Product Context](../product/product-context/example_product/CLAUDE.md) - system reference docs
- [Platform Overview](../product/product-context/example_product-platform-overview.md) - what example_product does end-to-end

## Slack Channels

| Channel | Purpose |
|---------|---------|
| `#example_product-eng` | Engineering discussion, architecture decisions |
| `#example_product-eng-standup` | Daily async standup posts |
| `#example_product-incidents` | Production incidents and on-call alerts |
| `#example_product-deploys` | Automated deploy notifications |
| `#example_product-general` | Team-wide announcements |

## People to Meet

| Person | Why |
|--------|-----|
| Alex Rivera | EM - team structure, sprint process, growth plan |
| Sam Torres | Engineering architecture, infrastructure |
| Priya Patel | Engineering architecture, code review norms |
| Jordan Kim | Eng peer - current sprint context |
| Sam Chen | Eng peer - frontend patterns |
| Riley Patel | Eng peer - AI pipeline |
| Morgan Wu | Eng peer - infrastructure |

## Org Chart

Engineering reports to Alex Rivera (EM). The team covers frontend, backend, AI pipeline, and infrastructure. Cross-functional partners: Product (Hannah Stulberg), Design (Taylor Brooks, Jamie Ortiz), Analytics (Casey Nguyen).

## First Tasks

- [ ] Get local dev environment running and passing tests
- [ ] Complete a test generation on staging
- [ ] Read the frontend conventions doc and one recent TDD
- [ ] Review 2-3 recent PRs to understand code review norms
- [ ] Pick up a starter bug or small feature from Linear / Jira / Asana (your manager will assign one)
- [ ] Shadow an on-call shift after your first month
