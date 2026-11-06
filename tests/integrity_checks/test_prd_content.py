from datetime import date, timedelta
from pathlib import Path

import pytest

from checks.prd_content import (
    check_acceptance_criteria,
    check_execution_path,
    check_missing_sections,
    check_sources_citation_validity,
    check_stale_status,
    check_strategy_review_decision_gate,
    parse_table,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


FULL_SECTIONS = (
    "## Overview\nx\n\n## User Stories\nx\n\n## Requirements\nx\n\n## Acceptance Criteria\nx\n\n"
    "## Design\nx\n\n## Technical Considerations\nx\n\n## Launch Plan\nx\n\n## Sources\nx\n"
)


def _header(status: str, tier: str, last_updated: str, path: str = "") -> str:
    extra = f"| **Execution Path** | {path} |\n" if path else ""
    return (
        "| Field | Value |\n|---|---|\n"
        f"| **Status** | {status} |\n| **Review Tier** | {tier} |\n| **Last Updated** | {last_updated} |\n"
        f"{extra}\n"
    )


AC_HEADER = "| ID | Given | When | Then | Covers | Verify by |\n|----|-------|------|------|--------|-----------|\n"


def _prd_body(p0_ids=("P0-1", "P0-2"), ac_rows=None) -> str:
    """A PRD body with a Requirements section and an Acceptance Criteria table."""
    if ac_rows is None:
        ac_rows = [
            "| AC-1 | g | w | t | P0-1, Story 1 | automated-test |",
            "| AC-2 | g | w | t | P0-2 | manual-qa |",
        ]
    reqs = "".join(f"| {i} | does {i} |\n" for i in p0_ids)
    return (
        "## Overview\nx\n\n## User Stories\nStory 1\n\n"
        "## Requirements\n\n### Must Have (P0)\n\n| ID | Requirement |\n|----|-------------|\n" + reqs +
        "\n### Should Have (P1)\n\n| ID | Requirement |\n|----|-------------|\n| P1-1 | optional |\n\n"
        "## Acceptance Criteria\n\n" + AC_HEADER + "\n".join(ac_rows) + "\n\n"
        "## Design\nx\n\n## Technical Considerations\nx\n\n## Launch Plan\nx\n\n## Sources\nx\n"
    )


def _write_prd(repo: Path, status: str, body: str, tier: str = "Local", path: str = "") -> None:
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header(status, tier, "2026-01-01", path) + body)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _write(tmp_path / "product-development/signals/signals.csv",
        "signal_id,date,source_type,source_ref,account,summary,detail,tags\n"
        "SIG-001,2026-01-01,support,ticket-1,,first,,\n")
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


def _prd_with_sources(repo: Path, sources: str) -> None:
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header("Draft", "Local", "2026-01-01") + f"## Overview\nx\n\n## Sources\n\n{sources}\n")


def test_sources_citation_validity_flags_unknown_id(repo: Path):
    _prd_with_sources(repo, "- SIG-999")
    findings = check_sources_citation_validity(repo, {})
    assert findings and "SIG-999" in findings[0].key


def test_sources_citation_validity_accepts_existing_signal(repo: Path):
    _prd_with_sources(repo, "- SIG-001")
    assert check_sources_citation_validity(repo, {}) == []


@pytest.mark.parametrize("leftover", ["INS-001", "SRC-001"])
def test_sources_citation_validity_rejects_leftover_old_ids(repo: Path, leftover: str):
    _prd_with_sources(repo, f"- {leftover}")
    findings = check_sources_citation_validity(repo, {})
    assert findings and leftover in findings[0].key


def test_stale_status_flags_old_draft(repo: Path):
    old_date = (date.today() - timedelta(days=100)).isoformat()
    _write(repo / "product-development/product/PRDs/area/feature-prd.md",
        _header("Draft", "Local", old_date) + FULL_SECTIONS)
    findings = check_stale_status(repo, {"stale-prd-status-days": 21})
    assert findings


# --- acceptance criteria -----------------------------------------------------


def test_parse_table_splits_on_unescaped_pipes_only():
    rows = parse_table("| ID | Then |\n|----|------|\n| AC-1 | a \\| b |\n")
    assert rows == [{"ID": "AC-1", "Then": "a | b"}]


def test_missing_ac_section_is_a_missing_section(repo: Path):
    body = _prd_body().replace("## Acceptance Criteria", "## Something Else")
    _write_prd(repo, "Draft", body)
    findings = check_missing_sections(repo, {})
    assert findings and "Acceptance Criteria" in findings[0].message


def test_draft_prds_skip_row_checks(repo: Path):
    _write_prd(repo, "Draft", _prd_body(ac_rows=["| AC-1 | g | w |  | P0-1 | eyeball |"]),
        path="agent-direct", tier="Strategy Review")
    assert check_acceptance_criteria(repo, {}) == []
    assert check_execution_path(repo, {}) == []


def test_bad_rows_are_reported(repo: Path):
    rows = [
        "| AC-1 | g | w | t | P0-1 | automated-test |",
        "| AC-2 | g | w |  | P0-2 | automated-test |",      # empty Then
        "| AC-3 | g | w | t | P0-2 | eyeball |",             # invalid Verify by
        "| AC-2 | g | w | t | P0-2 | manual-qa |",           # duplicate id
    ]
    _write_prd(repo, "In Review", _prd_body(ac_rows=rows))
    findings = check_acceptance_criteria(repo, {})
    assert len(findings) == 3
    assert len({f.key for f in findings}) == 3
    messages = " ".join(f.message for f in findings)
    assert "AC-2" in messages and "AC-3" in messages
    assert any("Then" in f.message for f in findings)
    assert any("eyeball" in f.message for f in findings)
    assert any("duplicate" in f.message.lower() for f in findings)


def test_uncovered_p0_is_reported(repo: Path):
    rows = ["| AC-1 | g | w | t | P0-1 | automated-test |"]
    _write_prd(repo, "In Review", _prd_body(ac_rows=rows))
    findings = check_acceptance_criteria(repo, {})
    assert [f.key for f in findings] == ["product-development/product/PRDs/area/feature-prd.md::uncovered::P0-2"]
    assert "P0-2" in findings[0].message


def test_escaped_pipe_in_cell(repo: Path):
    rows = [
        "| AC-1 | g | They pick a \\| b | t | P0-1, Story 1 | automated-test |",
        "| AC-2 | g | w | t | P0-2 | manual-qa |",
    ]
    _write_prd(repo, "In Review", _prd_body(ac_rows=rows))
    assert check_acceptance_criteria(repo, {}) == []


def test_agent_direct_with_strategy_review_is_reported(repo: Path):
    _write_prd(repo, "In Review", _prd_body(), tier="Strategy Review", path="agent-direct")
    findings = check_execution_path(repo, {})
    assert len(findings) == 1 and "Strategy Review" in findings[0].message


def test_agent_direct_with_analytics_criterion_is_reported(repo: Path):
    rows = [
        "| AC-1 | g | w | t | P0-1, Story 1 | analytics |",
        "| AC-2 | g | w | t | P0-2 | manual-qa |",
    ]
    _write_prd(repo, "Approved", _prd_body(ac_rows=rows), path="agent-direct")
    findings = check_execution_path(repo, {})
    assert len(findings) == 1 and "analytics" in findings[0].message


def test_invalid_execution_path_value_is_reported(repo: Path):
    _write_prd(repo, "In Review", _prd_body(), path="whenever")
    findings = check_execution_path(repo, {})
    assert len(findings) == 1 and "whenever" in findings[0].message


def test_clean_in_review_prd_has_no_findings(repo: Path):
    _write_prd(repo, "In Review", _prd_body(), path="agent-direct")
    assert check_acceptance_criteria(repo, {}) == []
    assert check_execution_path(repo, {}) == []
