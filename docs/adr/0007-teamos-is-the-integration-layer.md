# TeamOSTemplate is the integration layer; external agents are source adapters

The product loop ([`reference/product-loop.md`](../../reference/product-loop.md)) needs signals from many places: customer calls, support tickets, analytics, and public market signals. TeamOSTemplate is the system of record for evidence, signals, opportunities, hypotheses and their outcomes. External agents and MCP-backed tools are **source adapters** that add signals through one script (Plan 1), and every external tool is a **capability** filled by a named adapter per install ([`docs/agents/capabilities.md`](../agents/capabilities.md)). product-intelligence-agent (`https://github.com/AndyMelnykov/product-intelligence-agent`) is the first external adapter. A separate "Strategic Signals Agent" role is absorbed by this layer rather than built as its own system.

## Considered Options

- A separate "Strategic Signals Agent" repo that owns signals and hypotheses. Rejected: it would duplicate the hypothesis layer in a second place.
- Hypotheses living inside the external agent. Rejected: discovery spans all sources (calls, tickets, analytics), not only public text the agent can see.
- This repo as adapter host. Chosen: one store, one vocabulary, and any number of adapters writing into it.

## Consequences

The external agent's own consumer decision (its ADR 004) now names this repo as the consumer (handoff 2a). Adapter authors follow the signal contract delivered by Plan 1; until it lands, intake remains manual (`/customer-call`, the insights CSV). Workflow docs name capabilities, not vendors.
