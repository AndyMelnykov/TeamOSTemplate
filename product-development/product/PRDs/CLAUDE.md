# PRDs

## Purpose
Product Requirement Documents for example_product features.

Valid `**Status**` values are defined in [reference/status-definitions.md](../../../reference/status-definitions.md).

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

## Opportunities in progress (no PRD yet)

Framed but not yet committed to engineering time. See [reference/discovery-artifact-types.md](../../../reference/discovery-artifact-types.md).

| Opportunity | Hypothesis | Area |
|-------------|-----------|------|
| `extraction-quality/extraction-confidence-scoring-opportunity.md` (`OPP-EXTRACT-001`) | `extraction-quality/extraction-confidence-scoring-hypothesis.md` (`HYP-EXTRACT-001`) | Extraction Quality |

---

## Creating New PRDs

Use the `/prd` command to create new PRDs. The command will:
1. Load the PRD writing style
2. Guide you through required sections
3. Format according to example_product Labs standards
4. Run a CPO check against the finished draft before it's treated as ready to share

---

## PRD Template Sections

1. **Overview** - Problem statement, goals, success metrics
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes
5. **Technical Considerations** - Architecture, dependencies
6. **Launch Plan** - Rollout strategy, feature flags
7. **Sources** - `INS-###`, `SRC-###`, or file-path citations for claims already made in sections 1-6, one bullet each, in the same citation format as `templates/opportunity.md`'s "Evidence" section. A file-path citation must be a Markdown link (`[label](relative/path)`), not a bare backtick reference, so `scripts/check-references.ps1` can verify it resolves. This section consolidates citations already made elsewhere in the PRD — it is not a place to introduce a new unsupported claim. See `.claude/commands/prd.md`'s Step 6 (CPO check) for how these are validated.
