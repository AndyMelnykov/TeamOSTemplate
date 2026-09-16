from pathlib import Path

import pytest
import yaml

from checks.feature_index import check_broken_tickets, check_join_completeness


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _write(tmp_path / "product-development/feature-index.yaml",
        yaml.safe_dump({"area": {"feature": {
            "prd": "product/PRDs/area/feature-prd.md",
            "tickets": ["EXAMPLE_PRODUCT/1"],
        }}}))
    _write(tmp_path / "product-development/product/PRDs/area/feature-prd.md", "# Feature - PRD\n")
    return tmp_path


def test_join_completeness_flags_unindexed_prd(repo: Path):
    _write(repo / "product-development/product/PRDs/area/other-prd.md", "# Other - PRD\n")
    findings = check_join_completeness(repo, {})
    assert any(f.key == "product/PRDs/area/other-prd.md" for f in findings)


def test_join_completeness_clean_for_indexed_prd(repo: Path):
    findings = check_join_completeness(repo, {})
    assert not any(f.key == "product/PRDs/area/feature-prd.md" for f in findings)


def test_broken_tickets_flags_ticket_gh_cannot_resolve(repo: Path):
    findings = check_broken_tickets(repo, {}, gh_runner=lambda ticket: False)
    assert findings and findings[0].key == "EXAMPLE_PRODUCT/1"


def test_broken_tickets_clean_when_gh_resolves(repo: Path):
    findings = check_broken_tickets(repo, {}, gh_runner=lambda ticket: True)
    assert findings == []
