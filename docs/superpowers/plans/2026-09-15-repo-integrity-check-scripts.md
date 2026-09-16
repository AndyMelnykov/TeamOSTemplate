# Repo Integrity Check Scripts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a config-driven suite of Python scripts that check structural/process integrity across the discovery → PRD → engineering → decision pipeline (e.g. hypotheses with no supporting signal, PRDs missing required sections, feature-index.yaml drift, stale backlog entries), persist findings with first-detected dates in a committed status file so "how long has this been open" is derivable, generate a human-readable summary, and run on a schedule via one GitHub Actions workflow with a single enable/disable config file.

**Architecture:** New `scripts/integrity-checks/` package: `common.py` (shared `Finding` type + status-file persistence/merge logic), `run_checks.py` (orchestrator — reads `config.yaml`, dispatches to check modules, merges results into `reports/status.json`), five `checks/*.py` modules grouped by the files they read (not one file per check — see Global Constraints), and `summarize.py` (turns `reports/status.json` into `reports/summary.md`). No LLM calls anywhere in this plan — pure stdlib + PyYAML parsing, mirroring the existing deterministic-policy-layer pattern already in this repo (`scripts/check-references.ps1`, per `docs/architecture.md` and [ADR 0003](../../adr/0003-human-approval-for-canonical-writes.md)). `.github/workflows/integrity-checks.yml` runs the suite nightly plus on-demand and commits the updated `reports/` back to the branch.

**Tech Stack:** Python 3.12, PyYAML, pytest. `gh` CLI via `subprocess` for the one check that needs GitHub API access. No other runtime dependency. This is the first Python code in this repo — pytest is scoped to `scripts/integrity-checks/` only, not a repo-wide test runner.

**Spec:** None — designed and approved in chat during this session's brainstorming pass (a catalog of 17 integrity checks was proposed, then refined into 7 phases grouped by shared input files, plus the config/runner/summary/CI requirements below, all directed by the user). Following this repo's own precedent (`docs/superpowers/plans/2026-09-13-feature-request-intake-and-two-track-review.md`, which made the same call for a similarly chat-approved pair of additions), design decisions are captured inline below as Global Constraints instead of a separate spec file.

## Global Constraints

- **No repo-wide CI previously existed.** This plan's tests run with `pip install -r scripts/integrity-checks/requirements.txt && pytest scripts/integrity-checks tests/integrity_checks -q` from the repo root. Every task's verification step uses this exact command.
- **Tests use synthetic fixture trees (`tmp_path`), never the real `product-development/` tree.** This keeps tests stable as real example content changes — e.g. once `shared-components-prd.md`'s missing `## Sources` section (logged in `PAPERCUTS.md`, 2026-09-13) gets backfilled, a test hard-coded to expect that specific finding would start failing for the wrong reason.
- **Every check function has the signature `def check_x(repo_root: Path, thresholds: dict) -> list[Finding]`** and is registered in its module's `CHECKS: dict[str, Callable]` dict, keyed by its `check_id` string (kebab-case, matches the key used in `config.yaml`).
- **Findings are tracked across runs by `f"{check_id}::{key}"`.** `key` must be a stable identifier (a file path, an artifact ID, a ticket ref) — never a message string (wording may change) and never a timestamp. This is what lets `reports/status.json` carry a `first_detected` date forward run over run, which is how "how long has this been unresolved" gets computed without a database.
- **Grouping into phase modules follows the user's explicit rule:** checks that read the same source files/folders share one module and one task, even where that makes a task larger than the usual one-check-per-task granularity. This trades per-check reviewer granularity for fewer repeated file reads during implementation — the user's stated priority for this plan.
- **`feature-index-broken-tickets` (Task 4) ships disabled by default** (`false` in `config.yaml`). This repo's `feature-index.yaml` holds fabricated example ticket numbers (`EXAMPLE_PRODUCT/1042`, etc.) that don't correspond to real issues in `AndyMelnykov/TeamOSTemplate` — leaving it enabled would flag this repo's entire example dataset as "broken" on every run. A real install (real tickets, real `gh` repo) should flip it to `true`.
- **Delivery of `reports/summary.md` outside this repo (Slack, email, etc.) is out of scope for this plan.** The GitHub Actions workflow's job ends at committing the file back to the repo; a visibly failed/red workflow run (when findings exist) is the only notification mechanism this plan builds.
- Any step that runs `scripts/check-references.ps1` should use `powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1` — the bare form fails on a stock Windows execution policy (papercut logged 2026-09-13).
- Directory layout locked in by this plan:
  ```
  scripts/integrity-checks/
    requirements.txt
    config.yaml
    common.py
    run_checks.py
    summarize.py
    README.md
    checks/
      __init__.py
      insights_discovery.py
      feature_index.py
      prd_content.py
      decisions_adr.py
      process_health.py
    reports/
      status.json      # committed, updated in place each run
      summary.md        # committed, regenerated each run
  tests/integrity_checks/
    conftest.py
    test_common.py
    test_run_checks.py
    test_insights_discovery.py
    test_feature_index.py
    test_prd_content.py
    test_decisions_adr.py
    test_process_health.py
    test_summarize.py
  .github/workflows/integrity-checks.yml
  ```

---

### Task 1: Scaffolding + `common.py` (shared Finding type and status-file persistence)

**Files:**
- Create: `scripts/integrity-checks/requirements.txt`
- Create: `scripts/integrity-checks/common.py`
- Create: `scripts/integrity-checks/checks/__init__.py`
- Create: `tests/integrity_checks/conftest.py`
- Test: `tests/integrity_checks/test_common.py`

**Interfaces:**
- Produces: `Finding(check_id: str, key: str, message: str, file: str = "")` dataclass; `load_config(path) -> dict`; `load_status(path) -> dict`; `write_status(path, status: dict) -> None`; `merge_findings(previous: dict, current: list[Finding], today: date) -> dict`; `days_open(record: dict, today: date) -> int`. Every later task's check modules and `run_checks.py`/`summarize.py` import from here.

- [ ] **Step 1: Create `requirements.txt`**

```
PyYAML>=6.0
pytest>=8.0
```

- [ ] **Step 2: Create `tests/integrity_checks/conftest.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "integrity-checks"))
```

- [ ] **Step 3: Write the failing tests for `common.py`**

`tests/integrity_checks/test_common.py`:

```python
from datetime import date
from pathlib import Path

from common import Finding, days_open, load_config, load_status, merge_findings, write_status


def test_merge_findings_keeps_first_detected_for_repeated_key():
    previous = {
        "chk::a": {"check_id": "chk", "key": "a", "message": "old", "file": "",
                   "first_detected": "2026-01-01", "last_seen": "2026-01-01"}
    }
    current = [Finding("chk", "a", "new message", "")]
    merged = merge_findings(previous, current, date(2026, 1, 10))
    assert merged["chk::a"]["first_detected"] == "2026-01-01"
    assert merged["chk::a"]["last_seen"] == "2026-01-10"
    assert merged["chk::a"]["message"] == "new message"


def test_merge_findings_sets_first_detected_for_new_key():
    merged = merge_findings({}, [Finding("chk", "b", "msg", "")], date(2026, 1, 10))
    assert merged["chk::b"]["first_detected"] == "2026-01-10"


def test_merge_findings_drops_resolved_keys():
    previous = {
        "chk::a": {"check_id": "chk", "key": "a", "message": "old", "file": "",
                   "first_detected": "2026-01-01", "last_seen": "2026-01-01"}
    }
    assert merge_findings(previous, [], date(2026, 1, 10)) == {}


def test_days_open():
    assert days_open({"first_detected": "2026-01-01"}, date(2026, 1, 11)) == 10


def test_write_and_load_status_roundtrip(tmp_path: Path):
    status_path = tmp_path / "reports" / "status.json"
    write_status(status_path, {"generated_at": "2026-01-10", "findings": {}})
    assert load_status(status_path)["generated_at"] == "2026-01-10"


def test_load_status_missing_file_returns_empty(tmp_path: Path):
    assert load_status(tmp_path / "missing.json") == {"generated_at": None, "findings": {}}


def test_load_config(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("checks:\n  demo: true\nthresholds:\n  x: 5\n", encoding="utf-8")
    config = load_config(config_path)
    assert config["checks"]["demo"] is True
    assert config["thresholds"]["x"] == 5
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `pytest tests/integrity_checks/test_common.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'common'`

- [ ] **Step 5: Implement `common.py`**

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml


@dataclass
class Finding:
    check_id: str
    key: str
    message: str
    file: str = ""


def load_config(config_path: Path) -> dict:
    with config_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_status(status_path: Path) -> dict:
    if not status_path.exists():
        return {"generated_at": None, "findings": {}}
    with status_path.open(encoding="utf-8") as f:
        return json.load(f)


def write_status(status_path: Path, status: dict) -> None:
    status_path.parent.mkdir(parents=True, exist_ok=True)
    with status_path.open("w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, sort_keys=True)
        f.write("\n")


def merge_findings(previous: dict, current: list[Finding], today: date) -> dict:
    today_str = today.isoformat()
    merged: dict[str, dict] = {}
    for finding in current:
        record_key = f"{finding.check_id}::{finding.key}"
        prior = previous.get(record_key)
        first_detected = prior["first_detected"] if prior else today_str
        merged[record_key] = {
            "check_id": finding.check_id,
            "key": finding.key,
            "message": finding.message,
            "file": finding.file,
            "first_detected": first_detected,
            "last_seen": today_str,
        }
    return merged


def days_open(record: dict, today: date) -> int:
    return (today - date.fromisoformat(record["first_detected"])).days
```

Also create `scripts/integrity-checks/checks/__init__.py` (empty file).

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/integrity_checks/test_common.py -v`
Expected: PASS (7 tests)

- [ ] **Step 7: Commit**

```bash
git add scripts/integrity-checks/requirements.txt scripts/integrity-checks/common.py scripts/integrity-checks/checks/__init__.py tests/integrity_checks/conftest.py tests/integrity_checks/test_common.py
git commit -m "feat: add integrity-check framework core (Finding type, status persistence)"
```

---

### Task 2: `run_checks.py` orchestrator + `config.yaml`

**Files:**
- Create: `scripts/integrity-checks/run_checks.py`
- Create: `scripts/integrity-checks/config.yaml`
- Test: `tests/integrity_checks/test_run_checks.py`

**Interfaces:**
- Consumes: Task 1's `Finding`, `load_config`, `load_status`, `write_status`, `merge_findings`, `days_open`.
- Produces: `discover_checks(module_names: list[str]) -> dict[str, Callable]`; `run(repo_root: Path, config: dict, registry: dict, today: date) -> tuple[dict, list[Finding]]`; `main(argv=None) -> int`. Tasks 3-7 each add their module's dotted path to `CHECK_MODULES` and their check ids to `config.yaml`.

- [ ] **Step 1: Write the failing tests**

`tests/integrity_checks/test_run_checks.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integrity_checks/test_run_checks.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'run_checks'`

- [ ] **Step 3: Implement `run_checks.py`**

```python
from __future__ import annotations

import argparse
import sys
from datetime import date
from importlib import import_module
from pathlib import Path

from common import Finding, days_open, load_config, load_status, merge_findings, write_status

CHECK_MODULES = [
    "checks.insights_discovery",
    "checks.feature_index",
    "checks.prd_content",
    "checks.decisions_adr",
    "checks.process_health",
]


def discover_checks(module_names: list[str]) -> dict:
    registry: dict = {}
    for name in module_names:
        module = import_module(name)
        registry.update(module.CHECKS)
    return registry


def run(repo_root: Path, config: dict, registry: dict, today: date) -> tuple[dict, list[Finding]]:
    enabled = {cid for cid, on in config.get("checks", {}).items() if on}
    thresholds = config.get("thresholds", {})
    findings: list[Finding] = []
    for check_id in sorted(enabled):
        fn = registry.get(check_id)
        if fn is None:
            raise KeyError(f"config.yaml enables unknown check_id: {check_id}")
        findings.extend(fn(repo_root, thresholds))
    return {"findings": findings}, findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--config", default=None)
    parser.add_argument("--status", default=None)
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    config_path = Path(args.config) if args.config else Path(__file__).parent / "config.yaml"
    status_path = Path(args.status) if args.status else Path(__file__).parent / "reports" / "status.json"

    config = load_config(config_path)
    registry = discover_checks(CHECK_MODULES)
    today = date.today()

    _, findings = run(repo_root, config, registry, today)

    previous = load_status(status_path).get("findings", {})
    merged = merge_findings(previous, findings, today)
    write_status(status_path, {"generated_at": today.isoformat(), "findings": merged})

    print(f"{len(merged)} open finding(s) across {sum(1 for v in config.get('checks', {}).values() if v)} enabled check(s).")
    for record in sorted(merged.values(), key=lambda r: (r["check_id"], r["key"])):
        print(f"  [{record['check_id']}] {record['message']} (open {days_open(record, today)}d)")

    if merged and config.get("fail-on-findings", True):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Create `config.yaml`**

```yaml
checks: {}

thresholds:
  stale-insight-days: 30
  stale-prd-status-days: 21
  stale-bug-investigation-days: 14

fail-on-findings: true
```

(Left empty on purpose — Tasks 3-7 each add their own check ids here as they land, so `config.yaml` only ever references checks that actually exist.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/integrity_checks/test_run_checks.py -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/integrity-checks/run_checks.py scripts/integrity-checks/config.yaml tests/integrity_checks/test_run_checks.py
git commit -m "feat: add integrity-check runner and config file"
```

---

### Task 3: `checks/insights_discovery.py` — Insights ↔ Opportunity ↔ Hypothesis integrity

Reads: `product-development/product/Insights/{insights,sources}.csv`, `product-development/product/PRDs/**/*-opportunity.md`, `**/*-hypothesis.md`, `product-development/feature-index.yaml`. Grouped together because every check here opens the same insight/opportunity/hypothesis files.

**Files:**
- Create: `scripts/integrity-checks/checks/insights_discovery.py`
- Test: `tests/integrity_checks/test_insights_discovery.py`
- Modify: `scripts/integrity-checks/config.yaml`

**Interfaces:**
- Consumes: Task 1's `Finding`.
- Produces: `CHECKS` dict with keys `insights-orphan-hypothesis`, `insights-orphan-sources`, `insights-promotion-status`, `insights-stale`, `insights-orphan-opportunity`, `insights-id-collisions`.

- [ ] **Step 1: Write the failing tests**

`tests/integrity_checks/test_insights_discovery.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integrity_checks/test_insights_discovery.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'checks.insights_discovery'`

- [ ] **Step 3: Implement `checks/insights_discovery.py`**

```python
from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

import yaml

from common import Finding

OPP_HEADING_RE = re.compile(r"^#\s+(OPP-[A-Z]+-\d+)", re.MULTILINE)
HYP_HEADING_RE = re.compile(r"^#\s+(HYP-[A-Z]+-\d+)", re.MULTILINE)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def _load_insights(repo_root: Path) -> dict[str, dict]:
    path = repo_root / "product-development/product/Insights/insights.csv"
    with path.open(encoding="utf-8", newline="") as f:
        return {row["insight_id"]: row for row in csv.DictReader(f)}


def _load_sources(repo_root: Path) -> list[dict]:
    path = repo_root / "product-development/product/Insights/sources.csv"
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _opportunity_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "product-development/product/PRDs").rglob("*-opportunity.md"))


def _hypothesis_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "product-development/product/PRDs").rglob("*-hypothesis.md"))


def check_orphan_hypothesis(repo_root: Path, thresholds: dict) -> list[Finding]:
    insights = _load_insights(repo_root)
    opp_by_id: dict[str, Path] = {}
    for path in _opportunity_files(repo_root):
        m = OPP_HEADING_RE.search(_read(path))
        if m:
            opp_by_id[m.group(1)] = path

    findings = []
    for path in _hypothesis_files(repo_root):
        text = _read(path)
        hyp_match = HYP_HEADING_RE.search(text)
        hyp_id = hyp_match.group(1) if hyp_match else path.stem
        opp_ids = re.findall(r"OPP-[A-Z]+-\d+", _section(text, "Opportunity"))
        if not opp_ids:
            findings.append(Finding("insights-orphan-hypothesis", hyp_id,
                f"{path.name} has no OPP- id in its ## Opportunity section", str(path)))
            continue
        opp_path = opp_by_id.get(opp_ids[0])
        if opp_path is None:
            findings.append(Finding("insights-orphan-hypothesis", hyp_id,
                f"{path.name} cites {opp_ids[0]}, which has no matching opportunity file", str(path)))
            continue
        evidence = _section(_read(opp_path), "Evidence")
        cited = [i for i in re.findall(r"INS-\d+", evidence) if i in insights]
        if not cited:
            findings.append(Finding("insights-orphan-hypothesis", hyp_id,
                f"{path.name} -> {opp_path.name} cites no existing INS- signal in its ## Evidence section", str(path)))
    return findings


def check_orphan_sources(repo_root: Path, thresholds: dict) -> list[Finding]:
    insights = _load_insights(repo_root)
    findings = []
    for row in _load_sources(repo_root):
        if row["insight_id"] not in insights:
            findings.append(Finding("insights-orphan-sources", row["source_id"],
                f"{row['source_id']} references missing insight_id {row['insight_id']}",
                "product-development/product/Insights/sources.csv"))
    return findings


def check_promotion_status(repo_root: Path, thresholds: dict) -> list[Finding]:
    insights = _load_insights(repo_root)
    findings = []
    for path in _opportunity_files(repo_root):
        text = _read(path)
        m = OPP_HEADING_RE.search(text)
        opp_id = m.group(1) if m else path.stem
        for insight_id in re.findall(r"INS-\d+", _section(text, "Evidence")):
            row = insights.get(insight_id)
            if row and row["status"] == "new":
                findings.append(Finding("insights-promotion-status", insight_id,
                    f"{insight_id} is cited by {opp_id} ({path.name}) but status is still 'new', expected 'validated'+",
                    "product-development/product/Insights/insights.csv"))
    return findings


def check_stale_insights(repo_root: Path, thresholds: dict) -> list[Finding]:
    stale_days = thresholds.get("stale-insight-days", 30)
    today = date.today()
    findings = []
    for insight_id, row in _load_insights(repo_root).items():
        if row["status"] != "new":
            continue
        last_seen = date.fromisoformat(row["last_seen"])
        age = (today - last_seen).days
        if age > stale_days:
            findings.append(Finding("insights-stale", insight_id,
                f"{insight_id} has been 'new' since {row['last_seen']} ({age}d, threshold {stale_days}d)",
                "product-development/product/Insights/insights.csv"))
    return findings


def _flatten_md_paths(node) -> set[str]:
    out: set[str] = set()
    if isinstance(node, dict):
        for v in node.values():
            out |= _flatten_md_paths(v)
    elif isinstance(node, list):
        for v in node:
            out |= _flatten_md_paths(v)
    elif isinstance(node, str) and node.endswith(".md"):
        out.add(node)
    return out


def check_orphan_opportunity(repo_root: Path, thresholds: dict) -> list[Finding]:
    index_path = repo_root / "product-development/feature-index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    referenced = _flatten_md_paths(index)
    findings = []
    for path in _opportunity_files(repo_root) + _hypothesis_files(repo_root):
        rel = path.relative_to(repo_root / "product-development").as_posix()
        if rel not in referenced:
            findings.append(Finding("insights-orphan-opportunity", rel,
                f"{path.name} is not referenced by any feature-index.yaml entry", str(path)))
    return findings


def _record_collision(artifact_id: str, path: Path, seen: dict, findings: list) -> None:
    if artifact_id in seen:
        findings.append(Finding("insights-id-collisions", artifact_id,
            f"{artifact_id} appears in both {seen[artifact_id].name} and {path.name}", str(path)))
    else:
        seen[artifact_id] = path


def check_id_collisions(repo_root: Path, thresholds: dict) -> list[Finding]:
    seen: dict[str, Path] = {}
    findings: list = []
    for path in _opportunity_files(repo_root):
        m = OPP_HEADING_RE.search(_read(path))
        if m:
            _record_collision(m.group(1), path, seen, findings)
    for path in _hypothesis_files(repo_root):
        m = HYP_HEADING_RE.search(_read(path))
        if m:
            _record_collision(m.group(1), path, seen, findings)
    return findings


CHECKS = {
    "insights-orphan-hypothesis": check_orphan_hypothesis,
    "insights-orphan-sources": check_orphan_sources,
    "insights-promotion-status": check_promotion_status,
    "insights-stale": check_stale_insights,
    "insights-orphan-opportunity": check_orphan_opportunity,
    "insights-id-collisions": check_id_collisions,
}
```

- [ ] **Step 4: Add these check ids to `config.yaml`'s `checks:` map**

```yaml
checks:
  insights-orphan-hypothesis: true
  insights-orphan-sources: true
  insights-promotion-status: true
  insights-stale: true
  insights-orphan-opportunity: true
  insights-id-collisions: true
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/integrity_checks/test_insights_discovery.py -v`
Expected: PASS (8 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/integrity-checks/checks/insights_discovery.py scripts/integrity-checks/config.yaml tests/integrity_checks/test_insights_discovery.py
git commit -m "feat: add insights/opportunity/hypothesis integrity checks"
```

---

### Task 4: `checks/feature_index.py` — join-table completeness and ticket existence

Reads: `product-development/feature-index.yaml` plus a full glob of `product-development/**`. Grouped together because both checks flatten and cross-reference `feature-index.yaml` against an external truth (the filesystem, and GitHub respectively).

**Files:**
- Create: `scripts/integrity-checks/checks/feature_index.py`
- Test: `tests/integrity_checks/test_feature_index.py`
- Modify: `scripts/integrity-checks/config.yaml`

**Interfaces:**
- Consumes: Task 1's `Finding`.
- Produces: `CHECKS` dict with keys `feature-index-join-completeness`, `feature-index-broken-tickets`. `check_broken_tickets` accepts an injectable `gh_runner: Callable[[str], bool]` (defaults to a real `gh issue view` subprocess call) so it's testable without a live GitHub connection.

- [ ] **Step 1: Write the failing tests**

`tests/integrity_checks/test_feature_index.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integrity_checks/test_feature_index.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'checks.feature_index'`

- [ ] **Step 3: Implement `checks/feature_index.py`**

```python
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

from common import Finding

ARTIFACT_GLOBS = [
    "product/PRDs/**/*-prd.md",
    "engineering/rfcs/**/*-rfc.md",
    "engineering/plans/**/*.md",
    "data-engineering/rfcs/**/*-rfc.md",
    "data-engineering/plans/**/*.md",
    "analytics/schemas/**/*.md",
    "analytics/queries/**/*.sql",
    "analytics/dashboards/**/*.md",
    "analytics/experiments/**/*.md",
    "analytics/investigations/**/*.md",
    "engineering/bug-investigations/**/investigation-plan.md",
]

TICKET_RE = re.compile(r"^[A-Z0-9_]+/\d+$")


def _flatten_str(node) -> set[str]:
    out: set[str] = set()
    if isinstance(node, dict):
        for v in node.values():
            out |= _flatten_str(v)
    elif isinstance(node, list):
        for v in node:
            out |= _flatten_str(v)
    elif isinstance(node, str):
        out.add(node)
    return out


def check_join_completeness(repo_root: Path, thresholds: dict) -> list[Finding]:
    pd = repo_root / "product-development"
    index = yaml.safe_load((pd / "feature-index.yaml").read_text(encoding="utf-8"))
    referenced = {v for v in _flatten_str(index) if v.endswith(".md") or v.endswith(".sql")}
    findings = []
    for pattern in ARTIFACT_GLOBS:
        for path in sorted(pd.glob(pattern)):
            rel = path.relative_to(pd).as_posix()
            if rel not in referenced:
                findings.append(Finding("feature-index-join-completeness", rel,
                    f"{rel} exists on disk but is not referenced by any feature-index.yaml entry", str(path)))
    return findings


def _default_gh_runner(ticket: str) -> bool:
    number = ticket.split("/")[-1]
    result = subprocess.run(["gh", "issue", "view", number], capture_output=True, text=True)
    return result.returncode == 0


def check_broken_tickets(repo_root: Path, thresholds: dict, gh_runner=_default_gh_runner) -> list[Finding]:
    pd = repo_root / "product-development"
    index = yaml.safe_load((pd / "feature-index.yaml").read_text(encoding="utf-8"))
    tickets = {t for t in _flatten_str(index) if TICKET_RE.match(t)}
    findings = []
    for ticket in sorted(tickets):
        if not gh_runner(ticket):
            findings.append(Finding("feature-index-broken-tickets", ticket,
                f"{ticket} does not resolve via `gh issue view`", "product-development/feature-index.yaml"))
    return findings


CHECKS = {
    "feature-index-join-completeness": check_join_completeness,
    "feature-index-broken-tickets": check_broken_tickets,
}
```

- [ ] **Step 4: Add to `config.yaml`**

```yaml
  feature-index-join-completeness: true
  feature-index-broken-tickets: false
```

(`false` per the Global Constraints note — this repo's example tickets aren't real GitHub issues.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/integrity_checks/test_feature_index.py -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/integrity-checks/checks/feature_index.py scripts/integrity-checks/config.yaml tests/integrity_checks/test_feature_index.py
git commit -m "feat: add feature-index join-completeness and ticket-existence checks"
```

---

### Task 5: `checks/prd_content.py` — per-PRD content checks

Reads every file under `product-development/product/PRDs/**/*-prd.md`, plus `product-development/product/strategy/` and the two Insights CSVs for cross-checks. Grouped together because all four checks iterate the same PRD file set.

**Files:**
- Create: `scripts/integrity-checks/checks/prd_content.py`
- Test: `tests/integrity_checks/test_prd_content.py`
- Modify: `scripts/integrity-checks/config.yaml`

**Interfaces:**
- Consumes: Task 1's `Finding`.
- Produces: `CHECKS` dict with keys `prd-missing-sections`, `prd-strategy-review-decision-gate`, `prd-sources-citation-validity`, `prd-stale-status`.

- [ ] **Step 1: Write the failing tests**

`tests/integrity_checks/test_prd_content.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integrity_checks/test_prd_content.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'checks.prd_content'`

- [ ] **Step 3: Implement `checks/prd_content.py`**

```python
from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

from common import Finding

REQUIRED_SECTIONS = [
    "Overview", "User Stories", "Requirements", "Design",
    "Technical Considerations", "Launch Plan", "Sources",
]


def _prd_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "product-development/product/PRDs").rglob("*-prd.md"))


def _field(text: str, name: str) -> str:
    m = re.search(rf"\*\*{re.escape(name)}\*\*\s*\|\s*([^\n|]+)", text)
    return m.group(1).strip() if m else ""


def check_missing_sections(repo_root: Path, thresholds: dict) -> list[Finding]:
    findings = []
    for path in _prd_files(repo_root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        missing = [s for s in REQUIRED_SECTIONS if not re.search(rf"^##\s+{re.escape(s)}\s*$", text, re.MULTILINE)]
        if missing:
            findings.append(Finding("prd-missing-sections", rel,
                f"{path.name} is missing section(s): {', '.join(missing)}", rel))
    return findings


def check_strategy_review_decision_gate(repo_root: Path, thresholds: dict) -> list[Finding]:
    strategy_dir = repo_root / "product-development/product/strategy"
    strategy_text = "\n".join(
        f.read_text(encoding="utf-8") for f in strategy_dir.rglob("*-decision.md")
    ) if strategy_dir.exists() else ""
    findings = []
    for path in _prd_files(repo_root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        tier = _field(text, "Review Tier")
        status = _field(text, "Status")
        if tier == "Strategy Review" and status in {"Approved", "Shipped"}:
            feature_slug = path.stem.removesuffix("-prd")
            if feature_slug not in strategy_text and path.name not in strategy_text:
                findings.append(Finding("prd-strategy-review-decision-gate", rel,
                    f"{path.name} is Strategy Review / {status} but no decision file under product/strategy/ links to it", rel))
    return findings


def _load_ids(repo_root: Path, filename: str, id_field: str) -> set[str]:
    path = repo_root / "product-development/product/Insights" / filename
    with path.open(encoding="utf-8", newline="") as f:
        return {row[id_field] for row in csv.DictReader(f)}


def check_sources_citation_validity(repo_root: Path, thresholds: dict) -> list[Finding]:
    insight_ids = _load_ids(repo_root, "insights.csv", "insight_id")
    source_ids = _load_ids(repo_root, "sources.csv", "source_id")
    findings = []
    for path in _prd_files(repo_root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        m = re.search(r"^##\s+Sources\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
        section = m.group(1) if m else ""
        for cited in re.findall(r"\b(INS-\d+|SRC-\d+)\b", section):
            valid = cited in insight_ids if cited.startswith("INS-") else cited in source_ids
            if not valid:
                findings.append(Finding("prd-sources-citation-validity", f"{rel}::{cited}",
                    f"{path.name} cites {cited} in ## Sources, which does not exist", rel))
    return findings


def check_stale_status(repo_root: Path, thresholds: dict) -> list[Finding]:
    stale_days = thresholds.get("stale-prd-status-days", 21)
    today = date.today()
    findings = []
    for path in _prd_files(repo_root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        status = _field(text, "Status")
        last_updated = _field(text, "Last Updated")
        if status in {"Draft", "In Review"} and last_updated:
            days = (today - date.fromisoformat(last_updated)).days
            if days > stale_days:
                findings.append(Finding("prd-stale-status", rel,
                    f"{path.name} has been '{status}' since {last_updated} ({days}d, threshold {stale_days}d)", rel))
    return findings


CHECKS = {
    "prd-missing-sections": check_missing_sections,
    "prd-strategy-review-decision-gate": check_strategy_review_decision_gate,
    "prd-sources-citation-validity": check_sources_citation_validity,
    "prd-stale-status": check_stale_status,
}
```

- [ ] **Step 4: Add to `config.yaml`**

```yaml
  prd-missing-sections: true
  prd-strategy-review-decision-gate: true
  prd-sources-citation-validity: true
  prd-stale-status: true
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/integrity_checks/test_prd_content.py -v`
Expected: PASS (6 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/integrity-checks/checks/prd_content.py scripts/integrity-checks/config.yaml tests/integrity_checks/test_prd_content.py
git commit -m "feat: add PRD content integrity checks (sections, decision gate, citations, staleness)"
```

---

### Task 6: `checks/decisions_adr.py` — decision-file and ADR conventions

Reads: every `*-decision.md` under `product-development/`, and `docs/adr/*.md`. Grouped together because both checks validate naming/numbering conventions on small, self-contained file sets.

**Files:**
- Create: `scripts/integrity-checks/checks/decisions_adr.py`
- Test: `tests/integrity_checks/test_decisions_adr.py`
- Modify: `scripts/integrity-checks/config.yaml`

**Interfaces:**
- Consumes: Task 1's `Finding`.
- Produces: `CHECKS` dict with keys `decisions-naming-convention`, `adr-numbering`.

- [ ] **Step 1: Write the failing tests**

`tests/integrity_checks/test_decisions_adr.py`:

```python
from pathlib import Path

import pytest

from checks.decisions_adr import check_adr_numbering, check_decision_naming


def _write(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_decision_naming_flags_bad_filename(tmp_path: Path):
    _write(tmp_path / "product-development/product/strategy/q3-priorities-decision.md")
    findings = check_decision_naming(tmp_path, {})
    assert findings

def test_decision_naming_clean_for_valid_filename(tmp_path: Path):
    _write(tmp_path / "product-development/product/strategy/2026-04-01-q3-priorities-decision.md")
    assert check_decision_naming(tmp_path, {}) == []


def test_decision_naming_flags_top_level_archive(tmp_path: Path):
    _write(tmp_path / "product-development/decisions/2026-04-01-foo-decision.md")
    findings = check_decision_naming(tmp_path, {})
    assert any(f.key == "product-development/decisions" for f in findings)


def test_adr_numbering_flags_gap(tmp_path: Path):
    _write(tmp_path / "docs/adr/0001-first.md")
    _write(tmp_path / "docs/adr/0003-third.md")
    findings = check_adr_numbering(tmp_path, {})
    assert any(f.key == "0002" for f in findings)


def test_adr_numbering_flags_duplicate(tmp_path: Path):
    _write(tmp_path / "docs/adr/0001-first.md")
    _write(tmp_path / "docs/adr/0001-duplicate.md")
    findings = check_adr_numbering(tmp_path, {})
    assert any(f.key == "0001" for f in findings)


def test_adr_numbering_clean_for_sequential(tmp_path: Path):
    _write(tmp_path / "docs/adr/0001-first.md")
    _write(tmp_path / "docs/adr/0002-second.md")
    assert check_adr_numbering(tmp_path, {}) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integrity_checks/test_decisions_adr.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'checks.decisions_adr'`

- [ ] **Step 3: Implement `checks/decisions_adr.py`**

```python
from __future__ import annotations

import re
from pathlib import Path

from common import Finding

DECISION_NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+-decision\.md$")
ADR_NAME_RE = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")


def check_decision_naming(repo_root: Path, thresholds: dict) -> list[Finding]:
    pd = repo_root / "product-development"
    findings = []
    if pd.exists():
        for path in sorted(pd.rglob("*-decision.md")):
            rel = path.relative_to(repo_root).as_posix()
            if not DECISION_NAME_RE.match(path.name):
                findings.append(Finding("decisions-naming-convention", rel,
                    f"{path.name} does not match YYYY-MM-DD-{{topic}}-decision.md", rel))
    archive_dir = pd / "decisions"
    if archive_dir.exists():
        findings.append(Finding("decisions-naming-convention", "product-development/decisions",
            "a top-level product-development/decisions/ archive exists; decision files must live next to what they decided",
            "product-development/decisions"))
    return findings


def check_adr_numbering(repo_root: Path, thresholds: dict) -> list[Finding]:
    adr_dir = repo_root / "docs/adr"
    if not adr_dir.exists():
        return []
    numbers: dict[str, Path] = {}
    findings = []
    for path in sorted(adr_dir.glob("*.md")):
        m = ADR_NAME_RE.match(path.name)
        if not m:
            continue
        n = m.group(1)
        if n in numbers:
            findings.append(Finding("adr-numbering", n,
                f"ADR number {n} used by both {numbers[n].name} and {path.name}", str(path)))
        else:
            numbers[n] = path
    expected = {f"{i:04d}" for i in range(1, len(numbers) + 1)}
    for missing in sorted(expected - set(numbers)):
        findings.append(Finding("adr-numbering", missing,
            f"ADR number {missing} is missing (gap in sequence 0001..{len(numbers):04d})", str(adr_dir)))
    return findings


CHECKS = {
    "decisions-naming-convention": check_decision_naming,
    "adr-numbering": check_adr_numbering,
}
```

- [ ] **Step 4: Add to `config.yaml`**

```yaml
  decisions-naming-convention: true
  adr-numbering: true
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/integrity_checks/test_decisions_adr.py -v`
Expected: PASS (6 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/integrity-checks/checks/decisions_adr.py scripts/integrity-checks/config.yaml tests/integrity_checks/test_decisions_adr.py
git commit -m "feat: add decision-file naming and ADR numbering checks"
```

---

### Task 7: `checks/process_health.py` — backlog staleness (bug investigations, papercuts, skill gaps)

Reads: `product-development/engineering/bug-investigations/**/investigation-plan.md`, `PAPERCUTS.md`, `SKILL-GAPS.md`. Grouped together as the "how long has this backlog item sat open" pattern this repo's own docs already ask a human to do periodically by hand.

**Files:**
- Create: `scripts/integrity-checks/checks/process_health.py`
- Test: `tests/integrity_checks/test_process_health.py`
- Modify: `scripts/integrity-checks/config.yaml`

**Interfaces:**
- Consumes: Task 1's `Finding`.
- Produces: `CHECKS` dict with keys `process-stale-bug-investigations`, `process-papercuts-digest`, `process-skillgaps-digest`.

- [ ] **Step 1: Write the failing tests**

`tests/integrity_checks/test_process_health.py`:

```python
from datetime import date, timedelta
from pathlib import Path

from checks.process_health import (
    check_papercuts_digest,
    check_skillgaps_digest,
    check_stale_bug_investigations,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_stale_bug_investigation_flagged_when_incomplete_and_old(tmp_path: Path):
    old_date = (date.today() - timedelta(days=30)).isoformat()
    _write(tmp_path / "product-development/engineering/bug-investigations/area/bug-x/investigation-plan.md",
        "| Field | Value |\n|---|---|\n"
        f"| Run Date | {old_date} |\n| Status | In Progress |\n")
    findings = check_stale_bug_investigations(tmp_path, {"stale-bug-investigation-days": 14})
    assert findings


def test_stale_bug_investigation_clean_when_complete(tmp_path: Path):
    old_date = (date.today() - timedelta(days=30)).isoformat()
    _write(tmp_path / "product-development/engineering/bug-investigations/area/bug-x/investigation-plan.md",
        "| Field | Value |\n|---|---|\n"
        f"| Run Date | {old_date} |\n| Status | Complete |\n")
    assert check_stale_bug_investigations(tmp_path, {"stale-bug-investigation-days": 14}) == []


def test_papercuts_digest_flags_repeat_offender_tag(tmp_path: Path):
    _write(tmp_path / "PAPERCUTS.md",
        "## Log\n\n"
        "- **2026-01-01** [tooling] first thing. (minor, unresolved)\n"
        "- **2026-01-02** [tooling] second thing. (minor, unresolved)\n")
    findings = check_papercuts_digest(tmp_path, {})
    assert any(f.key == "tooling" for f in findings)


def test_papercuts_digest_clean_for_single_unresolved_tag(tmp_path: Path):
    _write(tmp_path / "PAPERCUTS.md",
        "## Log\n\n- **2026-01-01** [tooling] only one. (minor, unresolved)\n")
    assert check_papercuts_digest(tmp_path, {}) == []


def test_skillgaps_digest_flags_repeat_offender_area(tmp_path: Path):
    _write(tmp_path / "SKILL-GAPS.md",
        "## Log\n\n"
        "- **2026-01-01** [product] first recipe. (seen-1x, unresolved)\n"
        "- **2026-01-02** [product] second recipe. (seen-1x, unresolved)\n")
    findings = check_skillgaps_digest(tmp_path, {})
    assert any(f.key == "product" for f in findings)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integrity_checks/test_process_health.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'checks.process_health'`

- [ ] **Step 3: Implement `checks/process_health.py`**

```python
from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from common import Finding

LOG_LINE_RE = re.compile(
    r"^-\s+\*\*(\d{4}-\d{2}-\d{2})\*\*\s+\[([\w-]+)\].*\(([\w-]+),\s*(unresolved|resolved)\)\s*$"
)
STATUS_ROW_RE = re.compile(r"\|\s*Status\s*\|\s*([^\n|]+)\|")
RUN_DATE_RE = re.compile(r"\|\s*Run Date\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|")


def check_stale_bug_investigations(repo_root: Path, thresholds: dict) -> list[Finding]:
    stale_days = thresholds.get("stale-bug-investigation-days", 14)
    today = date.today()
    base = repo_root / "product-development/engineering/bug-investigations"
    if not base.exists():
        return []
    findings = []
    for path in sorted(base.rglob("investigation-plan.md")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        status_m = STATUS_ROW_RE.search(text)
        status = status_m.group(1).strip() if status_m else ""
        date_m = RUN_DATE_RE.search(text)
        if status == "Complete" or not date_m:
            continue
        days = (today - date.fromisoformat(date_m.group(1))).days
        if days > stale_days:
            findings.append(Finding("process-stale-bug-investigations", rel,
                f"{rel} has Status '{status}' since {date_m.group(1)} ({days}d, threshold {stale_days}d)", rel))
    return findings


def _digest(repo_root: Path, log_path: str, check_id: str) -> list[Finding]:
    path = repo_root / log_path
    if not path.exists():
        return []
    by_tag = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        m = LOG_LINE_RE.match(line.strip())
        if not m or m.group(4) != "unresolved":
            continue
        by_tag[m.group(2)].append(line.strip())
    findings = []
    for tag, lines in sorted(by_tag.items()):
        if len(lines) >= 2:
            findings.append(Finding(check_id, tag,
                f"{len(lines)} unresolved entries tagged [{tag}] in {log_path} -- repeat offender", log_path))
    return findings


def check_papercuts_digest(repo_root: Path, thresholds: dict) -> list[Finding]:
    return _digest(repo_root, "PAPERCUTS.md", "process-papercuts-digest")


def check_skillgaps_digest(repo_root: Path, thresholds: dict) -> list[Finding]:
    return _digest(repo_root, "SKILL-GAPS.md", "process-skillgaps-digest")


CHECKS = {
    "process-stale-bug-investigations": check_stale_bug_investigations,
    "process-papercuts-digest": check_papercuts_digest,
    "process-skillgaps-digest": check_skillgaps_digest,
}
```

- [ ] **Step 4: Add to `config.yaml`**

```yaml
  process-stale-bug-investigations: true
  process-papercuts-digest: true
  process-skillgaps-digest: true
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/integrity_checks/test_process_health.py -v`
Expected: PASS (5 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/integrity-checks/checks/process_health.py scripts/integrity-checks/config.yaml tests/integrity_checks/test_process_health.py
git commit -m "feat: add bug-investigation, papercuts, and skill-gaps staleness checks"
```

---

### Task 8: `summarize.py` — staleness/summary report

**Files:**
- Create: `scripts/integrity-checks/summarize.py`
- Test: `tests/integrity_checks/test_summarize.py`

**Interfaces:**
- Consumes: Task 1's `load_status`, `days_open`.
- Produces: `build_summary(status: dict, today: date) -> str`; `main(argv=None) -> int`, which writes `reports/summary.md`. This is the file whose delivery outside the repo is out of scope for this plan (per Global Constraints) — it's the artifact a future, separate integration would post somewhere.

- [ ] **Step 1: Write the failing tests**

`tests/integrity_checks/test_summarize.py`:

```python
from datetime import date
from pathlib import Path

from summarize import build_summary, main


def test_build_summary_reports_no_findings_when_empty():
    text = build_summary({"findings": {}}, date(2026, 1, 10))
    assert "No open findings." in text


def test_build_summary_includes_check_counts_and_oldest_finding():
    status = {"findings": {
        "chk-a::k1": {"check_id": "chk-a", "key": "k1", "message": "old one",
                      "file": "", "first_detected": "2026-01-01", "last_seen": "2026-01-10"},
        "chk-a::k2": {"check_id": "chk-a", "key": "k2", "message": "new one",
                      "file": "", "first_detected": "2026-01-09", "last_seen": "2026-01-10"},
    }}
    text = build_summary(status, date(2026, 1, 10))
    assert "chk-a | 2" in text
    assert "old one" in text
    lines = text.splitlines()
    old_line = next(l for l in lines if "old one" in l)
    new_line = next(l for l in lines if "new one" in l)
    assert lines.index(old_line) < lines.index(new_line)


def test_main_writes_summary_file(tmp_path: Path):
    status_path = tmp_path / "status.json"
    status_path.write_text('{"generated_at": "2026-01-10", "findings": {}}', encoding="utf-8")
    output_path = tmp_path / "summary.md"
    code = main(["--status", str(status_path), "--output", str(output_path)])
    assert code == 0
    assert output_path.exists()
    assert "No open findings." in output_path.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integrity_checks/test_summarize.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'summarize'`

- [ ] **Step 3: Implement `summarize.py`**

```python
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from common import days_open, load_status


def build_summary(status: dict, today: date) -> str:
    findings = status.get("findings", {})
    by_check = defaultdict(list)
    for record in findings.values():
        by_check[record["check_id"]].append(record)

    lines = [
        "# Integrity Check Summary", "",
        f"Generated: {today.isoformat()}",
        f"Total open findings: {len(findings)}", "",
    ]
    if not findings:
        lines.append("No open findings.")
        return "\n".join(lines) + "\n"

    lines += ["## By check", "", "| Check | Open findings |", "|---|---|"]
    for check_id in sorted(by_check):
        lines.append(f"| {check_id} | {len(by_check[check_id])} |")

    lines += ["", "## Longest open", "", "| Days open | Check | Key | Message |", "|---|---|---|---|"]
    ranked = sorted(findings.values(), key=lambda r: days_open(r, today), reverse=True)
    for record in ranked[:20]:
        lines.append(f"| {days_open(record, today)} | {record['check_id']} | {record['key']} | {record['message']} |")

    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    status_path = Path(args.status) if args.status else Path(__file__).parent / "reports" / "status.json"
    output_path = Path(args.output) if args.output else Path(__file__).parent / "reports" / "summary.md"

    summary = build_summary(load_status(status_path), date.today())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/integrity_checks/test_summarize.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/integrity-checks/summarize.py tests/integrity_checks/test_summarize.py
git commit -m "feat: add integrity-check summary report generator"
```

---

### Task 9: GitHub Actions cron workflow + README

**Files:**
- Create: `.github/workflows/integrity-checks.yml`
- Create: `scripts/integrity-checks/README.md`

**Interfaces:**
- Consumes: Tasks 1-8 (`run_checks.py`, `summarize.py`, `config.yaml`, `requirements.txt`).
- Produces: the scheduled entry point. This is the "mini-instruction for GitHub Actions cron" — the README documents the one-time repo setting a human must change by hand (Actions can't grant itself write access).

- [ ] **Step 1: Write the workflow**

`.github/workflows/integrity-checks.yml`:

```yaml
name: Integrity Checks

on:
  schedule:
    - cron: "0 8 * * *"
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  run-checks:
    runs-on: ubuntu-latest
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r scripts/integrity-checks/requirements.txt

      - name: Run checks
        id: run_checks
        continue-on-error: true
        run: python scripts/integrity-checks/run_checks.py --repo-root .

      - name: Build summary
        run: python scripts/integrity-checks/summarize.py

      - name: Commit updated reports
        run: |
          git config user.name "integrity-check-bot"
          git config user.email "actions@github.com"
          git add scripts/integrity-checks/reports/status.json scripts/integrity-checks/reports/summary.md
          git diff --cached --quiet || (git commit -m "chore: update integrity check reports" && git push)

      - name: Fail the job if open findings exist
        if: steps.run_checks.outcome == 'failure'
        run: exit 1
```

- [ ] **Step 2: Write `scripts/integrity-checks/README.md`**

```markdown
# Integrity Checks

Config-driven Python checks for structural/process integrity across the discovery -> PRD -> engineering -> decision pipeline (e.g. hypotheses with no supporting signal, PRDs missing required sections, feature-index.yaml drift, stale backlog entries). See `docs/architecture.md` for how this fits the repo's deterministic-policy-layer pattern.

## Run locally

```bash
pip install -r scripts/integrity-checks/requirements.txt
python scripts/integrity-checks/run_checks.py
python scripts/integrity-checks/summarize.py
cat scripts/integrity-checks/reports/summary.md
```

`run_checks.py` exits 1 if any check has an open finding and `fail-on-findings: true` in `config.yaml` (the default) -- same convention as `scripts/check-references.ps1`.

## Enable / disable a check

Edit `config.yaml`'s `checks:` map -- `true` runs it, `false` skips it. Thresholds (staleness day counts) live in the same file under `thresholds:`.

`feature-index-broken-tickets` ships disabled: this template repo's example ticket numbers aren't real GitHub issues. Flip it to `true` once your `feature-index.yaml` has real ticket references and `gh` is authenticated against your real repo.

## How staleness is tracked

Every run reads `reports/status.json` from the previous run, so a finding that already existed keeps its original `first_detected` date instead of resetting to today. A finding no longer produced by any check is dropped (treated as resolved) rather than kept around. `summarize.py` reads the same file and computes "days open" from `first_detected`. Both `reports/status.json` and `reports/summary.md` are committed back to the repo by the GitHub Actions workflow, so they're visible in a normal `git log`/diff without any external system.

## Setting up the GitHub Actions cron

1. This repo's `.github/workflows/integrity-checks.yml` already defines the schedule (`0 8 * * *`, i.e. 08:00 UTC daily) and a `workflow_dispatch` trigger for running it on demand from the Actions tab.
2. **One manual setting is required**, because a workflow can't grant itself permission to push commits: go to **Settings -> Actions -> General -> Workflow permissions** and select **"Read and write permissions"**, then Save. Without this, the "Commit updated reports" step fails with a 403.
3. No secrets need to be added by hand -- `secrets.GITHUB_TOKEN` is provided automatically by GitHub Actions and is enough for both `git push` and the `gh` CLI calls used by `feature-index-broken-tickets` (once enabled).
4. To change the schedule, edit the `cron:` line (standard 5-field cron, UTC). To run it immediately without waiting for the schedule, use **Actions -> Integrity Checks -> Run workflow**.
5. Posting `reports/summary.md` anywhere outside this repo (Slack, email, etc.) is intentionally not built here -- a red workflow run in the Actions tab is the only built-in signal. Add a separate step (or a Claude Code scheduled routine that reads `reports/summary.md`) if you want that.
```

- [ ] **Step 3: Validate the workflow YAML parses**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/integrity-checks.yml', encoding='utf-8'))"`
Expected: no output, exit code 0

- [ ] **Step 4: Verify references resolve**

Run: `powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/integrity-checks.yml scripts/integrity-checks/README.md
git commit -m "ci: add scheduled integrity-checks workflow and setup instructions"
```

---

### Task 10: End-to-end dry run against the real repo

**Files:** none created; this task exercises Tasks 1-9 for real and commits the first real `reports/status.json` + `reports/summary.md`. May also add an entry to `PAPERCUTS.md` if the dry run surfaces a real gap.

**Interfaces:**
- Consumes: everything from Tasks 1-9.
- Produces: confirmation the whole suite runs cleanly against this repo's real content, plus a real first snapshot of `reports/`.

- [ ] **Step 1: Run the full test suite**

Run: `pytest scripts/integrity-checks tests/integrity_checks -q`
Expected: all tests pass

- [ ] **Step 2: Run the checks for real**

Run: `python scripts/integrity-checks/run_checks.py`
Record the real output. Expect at least the pre-existing `shared-components-prd.md` missing-`## Sources` gap (logged in `PAPERCUTS.md`, 2026-09-13) to surface via `prd-missing-sections` — confirms the check reasons correctly about a known, already-documented gap rather than only synthetic fixtures.

- [ ] **Step 3: Build and review the summary**

Run: `python scripts/integrity-checks/summarize.py`
Read `scripts/integrity-checks/reports/summary.md`. For each finding, confirm it's either a real, actionable gap or expected noise already called out in this plan's Global Constraints (`feature-index-broken-tickets` is disabled, so it should contribute nothing).

- [ ] **Step 4: Log any new friction found**

If the dry run surfaces friction that isn't already covered by an existing `PAPERCUTS.md` entry (e.g. a doc inconsistency the checks exposed), append a new entry to `PAPERCUTS.md`'s Log section per its documented format. If nothing new is found beyond what Step 2 already expected, skip this step.

- [ ] **Step 5: Commit the first real report snapshot**

```bash
git add scripts/integrity-checks/reports/status.json scripts/integrity-checks/reports/summary.md
git commit -m "chore: commit first real integrity-check report snapshot"
```

---

### Task 11: Reconcile `ROADMAP.md`

**Files:**
- Modify: `ROADMAP.md` (Already shipped section)

**Interfaces:**
- Consumes: the shipped capability from Tasks 1-10.
- Produces: an accurate roadmap reflecting the new capability.

- [ ] **Step 1: Add the capability to "Already shipped"**

Append to the end of the "Already shipped" list:

```markdown
- **Repo integrity checks** — `scripts/integrity-checks/` runs a config-driven suite of Python checks (Insights/Opportunity/Hypothesis chain integrity, feature-index.yaml join-table completeness, PRD content completeness and staleness, decision/ADR naming conventions, backlog staleness for bug investigations/PAPERCUTS.md/SKILL-GAPS.md) on a daily GitHub Actions schedule (`.github/workflows/integrity-checks.yml`), committing `reports/status.json` (first-detected tracking) and `reports/summary.md` back to the repo. See `scripts/integrity-checks/README.md`.
```

- [ ] **Step 2: Verify references resolve**

Run: `powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1`
Expected: `No broken references found.`

- [ ] **Step 3: Commit**

```bash
git add ROADMAP.md
git commit -m "docs: reconcile ROADMAP with repo integrity checks"
```
