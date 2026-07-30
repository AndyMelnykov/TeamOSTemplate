# PRDs

## Purpose
Product Requirement Documents for example_product features.

---

## Naming Convention

```
[feature-name]-prd.md
```

Examples:
- `generation-quality-prd.md`
- `one-click-deploy-prd.md`
- `collaboration-prd.md`
- `template-library-prd.md`

---

## Current PRDs

PRDs are organized by product area:

| PRD | Feature |
|-----|---------|
| `billing/credit-usage-dashboard-prd.md` | Credit usage dashboard |
| `deployment/one-click-deploy-prd.md` | One-click deployment to production infrastructure |
| `deployment/custom-domains-prd.md` | Custom domains |
| `home-page/project-search-prd.md` | Project search |
| `prototyping/version-history-prd.md` | Project version history and rollback |
| `starter-templates/community-marketplace-prd.md` | Community template marketplace |

---

## Creating New PRDs

Use the `/prd` command to create new PRDs. The command will:
1. Load the PRD writing style
2. Guide you through required sections
3. Format according to example_product Labs standards

---

## PRD Template Sections

1. **Overview** - Problem statement, goals, success metrics
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes
5. **Technical Considerations** - Architecture, dependencies
6. **Launch Plan** - Rollout strategy, feature flags
