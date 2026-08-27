# Decision Types

Canonical decision categories for this repo. A decision file is named `YYYY-MM-DD-{topic}-decision.md` and placed in the folder matching its type, alongside the artifacts it affects (there is no separate top-level decision archive — decisions live next to what they decided).

| Type | Where it's recorded | Example location |
|------|---------------------|-------------------|
| Product decision | `product-development/product/strategy/` or the relevant feature's PRD folder | `product-development/product/strategy/2026-04-01-q3-priorities-decision.md` |
| Technical/architecture decision | `product-development/engineering/rfcs/{product-area}/` | `product-development/engineering/rfcs/billing/2026-04-01-ledger-storage-decision.md` |
| Process decision | `product-development/product/processes/` | `product-development/product/processes/2026-04-01-prd-review-cadence-decision.md` |

A decision file should state: the question being decided, the options considered, the decision, who made it, and the date. It should link back to the PRD, RFC, or feature-index entry it affects, and forward to any decision it supersedes.

Only the decision itself is durable and belongs here — see Principle 7 (Durable vs. transient context) in [`01-ai-native-product-os.md`](01-ai-native-product-os.md). Working hypotheses and unapproved alternatives stay out of this pattern.
