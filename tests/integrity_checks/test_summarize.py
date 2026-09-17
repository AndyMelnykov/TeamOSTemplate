from datetime import date
from pathlib import Path

from summarize import build_summary, main


def test_build_summary_reports_no_findings_when_empty():
    text = build_summary({"findings": {}}, date(2026, 1, 10))
    assert "No open findings." in text


def test_build_summary_includes_check_counts_and_oldest_finding():
    status = {"findings": {
        "chk-a::k1": {"check_id": "chk-a", "key": "k1", "message": "old one",
                      "file": "", "first_detected": "2026-01-01", "last_seen": "2026-01-10"},
        "chk-a::k2": {"check_id": "chk-a", "key": "k2", "message": "new one",
                      "file": "", "first_detected": "2026-01-09", "last_seen": "2026-01-10"},
    }}
    text = build_summary(status, date(2026, 1, 10))
    assert "chk-a | 2" in text
    assert "old one" in text
    lines = text.splitlines()
    old_line = next(l for l in lines if "old one" in l)
    new_line = next(l for l in lines if "new one" in l)
    assert lines.index(old_line) < lines.index(new_line)


def test_main_writes_summary_file(tmp_path: Path):
    status_path = tmp_path / "status.json"
    status_path.write_text('{"generated_at": "2026-01-10", "findings": {}}', encoding="utf-8")
    output_path = tmp_path / "summary.md"
    code = main(["--status", str(status_path), "--output", str(output_path)])
    assert code == 0
    assert output_path.exists()
    assert "No open findings." in output_path.read_text(encoding="utf-8")
