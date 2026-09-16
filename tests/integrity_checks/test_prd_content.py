from datetime import date, timedelta
from pathlib import Path

import pytest

from checks.prd_content import (
    check_missing_sections,
    check_sources_citation_validity,
    check_stale_status,
    check_strategy_review_decision_gate,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


FULL_SECTIONS = (
    "## Overview\nx\n\n## User Stories\nx\n\n## Requirements\nx\n\n## Design\nx\n\n"
    "## Technical Considerations\nx\n\n## Launch Plan\nx\n\n## Sources\nx\n"
)


def _header(status: str, tier: str, last_updated: str) -> str:
    return (
        "| Field | Value |\n|---|---|\n"
        f"| **Status** | {status} |\n| **Review Tier** | {tier} |\n| **Last Updated** | {last_updated} |\n\n"
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _write(tmp_path / "product-development/product/Insights/insights.csv",
        "insight_id,theme,user_intent,product_insight,status,first_seen,last_seen\n"
        "INS-001,trust,intent,implication,validated,2026-01-01,2026-01-01\n")
    _write(tmp_path / "product-development/product/Insights/sources.csv",
        "source_id,insight_id,source_type,source_ref,date,evidence\n")
    return tmp_path


def test_missing_sections_flags_incomplete_prd(repo: Path):
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header("Draft", "Local", "2026-01-01") + "## Overview\nx\n")
    findings = check_missing_sections(repo, {})
    assert findings and "Sources" in findings[0].message


def test_missing_sections_clean_when_all_present(repo: Path):
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header("Draft", "Local", "2026-01-01") + FULL_SECTIONS)
    assert check_missing_sections(repo, {}) == []


def test_strategy_review_gate_flags_approved_prd_without_decision(repo: Path):
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header("Approved", "Strategy Review", "2026-01-01") + FULL_SECTIONS)
    findings = check_strategy_review_decision_gate(repo, {})
    assert findings


def test_strategy_review_gate_clean_when_decision_file_links_back(repo: Path):
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header("Approved", "Strategy Review", "2026-01-01") + FULL_SECTIONS)
    _write(repo / "product-development/product/strategy/2026-01-05-feature-decision.md",
        "Resolves feature-prd.md.\n")
    assert check_strategy_review_decision_gate(repo, {}) == []


def test_sources_citation_validity_flags_unknown_id(repo: Path):
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header("Draft", "Local", "2026-01-01") +
        "## Overview\nx\n\n## Sources\n\n- INS-999\n")
    findings = check_sources_citation_validity(repo, {})
    assert findings and "INS-999" in findings[0].key


def test_stale_status_flags_old_draft(repo: Path):
    old_date = (date.today() - timedelta(days=100)).isoformat()
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header("Draft", "Local", old_date) + FULL_SECTIONS)
    findings = check_stale_status(repo, {"stale-prd-status-days": 21})
    assert findings
