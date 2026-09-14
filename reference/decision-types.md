# Decision Types

Canonical decision categories for this repo. A decision file is named `YYYY-MM-DD-{topic}-decision.md` and placed in the folder matching its type, alongside the artifacts it affects (there is no separate top-level decision archive — decisions live next to what they decided).

| Type | Where it's recorded | Example location |
|------|---------------------|-------------------|
| Product decision | `product-development/product/strategy/` or the relevant feature's PRD folder | `product-development/product/strategy/2026-04-01-q3-priorities-decision.md` |
| Technical/architecture decision | `product-development/engineering/rfcs/{product-area}/` | `product-development/engineering/rfcs/billing/2026-04-01-ledger-storage-decision.md` |
| Process decision | `product-development/product/processes/` | `product-development/product/processes/2026-04-01-prd-review-cadence-decision.md` |

A decision file should state: the question being decided, the options considered, the decision, who made it, and the date. It should link back to the PRD, RFC, or feature-index entry it affects, and forward to any decision it supersedes.

**Exception for `Strategy Review`-tier PRDs:** a Product decision that resolves a PRD marked `**Review Tier**: Strategy Review` (see `product-development/product/PRDs/CLAUDE.md`) must be recorded under `product-development/product/strategy/` specifically, not the PRD's own folder — this is what routes it through the human-approval gate in [ADR 0003](../docs/adr/0003-human-approval-for-canonical-writes.md). See [ADR 0006](../docs/adr/0006-two-track-prd-review.md) for why. This tightens the general "or" above into a "must" only for this case; other product decisions may still use either location.

Only the decision itself is durable and belongs here — see Principle 7 (Durable vs. transient context) in [`01-ai-native-product-os.md`](01-ai-native-product-os.md). Working hypotheses and unapproved alternatives stay out of this pattern.
