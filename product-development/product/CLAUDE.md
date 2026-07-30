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

## example_product Labs Terminology

| Term | Definition |
|------|------------|
| example_product Pro | example_product Pro tier - always capitalized (product name) |
| example_product Teams | example_product Teams tier - always capitalized (product name) |
| example_product Enterprise | example_product Enterprise tier - always capitalized (product name) |
| Dashboard | Customer-facing project dashboard - always capitalized when referring to the product surface |

## example_product Product Terminology

| Term | Definition |
|------|------------|
| Project | A customer workspace containing generated code, configuration, and deployment settings |
| Generation | A single AI code generation event (prompt in, code out) |
| Template | A pre-built starting point for common app types (SaaS dashboard, landing page, e-commerce, etc.) |
| Preview | The live rendered output of generated code before deployment |
| Deploy | Publishing a project to production infrastructure |
| Iteration | A follow-up generation that modifies existing project code |
| Prompt | The natural language input a customer provides to generate or iterate on code |
| GSR | Generation Success Rate - percentage of generations that produce working, error-free code |
| TTD | Time-to-Deploy - elapsed time from first generation to production deployment |
| PCR | Project Completion Rate - percentage of projects that reach deployment |
| Competitors | Lovable, Google Stitch, v0, Replit, Figma Make, Bolt (see `competitive-research/CLAUDE.md`) |
