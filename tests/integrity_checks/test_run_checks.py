from datetime import date
from pathlib import Path

from common import Finding
from run_checks import main, run


def fake_check_with_finding(repo_root, thresholds):
    return [Finding("fake-check", "k1", "problem found", "")]


def fake_check_clean(repo_root, thresholds):
    return []


def test_run_only_calls_enabled_checks():
    config = {"checks": {"a": True, "b": False}, "thresholds": {}}
    registry = {"a": fake_check_with_finding, "b": fake_check_clean}
    _, findings = run(Path("."), config, registry, date(2026, 1, 1))
    assert len(findings) == 1
    assert findings[0].check_id == "fake-check"


def test_run_raises_on_unknown_check_id():
    config = {"checks": {"missing": True}, "thresholds": {}}
    try:
        run(Path("."), config, {}, date(2026, 1, 1))
        raise AssertionError("expected KeyError")
    except KeyError:
        pass


def test_main_writes_status_and_returns_nonzero_on_findings(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("checks:\n  fake-check: true\nthresholds: {}\nfail-on-findings: true\n", encoding="utf-8")
    status_path = tmp_path / "status.json"

    import run_checks
    monkeypatch.setattr(run_checks, "discover_checks", lambda names: {"fake-check": fake_check_with_finding})

    code = main(["--repo-root", str(tmp_path), "--config", str(config_path), "--status", str(status_path)])
    assert code == 1
    assert status_path.exists()


def test_main_returns_zero_when_clean(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("checks:\n  fake-check: true\nthresholds: {}\nfail-on-findings: true\n", encoding="utf-8")
    status_path = tmp_path / "status.json"

    import run_checks
    monkeypatch.setattr(run_checks, "discover_checks", lambda names: {"fake-check": fake_check_clean})

    code = main(["--repo-root", str(tmp_path), "--config", str(config_path), "--status", str(status_path)])
    assert code == 0
