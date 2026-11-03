# Plan 6: Analytics → Signals Adapter — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Read `product-development/analytics/` on a schedule and on demand, and turn it into evidence through the Plan 1 contract:
- metric values that miss their target or move sharply;
- completed A/B experiments;
- completed investigations.

Analytics then feeds the loop the same way customer calls and external intelligence do, and experiment outcomes flow back to the hypotheses they tested.

**Background:** `analytics/` is already rich:
- metric definitions with targets and current values (`metrics/`);
- SQL queries that name a recommended schedule (`queries/`);
- dashboards (`dashboards/`);
- experiment write-ups with results and recommendations (`experiments/`);
- investigations with findings (`investigations/`);
- a funnel playbook.

What's missing is a reader: nothing turns these into signals, and metric values live only in prose.

**Architecture:** the warehouse is a capability this repo doesn't hold, so the adapter splits into **capture** and **evaluate**.
- **Capture:** an analyst, or a warehouse MCP server when one is configured, appends measured values to `analytics/snapshots/<metric_id>.csv` via `/analytics-snapshot`.
- **Evaluate:** a deterministic script, `scripts/signalstore/adapters/analytics.py`, reads three things and writes `teamos.analytics` evidence:
  - `analytics/metric-watch.yaml`: which metrics to watch, their query and snapshot files, targets (from `reference/metrics.md` or a feature metrics doc), and rules (`below-target`, `change`);
  - the snapshots;
  - completed experiment and investigation write-ups.
- **Schedule:** a weekly GitHub workflow runs the evaluation. `/analytics-sweep` runs it on demand. New evidence goes to `/signal-triage` (Plan 2) like any other source.

**Tech Stack:** Python 3.12, PyYAML, stdlib `csv`, pytest; `scripts/signalstore` (Plans 1–2).

**Spec:** the owner's stage 1 (product analytics as a signal source) and stage 7 (metric changes and A/B results close the loop); the owner's 2026-11-03 correction: "what is lacking is how data from these folders is read on a regular basis or on demand to get to signals"; [gap analysis](../../../gap-analysis-product-loop-2026-11-03.md) §3 Stage 1 gap 4 and Stage 7.

## Global Constraints

- Adapter id `teamos.analytics`. Source types and kinds:
  - metrics: `product-analytics` / `metric-change`;
  - experiments: `experiment` / `experiment-result`;
  - investigations: `analytics-investigation` / `investigation-finding`.

  `trust: internal`.
- Native keys (via `make_evidence_id`):
  - metrics: `f"metric/{metric_id}/{period}/{segment}/{rule_type}"`;
  - reports: `f"report/{path relative to product-development/analytics}"`.

  Re-running on unchanged inputs writes nothing.
- `metric-watch.yaml` entry keys:

  | Key | Rule |
  |---|---|
  | `id` | `^[a-z0-9-]+$` |
  | `name` | |
  | `unit` | |
  | `cadence` | `weekly` (period `YYYY-Www`) or `monthly` (period `YYYY-MM`) |
  | `target_source` | `reference`, or a path under `product-development/analytics/metrics/` |
  | `target` | required unless `target_source: reference`; string like `"> 12%"` |
  | `query` | path under `analytics/queries/`, or `null` |
  | `snapshot` | `analytics/snapshots/<id>.csv` |
  | `rules` | list of `{type: below-target}` or `{type: change, threshold_pct: <number>, direction: down\|up\|any}` |
  | `feature` | optional `"<area>.<feature>"` key in `feature-index.yaml` |

- Snapshot CSV columns: `period,segment,value,captured_at,captured_by`. `segment` defaults to `all`, `value` is a plain number in the watch entry's unit, and `captured_at` is ISO date-time with timezone.
- Target grammar: `^\s*([<>]=?)\s*(-?\d+(?:\.\d+)?)\s*(%|[a-zA-Z]+)?`, matched at the start of the string; the rest is ignored. `Tracking…` or no match means no target, so `below-target` is skipped with a note.
  - Violation for `>`/`>=` is value `<=`/`<` target; for `<`/`<=` it's value `>=`/`>` target.
  - Units must match the watch entry's `unit`, or the entry is invalid.
- `change` rule: `pct = (latest - previous) / abs(previous) * 100` over the two most recent periods per segment. A previous value of `0` skips the rule.
- Report headers come in three styles (`| **Status** | X |`, `| Status | X |`, `**Status:** X`), and all must parse.
  - Status must be `Complete`.
  - Date comes from the first present of `Experiment End`, `Run Date`, `Date`.
  - Summary comes from, in order: first paragraph under a `TL;DR` heading (any level); first bold sentence under a `Findings` heading; first paragraph under a `Question` heading; the H1 title. Truncated to 300 characters.
  - `hypothesis_id` comes from a `Hypothesis` header field holding a `HYP-` id (Plan 3).
- Example data is labelled: every seeded snapshot row has `captured_by: example-data`, and evidence derived from it carries `metadata.example_data: true`.
- No warehouse credentials in this repo or CI. A team that has them adds a capture step; this plan documents where.

## Review Focus

1. **A non-numeric snapshot value** (`n/a`, `92,1`). Expected: that row is skipped, `analytics-watch-invalid` names file and line, and other metrics still evaluate. Pinned in Task 2 (`test_bad_snapshot_value_is_skipped_and_reported`).
2. **Only one period of data.** Expected: `change` skipped silently, `below-target` still evaluated. Pinned in Task 2 (`test_single_period`).
3. **A previous value of zero.** Expected: `change` skipped, no ZeroDivisionError. Pinned in Task 2 (`test_previous_zero_skips_change`).
4. **Running the sweep twice.** Expected: the second run writes nothing. Pinned in Task 3 (`test_sweep_is_idempotent`).
5. **A report still `In Progress`, or written in a header style other than the table.** Expected: in-progress reports are not emitted; all three styles parse the same. Pinned in Task 3 (`test_header_styles_and_status_filter`).

---

## File Structure

| File | Responsibility |
|---|---|
| `product-development/analytics/metric-watch.yaml` (create) | Watched metrics, targets, rules |
| `product-development/analytics/snapshots/*.csv` (create; seeded with labelled example data) | Captured values |
| `product-development/analytics/CLAUDE.md` (modify) | Document watch, snapshots, sweep, capture |
| `scripts/signalstore/adapters/__init__.py`, `scripts/signalstore/adapters/analytics.py` (create) | Parse, evaluate, emit, sweep CLI |
| `scripts/integrity-checks/checks/analytics_watch.py` (create); `run_checks.py`, `config.yaml` (modify) | Watch validity, stale snapshots, unswept reports |
| `.claude/commands/analytics-snapshot.md`, `.claude/commands/analytics-sweep.md` (create) | Capture and on-demand sweep |
| `.github/workflows/signals-analytics-sweep.yml` (create) | Weekly scheduled sweep |
| `product-development/signals/adapters.yaml`, `docs/agents/capabilities.md`, `reference/product-loop.md`, `README.md` (modify) | Registration, capability row, status |
| `tests/signalstore/test_analytics_adapter.py`, `tests/integrity_checks/test_analytics_watch.py` (create) | Tests |

---

### Task 1: Watch file, snapshot format and target parsing

**Files:**
- Create: `scripts/signalstore/adapters/__init__.py`, `scripts/signalstore/adapters/analytics.py`, `tests/signalstore/test_analytics_adapter.py`, `product-development/analytics/metric-watch.yaml`, `product-development/analytics/snapshots/{esr,ttp,credit-to-upgrade}.csv`

**Interfaces:**
- Produces:

```python
@dataclass(frozen=True)
class Target: op: str; value: float; unit: str | None; text: str
@dataclass(frozen=True)
class WatchedMetric: id: str; name: str; unit: str; cadence: str; target: Target | None
                     query: str | None; snapshot: str; rules: list[dict]; feature: str | None
@dataclass(frozen=True)
class SnapshotRow: period: str; segment: str; value: float; captured_at: str; captured_by: str; line: int
@dataclass(frozen=True)
class WatchProblem: file: str; line: int; message: str

def parse_target(text: str) -> Target | None
def load_reference_targets(repo_root: Path) -> dict[str, Target]   # keys: lower-cased full name and abbreviation, e.g. "extraction success rate (esr)" and "esr"
def load_watch(repo_root: Path) -> tuple[list[WatchedMetric], list[WatchProblem]]
def read_snapshots(repo_root: Path, m: WatchedMetric) -> tuple[list[SnapshotRow], list[WatchProblem]]
```

- [ ] **Step 1: Write the failing tests.**

```python
@pytest.mark.parametrize("text,expected", [
    ("> 92%", (">", 92.0, "%")), ("< 15 min", ("<", 15.0, "min")), ("> 2", (">", 2.0, None)),
    (">12% (current baseline: 8%)", (">", 12.0, "%")), ("<3%. A refund rate above…", ("<", 3.0, "%")),
])
def test_parse_target(text, expected): ...
def test_tracking_has_no_target(): assert parse_target("Tracking (higher = engagement)") is None
def test_reference_targets_include_abbreviations(): ...      # from a fixture copy of reference/metrics.md
def test_watch_unit_mismatch_is_a_problem(): ...             # unit "min" vs target "%"
def test_watch_requires_target_when_not_reference(): ...
def test_bad_snapshot_value_is_skipped_and_reported(): ...   # "n/a" and "92,1" -> WatchProblem(line=…), other rows kept
def test_period_must_match_cadence(): ...                    # weekly metric with "2026-10" -> problem
```

- [ ] **Step 2: Run them and confirm they fail** — `pytest tests/signalstore/test_analytics_adapter.py -q`.
- [ ] **Step 3: Implement** the dataclasses and functions.
- [ ] **Step 4: Write `metric-watch.yaml`.** Entries:

  | Id | Name | Unit | Cadence | Target | Query | Rules |
  |---|---|---|---|---|---|---|
  | `esr` | Extraction Success Rate (ESR) | `%` | weekly | reference | `analytics/queries/prototyping/generation-success-rate.sql` | `below-target`; `change` 5% `down` |
  | `ttp` | Time-to-Publish (TTP) | `min` | weekly | reference | `analytics/queries/deployment/one-click-deploy-success.sql` | `below-target`; `change` 20% `up` |
  | `credit-to-upgrade` | Credit-to-Upgrade Rate | `%` | weekly | `analytics/metrics/billing/credit-usage-metrics.md`, target `"> 12%"` | `analytics/queries/billing/credit-burn-rate.sql` | `below-target` |

  Set each `feature` to its matching `feature-index.yaml` key.

- [ ] **Step 5: Seed snapshots** with four weekly periods each (`2026-W41`…`2026-W44`, segment `all`, `captured_by: example-data`):
  - ESR: 93.1, 92.8, 92.4, 89.5 (below target, and −3.1% wow, which doesn't trip the 5% rule).
  - TTP: 12, 12.5, 13, 16 (above the `< 15` target; +23% wow).
  - Credit-to-upgrade: 8, 8.4, 9.1, 9.6 (below target).
- [ ] **Step 6: Run the tests and confirm they pass.**
- [ ] **Step 7: Commit** — `git commit -m "feat(analytics): metric watch, snapshots and target parsing"`.

### Task 2: Metric rules → evidence

**Files:**
- Modify: `scripts/signalstore/adapters/analytics.py`, `tests/signalstore/test_analytics_adapter.py`

**Interfaces:**
- Produces:

```python
@dataclass(frozen=True)
class RuleHit: metric_id: str; rule_type: str; period: str; segment: str; value: float
               previous: float | None; previous_period: str | None; pct: float | None; detail: str

def evaluate_metric(m: WatchedMetric, rows: list[SnapshotRow]) -> list[RuleHit]   # latest period per segment only
def metric_evidence(m: WatchedMetric, hit: RuleHit, row: SnapshotRow, now: datetime) -> dict   # a contract-valid record
```

Record fields:
- `summary`: below-target → `f"{name} was {value}{unit} in {period} ({segment}), missing target {target.text}"`; change → `f"{name} {'rose' if pct > 0 else 'fell'} {abs(pct):.1f}% to {value}{unit} in {period} vs {previous_period} ({segment})"`.
- `metric`: `{name, value, unit, period, target, rule, segment}`.
- `observed_at`: `row.captured_at[:10]`.
- `source_name`: `"metric-watch"`.
- `source_ref`: the snapshot path.
- `metadata`: `{"metric_id", "feature", "query", "example_data"}`.

- [ ] **Step 1: Write the failing tests.**
  - `test_below_target_hit`
  - `test_target_met_no_hit`
  - `test_change_down_threshold`
  - `test_change_direction_respected`
  - `test_single_period`
  - `test_previous_zero_skips_change`
  - `test_segments_evaluated_independently`
  - `test_metric_evidence_is_contract_valid` (`validate_record(...) == []` against the real schema)
  - `test_seeded_data_hits` (ESR and credit-to-upgrade `below-target`; TTP `below-target` and `change`)
- [ ] **Step 2: Run them and confirm they fail.**
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run them and confirm they pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(analytics): metric rules emit contract evidence"`.

### Task 3: Experiments and investigations → evidence; the sweep

**Files:**
- Modify: `scripts/signalstore/adapters/analytics.py`, `tests/signalstore/test_analytics_adapter.py`

**Interfaces:**
- Produces:

```python
def header_field(text: str, name: str) -> str | None        # three header styles
def report_summary(text: str) -> str                         # rule order in Global Constraints
def scan_reports(repo_root: Path, now: datetime) -> list[dict]   # Complete experiments + investigations as records
def sweep(repo_root: Path, now: datetime, dry_run: bool = False) -> tuple[AppendResult | list[dict], list[WatchProblem]]
def main(argv=None) -> int   # --repo-root, --dry-run; prints "N new, M existing, K invalid, P problems"; exit 1 if invalid > 0
```

Report records:
- `source_name`: `"analytics/experiments"` or `"analytics/investigations"`.
- `source_ref`: path relative to the repo.
- `observed_at`: the report date.
- `summary`: from `report_summary`.
- `excerpt`: the first 2000 characters of the TL;DR or Findings section.
- `hypothesis_id`: set when present.
- `metadata`: `{"feature_area": <folder under experiments/ or investigations/>, "title": <H1>}`.

- [ ] **Step 1: Write the failing tests.** Fixtures copy three real reports, one per header style.
  - `test_header_styles_and_status_filter`
  - `test_summary_prefers_tldr_then_findings_then_question`
  - `test_hypothesis_link_is_carried`
  - `test_sweep_writes_metric_and_report_evidence`
  - `test_sweep_is_idempotent`
  - `test_dry_run_writes_nothing`
- [ ] **Step 2: Run them and confirm they fail.**
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run them and confirm they pass.**
- [ ] **Step 5: Run on the real repo.** `python scripts/signalstore/adapters/analytics.py --repo-root . --dry-run` lists exactly 4 metric hits (ESR below-target, TTP below-target, TTP change, credit-to-upgrade below-target) plus one record per `Complete` experiment or investigation (10 report files exist today; record the actual count in the commit message). Then run it for real, and `python scripts/signalstore/cli.py validate --repo-root .` → OK.
- [ ] **Step 6: Commit** the code, tests and the generated `evidence/teamos.analytics/*.jsonl` — `git commit -m "feat(analytics): sweep experiments, investigations and metric watch into evidence"`.

### Task 4: Integrity checks

**Files:**
- Create: `scripts/integrity-checks/checks/analytics_watch.py`, `tests/integrity_checks/test_analytics_watch.py`
- Modify: `run_checks.py`, `config.yaml`

**Interfaces:**
- Produces:

  | Check id | Finding | Key |
  |---|---|---|
  | `analytics-watch-invalid` | Every `WatchProblem` from `load_watch`/`read_snapshots`, plus a `query` or `snapshot` path that doesn't exist | `f"{file}:{line}"` |
  | `analytics-snapshot-stale` | Latest snapshot older than 2 × cadence (14 days weekly, 62 monthly) by `captured_at` | metric id |
  | `analytics-unswept-reports` | A `Complete` report whose evidence id isn't in the store | report path |

- [ ] **Step 1: Write the failing tests**, one per check, plus a clean case.
- [ ] **Step 2: Run them and confirm they fail.**
- [ ] **Step 3: Implement and register**; config keys set to `true`.
- [ ] **Step 4: Run the checks.** `pytest -q` → PASS. `python scripts/integrity-checks/run_checks.py --repo-root .` → `analytics-snapshot-stale` findings for the seeded example data once it's older than 14 days. That's expected, and it shows the check works.
- [ ] **Step 5: Commit** — `git commit -m "feat(integrity): analytics watch, stale snapshot and unswept report checks"`.

### Task 5: Capture and sweep commands, schedule, capability

**Files:**
- Create: `.claude/commands/analytics-snapshot.md`, `.claude/commands/analytics-sweep.md`, `.github/workflows/signals-analytics-sweep.yml`
- Modify: `product-development/analytics/CLAUDE.md`, `product-development/signals/adapters.yaml`, `docs/agents/capabilities.md`

- [ ] **Step 1: Write `/analytics-snapshot`.**
  1. Load the watch file and list metrics whose latest snapshot is due per cadence.
  2. For each, if `docs/agents/capabilities.md` names an analytics-warehouse adapter (an MCP server), run the metric's `query` file through it and map the result to `period,segment,value`. Otherwise show the query path and dashboard link (from `analytics/dashboards/`) and ask the human for the value(s).
  3. Append rows with `captured_by` set to the person or adapter.
  4. Offer `/analytics-sweep`.

  Never overwrite an existing `(period, segment)` row; a correction is a new row with a later `captured_at`, and the evaluator uses the latest `captured_at` per `(period, segment)`. Add a test `test_latest_capture_wins_for_same_period` to Task 1's file and the matching logic to `read_snapshots`.

- [ ] **Step 2: Write `/analytics-sweep`.** Run `--dry-run` and show the hits, with metric hits grouped by feature. Run it for real, then `cli.py validate`, then offer `/signal-triage --adapter teamos.analytics`. For `experiment-result` evidence with a `hypothesis_id`, prompt to update that hypothesis's `## Result` and `**Status**` (`validated`/`invalidated`), then run `scripts/hypotheses/score.py`.

- [ ] **Step 3: Write `signals-analytics-sweep.yml`.**
  - Triggers: `schedule: cron "0 7 * * 1"` and `workflow_dispatch`; `permissions: contents: write`.
  - Steps: Python 3.12, install requirements, run `python scripts/signalstore/adapters/analytics.py --repo-root .` and `python scripts/signalstore/cli.py validate --repo-root .`.
  - Commit `product-development/signals/evidence/teamos.analytics/` as `chore: weekly analytics sweep`, with the same bot identity as `integrity-checks.yml`. Push only if there's a diff.
  - Add a comment in the file saying where a team with warehouse credentials would add a capture step (a job that runs the queries and appends snapshots) before the sweep.

- [ ] **Step 4: Docs and registration.**
  - `analytics/CLAUDE.md`: add rows for `metric-watch.yaml` and `snapshots/`, and an "Analytics → signals" section covering capture vs evaluate, the cadences, the commands and the workflow.
  - `adapters.yaml`: `teamos.analytics` → `active`, cadence `weekly`.
  - `capabilities.md`: Analytics warehouse row → "snapshot files via `/analytics-snapshot`; swap by naming an MCP server here".
  - If Plan 3 is merged, extend `scripts/hypotheses/routing.instrumented_metrics` to include every `metric-watch.yaml` `name` and `id`. Add `test_watch_metrics_are_instrumented` to `tests/hypotheses/test_routing.py`, so a metric becomes A/B-eligible once it's watched.

- [ ] **Step 5: Commit** — `git commit -m "feat: analytics snapshot and sweep commands with weekly schedule"`.

### Task 6: Loop status and verification

- [ ] **Step 1: Update `reference/product-loop.md`.**
  - `1. Input signals`: add `product-development/analytics/metric-watch.yaml` and `scripts/signalstore/adapters/analytics.py`. It stays `partial` until a support-desk adapter exists.
  - `3. Validation`: → `implemented` if Plan 3 is merged (A/B results now flow back automatically).
  - `7. Rollout and measurement`: → `partial` (measurement automated; per-feature rollout record still a ROADMAP item).
  - `Loop closure`: → `partial` (analytics and experiments feed back; post-launch review per PRD is still manual).

  Mirror these in the README.
- [ ] **Step 2: Verify.**
  - `pytest -q` → pass.
  - The adapter run twice → second run `0 new`.
  - `python scripts/signalstore/cli.py validate --repo-root .` → OK.
  - `powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1` → clean.
- [ ] **Step 3: Commit, then ask before pushing.** The PR body notes the seeded data is example data, and that `reference/product-loop.md` needs ADR 0003 approval.
