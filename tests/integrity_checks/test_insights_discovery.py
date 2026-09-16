from pathlib import Path

import pytest
import yaml

from checks.insights_discovery import (
    check_id_collisions,
    check_orphan_hypothesis,
    check_orphan_opportunity,
    check_orphan_sources,
    check_promotion_status,
    check_stale_insights,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _write(tmp_path / "product-development/product/Insights/insights.csv",
        "insight_id,theme,user_intent,product_insight,status,first_seen,last_seen\n"
        "INS-001,trust,intent,implication,validated,2026-01-01,2026-01-01\n"
        "INS-002,trust,intent,implication,new,2026-01-01,2026-01-01\n")
    _write(tmp_path / "product-development/product/Insights/sources.csv",
        "source_id,insight_id,source_type,source_ref,date,evidence\n"
        "SRC-001,INS-001,customer-support,ticket-1,2026-01-01,quote\n")
    _write(tmp_path / "product-development/feature-index.yaml",
        yaml.safe_dump({"area": {"feature": {
            "opportunity": "product/PRDs/area/feature-opportunity.md",
            "hypothesis": "product/PRDs/area/feature-hypothesis.md",
        }}}))
    _write(tmp_path / "product-development/product/PRDs/area/feature-opportunity.md",
        "# OPP-AREA-001: title\n\n## Evidence\n\n- `INS-001` -- some reason\n")
    _write(tmp_path / "product-development/product/PRDs/area/feature-hypothesis.md",
        "# HYP-AREA-001\n\nstatement\n\n## Opportunity\n\nOPP-AREA-001\n")
    return tmp_path


def test_orphan_hypothesis_flags_missing_opportunity_section(repo: Path):
    _write(repo / "product-development/product/PRDs/area/other-hypothesis.md", "# HYP-AREA-002\n\nstatement\n")
    findings = check_orphan_hypothesis(repo, {})
    assert any(f.key == "HYP-AREA-002" for f in findings)


def test_orphan_hypothesis_flags_missing_evidence(repo: Path):
    _write(repo / "product-development/product/PRDs/area/other-opportunity.md",
        "# OPP-AREA-003: title\n\n## Evidence\n\nnone yet\n")
    _write(repo / "product-development/product/PRDs/area/other-hypothesis.md",
        "# HYP-AREA-003\n\nstatement\n\n## Opportunity\n\nOPP-AREA-003\n")
    findings = check_orphan_hypothesis(repo, {})
    assert any(f.key == "HYP-AREA-003" for f in findings)


def test_orphan_hypothesis_clean_chain_has_no_finding(repo: Path):
    findings = check_orphan_hypothesis(repo, {})
    assert not any(f.key == "HYP-AREA-001" for f in findings)


def test_orphan_sources_flags_unknown_insight_id(repo: Path):
    _write(repo / "product-development/product/Insights/sources.csv",
        "source_id,insight_id,source_type,source_ref,date,evidence\n"
        "SRC-002,INS-999,customer-support,ticket-2,2026-01-01,quote\n")
    findings = check_orphan_sources(repo, {})
    assert findings and findings[0].key == "SRC-002"


def test_promotion_status_flags_new_insight_cited_by_opportunity(repo: Path):
    _write(repo / "product-development/product/PRDs/area/feature-opportunity.md",
        "# OPP-AREA-001: title\n\n## Evidence\n\n- `INS-002` -- some reason\n")
    findings = check_promotion_status(repo, {})
    assert any(f.key == "INS-002" for f in findings)


def test_stale_insights_flags_old_new_insight(repo: Path):
    _write(repo / "product-development/product/Insights/insights.csv",
        "insight_id,theme,user_intent,product_insight,status,first_seen,last_seen\n"
        "INS-003,trust,intent,implication,new,2020-01-01,2020-01-01\n")
    findings = check_stale_insights(repo, {"stale-insight-days": 30})
    assert findings and findings[0].key == "INS-003"


def test_orphan_opportunity_flags_unwired_file(repo: Path):
    _write(repo / "product-development/product/PRDs/area/loose-opportunity.md", "# OPP-AREA-999: title\n\n## Evidence\n")
    findings = check_orphan_opportunity(repo, {})
    assert any("loose-opportunity.md" in f.file for f in findings)


def test_id_collisions_flags_duplicate_id(repo: Path):
    _write(repo / "product-development/product/PRDs/area/dup-opportunity.md", "# OPP-AREA-001: duplicate\n\n## Evidence\n")
    findings = check_id_collisions(repo, {})
    assert any(f.key == "OPP-AREA-001" for f in findings)
