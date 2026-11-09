# Analytics Sweep

You are turning the analytics folder into signals: watched metrics that missed their target or moved sharply, `Complete` experiments, and `Complete` investigations.

The same sweep runs weekly in `.github/workflows/analytics-sweep.yml`. This command is the on-demand version. The sweep is idempotent: a second run on unchanged inputs adds nothing.

## Step 1: Dry run

```bash
python scripts/signals/analytics_sweep.py --dry-run
```

It prints a `would add` line per new signal, `problem:` lines on stderr for anything it could not read (a non-numeric snapshot value, a report with no usable date), and a count line `N new, M existing, K invalid, P problems`.

Show the `would add` lines grouped by feature area (the `tags` of the signal, or the folder of the report). Fix or report each `problem:` line first: a skipped row is a metric not being evaluated. If nothing is new, say so and stop.

## Step 2: Run for real

```bash
python scripts/signals/analytics_sweep.py
python scripts/signals/signals.py check
```

Both must succeed. Report the count line and the ids written. Never edit `signals.csv` directly.

Rows whose `detail` says "Seeded example data" come from the sample snapshots (`captured_by: example-data`), not a real measurement. Say so when you show them.

## Step 3: Close the loop on experiments

For each new signal with `source_type: experiment`, ask the user which hypothesis it concerns. If they name one:

1. Offer to add `SIG-###` under that hypothesis's `## Signals`, with one line on why it supports or contradicts the bet.
2. Offer to update its `## Result` and set the status: `validated` if the result met the Success criteria, `invalidated` if it did not. Let the user decide which; do not apply the status yourself. Set **Last Updated** to today.
3. Run `python scripts/signals/hypotheses.py list` and `python scripts/integrity-checks/run_checks.py`; neither may show a `hyp-*` or `signals-*` finding for that file.

Do none of this without the user's say-so. New `analytics` signals with no hypothesis can be grouped into one with `/hypothesis`.
