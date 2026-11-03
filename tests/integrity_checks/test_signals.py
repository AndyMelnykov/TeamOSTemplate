from pathlib import Path

import pytest
import yaml

from checks.signals import (
    check_id_collisions,
    check_invalid_row,
    check_orphan_hypothesis,
    check_unassigned_stale,
    check_unindexed_hypothesis,
    check_unknown_citation,
)

HEADER = "signal_id,date,source_type,source_ref,account,summary,detail,tags\n"
HYP = "product-development/product/PRDs/area/feature-hypothesis.md"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _write(tmp_path / "product-development/signals/signals.csv", HEADER
        + "SIG-001,2026-01-01,support,ticket-1,,first,,\n"
        + "SIG-002,2026-01-01,support,ticket-2,,second,,\n")
    _write(tmp_path / "product-development/feature-index.yaml",
        yaml.safe_dump({"area": {"feature": {"hypothesis": "product/PRDs/area/feature-hypothesis.md"}}}))
    _write(tmp_path / HYP, "# HYP-AREA-001: title\n\nstatement\n\n## Signals\n\n- `SIG-001` -- some reason\n")
    return tmp_path


def test_invalid_row_flags_bad_source_type(repo: Path):
    _write(repo / "product-development/signals/signals.csv", HEADER
        + "SIG-001,2026-01-01,bogus,ticket-1,,first,,\n")
    findings = check_invalid_row(repo, {})
    assert [f.key for f in findings] == ["SIG-001"] and "source_type" in findings[0].message


def test_invalid_row_flags_duplicate_signal_id(repo: Path):
    _write(repo / "product-development/signals/signals.csv", HEADER
        + "SIG-001,2026-01-01,support,a,,first,,\n"
        + "SIG-001,2026-01-01,support,b,,second,,\n")
    findings = check_invalid_row(repo, {})
    assert len(findings) == 1 and "duplicate" in findings[0].message


def test_invalid_row_keys_a_row_without_an_id_by_line(repo: Path):
    _write(repo / "product-development/signals/signals.csv", HEADER + ",2026-01-01,support,a,,first,,\n")
    assert [f.key for f in check_invalid_row(repo, {})] == ["line 2"]


def test_invalid_row_flags_unknown_account(repo: Path):
    _write(repo / "product-development/signals/signals.csv", HEADER
        + "SIG-001,2026-01-01,support,ticket-1,nope,first,,\n")
    findings = check_invalid_row(repo, {})
    assert [f.key for f in findings] == ["SIG-001"] and "account" in findings[0].message


def test_invalid_row_clean_store_has_no_finding(repo: Path):
    assert check_invalid_row(repo, {}) == []


def test_unknown_citation_names_hypothesis_and_signal(repo: Path):
    _write(repo / HYP, "# HYP-AREA-001: t\n\n## Signals\n\n- `SIG-001` -- ok\n- `SIG-999` -- missing\n")
    findings = check_unknown_citation(repo, {})
    assert [f.key for f in findings] == [f"{HYP}::SIG-999"]
    assert "SIG-999" in findings[0].message and "feature-hypothesis.md" in findings[0].message


def test_unknown_citation_clean_chain_has_no_finding(repo: Path):
    assert check_unknown_citation(repo, {}) == []


def test_orphan_hypothesis_flags_hypothesis_citing_no_signal(repo: Path):
    _write(repo / "product-development/product/PRDs/area/other-hypothesis.md", "# HYP-AREA-002\n\nstatement\n")
    findings = check_orphan_hypothesis(repo, {})
    assert [f.key for f in findings] == ["product-development/product/PRDs/area/other-hypothesis.md"]


def test_orphan_hypothesis_ignores_old_id_schemes(repo: Path):
    _write(repo / HYP, "# HYP-AREA-001\n\n## Signals\n\n- `INS-001` -- old scheme\n")
    assert [f.key for f in check_orphan_hypothesis(repo, {})] == [HYP]


def test_orphan_hypothesis_clean_chain_has_no_finding(repo: Path):
    assert check_orphan_hypothesis(repo, {}) == []


def test_unassigned_stale_flags_old_uncited_signal(repo: Path):
    findings = check_unassigned_stale(repo, {"unassigned-signal-days": 30})
    assert [f.key for f in findings] == ["SIG-002"]


def test_unassigned_stale_ignores_recent_signal(repo: Path):
    from datetime import date
    _write(repo / "product-development/signals/signals.csv", HEADER
        + f"SIG-002,{date.today().isoformat()},support,ticket-2,,second,,\n")
    assert check_unassigned_stale(repo, {"unassigned-signal-days": 30}) == []


def test_unindexed_hypothesis_flags_unwired_file(repo: Path):
    _write(repo / "product-development/product/PRDs/area/loose-hypothesis.md", "# HYP-AREA-999: title\n\n## Signals\n")
    findings = check_unindexed_hypothesis(repo, {})
    assert any("loose-hypothesis.md" in f.file for f in findings)


def test_id_collisions_flags_duplicate_id(repo: Path):
    _write(repo / "product-development/product/PRDs/area/dup-hypothesis.md", "# HYP-AREA-001: duplicate\n\n## Signals\n")
    assert any(f.key == "HYP-AREA-001" for f in check_id_collisions(repo, {}))
