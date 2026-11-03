# Discovery Artifact Types

The canonical artifact for framing a problem before it becomes a PRD is the hypothesis. A hypothesis file is named `{feature}-hypothesis.md` and placed in the same folder as the PRD it feeds -- there is no separate top-level discovery tree, matching how decision files live next to what they decided (see `decision-types.md`). A hypothesis aggregates the signals that support it; see [product-loop.md](product-loop.md).

| Type | Where it's recorded | Example location |
|------|---------------------|-------------------|
| Hypothesis | `product-development/product/PRDs/{area}/` | `product-development/product/PRDs/extraction-quality/extraction-confidence-scoring-hypothesis.md` |

## ID scheme

`HYP-{AREA}-{NNN}` -- one per hypothesis. `{AREA}` is a short mnemonic for the feature-index area (doesn't have to match the `feature-index.yaml` key exactly -- e.g. `EXTRACT` for `extraction-quality`). `{NNN}` is sequential starting at 001 within that area.

IDs are for cross-referencing only (in `feature-index.yaml`, PRDs, and `product-development/signals/signals.csv` rows) -- they don't replace the dated-filename convention used elsewhere in this repo (`decision-types.md`).

## Statuses

`proposed` (the problem and its signals are written down; no test chosen yet) -> `testing` -> `validated` | `invalidated` -> `in-prd` -> `shipped`. Recorded in the file's `## Status` section.

## When to write one

Write a hypothesis file when a pattern in `product-development/signals/signals.csv` (or an analytics investigation, or competitive research) looks worth solving. Fill in `## Problem` and `## Signals` first; add the test and success criteria when a specific bet is chosen and needs a falsifiable test before a PRD gets written. Skip it for small, uncontested fixes -- it exists to make "why does this PRD exist" answerable, not to gate every change.

## Templates

Start from `templates/hypothesis.md`.

## Wiring into feature-index.yaml

Add a `hypothesis:` key to the feature's entry once the file exists, the same way `prd:` or `eng-rfc:` are added today. Optional `read_first:` and `do_not_load_by_default:` list keys may also be added to any feature-index entry -- `read_first` names the paths (relative to `product-development/`) an agent should open before anything else in that entry; `do_not_load_by_default` names paths that exist but shouldn't be pulled in without a specific reason (e.g. an archived experiment). Both are hints, not enforced by tooling.

## Promotion

Signals have no status to bump; a signal is picked up when a hypothesis cites its `SIG-###`. If the resulting initiative surfaces a learning worth keeping beyond this one feature, promote it into the relevant `PRDs/{area}/CONTEXT.md` as a closed line, or into `product/CLAUDE.md` if it's broadly applicable -- don't leave durable learnings stranded only in a closed hypothesis file.
