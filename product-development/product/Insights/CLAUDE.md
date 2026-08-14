# Insights

Customer signal aggregated across support, success, and external research touchpoints — distinct from `customers/` (named-account context and calls) and `analytics/` (product usage metrics).

Insights are stored as two flat CSVs shared across all sources, not as per-folder docs. The same underlying insight often shows up more than once — a Reddit thread today, a support ticket next month — so insights and their evidence are tracked separately and linked by ID. This keeps the store simple at 20 rows and still works at thousands.

## Folder Structure

```text
Insights/
├── insights.csv                  # Canonical insight patterns (one row per distinct pattern)
├── sources.csv                   # Evidence rows — one per observation, linked to an insight_id
├── customer-support/              # Raw sweep notes from support tickets, escalations, help-center interactions
├── customer-success/              # Raw sweep notes from CS check-ins, renewals, health scores, QBRs
└── customer-research-reddit/      # Raw sweep notes from public Reddit research (r/lovable, etc.)
```

The per-source folders are optional scratch space for raw notes from a research pass (e.g. `2026-08-12-sweep-notes.md`). The CSVs are the source of truth — folders just hold backing material worth keeping.

## Schema

**`insights.csv`** — one row per distinct pattern:

| Column | Notes |
|--------|-------|
| `insight_id` | `INS-###`, sequential |
| `theme` | Free-text category. Current values: `production-readiness`, `trust-security`, `ai-cost-control`, `iteration-feedback-recovery`, `platform-intelligence`, `maintainability` |
| `user_intent` | What the user is trying to do, in their own framing |
| `product_insight` | The product implication — what this suggests we build or change |
| `status` | `new` → `validated` → `actioned` → `archived` |
| `first_seen` / `last_seen` | Dates, updated as new sources roll in |

**`sources.csv`** — one row per observation of an insight:

| Column | Notes |
|--------|-------|
| `source_id` | `SRC-###`, sequential |
| `insight_id` | FK into `insights.csv` |
| `source_type` | `customer-support`, `customer-success`, `customer-research-reddit`, or a new value as sources expand (e.g. `sales-call`, `user-interview`) |
| `source_ref` | Where it came from — thread title, ticket ID, call date, etc. (no fabricated URLs) |
| `date` | When this observation was captured |
| `evidence` | The specific quote or note backing this instance |

**Weight is derived, not stored**: an insight's weight is the count of `sources.csv` rows with that `insight_id`. An insight seen in 3 places outweighs one seen in 1 — no separate column to keep in sync.

## Adding new findings

1. Check `insights.csv` for an existing pattern that matches. If found, just add a row to `sources.csv` with that `insight_id` and bump `last_seen` — this is how weight grows.
2. If it's genuinely new, add a row to both: a new `insight_id` in `insights.csv`, and its first `sources.csv` row.
3. Drop any raw notes worth keeping in the matching source folder (create one if the source type is new).

## Related

| Looking for... | Where to find it |
|-----------------|-------------------|
| Named-account context, calls, feature requests | [`../customers/CLAUDE.md`](../customers/CLAUDE.md) |
| Product usage metrics, dashboards | [`../../analytics/CLAUDE.md`](../../analytics/CLAUDE.md) |
| Competitor-sourced insights | [`../competitive-research/CLAUDE.md`](../competitive-research/CLAUDE.md) |
