# Terminology

Canonical vocabulary for example_product Labs and the example_product product. Every document in this repo should link here instead of redefining these terms locally.

For metric definitions and targets (ESR, TTP, WCR, etc.), see [metrics.md](metrics.md).
For customer segment and lifecycle-stage definitions, see [segments.md](segments.md).

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
| Workflow | A customer's document automation unit: intake template, extraction rules, approval routing, signature, and delivery settings |
| Automation Run | A single AI-powered document processing execution (document in, extracted structured data + routing out) |
| Template | A pre-built starting point for common document types (NDA, invoice, vendor onboarding form, sales contract, etc.) |
| Preview | The rendered, simulated output of a workflow before publishing |
| Publish | Making a workflow live for signers/submitters |
| Refinement | A follow-up edit that modifies an existing workflow's extraction rules or routing logic |
| Instruction | The natural language input a customer provides to configure what a workflow extracts or how it routes a document |
| Competitors | DocuSign, PandaDoc, Ironclad, Conga, Dropbox Sign, Adobe Acrobat Sign (see `../product-development/product/competitive-research/CLAUDE.md`) |

## Product Loop Terminology

Defined once in [product-loop.md](product-loop.md); these entries point there.

| Term | Definition |
|------|------------|
| Signal | A recurring pattern across evidence (`SIG-###`). See [product-loop.md](product-loop.md). |
| Evidence | One observation from one source (`EV-…`). See [product-loop.md](product-loop.md). |
| Source adapter | Anything that writes evidence through the signal-source contract. See [product-loop.md](product-loop.md). |
| Capability | A kind of external tool (issue tracker, support desk, analytics warehouse, …) filled by a named adapter per install. See [product-loop.md](product-loop.md). |
| Opportunity | A framed customer problem or market gap that signals point to. See [product-loop.md](product-loop.md). |
| Hypothesis | A testable belief about an opportunity, with what would change our mind. See [product-loop.md](product-loop.md). |
| Validation path | The cheapest adequate test of a hypothesis: A/B, prototype, survey or interviews. See [product-loop.md](product-loop.md). |
| Rollout record | The per-feature record of what shipped, when and to whom (planned; Later roadmap). See [product-loop.md](product-loop.md). |
| Measurement | Post-rollout metric results written back as evidence. See [product-loop.md](product-loop.md). |
