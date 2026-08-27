# example_product Product Context

## Overview

example_product is example_product Labs' AI prototyping platform that enables developers and teams to turn ideas into production-ready applications through intelligent code generation, real-time collaboration, and one-click deployment.

**North Star:** Build the most reliable AI-powered development platform - empowering customers to go from concept to production by improving generation quality, developer experience, and deployment velocity.

**New to example_product?** See the [Onboarding Guide](../../team/onboarding-guides/onboarding-general.md) for a comprehensive introduction.

---

## Folder Structure

```
product/
├── competitive-research/
│   └── competitors/          # Competitor audits and feature matrices
├── customers/                # Account context, calls, feature requests
├── Insights/                 # Customer signal aggregated across support, success & external research
├── strategy/                 # Roadmaps, vision, business context
├── product-context/          # Reference docs for example_product systems
├── PRDs/                     # Product requirement documents
├── launch-emails/            # Launch communications
├── sales-enablement/         # Sales-facing docs, onboarding
├── processes/                # Operational processes
├── meetings/                 # Meeting notes
└── workflows/                # Workflow specs
```

Note: `analytics/`, `engineering/`, `data-engineering/`, and `design/` are sibling folders to `product/` under `product-development/`.

Each folder has its own `CLAUDE.md` with folder-specific context.

---

## Five Core Pillars

| Pillar | Purpose | P0 Features |
|--------|---------|-------------|
| **1. Generation Quality** | Make AI output production-ready | Multi-file generation, framework detection, code quality scoring |
| **2. Developer Experience** | Seamless build-to-ship workflow | Inline editing, real-time preview, version history, undo/redo |
| **3. Deployment** | One-click production deploys | Auto-provisioning, custom domains, environment variables, CI/CD |
| **4. Collaboration** | Team-based prototyping | Shared projects, commenting, branching, role-based permissions |
| **5. Enterprise** | Scale for organizations | SSO, audit logs, usage analytics, team management, SLAs |

---

## Key Documents

| Purpose | Path |
|---------|------|
| Full Business Context | `strategy/business-context/example_product-business-info.md` |
| Product Roadmap | `strategy/roadmaps/q2-2026-roadmap.md` |
| Competitive Research | `competitive-research/CLAUDE.md` |
| Competitive Feature Matrix | `competitive-research/competitors/competitive-matrix.md` |
| Competitor Teardowns | `competitive-research/competitors/CLAUDE.md` (6 competitor audits, product + website) |
| Users & JTBD | `strategy/business-context/example_product-jtbd-and-users.md` |
| Customer Accounts | `customers/CLAUDE.md` (named accounts, segments, data source pointers) |
| PRDs | `PRDs/CLAUDE.md` |
| Analytics | `../analytics/CLAUDE.md` |

---

## Terminology

Canonical term definitions, metric definitions, and segment definitions live in [reference/](../../reference/CLAUDE.md), not here — see [reference/terminology.md](../../reference/terminology.md).
