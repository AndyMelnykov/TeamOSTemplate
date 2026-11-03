# Plan 4: Analytics → Signals — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Read `product-development/analytics/` regularly and on demand, and turn it into signals: a watched metric that misses its target or moves sharply, a completed A/B experiment, a completed investigation. Analytics then feeds the loop like customer calls do, and experiment and metric results flow back to the hypotheses they concern.

**Background:** `analytics/` already holds metric definitions with targets (`metrics/`), queries with a recommended schedule (`queries/`), dashboards, experiment write-ups with results (`experiments/`) and investigations with findings. Nothing reads them, and metric values live only in prose.

**Architecture:** the warehouse is a capability this repo doesn't hold, so there are two halves.
- **Capture:** an analyst, or a warehouse MCP server if `docs/agents/capabilities.md` names one, appends measured values to `analytics/snapshots/<metric_id>.csv` via `/analytics-snapshot`.
- **Sweep:** `scripts/signals/analytics_sweep.py` reads `analytics/metric-watch.yaml`, the snapshots and the completed reports, and adds signals through `signals.add` (Plan 1). A weekly GitHub workflow runs it; `/analytics-sweep` runs it on demand.

**Tech Stack:** Python 3.12, PyYAML, stdlib `csv`, pytest; `scripts/signals/signals.py` (Plan 1).

**Spec:** the owner's stage 1 (product analytics as a source) and stage 7 (metric shifts and A/B results close the loop), plus the owner's correction: "what is lacking is how data from these folders is read on a regular basis or on demand to get to signals". [Plans index](2026-11-03-product-loop-plans-index.md).

## Global Constraints

- Signals written: metrics → `source_type: analytics`; experiments → `experiment`; investigations → `analytics` with tag `investigation`. `account` empty. `source_ref` = the snapshot path or the report path. `tags` carries the metric id or feature area.
- Re-running on unchanged inputs writes nothing (Plan 1's duplicate rule: same `source_ref` + `summary`). Metric summaries therefore include the period.
- `metric-watch.yaml` entry keys: `id` (`^[a-z0-9-]+$`), `name`, `unit`, `cadence` (`weekly` → period `YYYY-Www`, `monthly` → `YYYY-MM`), `target_source` (`reference` for `reference/metrics.md`, or a path under `analytics/metrics/`), `target` (required unless `reference`; string like `"> 12%"`), `snapshot` (`analytics/snapshots/<id>.csv`), `rules` (list of `{type: below-target}` or `{type: change, threshold_pct, direction: down|up|any}`).
- Snapshot CSV columns: `period,segment,value,captured_at,captured_by`. `segment` defaults to `all`; `value` is a plain number in the entry's unit. A correction is a new row with a later `captured_at`; the latest per `(period, segment)` wins.
- Target grammar: `^\s*([<>]=?)\s*(-?\d+(?:\.\d+)?)\s*(%|[a-zA-Z]+)?` at the start of the string, rest ignored; no match (e.g. `Tracking…`) means no target, and `below-target` is skipped. Units must match the entry's `unit`.
- `change` rule: `(latest − previous) / abs(previous) × 100` over the two latest periods per segment; previous `0` skips the rule.
- Report headers come in three styles (`| **Status** | X |`, `| Status | X |`, `**Status:** X`); all must parse. Only `Status: Complete` reports are swept. Date: first present of `Experiment End`, `Run Date`, `Date`. Summary: first paragraph under a `TL;DR` heading, else first bold sentence under `Findings`, else first paragraph under `Question`, else the H1; max 300 characters.
- Seeded snapshot rows have `captured_by: example-data` and the signal's `detail` says so.
- No warehouse credentials in the repo or CI.

## Review Focus

1. **A non-numeric snapshot value** (`n/a`, `92,1`). Expected: row skipped and reported; other metrics still evaluate. Pinned in Task 1.
2. **Only one period of data.** Expected: `change` skipped, `below-target` still evaluated. Pinned in Task 1.
3. **Previous value zero.** Expected: `change` skipped, no ZeroDivisionError. Pinned in Task 1.
4. **Running the sweep twice.** Expected: second run adds nothing. Pinned in Task 2.
5. **A report `In Progress` or written in another header style.** Expected: in-progress not swept; all styles parse. Pinned in Task 2.

---

## File Structure

| File | Responsibility |
|---|---|
| `product-development/analytics/metric-watch.yaml`, `snapshots/*.csv` (create) | Watched metrics; captured values (seeded with labelled example data) |
| `scripts/signals/analytics_sweep.py` (create) | Parse watch and snapshots, evaluate rules, scan reports, add signals |
| `scripts/integrity-checks/checks/analytics_watch.py` (create); `run_checks.py`, `config.yaml` (modify) | Watch validity, unswept reports |
| `.claude/commands/analytics-snapshot.md`, `analytics-sweep.md` (create) | Capture; on-demand sweep |
| `.github/workflows/analytics-sweep.yml` (create) | Weekly sweep |
| `product-development/analytics/CLAUDE.md`, `docs/agents/capabilities.md` (modify) | Docs, capability row |
| `tests/signals/test_analytics_sweep.py`, `tests/integrity_checks/test_analytics_watch.py` (create) | Tests |

---

### Task 1: Watch file, snapshots and metric rules

**Files:**
- Create: `scripts/signals/analytics_sweep.py`, `tests/signals/test_analytics_sweep.py`, `product-development/analytics/metric-watch.yaml`, `product-development/analytics/snapshots/{esr,ttp,credit-to-upgrade}.csv`

**Interfaces:**
- Produces: `parse_target(text) -> Target | None`; `load_watch(repo_root) -> (list[WatchedMetric], list[Problem])`; `read_snapshots(repo_root, metric) -> (list[SnapshotRow], list[Problem])`; `evaluate(metric, rows) -> list[Hit]` (latest period per segment only); `hit_to_signal(metric, hit) -> dict` (a valid `signals.add` row). Summaries: below-target → `f"{name} was {value}{unit} in {period} ({segment}), missing target {target.text}"`; change → `f"{name} {'rose' or 'fell'} {abs(pct):.1f}% to {value}{unit} in {period} vs {previous_period} ({segment})"`.

- [ ] **Step 1: Write the failing tests.**

```python
@pytest.mark.parametrize("text,expected", [("> 92%", (">", 92.0, "%")), ("< 15 min", ("<", 15.0, "min")), (">12% (current baseline: 8%)", (">", 12.0, "%"))])
def test_parse_target(text, expected): ...
def test_tracking_has_no_target(): ...
def test_unit_mismatch_is_a_problem(): ...
def test_bad_snapshot_value_is_skipped_and_reported(): ...
def test_period_must_match_cadence(): ...
def test_latest_capture_wins_for_same_period(): ...
def test_below_target_hit(): ...
def test_target_met_no_hit(): ...
def test_change_threshold_and_direction(): ...
def test_single_period(): ...
def test_previous_zero_skips_change(): ...
def test_segments_evaluated_independently(): ...
def test_hit_to_signal_is_valid(): ...              # signals.validate(...) == []
```

- [ ] **Step 2: Run them and confirm they fail.**
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Write `metric-watch.yaml`** with three entries:

  | Id | Name | Unit | Cadence | Target | Rules |
  |---|---|---|---|---|---|
  | `esr` | Extraction Success Rate (ESR) | `%` | weekly | reference | `below-target`; `change` 5% `down` |
  | `ttp` | Time-to-Publish (TTP) | `min` | weekly | reference | `below-target`; `change` 20% `up` |
  | `credit-to-upgrade` | Credit-to-Upgrade Rate | `%` | weekly | `analytics/metrics/billing/credit-usage-metrics.md`, `"> 12%"` | `below-target` |

- [ ] **Step 5: Seed snapshots**, four weekly periods each (`2026-W41`…`2026-W44`, `captured_by: example-data`): ESR 93.1, 92.8, 92.4, 89.5; TTP 12, 12.5, 13, 16; credit-to-upgrade 8, 8.4, 9.1, 9.6.
- [ ] **Step 6: Run the tests and confirm they pass.**
- [ ] **Step 7: Commit** — `git commit -m "feat(analytics): metric watch, snapshots and rules"`.

### Task 2: Reports and the sweep

**Files:**
- Modify: `scripts/signals/analytics_sweep.py`, `tests/signals/test_analytics_sweep.py`

**Interfaces:**
- Produces: `header_field(text, name) -> str | None` (three styles); `report_summary(text) -> str`; `scan_reports(repo_root) -> list[dict]` (signal rows for `Complete` experiments and investigations; `detail` = first 2000 characters of the TL;DR or Findings section); `sweep(repo_root, dry_run=False) -> AddResult`; `main(argv)` with `--repo-root`, `--dry-run`, printing `N new, M existing, K invalid, P problems`, exit 1 if any invalid.

- [ ] **Step 1: Write the failing tests** (fixtures copy three real reports, one per header style): `test_header_styles_and_status_filter`, `test_summary_prefers_tldr_then_findings_then_question`, `test_sweep_adds_metric_and_report_signals`, `test_sweep_is_idempotent`, `test_dry_run_adds_nothing`.
- [ ] **Step 2: Run them and confirm they fail.**
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run them and confirm they pass.**
- [ ] **Step 5: Run on the real repo.** `--dry-run` lists exactly 4 metric hits (ESR below-target, TTP below-target, TTP change, credit-to-upgrade below-target) plus one row per `Complete` report; record the count in the commit message. Run for real; `signals.py check` → OK.
- [ ] **Step 6: Commit** the code, tests and new rows — `git commit -m "feat(analytics): sweep metrics, experiments and investigations into signals"`.

### Task 3: Checks, commands, schedule

**Files:**
- Create: `scripts/integrity-checks/checks/analytics_watch.py`, `tests/integrity_checks/test_analytics_watch.py`, `.claude/commands/analytics-snapshot.md`, `.claude/commands/analytics-sweep.md`, `.github/workflows/analytics-sweep.yml`
- Modify: `run_checks.py`, `config.yaml`, `product-development/analytics/CLAUDE.md`, `docs/agents/capabilities.md`

- [ ] **Step 1: Checks** (write tests first, confirm they fail, implement, register, config `true`): `analytics-watch-invalid` (every Problem from `load_watch`/`read_snapshots`, plus a missing `snapshot` path; key `file:line`) and `analytics-unswept-reports` (a `Complete` report with no signal whose `source_ref` is its path; key = path).
- [ ] **Step 2: `/analytics-snapshot`.** List metrics whose latest snapshot is due by cadence. For each: if `capabilities.md` names an analytics-warehouse adapter, run the metric's query through it; otherwise show the dashboard link and ask the human for the value. Append rows (`captured_by` = person or adapter); never overwrite a row. Offer `/analytics-sweep`.
- [ ] **Step 3: `/analytics-sweep`.** Run `--dry-run`, show hits grouped by feature, run for real, then `signals.py check`. For an `experiment` signal, ask which hypothesis it concerns and offer to add it to that hypothesis's `## Signals` and update its `## Result` and status (`validated` / `invalidated`).
- [ ] **Step 4: `analytics-sweep.yml`.** `schedule: cron "0 7 * * 1"` plus `workflow_dispatch`; `permissions: contents: write`; Python 3.12; run the sweep and `signals.py check`; commit `signals.csv` as `chore: weekly analytics sweep` with the same bot identity as `integrity-checks.yml`, only if there is a diff. A comment marks where a team with warehouse credentials would add a capture job.
- [ ] **Step 5: Docs.** `analytics/CLAUDE.md` gains rows for `metric-watch.yaml` and `snapshots/` and an "Analytics → signals" section (capture vs sweep, cadences, commands, workflow). `capabilities.md` Analytics row → "snapshot files via `/analytics-snapshot`; swap by naming an MCP server here". If Plan 2 is merged, add every `metric-watch.yaml` name and id to `hypotheses.instrumented_metrics` (test `test_watched_metrics_are_instrumented`), so a watched metric becomes A/B-eligible.
- [ ] **Step 6: Commit** — `git commit -m "feat: analytics checks, commands and weekly sweep"`.

### Task 4: Loop status and verification

- [ ] **Step 1: Update `reference/product-loop.md`.** `1. Input signals`: add `product-development/analytics/metric-watch.yaml` and `scripts/signals/analytics_sweep.py`; stays `partial` until a support-desk adapter exists. `3. Validation` → `implemented` if Plan 2 is merged. `7. Rollout and measurement` → `partial` (measurement automated). `Loop closure` → `partial` (analytics and experiments feed back as signals). Mirror in the README.
- [ ] **Step 2: Verify** — `pytest -q`; the sweep run twice → second run `0 new`; `signals.py check` OK; `check-references.ps1` clean.
- [ ] **Step 3: Commit, then ask before pushing.** The PR body notes the seeded rows are example data.
