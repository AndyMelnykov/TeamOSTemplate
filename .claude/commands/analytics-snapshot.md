# Analytics Snapshot

You are capturing measured metric values into `product-development/analytics/snapshots/<metric_id>.csv`, so that `/analytics-sweep` can turn misses and sharp moves into signals.

**Contract:** `product-development/analytics/metric-watch.yaml` lists the watched metrics, their cadence, unit and snapshot file. Snapshot columns are `period,segment,value,captured_at,captured_by`. `value` is a plain number in the metric's unit: no `%`, no thousands separators, no `n/a`.

## Step 1: Find what is due

Read `metric-watch.yaml`. For each metric, read the last row of its snapshot file and work out the period that is now complete:

- `weekly`: the last finished ISO week, written `YYYY-Www` (for example `2026-W44`)
- `monthly`: the last finished month, written `YYYY-MM`

A metric is **due** if its snapshot file has no row for that period (any segment). List the due metrics, and stop here if none are due.

## Step 2: Get each value

Read `docs/agents/capabilities.md`, row "Analytics warehouse".

- **An adapter (for example an MCP server) is named:** run the metric's query from `product-development/analytics/queries/` through it for the period. Set `captured_by` to the adapter's name.
- **Snapshot files only:** show the metric's dashboard link from `product-development/analytics/dashboards.md` and ask the human for the value for that period. Set `captured_by` to the person's name or handle. Never estimate, copy or invent a value; if the human has none, skip that metric.

Ask for one row per segment only if the metric is tracked by segment. Otherwise `segment` is `all`.

## Step 3: Append

Append rows to the snapshot file. Never overwrite or delete an existing row: a correction is a new row for the same `(period, segment)` with a later `captured_at`, and the latest one wins.

- `captured_at`: now, ISO 8601 UTC (`2026-11-09T09:00:00Z`)
- Never write `captured_by: example-data`; that label marks the seeded sample rows.

## Step 4: Offer the sweep

Report the rows appended and any metric you skipped. Then offer `/analytics-sweep`. Do not run it without the user's say-so.
