# A hypothesis is the one discovery artifact; signals feed it

The discovery model is signals aggregated into hypotheses ([`reference/product-loop.md`](../../reference/product-loop.md)). A hypothesis starts at status `proposed`, when the problem and its signals are written down, and moves on from there. There is no separate artifact for a framed-but-unchosen problem.

## Considered Options

- Keep a separate `{feature}-opportunity.md` next to each hypothesis ([ADR 0005](0005-opportunity-hypothesis-layer.md)). Rejected: two files and a link between them for what is one status field.
- Put framed problems into the signal store. Rejected: signals are events, not framed problems.

## Consequences

`templates/opportunity.md`, the `-opportunity.md` convention, `OPP-` ids and the `opportunity:` feature-index key are retired. `OPP-EXTRACT-001` was folded into `HYP-EXTRACT-001`. ADR 0005 is superseded by this decision.
