from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "signals"))

import signals  # noqa: E402  (scripts/signals/signals.py, the store's only writer)
from common import Finding  # noqa: E402

HYP_HEADING_RE = re.compile(r"^#\s+(HYP-[A-Z]+-\d+)", re.MULTILINE)
STORE_FILE = signals.STORE.as_posix()


def _hypothesis_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / signals.HYPOTHESES_ROOT).rglob("*-hypothesis.md"))


def _rel(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def check_invalid_row(repo_root: Path, thresholds: dict) -> list[Finding]:
    findings = []
    seen: set[str] = set()
    for line, row in enumerate(signals.load(repo_root), start=2):
        key = row.signal_id or f"line {line}"
        problems = signals.validate(row.__dict__, repo_root)
        if not row.signal_id:
            problems.append("signal_id is required")
        elif row.signal_id in seen:
            problems.append("duplicate signal_id")
        seen.add(row.signal_id)
        if problems:
            findings.append(Finding("signals-invalid-row", key,
                f"{key} is invalid: {'; '.join(problems)}", STORE_FILE))
    return findings


def check_unknown_citation(repo_root: Path, thresholds: dict) -> list[Finding]:
    known = {s.signal_id for s in signals.load(repo_root)}
    findings = []
    for signal_id, paths in sorted(signals.cited(repo_root).items()):
        if signal_id in known:
            continue
        for rel in paths:
            findings.append(Finding("signals-unknown-citation", f"{rel}::{signal_id}",
                f"{Path(rel).name} cites {signal_id}, which is not in signals.csv", rel))
    return findings


def check_orphan_hypothesis(repo_root: Path, thresholds: dict) -> list[Finding]:
    findings = []
    for path in _hypothesis_files(repo_root):
        if not signals.SIGNAL_ID_IN_TEXT.search(path.read_text(encoding="utf-8")):
            rel = _rel(repo_root, path)
            findings.append(Finding("signals-orphan-hypothesis", rel,
                f"{path.name} cites no SIG- signal", rel))
    return findings


def check_unassigned_stale(repo_root: Path, thresholds: dict) -> list[Finding]:
    stale_days = thresholds.get("unassigned-signal-days", 30)
    today = date.today()
    findings = []
    for s in signals.unassigned(repo_root):
        try:
            age = (today - date.fromisoformat(s.date)).days
        except ValueError:
            continue  # a bad date is signals-invalid-row's finding
        if age > stale_days:
            findings.append(Finding("signals-unassigned-stale", s.signal_id,
                f"{s.signal_id} has been cited by no hypothesis since {s.date} ({age}d, threshold {stale_days}d)",
                STORE_FILE))
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


def check_unindexed_hypothesis(repo_root: Path, thresholds: dict) -> list[Finding]:
    index_path = repo_root / "product-development/feature-index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    referenced = _flatten_md_paths(index)
    findings = []
    for path in _hypothesis_files(repo_root):
        rel = path.relative_to(repo_root / "product-development").as_posix()
        if rel not in referenced:
            findings.append(Finding("signals-unindexed-hypothesis", rel,
                f"{path.name} is not referenced by any feature-index.yaml entry", str(path)))
    return findings


def check_id_collisions(repo_root: Path, thresholds: dict) -> list[Finding]:
    seen: dict[str, Path] = {}
    findings = []
    for path in _hypothesis_files(repo_root):
        m = HYP_HEADING_RE.search(path.read_text(encoding="utf-8"))
        if not m:
            continue
        hyp_id = m.group(1)
        if hyp_id in seen:
            findings.append(Finding("signals-id-collisions", hyp_id,
                f"{hyp_id} appears in both {seen[hyp_id].name} and {path.name}", str(path)))
        else:
            seen[hyp_id] = path
    return findings


CHECKS = {
    "signals-invalid-row": check_invalid_row,
    "signals-unknown-citation": check_unknown_citation,
    "signals-orphan-hypothesis": check_orphan_hypothesis,
    "signals-unassigned-stale": check_unassigned_stale,
    "signals-unindexed-hypothesis": check_unindexed_hypothesis,
    "signals-id-collisions": check_id_collisions,
}
