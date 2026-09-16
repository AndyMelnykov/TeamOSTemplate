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
