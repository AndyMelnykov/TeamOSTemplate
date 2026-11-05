"""Hypotheses: parse, derived reach, validation-path recommendation.

Usage:
    python scripts/signals/hypotheses.py list [--repo-root .]
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from signals import HYPOTHESES_ROOT, SIGNAL_ID_IN_TEXT, Signal, load

STATUSES = ("proposed", "testing", "validated", "invalidated", "in-prd", "shipped")
CONFIDENCES = ("low", "medium", "high")
EFFORTS = ("cheap", "costly")
VALIDATION_PATHS = ("ab-test", "prototype", "survey", "interviews")

METRICS_REFERENCE = Path("reference/metrics.md")
METRICS_DOCS = Path("product-development/analytics/metrics")

# Required at every status / from `testing` onward. "?" counts as present.
ALWAYS_FIELDS = ("Status", "Confidence", "Effort", "Target metric")
ALWAYS_SECTIONS = ("Problem", "Signals")
TESTING_FIELDS = ("Validation path", "Last Updated")
TESTING_SECTIONS = ("Test", "Success criteria")

_TITLE_ID = re.compile(r"^#\s+(HYP-[A-Z0-9]+-\d{3,})\b", re.MULTILINE)
_SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Hypothesis:
    hyp_id: str
    path: Path
    status: str
    confidence: str
    effort: str
    validation_path: str
    target_metric: str
    last_updated: str
    prd: str
    signal_ids: list[str]
    sections: set[str]
    missing: list[str]  # fields/sections required at this status


def _field(text: str, name: str) -> str:
    m = re.search(rf"\*\*{re.escape(name)}\*\*[ \t]*\|[ \t]*([^\n|]*)", text)
    return m.group(1).strip().strip("`").strip() if m else ""


def _has_field(text: str, name: str) -> bool:
    return bool(_field(text, name))


def hypothesis_files(repo_root: Path) -> list[Path]:
    return sorted((Path(repo_root) / HYPOTHESES_ROOT).rglob("*-hypothesis.md"))


def parse(path: Path) -> Hypothesis:
    text = Path(path).read_text(encoding="utf-8")
    title = _TITLE_ID.search(text)
    sections = set(_SECTION.findall(text))
    status = _field(text, "Status")

    fields = list(ALWAYS_FIELDS)
    required_sections = list(ALWAYS_SECTIONS)
    if status in STATUSES and status != "proposed":
        fields += TESTING_FIELDS
        required_sections += TESTING_SECTIONS
    missing = [f"field: {f}" for f in fields if not _has_field(text, f)]
    missing += [f"section: {s}" for s in required_sections if s not in sections]

    return Hypothesis(
        hyp_id=title.group(1) if title else "",
        path=Path(path),
        status=status,
        confidence=_field(text, "Confidence"),
        effort=_field(text, "Effort"),
        validation_path=_field(text, "Validation path"),
        target_metric=_field(text, "Target metric"),
        last_updated=_field(text, "Last Updated"),
        prd=_field(text, "PRD"),
        signal_ids=list(dict.fromkeys(SIGNAL_ID_IN_TEXT.findall(text))),
        sections=sections,
        missing=missing,
    )


def reach(h: Hypothesis, signals: dict[str, Signal]) -> tuple[int, int]:
    """(cited signals found in the store, distinct accounts among them)."""
    found = [signals[i] for i in h.signal_ids if i in signals]
    return len(found), len({s.account for s in found if s.account})


def _names(label: str) -> set[str]:
    """'Extraction Success Rate (ESR)' -> full name, name without the parenthetical, abbreviation."""
    label = re.sub(r"[*`]", "", label).strip().lower()
    if not label:
        return set()
    names = {label}
    m = re.fullmatch(r"(.*?)\s*\(([^)]+)\)", label)
    if m:
        names |= {n for n in (m.group(1).strip(), m.group(2).strip()) if n}
    return names


def instrumented_metrics(repo_root: Path) -> set[str]:
    """Lower-cased metric names and abbreviations from reference/metrics.md and analytics/metrics/**."""
    root = Path(repo_root)
    found: set[str] = set()
    reference = root / METRICS_REFERENCE
    if reference.exists():
        for m in re.finditer(r"^\|\s*(\*\*[^|]+?\*\*)\s*\|", reference.read_text(encoding="utf-8"), re.MULTILINE):
            found |= _names(m.group(1))
    docs = root / METRICS_DOCS
    if docs.exists():
        for doc in docs.rglob("*.md"):
            for m in re.finditer(r"^###\s+(.+?)\s*$", doc.read_text(encoding="utf-8"), re.MULTILINE):
                found |= _names(m.group(1))
    return found


def recommend(h: Hypothesis, instrumented: set[str]) -> tuple[str, str]:
    """(path, reason). A recommendation only; a human chooses. ("", reason) when effort is unknown."""
    if h.effort not in EFFORTS:
        return "", "effort unknown (set Effort to cheap or costly)"
    alternatives = "alternatives: survey, interviews"
    if h.effort == "costly":
        return "prototype", f"effort is costly, so validate before building ({alternatives})"
    if _names(h.target_metric) & instrumented:
        return "ab-test", f"cheap to build and {h.target_metric} is instrumented"
    return "prototype", (f"cheap, but target metric {h.target_metric or '(none)'!r} is not instrumented, "
                         f"so an A/B test cannot read it ({alternatives})")


def _cmd_list(args) -> int:
    signals = {s.signal_id: s for s in load(args.repo_root)}
    instrumented = instrumented_metrics(args.repo_root)
    rows = [("ID", "STATUS", "SIGNALS", "ACCOUNTS", "CONFIDENCE", "EFFORT", "RECOMMENDED")]
    for path in hypothesis_files(args.repo_root):
        h = parse(path)
        n_signals, n_accounts = reach(h, signals)
        rec, _ = recommend(h, instrumented)
        rows.append((h.hyp_id or path.name, h.status or "-", str(n_signals), str(n_accounts),
                     h.confidence or "-", h.effort or "-", rec or "-"))
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    for r in rows:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hypotheses.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("list")
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.set_defaults(handler=_cmd_list)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
