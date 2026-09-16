from datetime import date, timedelta
from pathlib import Path

from checks.process_health import (
    check_papercuts_digest,
    check_skillgaps_digest,
    check_stale_bug_investigations,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_stale_bug_investigation_flagged_when_incomplete_and_old(tmp_path: Path):
    old_date = (date.today() - timedelta(days=30)).isoformat()
    _write(tmp_path / "product-development/engineering/bug-investigations/area/bug-x/investigation-plan.md",
        "| Field | Value |\n|---|---|\n"
        f"| Run Date | {old_date} |\n| Status | In Progress |\n")
    findings = check_stale_bug_investigations(tmp_path, {"stale-bug-investigation-days": 14})
    assert findings


def test_stale_bug_investigation_clean_when_complete(tmp_path: Path):
    old_date = (date.today() - timedelta(days=30)).isoformat()
    _write(tmp_path / "product-development/engineering/bug-investigations/area/bug-x/investigation-plan.md",
        "| Field | Value |\n|---|---|\n"
        f"| Run Date | {old_date} |\n| Status | Complete |\n")
    assert check_stale_bug_investigations(tmp_path, {"stale-bug-investigation-days": 14}) == []


def test_papercuts_digest_flags_repeat_offender_tag(tmp_path: Path):
    _write(tmp_path / "PAPERCUTS.md",
        "## Log\n\n"
        "- **2026-01-01** [tooling] first thing. (minor, unresolved)\n"
        "- **2026-01-02** [tooling] second thing. (minor, unresolved)\n")
    findings = check_papercuts_digest(tmp_path, {})
    assert any(f.key == "tooling" for f in findings)


def test_papercuts_digest_clean_for_single_unresolved_tag(tmp_path: Path):
    _write(tmp_path / "PAPERCUTS.md",
        "## Log\n\n- **2026-01-01** [tooling] only one. (minor, unresolved)\n")
    assert check_papercuts_digest(tmp_path, {}) == []


def test_skillgaps_digest_flags_repeat_offender_area(tmp_path: Path):
    _write(tmp_path / "SKILL-GAPS.md",
        "## Log\n\n"
        "- **2026-01-01** [product] first recipe. (seen-1x, unresolved)\n"
        "- **2026-01-02** [product] second recipe. (seen-1x, unresolved)\n")
    findings = check_skillgaps_digest(tmp_path, {})
    assert any(f.key == "product" for f in findings)
