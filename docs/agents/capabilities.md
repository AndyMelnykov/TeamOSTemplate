# Capabilities

The product loop ([`reference/product-loop.md`](../../reference/product-loop.md)) depends on tools that differ per team. Each kind of tool is a **capability**, and each install configures one named adapter per capability.

| Capability | Used by | Configured adapter in this install | How to swap |
|---|---|---|---|
| Issue tracker | `/feature-request-intake`, `/triage`, `/to-tickets`, `/customer-call` | GitHub Issues via `gh` — [`issue-tracker.md`](issue-tracker.md) | Rewrite `issue-tracker.md` for the new tracker's conventions; update this row. |
| Support desk | Input signals (stage 1) | None yet | Name the adapter here once one adds signals through `scripts/signals/signals.py`; see [`signal-contract.md`](../../reference/signal-contract.md). |
| CRM / call recorder | `/customer-call` | Manual paste of the transcript into `/customer-call` | Replace the paste step with a source adapter that adds signals through `scripts/signals/signals.py`; see [`signal-contract.md`](../../reference/signal-contract.md). |
| Analytics warehouse | Measurement (stage 7), `/analytics-snapshot`, `product-development/analytics/` | Snapshot files via `/analytics-snapshot` | Name an MCP server here; `/analytics-snapshot` then runs the metric queries through it. |
| External intelligence | Input signals (stage 1) | product-intelligence-agent (handoff 2a; see [ADR 0007](../adr/0007-teamos-is-the-integration-layer.md)) | Any agent that adds signals can take this row. |
| Design tool | Prototyping (stage 4), PRDs | Figma links in `product-development/feature-index.yaml` | Change the link convention in `feature-index.yaml` and update this row. |

A skill names the capability, never the vendor. To swap a vendor, change this table's row and the doc it points to.
