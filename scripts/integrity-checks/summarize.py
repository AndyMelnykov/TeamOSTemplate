from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from common import days_open, load_status


def build_summary(status: dict, today: date) -> str:
    findings = status.get("findings", {})
    by_check = defaultdict(list)
    for record in findings.values():
        by_check[record["check_id"]].append(record)

    lines = [
        "# Integrity Check Summary", "",
        f"Generated: {today.isoformat()}",
        f"Total open findings: {len(findings)}", "",
    ]
    if not findings:
        lines.append("No open findings.")
        return "\n".join(lines) + "\n"

    lines += ["## By check", "", "| Check | Open findings |", "|---|---|"]
    for check_id in sorted(by_check):
        lines.append(f"| {check_id} | {len(by_check[check_id])} |")

    lines += ["", "## Longest open", "", "| Days open | Check | Key | Message |", "|---|---|---|---|"]
    ranked = sorted(findings.values(), key=lambda r: days_open(r, today), reverse=True)
    for record in ranked[:20]:
        lines.append(f"| {days_open(record, today)} | {record['check_id']} | {record['key']} | {record['message']} |")

    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    status_path = Path(args.status) if args.status else Path(__file__).parent / "reports" / "status.json"
    output_path = Path(args.output) if args.output else Path(__file__).parent / "reports" / "summary.md"

    summary = build_summary(load_status(status_path), date.today())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
