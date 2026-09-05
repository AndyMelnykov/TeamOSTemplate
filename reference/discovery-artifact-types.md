# Discovery Artifact Types

Canonical artifact types for framing a problem before it becomes a PRD. An opportunity or hypothesis file is named `{feature}-opportunity.md` / `{feature}-hypothesis.md` and placed in the same folder as the PRD it feeds — there is no separate top-level discovery tree, matching how decision files live next to what they decided (see `decision-types.md`).

| Type | Where it's recorded | Example location |
|------|---------------------|-------------------|
| Opportunity | `product-development/product/PRDs/{area}/` | `product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-opportunity.md` |
| Hypothesis | Same folder as its opportunity | `product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-hypothesis.md` |

## ID scheme

- `OPP-{AREA}-{NNN}` — one per opportunity. `{AREA}` is a short mnemonic for the feature-index area (doesn't have to match the `feature-index.yaml` key exactly — e.g. `EXTRACT` for `extraction-quality`). `{NNN}` is sequential starting at 001 within that area.
- `HYP-{AREA}-{NNN}` — one per hypothesis, same numbering rule, references exactly one `OPP-` id in its own `## Opportunity` section.

IDs are for cross-referencing only (in `feature-index.yaml`, PRDs, and `product/Insights/insights.csv` rows) — they don't replace the dated-filename convention used elsewhere in this repo (`decision-types.md`).

## When to write one

Write an opportunity file when a pattern in `product/Insights/insights.csv` (or an analytics investigation, or competitive research) looks worth solving but nothing has committed engineering time yet. Write a hypothesis file once a specific bet is chosen and needs a falsifiable test before a PRD gets written. Skip both for small, uncontested fixes — they exist to make "why does this PRD exist" answerable, not to gate every change.

## Templates

Start from `templates/opportunity.md` and `templates/hypothesis.md`.

## Wiring into feature-index.yaml

Add `opportunity:` and `hypothesis:` keys to the feature's entry once the files exist, the same way `prd:` or `eng-rfc:` are added today. Optional `read_first:` and `do_not_load_by_default:` list keys may also be added to any feature-index entry — `read_first` names the paths (relative to `product-development/`) an agent should open before anything else in that entry; `do_not_load_by_default` names paths that exist but shouldn't be pulled in without a specific reason (e.g. an archived experiment). Both are hints, not enforced by tooling.

## Promotion

Once an opportunity file cites an `insight_id`, bump that row's `status` in `insights.csv` to `validated`. Once a PRD is committed against the hypothesis, bump the same rows to `actioned`. If the resulting initiative surfaces a learning worth keeping beyond this one feature, promote it into the relevant `PRDs/{area}/CONTEXT.md`'s "Active opportunities" section becoming a closed line, or into `product/CLAUDE.md` if it's broadly applicable — don't leave durable learnings stranded only in a closed opportunity file.
