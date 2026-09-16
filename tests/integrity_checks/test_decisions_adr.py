from pathlib import Path

from checks.decisions_adr import check_adr_numbering, check_decision_naming


def _write(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_decision_naming_flags_bad_filename(tmp_path: Path):
    _write(tmp_path / "product-development/product/strategy/q3-priorities-decision.md")
    findings = check_decision_naming(tmp_path, {})
    assert findings


def test_decision_naming_clean_for_valid_filename(tmp_path: Path):
    _write(tmp_path / "product-development/product/strategy/2026-04-01-q3-priorities-decision.md")
    assert check_decision_naming(tmp_path, {}) == []


def test_decision_naming_flags_top_level_archive(tmp_path: Path):
    _write(tmp_path / "product-development/decisions/2026-04-01-foo-decision.md")
    findings = check_decision_naming(tmp_path, {})
    assert any(f.key == "product-development/decisions" for f in findings)


def test_adr_numbering_flags_gap(tmp_path: Path):
    _write(tmp_path / "docs/adr/0001-first.md")
    _write(tmp_path / "docs/adr/0003-third.md")
    findings = check_adr_numbering(tmp_path, {})
    assert any(f.key == "0002" for f in findings)


def test_adr_numbering_flags_duplicate(tmp_path: Path):
    _write(tmp_path / "docs/adr/0001-first.md")
    _write(tmp_path / "docs/adr/0001-duplicate.md")
    findings = check_adr_numbering(tmp_path, {})
    assert any(f.key == "0001" for f in findings)


def test_adr_numbering_clean_for_sequential(tmp_path: Path):
    _write(tmp_path / "docs/adr/0001-first.md")
    _write(tmp_path / "docs/adr/0002-second.md")
    assert check_adr_numbering(tmp_path, {}) == []
