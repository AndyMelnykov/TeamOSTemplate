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
