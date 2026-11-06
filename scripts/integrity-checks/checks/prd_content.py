from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

from common import Finding

REQUIRED_SECTIONS = [
    "Overview", "User Stories", "Requirements", "Acceptance Criteria", "Design",
    "Technical Considerations", "Launch Plan", "Sources",
]

# Statuses at which acceptance-criteria and execution-path rules are enforced.
# Draft is excluded (only the missing-section finding applies); Archived is history.
ENFORCED_STATUSES = {"In Review", "Approved", "Shipped"}
VERIFY_BY_VALUES = {"automated-test", "manual-qa", "analytics"}
EXECUTION_PATHS = {"agent-direct", "engineering-mediated"}

_UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")
_SEPARATOR_CELL = re.compile(r"^:?-+:?$")


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


def _load_signal_ids(repo_root: Path) -> set[str]:
    path = repo_root / "product-development/signals/signals.csv"
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as f:
        return {row["signal_id"] for row in csv.DictReader(f)}


def check_sources_citation_validity(repo_root: Path, thresholds: dict) -> list[Finding]:
    signal_ids = _load_signal_ids(repo_root)
    findings = []
    for path in _prd_files(repo_root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        m = re.search(r"^##\s+Sources\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
        section = m.group(1) if m else ""
        for cited in re.findall(r"(?<![\w-])((?:SIG|INS|SRC)-\d{3,})(?![\w-])", section):
            if cited.startswith("SIG-"):
                if cited in signal_ids:
                    continue
                message = f"{path.name} cites {cited} in ## Sources, which does not exist"
            else:
                message = f"{path.name} cites retired id {cited} in ## Sources; cite the SIG- signal instead"
            findings.append(Finding("prd-sources-citation-validity", f"{rel}::{cited}", message, rel))
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


def _section(text: str, name: str) -> str:
    m = re.search(rf"^##\s+{re.escape(name)}\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def _p0_section(text: str) -> str:
    m = re.search(r"^###\s+Must Have \(P0\)\s*$(.*?)(?=^#{2,3}\s|\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def _split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [cell.strip().replace("\\|", "|") for cell in _UNESCAPED_PIPE.split(line)]


def parse_table(section_text: str) -> list[dict[str, str]]:
    """Parse the first Markdown table in section_text into one dict per body row.

    Cells split on unescaped `|`; an escaped `\\|` stays in the cell as a literal `|`.
    """
    lines = [ln for ln in section_text.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return []
    header = _split_row(lines[0])
    rows = []
    for line in lines[1:]:
        cells = _split_row(line)
        if all(_SEPARATOR_CELL.match(c) for c in cells if c):
            continue
        cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return rows


def _enforced(text: str) -> bool:
    return _field(text, "Status") in ENFORCED_STATUSES


def _ac_rows(text: str) -> list[dict[str, str]]:
    return parse_table(_section(text, "Acceptance Criteria"))


def check_acceptance_criteria(repo_root: Path, thresholds: dict) -> list[Finding]:
    findings = []
    for path in _prd_files(repo_root):
        text = path.read_text(encoding="utf-8")
        if not _enforced(text):
            continue
        rel = path.relative_to(repo_root).as_posix()
        rows = _ac_rows(text)
        seen: dict[str, int] = {}
        covered: set[str] = set()
        for row in rows:
            ac_id = row.get("ID", "")
            seen[ac_id] = seen.get(ac_id, 0) + 1
            problems = []
            if not re.fullmatch(r"AC-\d+", ac_id):
                problems.append(f"id '{ac_id}' is not of the form AC-<n>")
            if seen[ac_id] > 1:
                problems.append("duplicate id")
            problems += [f"empty {col}" for col in ("Given", "When", "Then", "Covers") if not row.get(col, "")]
            verify = row.get("Verify by", "")
            if verify not in VERIFY_BY_VALUES:
                problems.append(f"invalid Verify by '{verify}' (use automated-test, manual-qa or analytics)")
            if problems:
                key = f"{rel}::{ac_id}" if seen[ac_id] == 1 else f"{rel}::{ac_id}#{seen[ac_id]}"
                findings.append(Finding("prd-acceptance-criteria", key,
                    f"{path.name} {ac_id or '(no id)'}: {'; '.join(problems)}", rel))
            covered.update(c.strip() for c in row.get("Covers", "").split(","))
        p0_ids = [r.get("ID", "") for r in parse_table(_p0_section(text))]
        for p0 in p0_ids:
            if re.fullmatch(r"P0-\d+", p0) and p0 not in covered:
                findings.append(Finding("prd-acceptance-criteria", f"{rel}::uncovered::{p0}",
                    f"{path.name}: must-have {p0} is not covered by any acceptance criterion", rel))
        if not rows and not p0_ids:
            findings.append(Finding("prd-acceptance-criteria", f"{rel}::no-criteria",
                f"{path.name} is {_field(text, 'Status')} but has no acceptance criteria", rel))
    return findings


def check_execution_path(repo_root: Path, thresholds: dict) -> list[Finding]:
    findings = []
    for path in _prd_files(repo_root):
        text = path.read_text(encoding="utf-8")
        if not _enforced(text):
            continue
        rel = path.relative_to(repo_root).as_posix()
        value = _field(text, "Execution Path").strip("`")
        if value not in EXECUTION_PATHS:
            findings.append(Finding("prd-execution-path", rel,
                f"{path.name} has Execution Path '{value}'; must be agent-direct or engineering-mediated", rel))
            continue
        if value != "agent-direct":
            continue
        reasons = []
        tier = _field(text, "Review Tier")
        if tier != "Local":
            reasons.append(f"Review Tier is '{tier}', not Local")
        if any(r.get("Verify by") == "analytics" for r in _ac_rows(text)):
            reasons.append("an acceptance criterion is verified by analytics")
        if reasons:
            findings.append(Finding("prd-execution-path", rel,
                f"{path.name} is agent-direct but {' and '.join(reasons)}; use engineering-mediated", rel))
    return findings


CHECKS = {
    "prd-missing-sections": check_missing_sections,
    "prd-acceptance-criteria": check_acceptance_criteria,
    "prd-execution-path": check_execution_path,
    "prd-strategy-review-decision-gate": check_strategy_review_decision_gate,
    "prd-sources-citation-validity": check_sources_citation_validity,
    "prd-stale-status": check_stale_status,
}
