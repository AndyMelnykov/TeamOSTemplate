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
