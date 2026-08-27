# Status Definitions

Canonical status values for the `**Status**` field used in PRD and RFC header tables (see any file under `product-development/product/PRDs/` or `product-development/engineering/rfcs/`).

| Status | Meaning |
|--------|---------|
| Draft | Being written; not yet shared for feedback |
| In Review | Shared for feedback; open questions being resolved |
| Approved | Reviewers signed off; implementation may begin or is in progress |
| Shipped | Feature is live in production |
| Archived | Superseded, cancelled, or no longer relevant; kept for history |

Use exactly one of these five values in the `**Status**` field. Update it as the artifact's real-world state changes — do not leave it at `Draft` once work has progressed past that stage.
