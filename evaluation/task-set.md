# Evaluation Task Set

Each task has a real, verifiable expected answer and expected source file(s) in this repo, as of 2026-08-27. Run each task against an agent that has this repo in context, and record: did it reach the correct answer, did it cite the correct source, how many files did it open, and how many tokens did it consume.

## 1. Find the current definition of a metric

**Prompt:** "What is the current target for Extraction Success Rate (ESR)?"
**Expected answer:** > 92%
**Expected source:** `reference/metrics.md`

## 2. Locate all artifacts related to one feature

**Prompt:** "What artifacts exist for the credit-usage-dashboard feature?"
**Expected answer:** PRD, eng RFC, eng plan, data-eng RFC, data-eng plan, Figma link, 3 tickets, 1 table schema, 1 query, 1 dashboard doc, 1 experiment result, 1 investigation, 1 bug investigation.
**Expected source:** `product-development/feature-index.yaml`, `billing.credit-usage-dashboard`

## 3. Identify the approved product decision

**Prompt:** "What is example_product's Status field convention, and what does 'Shipped' mean?"
**Expected answer:** Five defined values (Draft, In Review, Approved, Shipped, Archived); Shipped = feature is live in production.
**Expected source:** `reference/status-definitions.md`

## 4. Summarize customer evidence behind a roadmap item

**Prompt:** "What customer evidence supports building Team Workspaces?"
**Expected answer:** Acme Corp's account team requested manager-level review workflows and assigned internal owners to plan a rollout before the feature shipped.
**Expected source:** `product-development/product/PRDs/team-workspaces-prd.md`, `product-development/product/customers/accounts/acme-corp/`

## 5. Find the latest experiment result

**Prompt:** "What was the result of the low-balance-warning experiment?"
**Expected answer:** A 22% reduction in churn-from-depletion (cited in the credit-usage-dashboard PRD's Business Opportunity section).
**Expected source:** `product-development/analytics/experiments/billing/low-balance-warning-03-05-2026-experiment-results.md`, cross-referenced from `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md`

## 6. Identify conflicting or outdated context

**Prompt:** "Is there any inconsistency in how customer segments are defined across this repo?"
**Expected answer:** Before this plan's Task 4, segments were defined independently in `product-development/product/customers/CLAUDE.md` and customer-lifecycle categories in `product-development/product/workflows/bi-weekly-update/workflow-spec.md`, with no cross-reference. After Task 4, both point to `reference/segments.md`.
**Expected source:** `reference/segments.md`

## 7. Generate a bi-weekly product update

**Prompt:** "Generate this cycle's bi-weekly product update."
**Expected answer:** A document following the structure in `product-development/product/workflows/bi-weekly-update/workflow-spec.md`, written to `product-development/product/meetings/team-bi-weekly/docs/`.
**Expected source:** `product-development/product/workflows/bi-weekly-update/workflow-spec.md`, `product-development/product/workflows/bi-weekly-update/reference/2026-02-11.md` (canonical good output)
