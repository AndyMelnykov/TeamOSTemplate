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


# ---- Task 2: reports and the sweep -------------------------------------------------

import shutil

import analytics_sweep
from analytics_sweep import header_field, main, report_summary, scan_reports, sweep
from signals import load

FIXTURES = Path(__file__).parent / "fixtures" / "analytics"
REPORTS = {  # fixture -> where it lives in the analytics tree (one per header style)
    "experiment-table-bold.md": "experiments/billing/low-balance.md",           # | **Status** | X |
    "experiment-inline-bold.md": "experiments/deployment/one-click.md",          # **Status:** X
    "investigation-table-plain.md": "investigations/home-page/search-zero.md",   # | Status | X |
}
SNAPSHOTS = (  # ESR falls 95 -> 89.5 (-5.8%): misses the 92% target and trips the 5% change rule
    "2026-W43,all,95,2026-10-26T09:00:00Z,analyst\n"
    "2026-W44,all,89.5,2026-11-02T09:00:00Z,analyst\n"
)


def _repo_with_reports(tmp_path: Path, snapshots: str = SNAPSHOTS) -> Path:
    repo = _repo(tmp_path, snapshots={"esr.csv": snapshots} if snapshots else None)
    for fixture, dest in REPORTS.items():
        target = repo / "product-development/analytics" / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(FIXTURES / fixture, target)
    return repo


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_header_styles_and_status_filter(tmp_path):
    assert header_field(_read("experiment-table-bold.md"), "Status") == "Complete"
    assert header_field(_read("experiment-inline-bold.md"), "Status") == "Complete"
    assert header_field(_read("investigation-table-plain.md"), "Status") == "Complete"
    assert header_field(_read("experiment-table-bold.md"), "Experiment End") == "2026-03-19"
    assert header_field(_read("experiment-inline-bold.md"), "Date") == "2026-03-15"
    assert header_field(_read("investigation-table-plain.md"), "Run Date") == "2026-03-15"
    assert header_field(_read("experiment-table-bold.md"), "Nope") is None

    repo = _repo_with_reports(tmp_path)
    assert len(scan_reports(repo)) == 3
    path = repo / "product-development/analytics/experiments/billing/low-balance.md"
    path.write_text(path.read_text(encoding="utf-8").replace("| **Status** | Complete |", "| **Status** | In Progress |"), encoding="utf-8")
    refs = {r["source_ref"] for r in scan_reports(repo)}
    assert len(refs) == 2 and not any("low-balance" in r for r in refs)


def test_report_rows_are_valid_signals(tmp_path):
    rows = {Path(r["source_ref"]).name: r for r in scan_reports(_repo_with_reports(tmp_path))}
    experiment, investigation = rows["low-balance.md"], rows["search-zero.md"]
    for row in rows.values():
        assert validate(row) == [] and row["account"] == ""
        assert row["source_ref"].startswith("product-development/analytics/")
    assert experiment["source_type"] == "experiment" and experiment["tags"] == "billing"
    assert experiment["date"] == "2026-03-19"  # Experiment End beats the other date fields
    assert experiment["summary"].startswith("Showing a warning banner")
    assert investigation["source_type"] == "analytics" and investigation["tags"] == "investigation;home-page"
    assert investigation["date"] == "2026-03-15"


def test_summary_prefers_tldr_then_findings_then_question():
    tldr = "# T\n\n## Question\n\nQ text.\n\n## Findings\n\n**Bold finding.**\n\n## TL;DR\n\nFirst para line one\nline two.\n\nSecond para.\n"
    assert report_summary(tldr) == "First para line one line two."
    findings = "# T\n\n## Question\n\nQ text.\n\n## Key Findings\n\n| a | **b** |\n|---|---|\n| 1 | **2** |\n\n**Users churn 3x more.** More words.\n"
    assert report_summary(findings) == "Users churn 3x more."
    inline = "# T\n\n# Key Finding\n\n**35% drop off at DNS** (between steps).\n"
    assert report_summary(inline) == "35% drop off at DNS"
    question = "# T\n\n| Field | Value |\n|---|---|\n\n---\n\n## Question\n\nDo restorers abandon?\n\n## Findings\n\n| x | **y** |\n"
    assert report_summary(question) == "Do restorers abandon?"
    assert report_summary("# Investigation: Zero results\n\n## Method\n\nStuff.\n") == "Investigation: Zero results"


def test_summary_is_capped_at_300_characters():
    summary = report_summary("# T\n\n## TL;DR\n\n" + "word " * 200)
    assert len(summary) <= 300


def test_report_without_a_usable_date_is_reported_not_swept(tmp_path):
    repo = _repo_with_reports(tmp_path)
    path = repo / "product-development/analytics/experiments/billing/low-balance.md"
    path.write_text(path.read_text(encoding="utf-8").replace("2026-03-19", "TBD").replace("2026-03-05", "TBD"), encoding="utf-8")
    rows, problems = analytics_sweep.collect(repo)
    assert not any("low-balance" in r["source_ref"] for r in rows)
    assert any("low-balance" in p.file and "date" in p.message for p in problems)


def test_sweep_adds_metric_and_report_signals(tmp_path):
    repo = _repo_with_reports(tmp_path)
    result = sweep(repo)
    assert len(result.written) == 5 and result.skipped == 0 and result.invalid == {}
    by_type: dict[str, int] = {}
    for s in load(repo):
        by_type[s.source_type] = by_type.get(s.source_type, 0) + 1
    assert by_type == {"analytics": 3, "experiment": 2}  # 2 metric hits + 1 investigation; 2 experiments
    metric_rows = [s for s in load(repo) if s.source_ref.endswith("snapshots/esr.csv")]
    assert sorted(("fell" in s.summary, "missing target" in s.summary) for s in metric_rows) == [(False, True), (True, False)]


def test_sweep_is_idempotent(tmp_path):
    repo = _repo_with_reports(tmp_path)
    sweep(repo)
    before = (repo / "product-development/signals/signals.csv").read_text(encoding="utf-8")
    again = sweep(repo)
    assert again.written == [] and again.skipped == 5 and again.invalid == {}
    assert (repo / "product-development/signals/signals.csv").read_text(encoding="utf-8") == before


def test_dry_run_adds_nothing(tmp_path):
    repo = _repo_with_reports(tmp_path)
    result = sweep(repo, dry_run=True)
    assert len(result.written) == 5 and result.skipped == 0
    assert not (repo / "product-development/signals/signals.csv").exists()
    sweep(repo)
    assert sweep(repo, dry_run=True).written == []  # already-present rows count as existing


def test_main_prints_counts_and_exit_code(tmp_path, capsys):
    repo = _repo_with_reports(tmp_path)
    assert main(["--repo-root", str(repo), "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines()[-1] == "5 new, 0 existing, 0 invalid, 0 problems"
    assert "was 89.5%" in out  # dry run lists what it would add
    assert not (repo / "product-development/signals/signals.csv").exists()
    assert main(["--repo-root", str(repo)]) == 0
    assert capsys.readouterr().out.strip().splitlines()[-1] == "5 new, 0 existing, 0 invalid, 0 problems"
    assert main(["--repo-root", str(repo)]) == 0
    assert capsys.readouterr().out.strip().splitlines()[-1] == "0 new, 5 existing, 0 invalid, 0 problems"


def test_main_counts_problems_and_fails_on_invalid(tmp_path, capsys, monkeypatch):
    repo = _repo_with_reports(tmp_path, snapshots=SNAPSHOTS + "2026-W45,all,n/a,2026-11-09T09:00:00Z,analyst\n")
    assert main(["--repo-root", str(repo)]) == 0
    assert capsys.readouterr().out.strip().splitlines()[-1] == "5 new, 0 existing, 0 invalid, 1 problems"
    monkeypatch.setattr(analytics_sweep, "collect", lambda root: ([{"date": "bad", "source_type": "analytics", "source_ref": "x", "summary": "s"}], []))
    assert main(["--repo-root", str(repo)]) == 1
