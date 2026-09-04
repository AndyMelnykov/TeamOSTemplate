# example_product Product Context

## Overview

example_product is example_product Labs' AI-powered SaaS document automation platform that enables ops, legal, and finance teams to turn manual paperwork into automated digital workflows through intelligent document extraction, real-time collaboration, and one-click publishing.

**North Star:** Build the most reliable AI-powered document automation platform - empowering customers to go from raw paperwork to published workflow by improving extraction quality, workflow building experience, and publishing velocity.

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
| **1. Extraction Quality** | Make AI-extracted data trustworthy | Multi-format OCR, field & clause detection, extraction confidence scoring |
| **2. Workflow Building Experience** | Seamless build-to-publish workflow | Inline field mapping, real-time preview, version history, undo/redo |
| **3. Publishing** | One-click live document portals | Auto-provisioning, custom domains, environment previews, delivery integrations |
| **4. Collaboration** | Team-based document workflows | Shared workflows, commenting, branching, role-based permissions |
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
