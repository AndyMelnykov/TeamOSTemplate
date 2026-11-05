from datetime import date, timedelta
from pathlib import Path

import pytest

from checks.hypotheses import CHECKS, check_invalid_values, check_missing_fields, check_stale_testing

HYP = "product-development/product/PRDs/area/feature-hypothesis.md"

FIELDS = {
    "Status": "proposed",
    "Confidence": "?",
    "Effort": "?",
    "Validation path": "",
    "Target metric": "Extraction Success Rate (ESR)",
    "Owner": "",
    "Last Updated": "2026-11-01",
    "PRD": "",
}


def _text(sections=("Problem", "Signals"), **fields) -> str:
    values = {**FIELDS, **fields}
    table = "\n".join(f"| **{k}** | {v} |" for k, v in values.items())
    parts = [f"# HYP-AREA-001: title\n\n| Field | Value |\n|---|---|\n{table}\n"]
    parts += [f"## {name}\n\ntext `SIG-001`\n" for name in sections]
    return "\n".join(parts)


TESTING = dict(Status="testing", Confidence="medium", Effort="costly", **{"Validation path": "prototype"})
ALL_SECTIONS = ("Problem", "Signals", "Test", "Success criteria")


def _write(repo: Path, text: str, rel: str = HYP) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _write(tmp_path, _text())
    return tmp_path


def test_checks_are_registered_under_their_ids():
    assert set(CHECKS) == {"hyp-missing-fields", "hyp-invalid-values", "hyp-stale-testing"}


# --- Review Focus 1 and 2 -------------------------------------------------------------

def test_proposed_without_test_is_valid(repo: Path):
    assert check_missing_fields(repo, {}) == []
    assert check_invalid_values(repo, {}) == []


def test_testing_without_test_section_names_the_missing_section(repo: Path):
    _write(repo, _text(sections=("Problem", "Signals", "Success criteria"), **TESTING))
    findings = check_missing_fields(repo, {})
    assert [f.key for f in findings] == ["HYP-AREA-001"]
    assert findings[0].check_id == "hyp-missing-fields"
    assert "section: Test" in findings[0].message and "Success criteria" not in findings[0].message
    assert findings[0].file == HYP


def test_missing_fields_reports_a_missing_header_field(repo: Path):
    text = _text().replace("| **Target metric** | Extraction Success Rate (ESR) |\n", "")
    _write(repo, text)
    findings = check_missing_fields(repo, {})
    assert len(findings) == 1 and "field: Target metric" in findings[0].message


def test_missing_fields_clean_testing_hypothesis_has_no_finding(repo: Path):
    _write(repo, _text(sections=ALL_SECTIONS, **TESTING))
    assert check_missing_fields(repo, {}) == []


def test_missing_fields_keys_a_file_without_an_id_by_path(repo: Path):
    _write(repo, "no title here\n")
    assert [f.key for f in check_missing_fields(repo, {})] == [HYP]


# --- hyp-invalid-values ---------------------------------------------------------------

def test_question_mark_confidence_at_testing_is_invalid(repo: Path):
    _write(repo, _text(sections=ALL_SECTIONS, **{**TESTING, "Confidence": "?"}))
    findings = check_invalid_values(repo, {})
    assert [f.key for f in findings] == ["HYP-AREA-001"]
    assert findings[0].check_id == "hyp-invalid-values" and "Confidence" in findings[0].message


def test_question_mark_effort_at_testing_is_invalid(repo: Path):
    _write(repo, _text(sections=ALL_SECTIONS, **{**TESTING, "Effort": "?"}))
    assert "Effort" in check_invalid_values(repo, {})[0].message


def test_question_mark_is_allowed_at_proposed(repo: Path):
    _write(repo, _text(Confidence="?", Effort="?"))
    assert check_invalid_values(repo, {}) == []


@pytest.mark.parametrize("field,value", [
    ("Status", "done"),
    ("Confidence", "certain"),
    ("Effort", "huge"),
    ("Validation path", "vibes"),
])
def test_unknown_value_is_invalid(repo: Path, field: str, value: str):
    _write(repo, _text(sections=ALL_SECTIONS, **{**TESTING, field: value}))
    findings = check_invalid_values(repo, {})
    assert len(findings) == 1 and field in findings[0].message and value in findings[0].message


def test_empty_values_are_missing_fields_not_invalid_values(repo: Path):
    _write(repo, _text(Confidence=""))
    assert check_invalid_values(repo, {}) == []
    assert "field: Confidence" in check_missing_fields(repo, {})[0].message


def test_valid_testing_hypothesis_has_no_invalid_values(repo: Path):
    _write(repo, _text(sections=ALL_SECTIONS, **TESTING))
    assert check_invalid_values(repo, {}) == []


# --- hyp-stale-testing ----------------------------------------------------------------

def _ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def test_stale_testing_flags_old_testing_hypothesis(repo: Path):
    _write(repo, _text(sections=ALL_SECTIONS, **{**TESTING, "Last Updated": _ago(45)}))
    findings = check_stale_testing(repo, {"stale-testing-days": 30})
    assert [f.key for f in findings] == ["HYP-AREA-001"]
    assert findings[0].check_id == "hyp-stale-testing" and "45d" in findings[0].message


def test_stale_testing_ignores_recently_updated(repo: Path):
    _write(repo, _text(sections=ALL_SECTIONS, **{**TESTING, "Last Updated": _ago(5)}))
    assert check_stale_testing(repo, {"stale-testing-days": 30}) == []


def test_stale_testing_ignores_other_statuses(repo: Path):
    _write(repo, _text(**{"Last Updated": _ago(400)}))
    assert check_stale_testing(repo, {"stale-testing-days": 30}) == []


def test_stale_testing_defaults_to_30_days(repo: Path):
    _write(repo, _text(sections=ALL_SECTIONS, **{**TESTING, "Last Updated": _ago(31)}))
    assert len(check_stale_testing(repo, {})) == 1


def test_stale_testing_skips_an_unreadable_date(repo: Path):
    _write(repo, _text(sections=ALL_SECTIONS, **{**TESTING, "Last Updated": "soon"}))
    assert check_stale_testing(repo, {}) == []
