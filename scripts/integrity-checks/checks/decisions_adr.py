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
