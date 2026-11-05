# HYP-{AREA}-{NNN}: {Hypothesis title}

| Field | Value |
|-------|-------|
| **Status** | {proposed \| testing \| validated \| invalidated \| in-prd \| shipped} |
| **Confidence** | {low \| medium \| high \| ?} -- how sure we are the target metric moves; `?` allowed only at `proposed` |
| **Effort** | {cheap \| costly \| ?} -- cheap = about a week or less to build and test; `?` allowed only at `proposed` |
| **Validation path** | {ab-test \| prototype \| survey \| interviews} -- blank at `proposed`; see `hypotheses.py list` for the recommendation |
| **Target metric** | {metric name from `reference/metrics.md`, e.g. Extraction Success Rate (ESR)} |
| **Owner** | {name} |
| **Last Updated** | {YYYY-MM-DD} |
| **PRD** | {path to the PRD once written, else blank} |

If {change}, then {expected user behavior change}, because {underlying belief}.

## Problem

{What friction or unmet need are users experiencing, stated in their own terms, and who experiences it.}

## Signals

- {SIG-### from signals.csv, a file path to an analytics investigation or competitive research finding} -- {why it supports this}

## Why it matters

{What it costs the business or the user if unaddressed.}

## Test

{Method: interviews, prototype, fake door, live experiment, etc.}

## Success criteria

- {Measurable threshold 1}
- {Measurable threshold 2}

## Result

`{pending | supported | not supported}` -- {one-line outcome once known; link to the relevant `analytics/experiments/` file if a live experiment ran}
