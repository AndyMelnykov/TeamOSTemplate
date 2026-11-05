from pathlib import Path

from hypotheses import hypothesis_files, instrumented_metrics, main, parse, reach, recommend
from signals import Signal

HEADER_FIELDS = {
    "Status": "proposed",
    "Confidence": "?",
    "Effort": "?",
    "Validation path": "",
    "Target metric": "Extraction Success Rate (ESR)",
    "Owner": "",
    "Last Updated": "2026-11-01",
    "PRD": "",
}


def _text(sections=("Problem", "Signals"), body="- `SIG-001` -- a\n- `SIG-002` -- b", **fields) -> str:
    values = {**HEADER_FIELDS, **fields}
    table = "\n".join(f"| **{k}** | {v} |" for k, v in values.items())
    parts = [f"# HYP-EXTRACT-001: Users cannot tell\n\n| Field | Value |\n|---|---|\n{table}\n"]
    for name in sections:
        parts.append(f"## {name}\n\n{body if name == 'Signals' else 'text'}\n")
    return "\n".join(parts)


def _write(tmp_path: Path, text: str, name="x-hypothesis.md") -> Path:
    path = tmp_path / "product-development/product/PRDs/area" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _sig(signal_id: str, account: str = "") -> Signal:
    return Signal(signal_id, "2026-01-01", "support", "T-1", account, "s", "", "")


def _hyp(tmp_path, **kw):
    return parse(_write(tmp_path, _text(**kw)))


def test_parse_example(tmp_path):
    path = _write(tmp_path, _text(
        sections=("Problem", "Signals", "Test", "Success criteria"),
        Status="testing", Confidence="medium", Effort="cheap", **{"Validation path": "prototype"},
        Owner="alexrivera", PRD="",
    ))
    h = parse(path)
    assert (h.hyp_id, h.status, h.confidence, h.effort) == ("HYP-EXTRACT-001", "testing", "medium", "cheap")
    assert (h.validation_path, h.target_metric, h.last_updated) == (
        "prototype", "Extraction Success Rate (ESR)", "2026-11-01")
    assert h.signal_ids == ["SIG-001", "SIG-002"]
    assert h.sections >= {"Problem", "Signals", "Test", "Success criteria"}
    assert h.missing == []
    assert hypothesis_files(tmp_path) == [path]


def test_proposed_needs_only_problem_and_signals(tmp_path):
    h = _hyp(tmp_path)  # no Test, no Success criteria, Confidence/Effort are "?"
    assert h.status == "proposed"
    assert h.missing == []


def test_testing_requires_test_and_criteria(tmp_path):
    h = _hyp(tmp_path, Status="testing", Confidence="low", Effort="cheap")
    assert "section: Test" in h.missing
    assert "section: Success criteria" in h.missing
    assert "field: Validation path" in h.missing


def test_missing_section_at_proposed(tmp_path):
    h = _hyp(tmp_path, sections=("Problem",))
    assert h.missing == ["section: Signals"]


def test_reach_counts_signals_and_distinct_accounts(tmp_path):
    h = _hyp(tmp_path, body="`SIG-001` `SIG-002` `SIG-003` `SIG-009`")
    signals = {
        "SIG-001": _sig("SIG-001", "acme"),
        "SIG-002": _sig("SIG-002", "acme"),
        "SIG-003": _sig("SIG-003", ""),
    }
    assert reach(h, signals) == (3, 1)  # SIG-009 is not in the store; no-account signals add none


def _repo_with_metrics(tmp_path: Path) -> Path:
    ref = tmp_path / "reference/metrics.md"
    ref.parent.mkdir(parents=True)
    ref.write_text(
        "| Metric | Definition | Target |\n|---|---|---|\n"
        "| **Extraction Success Rate (ESR)** | x | > 92% |\n"
        "| **User Retention (D7)** | y | > 45% |\n", encoding="utf-8")
    doc = tmp_path / "product-development/analytics/metrics/billing/credit.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# Credit\n\n### Credit Utilization Rate\n\ntext\n", encoding="utf-8")
    return tmp_path


def test_metric_abbreviation_counts_as_instrumented(tmp_path):
    instrumented = instrumented_metrics(_repo_with_metrics(tmp_path))
    assert {"esr", "extraction success rate", "credit utilization rate"} <= instrumented
    for metric in ("ESR", "Extraction Success Rate (ESR)"):
        h = _hyp(tmp_path, Effort="cheap", **{"Target metric": metric})
        assert recommend(h, instrumented)[0] == "ab-test"


def test_cheap_and_instrumented_recommends_ab_test(tmp_path):
    instrumented = instrumented_metrics(_repo_with_metrics(tmp_path))
    path, reason = recommend(_hyp(tmp_path, Effort="cheap"), instrumented)
    assert path == "ab-test"
    assert reason


def test_costly_recommends_prototype_with_alternatives(tmp_path):
    instrumented = instrumented_metrics(_repo_with_metrics(tmp_path))
    path, reason = recommend(_hyp(tmp_path, Effort="costly"), instrumented)
    assert path == "prototype"
    assert "survey" in reason and "interviews" in reason


def test_uninstrumented_metric_never_recommends_ab_test(tmp_path):
    instrumented = instrumented_metrics(_repo_with_metrics(tmp_path))
    h = _hyp(tmp_path, Effort="cheap", **{"Target metric": "Delight Index"})
    path, reason = recommend(h, instrumented)
    assert path == "prototype"
    assert "instrumented" in reason


def test_question_mark_effort_has_no_recommendation(tmp_path):
    instrumented = instrumented_metrics(_repo_with_metrics(tmp_path))
    path, reason = recommend(_hyp(tmp_path, Effort="?"), instrumented)
    assert path == ""
    assert "effort" in reason.lower()


def test_list_prints_reach_and_recommendation(tmp_path, capsys):
    repo = _repo_with_metrics(tmp_path)
    _write(repo, _text(Effort="cheap"))
    (repo / "product-development/signals").mkdir(parents=True)
    (repo / "product-development/signals/signals.csv").write_text(
        "signal_id,date,source_type,source_ref,account,summary,detail,tags\n"
        "SIG-001,2026-01-01,support,T-1,acme,s,,\nSIG-002,2026-01-01,support,T-2,acme,s2,,\n",
        encoding="utf-8")
    assert main(["list", "--repo-root", str(repo)]) == 0
    row = next(line for line in capsys.readouterr().out.splitlines() if "HYP-EXTRACT-001" in line)
    assert "proposed" in row and "ab-test" in row
    assert row.split()[2:4] == ["2", "1"]  # signals, accounts
