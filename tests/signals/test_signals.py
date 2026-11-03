import csv
import json
from pathlib import Path

import pytest

from signals import SIGNAL_ID_IN_TEXT, add, cited, load, main, unassigned, validate

HEADER = "signal_id,date,source_type,source_ref,account,summary,detail,tags\n"


def _repo(tmp_path: Path, rows: str = "") -> Path:
    store = tmp_path / "product-development/signals/signals.csv"
    store.parent.mkdir(parents=True)
    store.write_text(HEADER + rows, encoding="utf-8", newline="")
    return tmp_path


def _row(**over) -> dict:
    base = {
        "date": "2026-01-01",
        "source_type": "support",
        "source_ref": "TCK-1",
        "summary": "User cannot export",
    }
    base.update(over)
    return base


def _hypothesis(repo: Path, name: str, body: str) -> None:
    path = repo / "product-development/product/PRDs/area" / f"{name}-hypothesis.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {name}\n\n## Signals\n\n{body}\n", encoding="utf-8")


def test_add_allocates_sequential_ids(tmp_path):
    repo = _repo(tmp_path)
    result = add(repo, [_row(source_ref="A"), _row(source_ref="B")])
    assert result.written == ["SIG-001", "SIG-002"]


def test_add_continues_after_highest_id(tmp_path):
    repo = _repo(tmp_path, "SIG-019,2026-01-01,support,X,,old,,\n")
    result = add(repo, [_row()])
    assert result.written == ["SIG-020"]


def test_duplicate_is_skipped(tmp_path):
    repo = _repo(tmp_path)
    assert add(repo, [_row()]).written == ["SIG-001"]
    second = add(repo, [_row()])
    assert second.written == [] and second.skipped == 1
    assert len(load(repo)) == 1


def test_duplicate_within_one_batch_is_skipped(tmp_path):
    repo = _repo(tmp_path)
    result = add(repo, [_row(), _row()])
    assert result.written == ["SIG-001"] and result.skipped == 1


def test_repeat_with_new_source_ref_is_kept(tmp_path):
    repo = _repo(tmp_path)
    add(repo, [_row(source_ref="TCK-1")])
    result = add(repo, [_row(source_ref="TCK-2")])
    assert result.written == ["SIG-002"]


def test_invalid_rows_are_not_written(tmp_path):
    repo = _repo(tmp_path)
    rows = [
        _row(source_type="bogus"),
        _row(summary=""),
        _row(summary="x" * 301),
        _row(date="2026-13-45"),
        _row(source_ref="GOOD"),
    ]
    result = add(repo, rows)
    assert result.written == ["SIG-001"]
    assert sorted(result.invalid) == [0, 1, 2, 3]
    assert [s.source_ref for s in load(repo)] == ["GOOD"]


def test_validate_reports_one_message_per_bad_column():
    problems = validate(_row(source_type="bogus", summary="", date="nope"))
    assert len(problems) == 3
    assert validate(_row()) == []


def test_validate_rejects_long_detail_and_empty_source_ref():
    assert len(validate(_row(detail="x" * 2001))) == 1
    assert len(validate(_row(source_ref=""))) == 1


def test_csv_quoting_round_trips(tmp_path):
    repo = _repo(tmp_path)
    text = 'a, "b"\nc'
    add(repo, [_row(summary=text, detail=text)])
    (loaded,) = load(repo)
    assert loaded.summary == text and loaded.detail == text
    with open(repo / "product-development/signals/signals.csv", encoding="utf-8", newline="") as f:
        assert len(list(csv.DictReader(f))) == 1


def test_non_ascii_round_trips(tmp_path):
    repo = _repo(tmp_path)
    add(repo, [_row(summary="Café “quoted” — 日本語")])
    assert load(repo)[0].summary == "Café “quoted” — 日本語"


def test_unassigned_excludes_cited_signals(tmp_path):
    repo = _repo(tmp_path)
    add(repo, [_row(source_ref="A"), _row(source_ref="B")])
    _hypothesis(repo, "HYP-1", "- `SIG-001` -- reason")
    assert [s.signal_id for s in unassigned(repo)] == ["SIG-002"]
    assert list(cited(repo)) == ["SIG-001"]
    assert cited(repo)["SIG-001"] == [
        "product-development/product/PRDs/area/HYP-1-hypothesis.md"
    ]


def test_signal_id_regex_ignores_other_id_schemes():
    assert SIGNAL_ID_IN_TEXT.findall("SIG-2026-0001 and SIG-004") == ["SIG-004"]


def test_cli_add_and_show(tmp_path, capsys):
    repo = _repo(tmp_path)
    payload = tmp_path / "in.json"
    payload.write_text(json.dumps(_row()), encoding="utf-8")
    assert main(["add", "--json", str(payload), "--repo-root", str(repo)]) == 0
    assert "SIG-001" in capsys.readouterr().out
    _hypothesis(repo, "HYP-1", "- `SIG-001` -- reason")
    assert main(["show", "SIG-001", "--repo-root", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "User cannot export" in out and "HYP-1-hypothesis.md" in out


def test_cli_unknown_signal_is_an_error(tmp_path, capsys):
    repo = _repo(tmp_path)
    assert main(["show", "SIG-999", "--repo-root", str(repo)]) == 1
    assert capsys.readouterr().err.startswith("error: ")


def test_cli_check_flags_invalid_row(tmp_path, capsys):
    repo = _repo(tmp_path, "SIG-001,2026-01-01,bogus,X,,s,,\n")
    assert main(["check", "--repo-root", str(repo)]) == 1
    assert "SIG-001" in capsys.readouterr().err
    clean = _repo(tmp_path / "clean")
    assert main(["check", "--repo-root", str(clean)]) == 0


def test_cli_unassigned_filters_by_tag(tmp_path, capsys):
    repo = _repo(tmp_path)
    add(repo, [_row(source_ref="A", tags="trust;security"), _row(source_ref="B", tags="cost")])
    assert main(["unassigned", "--tag", "trust", "--repo-root", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "SIG-001" in out and "SIG-002" not in out


def _account(repo: Path, slug: str) -> None:
    (repo / "product-development/product/customers/accounts" / slug).mkdir(parents=True)


def test_validate_checks_account_folder_when_given_a_repo(tmp_path):
    repo = _repo(tmp_path)
    _account(repo, "acme-corp")
    assert validate(_row(account="acme-corp"), repo) == []
    problems = validate(_row(account="nope"), repo)
    assert len(problems) == 1 and "account" in problems[0]


def test_validate_rejects_account_that_is_a_path(tmp_path):
    repo = _repo(tmp_path)
    _account(repo, "acme-corp")
    assert validate(_row(account="../accounts/acme-corp"), repo)


def test_validate_without_a_repo_skips_the_account_folder_check():
    assert validate(_row(account="anything")) == []


def test_add_rejects_unknown_account_and_keeps_valid_rows(tmp_path):
    repo = _repo(tmp_path)
    _account(repo, "acme-corp")
    result = add(repo, [_row(account="nope"), _row(account="acme-corp", source_ref="B")])
    assert result.written == ["SIG-001"] and list(result.invalid) == [0]


def test_cli_check_flags_unknown_account(tmp_path, capsys):
    repo = _repo(tmp_path, "SIG-001,2026-01-01,support,X,nope,s,,\n")
    assert main(["check", "--repo-root", str(repo)]) == 1
    assert "account" in capsys.readouterr().err
