from pathlib import Path

from checks.analytics_watch import CHECKS, check_unswept_reports, check_watch_invalid
from run_checks import CHECK_MODULES, discover_checks
from signals import add

REFERENCE = """# Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Extraction Success Rate (ESR)** | Runs that extract all fields | > 92% |
"""

WATCH = """metrics:
  - id: esr
    name: Extraction Success Rate (ESR)
    unit: "%"
    cadence: weekly
    target_source: reference
    snapshot: analytics/snapshots/esr.csv
    rules:
      - type: below-target
"""

GOOD_SNAPSHOT = (
    "period,segment,value,captured_at,captured_by\n"
    "2026-W43,all,93,2026-10-26T09:00:00Z,analyst\n"
    "2026-W44,all,92.5,2026-11-02T09:00:00Z,analyst\n"
)

REPORT = """# Low balance banner

| **Status** | {status} |
| **Experiment End** | 2026-03-19 |

## TL;DR

The banner lifted upgrades.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")


def _repo(tmp_path: Path, watch: str = WATCH, snapshot: str | None = GOOD_SNAPSHOT) -> Path:
    _write(tmp_path / "reference/metrics.md", REFERENCE)
    _write(tmp_path / "product-development/analytics/metric-watch.yaml", watch)
    if snapshot is not None:
        _write(tmp_path / "product-development/analytics/snapshots/esr.csv", snapshot)
    return tmp_path


def _report(repo: Path, status: str = "Complete", name: str = "experiments/billing/low-balance.md") -> str:
    _write(repo / "product-development/analytics" / name, REPORT.format(status=status))
    return f"product-development/analytics/{name}"


# ---- analytics-watch-invalid ---------------------------------------------------

def test_valid_watch_has_no_findings(tmp_path):
    assert check_watch_invalid(_repo(tmp_path), {}) == []


def test_bad_snapshot_value_is_a_finding_keyed_by_file_and_line(tmp_path):
    snapshot = GOOD_SNAPSHOT + "2026-W45,all,n/a,2026-11-09T09:00:00Z,analyst\n"
    findings = check_watch_invalid(_repo(tmp_path, snapshot=snapshot), {})
    assert [f.key for f in findings] == ["product-development/analytics/snapshots/esr.csv:4"]
    assert findings[0].check_id == "analytics-watch-invalid"
    assert "not a plain number" in findings[0].message
    assert findings[0].file == "product-development/analytics/snapshots/esr.csv"


def test_invalid_watch_entry_is_a_finding_at_its_line(tmp_path):
    watch = WATCH.replace("cadence: weekly", "cadence: daily")
    findings = check_watch_invalid(_repo(tmp_path, watch=watch), {})
    assert [f.key for f in findings] == ["product-development/analytics/metric-watch.yaml:2"]
    assert "cadence" in findings[0].message


def test_problems_on_the_same_line_are_one_finding(tmp_path):
    watch = WATCH.replace("cadence: weekly", "cadence: daily").replace("    unit: \"%\"\n", "")
    findings = check_watch_invalid(_repo(tmp_path, watch=watch), {})
    assert len(findings) == 1
    assert "cadence" in findings[0].message and "unit" in findings[0].message


def test_missing_snapshot_file_is_a_finding_at_the_entry(tmp_path):
    findings = check_watch_invalid(_repo(tmp_path, snapshot=None), {})
    assert [f.key for f in findings] == ["product-development/analytics/metric-watch.yaml:2"]
    assert "analytics/snapshots/esr.csv" in findings[0].message and "not found" in findings[0].message


def test_missing_watch_file_is_a_finding(tmp_path):
    findings = check_watch_invalid(tmp_path, {})
    assert [f.key for f in findings] == ["product-development/analytics/metric-watch.yaml:1"]


def test_one_bad_metric_does_not_hide_another(tmp_path):
    second = WATCH.replace("metrics:\n", "").replace("esr", "ttp").replace("weekly", "yearly")
    findings = check_watch_invalid(_repo(tmp_path, watch=WATCH + second), {})
    assert [f.key for f in findings] == ["product-development/analytics/metric-watch.yaml:10"]
    assert "cadence" in findings[0].message


# ---- analytics-unswept-reports -------------------------------------------------

def test_complete_report_without_a_signal_is_a_finding(tmp_path):
    repo = _repo(tmp_path)
    ref = _report(repo)
    findings = check_unswept_reports(repo, {})
    assert [(f.check_id, f.key, f.file) for f in findings] == [("analytics-unswept-reports", ref, ref)]


def test_swept_report_is_clean(tmp_path):
    repo = _repo(tmp_path)
    ref = _report(repo)
    add(repo, [{"date": "2026-03-19", "source_type": "experiment", "source_ref": ref,
                "account": "", "summary": "The banner lifted upgrades.", "detail": "", "tags": "billing"}])
    assert check_unswept_reports(repo, {}) == []


def test_in_progress_report_is_not_expected_to_be_swept(tmp_path):
    repo = _repo(tmp_path)
    _report(repo, status="In Progress")
    assert check_unswept_reports(repo, {}) == []


def test_complete_report_with_no_usable_date_is_a_finding(tmp_path):
    repo = _repo(tmp_path)
    ref = _report(repo)
    path = repo / ref
    path.write_text(path.read_text(encoding="utf-8").replace("| **Experiment End** | 2026-03-19 |\n", ""), encoding="utf-8")
    assert [f.key for f in check_unswept_reports(repo, {})] == [ref]


# ---- registration --------------------------------------------------------------

def test_checks_are_registered():
    assert set(CHECKS) == {"analytics-watch-invalid", "analytics-unswept-reports"}
    assert set(CHECKS) <= set(discover_checks(CHECK_MODULES))
