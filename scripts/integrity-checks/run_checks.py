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
