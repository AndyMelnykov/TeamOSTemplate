"""One-off: migrate product/Insights/ (insights.csv + sources.csv) into signals.csv.

Usage: python scripts/signals/migrate_insights.py --repo-root . [--dry-run]

One signal per sources.csv row. INS-NNN / SRC-NNN citations across the repo are rewritten to
the SIG- id of the signal built from that source. Historical docs are left as written.
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import signals

INSIGHTS_DIR = "product-development/product/Insights"
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".csv"}
SKIP_DIRS = {".git", ".superpowers", "node_modules", "__pycache__", ".venv", "venv"}
EXCLUDED = (
    "docs/superpowers/plans/*",
    "docs/gap-analysis-*.md",
    "docs/adr/*",
    "docs/handoffs/*",
    "scripts/integrity-checks/reports/*",  # generated; the next run_checks run rewrites it
    f"{INSIGHTS_DIR}/*",
    signals.STORE.as_posix(),
)
CITATION = re.compile(r"(?<![\w-])(?:INS|SRC)-\d{3}(?![\w-])")
SOURCE_TYPE_MAP = {"customer-research-reddit": "community", "customer-support": "support"}


@dataclass
class MigrationReport:
    signals: int
    files_rewritten: list[str]


def rewrite_citations(text: str, mapping: dict[str, str]) -> str:
    return CITATION.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)


def _read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _number(identifier: str) -> int:
    return int(identifier.split("-")[1])


def _signal_rows(insights: list[dict], sources: list[dict]) -> list[dict]:
    by_id = {i["insight_id"]: i for i in insights}
    rows = []
    for src in sorted(sources, key=lambda s: (_number(s["insight_id"]), _number(s["source_id"]))):
        insight = by_id.get(src["insight_id"], {})
        evidence = src["evidence"]
        detail = insight.get("product_insight", "")
        if len(evidence) > signals.SUMMARY_MAX:
            detail = f"{detail}\n\nEvidence: {evidence}".strip()
        raw_type = src["source_type"]
        rows.append({
            "date": src["date"],
            "source_type": raw_type if raw_type in signals.SOURCE_TYPES
            else SOURCE_TYPE_MAP.get(raw_type, "other"),
            "source_ref": src["source_ref"],
            "summary": evidence[:signals.SUMMARY_MAX],
            "detail": detail,
            "tags": insight.get("theme", ""),
        })
    return rows


def _candidate_files(root: Path) -> list[Path]:
    if (root / ".git").exists():
        out = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True,
                             capture_output=True, text=True, encoding="utf-8").stdout
        paths = [root / p for p in out.split("\0") if p]
    else:
        paths = [p for p in root.rglob("*") if p.is_file()
                 and not SKIP_DIRS.intersection(p.relative_to(root).parts)]
    result = []
    for p in paths:
        rel = p.relative_to(root).as_posix()
        if p.suffix in TEXT_SUFFIXES and p.is_file() \
                and not any(fnmatch.fnmatch(rel, pat) for pat in EXCLUDED):
            result.append(p)
    return sorted(result)


def migrate(repo_root: Path, dry_run: bool = False, keep_insights: bool = False) -> MigrationReport:
    root = Path(repo_root)
    insights_dir = root / INSIGHTS_DIR
    if not (insights_dir / "sources.csv").exists():
        return MigrationReport(0, [])

    rows = _signal_rows(_read_csv(insights_dir / "insights.csv"), _read_csv(insights_dir / "sources.csv"))
    sources = sorted(_read_csv(insights_dir / "sources.csv"),
                     key=lambda s: (_number(s["insight_id"]), _number(s["source_id"])))

    # Dry runs allocate ids in a scratch copy of the store, so the report matches a real run.
    with tempfile.TemporaryDirectory() as scratch:
        target = Path(scratch) if dry_run else root
        if dry_run and (root / signals.STORE).exists():
            (Path(scratch) / signals.STORE).parent.mkdir(parents=True)
            shutil.copy(root / signals.STORE, Path(scratch) / signals.STORE)
        result = signals.add(target, rows)
        if result.invalid:
            detail = "; ".join(f"row {i}: {', '.join(p)}" for i, p in result.invalid.items())
            raise ValueError(f"migration produced invalid signals: {detail}")
        ids = {(s.source_ref, s.summary): s.signal_id for s in signals.load(target)}

    mapping: dict[str, str] = {}
    for src, row in zip(sources, rows):
        signal_id = ids[(row["source_ref"], row["summary"])]
        mapping[src["source_id"]] = signal_id
        mapping.setdefault(src["insight_id"], signal_id)

    rewritten = []
    for path in _candidate_files(root):
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        updated = rewrite_citations(text, mapping)
        if updated != text:
            rewritten.append(path.relative_to(root).as_posix())
            if not dry_run:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(updated)

    if not dry_run and not keep_insights:
        shutil.rmtree(insights_dir)
    return MigrationReport(len(result.written), rewritten)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = migrate(args.repo_root, dry_run=args.dry_run)
    except (OSError, ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    prefix = "would write" if args.dry_run else "wrote"
    print(f"{prefix} {report.signals} signals; {len(report.files_rewritten)} files rewritten")
    for rel in report.files_rewritten:
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
