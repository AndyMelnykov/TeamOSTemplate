# Opportunity and hypothesis files as a discovery layer before PRDs

Nothing between `product/Insights/insights.csv` (raw customer signal) and a PRD currently records why a PRD exists or what was actually being bet on. We add two lightweight artifact types — `{feature}-opportunity.md` and `{feature}-hypothesis.md` — defined in [`reference/discovery-artifact-types.md`](../../reference/discovery-artifact-types.md), living next to the PRD they feed rather than in a separate top-level tree, consistent with how decision files already live next to what they decided ([`reference/decision-types.md`](../../reference/decision-types.md)).

## Considered Options

- A separate top-level `discovery/` or `opportunities/` tree. Rejected: it would fragment a feature's history across yet another folder on top of the eight functions ADR 0002 already reassembles through `feature-index.yaml`, for artifacts that are only ever read alongside the PRD they justify.
- Folding "why this PRD" reasoning directly into the PRD's Overview section instead of a separate file. Rejected: a PRD's Overview is written after a bet is already chosen; there's no place to record the opportunity before a hypothesis narrows it, or to keep the falsifiable test/result visible once the PRD ships.
- A full domain-first restructure (`CONTEXT.md`/`CURRENT.md`/`METRICS.md` per product domain) instead of this narrower addition. Rejected for the same reason ADR 0002 rejected feature-first folders: it would give up the ownership clarity function-first folders give each team. A lighter per-area `CONTEXT.md` under `PRDs/{area}/` is added instead, without moving anything.

## Consequences

`insights.csv` rows cited by an opportunity should have their `status` bumped to `validated`; rows behind a hypothesis whose PRD is committed should bump to `actioned` — this is a manual step until the "Automatic feature-index maintenance" roadmap item is extended to cover it. `feature-index.yaml` entries may now also carry `opportunity:` / `hypothesis:` keys and optional `read_first:` / `do_not_load_by_default:` loading hints.
