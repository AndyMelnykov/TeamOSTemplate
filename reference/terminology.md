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
| Signal | One thing that happened, from any source (a customer quote, a forum thread, a ticket, a metric miss, an A/B result). Unique or repeated; repeats are separate signals. See [product-loop.md](product-loop.md). |
| Hypothesis | A testable bet that aggregates signals. Its first status, `opportunity`, is the problem framed before a bet is chosen. See [product-loop.md](product-loop.md). |
| Validation path | The cheapest adequate test of a hypothesis: A/B, prototype, survey or interviews. See [product-loop.md](product-loop.md). |
| Source adapter | Anything that adds signals: a skill, a script, an MCP-backed workflow or an external agent. See [product-loop.md](product-loop.md). |
| Capability | A kind of external tool (issue tracker, support desk, analytics warehouse, …) filled by a named adapter per install. See [product-loop.md](product-loop.md). |
