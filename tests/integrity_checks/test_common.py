from datetime import date
from pathlib import Path

from common import Finding, days_open, load_config, load_status, merge_findings, write_status


def test_merge_findings_keeps_first_detected_for_repeated_key():
    previous = {
        "chk::a": {"check_id": "chk", "key": "a", "message": "old", "file": "",
                   "first_detected": "2026-01-01", "last_seen": "2026-01-01"}
    }
    current = [Finding("chk", "a", "new message", "")]
    merged = merge_findings(previous, current, date(2026, 1, 10))
    assert merged["chk::a"]["first_detected"] == "2026-01-01"
    assert merged["chk::a"]["last_seen"] == "2026-01-10"
    assert merged["chk::a"]["message"] == "new message"


def test_merge_findings_sets_first_detected_for_new_key():
    merged = merge_findings({}, [Finding("chk", "b", "msg", "")], date(2026, 1, 10))
    assert merged["chk::b"]["first_detected"] == "2026-01-10"


def test_merge_findings_drops_resolved_keys():
    previous = {
        "chk::a": {"check_id": "chk", "key": "a", "message": "old", "file": "",
                   "first_detected": "2026-01-01", "last_seen": "2026-01-01"}
    }
    assert merge_findings(previous, [], date(2026, 1, 10)) == {}


def test_days_open():
    assert days_open({"first_detected": "2026-01-01"}, date(2026, 1, 11)) == 10


def test_write_and_load_status_roundtrip(tmp_path: Path):
    status_path = tmp_path / "reports" / "status.json"
    write_status(status_path, {"generated_at": "2026-01-10", "findings": {}})
    assert load_status(status_path)["generated_at"] == "2026-01-10"


def test_load_status_missing_file_returns_empty(tmp_path: Path):
    assert load_status(tmp_path / "missing.json") == {"generated_at": None, "findings": {}}


def test_load_config(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("checks:\n  demo: true\nthresholds:\n  x: 5\n", encoding="utf-8")
    config = load_config(config_path)
    assert config["checks"]["demo"] is True
    assert config["thresholds"]["x"] == 5
