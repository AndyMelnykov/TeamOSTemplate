from pathlib import Path

from migrate_insights import MigrationReport, migrate, rewrite_citations
from signals import load

INSIGHTS = "product-development/product/Insights"
INSIGHTS_HEADER = "insight_id,theme,user_intent,product_insight,status,first_seen,last_seen\n"
SOURCES_HEADER = "source_id,insight_id,source_type,source_ref,date,evidence\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")


def _repo(tmp_path: Path, sources: str | None = None) -> Path:
    _write(tmp_path / INSIGHTS / "insights.csv", INSIGHTS_HEADER
           + "INS-001,trust,intent,The implication,new,2026-01-01,2026-01-01\n"
           + "INS-002,cost,intent,Another implication,validated,2026-01-02,2026-01-02\n")
    _write(tmp_path / INSIGHTS / "sources.csv", SOURCES_HEADER + (sources or (
        'SRC-001,INS-001,customer-research-reddit,"r/x - thread one",2026-01-01,"first quote"\n'
        'SRC-002,INS-002,customer-support,TCK-9,2026-01-02,"second quote"\n')))
    _write(tmp_path / "product-development/signals/signals.csv",
           "signal_id,date,source_type,source_ref,account,summary,detail,tags\n")
    return tmp_path


def test_rewrite_citations():
    mapping = {"INS-002": "SIG-002", "SRC-014": "SIG-031"}
    assert rewrite_citations("`INS-002` and SRC-014", mapping) == "`SIG-002` and SIG-031"


def test_rewrite_citations_leaves_unmapped_and_longer_ids_alone():
    mapping = {"INS-002": "SIG-002"}
    text = "INS-999, INS-2026-0001, XINS-002, INS-###"
    assert rewrite_citations(text, mapping) == text


def test_migration_maps_rows(tmp_path):
    repo = _repo(tmp_path)
    report = migrate(repo)
    assert isinstance(report, MigrationReport) and report.signals == 2
    first, second = load(repo)
    assert (first.signal_id, first.date, first.source_ref) == ("SIG-001", "2026-01-01", "r/x - thread one")
    assert first.summary == "first quote" and first.tags == "trust" and first.detail == "The implication"
    assert second.signal_id == "SIG-002" and second.tags == "cost"


def test_reddit_rows_become_community(tmp_path):
    repo = _repo(tmp_path)
    migrate(repo)
    first, second = load(repo)
    assert first.source_type == "community"
    assert second.source_type == "support"


def test_unknown_source_type_becomes_other(tmp_path):
    repo = _repo(tmp_path, 'SRC-001,INS-001,sales-call,ref,2026-01-01,"q"\n'
                           'SRC-002,INS-002,market,ref2,2026-01-02,"q2"\n')
    migrate(repo)
    assert [s.source_type for s in load(repo)] == ["other", "market"]


def test_long_evidence_is_truncated_and_kept_in_detail(tmp_path):
    evidence = "e" * 450
    repo = _repo(tmp_path, f'SRC-001,INS-001,customer-research-reddit,ref,2026-01-01,"{evidence}"\n'
                           'SRC-002,INS-002,customer-research-reddit,ref2,2026-01-02,"short"\n')
    migrate(repo)
    first = load(repo)[0]
    assert first.summary == evidence[:300]
    assert first.detail.startswith("The implication") and evidence in first.detail


def test_citations_are_rewritten_in_tracked_text_files(tmp_path):
    repo = _repo(tmp_path)
    _write(repo / "product-development/product/PRDs/a-hypothesis.md", "- `INS-002` -- why; evidence SRC-001\n")
    _write(repo / "feature-index.yaml", "evidence: [INS-001]\n")
    report = migrate(repo)
    assert (repo / "product-development/product/PRDs/a-hypothesis.md").read_text(encoding="utf-8") == \
        "- `SIG-002` -- why; evidence SIG-001\n"
    assert (repo / "feature-index.yaml").read_text(encoding="utf-8") == "evidence: [SIG-001]\n"
    assert sorted(report.files_rewritten) == [
        "feature-index.yaml", "product-development/product/PRDs/a-hypothesis.md"]


def test_insights_folder_is_removed(tmp_path):
    repo = _repo(tmp_path)
    migrate(repo)
    assert not (repo / INSIGHTS).exists()


def test_dry_run_changes_nothing(tmp_path):
    repo = _repo(tmp_path)
    _write(repo / "a.md", "INS-001\n")
    report = migrate(repo, dry_run=True)
    assert report.signals == 2 and report.files_rewritten == ["a.md"]
    assert (repo / "a.md").read_text(encoding="utf-8") == "INS-001\n"
    assert (repo / INSIGHTS).exists() and load(repo) == []


def test_migration_is_idempotent(tmp_path):
    repo = _repo(tmp_path)
    _write(repo / "a.md", "INS-001 and SRC-002\n")
    migrate(repo)
    before = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()}
    report = migrate(repo)
    assert report.signals == 0 and report.files_rewritten == []
    assert before == {p: p.read_bytes() for p in repo.rglob("*") if p.is_file()}


def test_rerun_with_insights_still_present_adds_nothing(tmp_path):
    repo = _repo(tmp_path)
    migrate(repo, keep_insights=True)
    assert migrate(repo, keep_insights=True).signals == 0
    assert len(load(repo)) == 2


def test_historical_docs_are_not_rewritten(tmp_path):
    repo = _repo(tmp_path)
    historical = [
        "docs/superpowers/plans/old-plan.md",
        "docs/gap-analysis-product-loop-2026-11-03.md",
        "docs/adr/0005-opportunity-hypothesis-layer.md",
        "docs/handoffs/2026-11-03-note.md",
    ]
    for rel in historical:
        _write(repo / rel, "cites INS-001 and SRC-002\n")
    report = migrate(repo)
    for rel in historical:
        assert (repo / rel).read_text(encoding="utf-8") == "cites INS-001 and SRC-002\n"
    assert report.files_rewritten == []


def test_line_endings_are_preserved(tmp_path):
    repo = _repo(tmp_path)
    _write(repo / "crlf.md", "INS-001\r\nline\r\n")
    migrate(repo)
    assert (repo / "crlf.md").read_bytes() == b"SIG-001\r\nline\r\n"
