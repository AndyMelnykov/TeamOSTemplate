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
