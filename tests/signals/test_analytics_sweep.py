from pathlib import Path

import pytest

from analytics_sweep import (
    SnapshotRow,
    Target,
    WatchedMetric,
    evaluate,
    hit_to_signal,
    load_watch,
    parse_target,
    read_snapshots,
)
from signals import validate

REFERENCE = """# Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Extraction Success Rate (ESR)** | Runs that extract all fields | > 92% |
| **Time-to-Publish (TTP)** | Median time to publish | < 15 min |
| **Refinement Depth** | Follow-up edits per workflow | Tracking (higher = engagement) |
"""

SNAPSHOT_HEADER = "period,segment,value,captured_at,captured_by\n"

WATCH = """metrics:
  - id: esr
    name: Extraction Success Rate (ESR)
    unit: "%"
    cadence: weekly
    target_source: reference
    snapshot: analytics/snapshots/esr.csv
    rules:
      - type: below-target
      - type: change
        threshold_pct: 5
        direction: down
"""


def _repo(tmp_path: Path, watch: str = WATCH, snapshots: dict[str, str] | None = None) -> Path:
    analytics = tmp_path / "product-development/analytics"
    analytics.mkdir(parents=True)
    (analytics / "metric-watch.yaml").write_text(watch, encoding="utf-8")
    (tmp_path / "reference").mkdir()
    (tmp_path / "reference/metrics.md").write_text(REFERENCE, encoding="utf-8")
    for name, body in (snapshots or {}).items():
        path = analytics / "snapshots" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(SNAPSHOT_HEADER + body, encoding="utf-8", newline="")
    return tmp_path


def _metric(**over) -> WatchedMetric:
    base = dict(
        id="esr",
        name="Extraction Success Rate (ESR)",
        unit="%",
        cadence="weekly",
        target_source="reference",
        target=Target(">", 92.0, "%", "> 92%"),
        snapshot="analytics/snapshots/esr.csv",
        rules=({"type": "below-target"}, {"type": "change", "threshold_pct": 5, "direction": "down"}),
        line=1,
    )
    base.update(over)
    return WatchedMetric(**base)


def _rows(*values, by="analyst") -> list[SnapshotRow]:
    """(period, value) or (period, segment, value) tuples -> SnapshotRow."""
    out = []
    for v in values:
        period, segment, value = (v[0], "all", v[1]) if len(v) == 2 else v
        out.append(SnapshotRow(period, segment, float(value), "2026-10-26T09:00:00Z", by))
    return out


@pytest.mark.parametrize(
    "text,expected",
    [
        ("> 92%", (">", 92.0, "%")),
        ("< 15 min", ("<", 15.0, "min")),
        (">12% (current baseline: 8%)", (">", 12.0, "%")),
    ],
)
def test_parse_target(text, expected):
    t = parse_target(text)
    assert (t.op, t.value, t.unit) == expected


def test_tracking_has_no_target():
    assert parse_target("Tracking (higher = engagement)") is None


def test_reference_target_comes_from_metrics_md(tmp_path):
    metrics, problems = load_watch(_repo(tmp_path))
    assert problems == []
    assert [m.id for m in metrics] == ["esr"]
    assert (metrics[0].target.op, metrics[0].target.value) == (">", 92.0)


def test_unit_mismatch_is_a_problem(tmp_path):
    watch = WATCH.replace('unit: "%"', "unit: min")  # reference target for ESR is in %
    metrics, problems = load_watch(_repo(tmp_path, watch))
    assert len(problems) == 1 and "unit" in problems[0].message
    assert metrics[0].target is None  # below-target will be skipped


def test_invalid_watch_entry_is_reported_with_its_line(tmp_path):
    watch = WATCH + """  - id: Bad_Id
    name: Broken
    unit: "%"
    cadence: daily
    target_source: analytics/metrics/x.md
    snapshot: analytics/snapshots/bad.csv
    rules:
      - type: nonsense
"""
    metrics, problems = load_watch(_repo(tmp_path, watch))
    assert [m.id for m in metrics] == ["esr"]  # the valid entry survives
    assert problems and all(p.line == 13 for p in problems)  # the second entry starts on line 13
    text = " ".join(p.message for p in problems)
    for fragment in ("id", "cadence", "rule"):
        assert fragment in text


def test_bad_snapshot_value_is_skipped_and_reported(tmp_path):
    repo = _repo(tmp_path, snapshots={"esr.csv": (
        "2026-W42,all,n/a,2026-10-19T09:00:00Z,analyst\n"
        '2026-W43,all,"92,1",2026-10-26T09:00:00Z,analyst\n'
        "2026-W44,all,89.5,2026-11-02T09:00:00Z,analyst\n"
    )})
    metric = load_watch(repo)[0][0]
    rows, problems = read_snapshots(repo, metric)
    assert [(r.period, r.value) for r in rows] == [("2026-W44", 89.5)]
    assert [p.line for p in problems] == [2, 3]
    assert all("value" in p.message for p in problems)


def test_period_must_match_cadence(tmp_path):
    repo = _repo(tmp_path, snapshots={"esr.csv": (
        "2026-10,all,90,2026-10-26T09:00:00Z,analyst\n"
        "2026-W44,all,89.5,2026-11-02T09:00:00Z,analyst\n"
    )})
    metric = load_watch(repo)[0][0]
    rows, problems = read_snapshots(repo, metric)
    assert [r.period for r in rows] == ["2026-W44"]
    assert len(problems) == 1 and "period" in problems[0].message


def test_blank_segment_defaults_to_all(tmp_path):
    repo = _repo(tmp_path, snapshots={"esr.csv": "2026-W44,,89.5,2026-11-02T09:00:00Z,analyst\n"})
    rows, _ = read_snapshots(repo, load_watch(repo)[0][0])
    assert rows[0].segment == "all"


def test_missing_snapshot_file_yields_no_rows(tmp_path):
    repo = _repo(tmp_path)
    assert read_snapshots(repo, load_watch(repo)[0][0]) == ([], [])


def test_latest_capture_wins_for_same_period(tmp_path):
    repo = _repo(tmp_path, snapshots={"esr.csv": (
        "2026-W44,all,80,2026-11-02T09:00:00Z,analyst\n"
        "2026-W44,all,95,2026-11-03T09:00:00Z,analyst\n"
    )})
    rows, problems = read_snapshots(repo, load_watch(repo)[0][0])
    assert problems == []
    assert [(r.period, r.value) for r in rows] == [("2026-W44", 95.0)]


def test_below_target_hit():
    hits = evaluate(_metric(), _rows(("2026-W43", 92.4), ("2026-W44", 89.5)))
    assert [(h.rule, h.period, h.value) for h in hits] == [("below-target", "2026-W44", 89.5)]


def test_less_than_target_is_missed_when_value_is_too_high():
    metric = _metric(unit="min", target=Target("<", 15.0, "min", "< 15 min"), rules=({"type": "below-target"},))
    assert [h.value for h in evaluate(metric, _rows(("2026-W44", 16)))] == [16.0]
    assert evaluate(metric, _rows(("2026-W44", 14))) == []


def test_target_met_no_hit():
    assert evaluate(_metric(), _rows(("2026-W43", 91), ("2026-W44", 93.5))) == []


def test_only_latest_period_is_evaluated():
    assert evaluate(_metric(), _rows(("2026-W42", 80), ("2026-W43", 85), ("2026-W44", 93))) == []


@pytest.mark.parametrize(
    "threshold,direction,expect_hit",
    [(5, "down", True), (5, "up", False), (5, "any", True), (10, "down", False), (10, "any", False)],
)
def test_change_threshold_and_direction(threshold, direction, expect_hit):
    metric = _metric(target=None, rules=({"type": "change", "threshold_pct": threshold, "direction": direction},))
    hits = evaluate(metric, _rows(("2026-W43", 100), ("2026-W44", 94)))  # -6%
    assert [h.rule for h in hits] == (["change"] if expect_hit else [])
    if expect_hit:
        assert hits[0].pct == pytest.approx(-6.0) and hits[0].previous_period == "2026-W43"


def test_single_period():
    hits = evaluate(_metric(), _rows(("2026-W44", 89.5)))
    assert [h.rule for h in hits] == ["below-target"]  # change skipped, no error


def test_previous_zero_skips_change():
    metric = _metric(target=None, rules=({"type": "change", "threshold_pct": 5, "direction": "any"},))
    assert evaluate(metric, _rows(("2026-W43", 0), ("2026-W44", 50))) == []


def test_segments_evaluated_independently():
    rows = _rows(
        ("2026-W43", "free", 95), ("2026-W44", "free", 93),   # fine
        ("2026-W43", "pro", 96), ("2026-W44", "pro", 88),     # misses target and drops 8.3%
        ("2026-W44", "team", 90),                             # one period: only below-target
    )
    hits = evaluate(_metric(), rows)
    assert sorted((h.segment, h.rule) for h in hits) == [
        ("pro", "below-target"), ("pro", "change"), ("team", "below-target"),
    ]


def test_hit_to_signal_is_valid():
    metric = _metric()
    rows = _rows(("2026-W43", 92.4), ("2026-W44", 89.5), by="example-data")
    hits ={h.rule: h for h in evaluate(metric, rows)}
    below = hit_to_signal(metric, hits["below-target"])
    assert validate(below) == []
    assert below["source_type"] == "analytics"
    assert below["source_ref"] == "product-development/analytics/snapshots/esr.csv"
    assert below["account"] == "" and below["tags"] == "esr"
    assert below["date"] == "2026-10-26"
    assert below["summary"] == "Extraction Success Rate (ESR) was 89.5% in 2026-W44 (all), missing target > 92%"
    assert "example-data" in below["detail"]

    metric = _metric(rules=({"type": "change", "threshold_pct": 3, "direction": "down"},))
    change = hit_to_signal(metric, evaluate(metric, rows)[0])
    assert validate(change) == []
    assert change["summary"] == "Extraction Success Rate (ESR) fell 3.1% to 89.5% in 2026-W44 vs 2026-W43 (all)"


def test_real_analyst_rows_are_not_labelled_example_data():
    hit = evaluate(_metric(), _rows(("2026-W44", 89.5), by="dana"))[0]
    assert "example-data" not in hit_to_signal(_metric(), hit)["detail"]
