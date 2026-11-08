"""Analytics sweep: turn watched metrics, completed experiments and investigations into signals.

Metrics: read `analytics/metric-watch.yaml` and the snapshot CSVs, evaluate each metric's
rules, and shape hits into `signals.add` rows. Reports: every `Status: Complete` experiment
and investigation becomes one signal. `main` runs both and prints `N new, M existing, K invalid, P problems`.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import date as _date
from pathlib import Path

import yaml

import signals
from signals import DETAIL_MAX, SUMMARY_MAX, AddResult

ANALYTICS = Path("product-development/analytics")
WATCH_FILE = ANALYTICS / "metric-watch.yaml"
REFERENCE_METRICS = Path("reference/metrics.md")
# `snapshot` and `target_source` paths in the watch file are relative to product-development/.
PRODUCT_ROOT = Path("product-development")

METRIC_ID = re.compile(r"^[a-z0-9-]+$")
TARGET = re.compile(r"^\s*([<>]=?)\s*(-?\d+(?:\.\d+)?)\s*(%|[a-zA-Z]+)?")
PERIOD = {"weekly": re.compile(r"^\d{4}-W\d{2}$"), "monthly": re.compile(r"^\d{4}-\d{2}$")}
RULE_TYPES = ("below-target", "change")
DIRECTIONS = ("down", "up", "any")
SNAPSHOT_COLUMNS = ("period", "segment", "value", "captured_at", "captured_by")
EXAMPLE_DATA = "example-data"


@dataclass(frozen=True)
class Target:
    op: str
    value: float
    unit: str
    text: str


@dataclass(frozen=True)
class WatchedMetric:
    id: str
    name: str
    unit: str
    cadence: str
    target_source: str
    target: Target | None
    snapshot: str
    rules: tuple[dict, ...]
    line: int = 0


@dataclass(frozen=True)
class Problem:
    file: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.message}"


@dataclass(frozen=True)
class SnapshotRow:
    period: str
    segment: str
    value: float
    captured_at: str
    captured_by: str


@dataclass(frozen=True)
class Hit:
    rule: str  # "below-target" | "change"
    period: str
    segment: str
    value: float
    captured_at: str
    captured_by: str
    previous_period: str | None = None
    previous_value: float | None = None
    pct: float | None = None


def parse_target(text: str) -> Target | None:
    """Read `> 92%`, `< 15 min` ... from the start of `text`; anything else (e.g. `Tracking`) is no target."""
    m = TARGET.match(text or "")
    if not m:
        return None
    op, number, unit = m.group(1), m.group(2), m.group(3) or ""
    spaced = f" {unit}" if unit.isalpha() else unit
    return Target(op, float(number), unit, f"{op} {number}{spaced}")


def _reference_target(repo_root: Path, name: str) -> tuple[bool, str]:
    """(found, target cell) for the `reference/metrics.md` row whose first cell is `name`."""
    path = Path(repo_root) / REFERENCE_METRICS
    if not path.exists():
        return False, ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].strip("*").strip() == name:
            return True, cells[-1]
    return False, ""


def _entry_lines(text: str, count: int) -> list[int]:
    """1-based start line of each item under `metrics:`; falls back to line 1."""
    lines = [1] * count
    try:
        root = yaml.compose(text)
        for key, value in root.value:
            if key.value == "metrics" and isinstance(value, yaml.SequenceNode):
                lines = [node.start_mark.line + 1 for node in value.value][:count] or lines
    except (yaml.YAMLError, AttributeError, TypeError):
        pass
    return lines + [1] * (count - len(lines))


def _is_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _build_metric(entry, line: int, repo_root: Path, file: str, seen: set[str]) -> tuple[WatchedMetric | None, list[Problem]]:
    """Validate one watch entry. Errors drop the entry; a target problem keeps it with no target."""
    if not isinstance(entry, dict):
        return None, [Problem(file, line, "entry must be a mapping")]
    errors: list[str] = []
    soft: list[str] = []

    def text(key: str) -> str:
        v = entry.get(key)
        return v.strip() if isinstance(v, str) else ""

    mid = text("id")
    if not METRIC_ID.match(mid):
        errors.append(f"id {entry.get('id')!r} must match ^[a-z0-9-]+$")
    elif mid in seen:
        errors.append(f"duplicate id {mid!r}")
    name = text("name")
    if not name:
        errors.append("name is required")
    unit = entry.get("unit")
    if not isinstance(unit, str):
        errors.append("unit is required (a string such as '%' or 'min')")
        unit = ""
    cadence = text("cadence")
    if cadence not in PERIOD:
        errors.append(f"cadence {entry.get('cadence')!r} must be one of {', '.join(PERIOD)}")
    snapshot = text("snapshot")
    if not (snapshot.startswith("analytics/snapshots/") and snapshot.endswith(".csv")):
        errors.append(f"snapshot {entry.get('snapshot')!r} must look like analytics/snapshots/<id>.csv")

    rules: list[dict] = []
    raw_rules = entry.get("rules")
    if not isinstance(raw_rules, list) or not raw_rules:
        errors.append("rules must be a non-empty list")
    else:
        for rule in raw_rules:
            rtype = rule.get("type") if isinstance(rule, dict) else None
            if rtype not in RULE_TYPES:
                errors.append(f"rule type {rtype!r} must be one of {', '.join(RULE_TYPES)}")
            elif rtype == "change":
                threshold, direction = rule.get("threshold_pct"), rule.get("direction", "any")
                if not _is_number(threshold) or threshold <= 0:
                    errors.append("change rule needs threshold_pct > 0")
                elif direction not in DIRECTIONS:
                    errors.append(f"change rule direction {direction!r} must be one of {', '.join(DIRECTIONS)}")
                else:
                    rules.append({"type": "change", "threshold_pct": threshold, "direction": direction})
            else:
                rules.append({"type": "below-target"})

    source = text("target_source")
    target: Target | None = None
    if source == "reference":
        found, cell = _reference_target(repo_root, name)
        if not found:
            soft.append(f"no row named {name!r} in {REFERENCE_METRICS.as_posix()}")
        else:
            target = parse_target(cell)
    elif source.startswith("analytics/metrics/"):
        if not (Path(repo_root) / PRODUCT_ROOT / source).is_file():
            errors.append(f"target_source {source!r} does not exist")
        target_text = entry.get("target")
        if not isinstance(target_text, str) or not target_text.strip():
            errors.append("target is required unless target_source is 'reference'")
        else:
            target = parse_target(target_text)
    else:
        errors.append(f"target_source {entry.get('target_source')!r} must be 'reference' or a path under analytics/metrics/")

    if target is not None and target.unit != unit:
        soft.append(f"target {target.text!r} is in {target.unit or 'no unit'!r} but unit is {unit!r}; below-target skipped")
        target = None

    problems = [Problem(file, line, m) for m in errors + soft]
    if errors:
        return None, problems
    seen.add(mid)
    return WatchedMetric(mid, name, unit, cadence, source, target, snapshot, tuple(rules), line), problems


def load_watch(repo_root: Path) -> tuple[list[WatchedMetric], list[Problem]]:
    repo_root = Path(repo_root)
    file = WATCH_FILE.as_posix()
    path = repo_root / WATCH_FILE
    if not path.exists():
        return [], [Problem(file, 1, "file not found")]
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return [], [Problem(file, 1, f"invalid YAML: {e}")]
    entries = data.get("metrics") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return [], [Problem(file, 1, "expected a top-level `metrics:` list")]

    metrics: list[WatchedMetric] = []
    problems: list[Problem] = []
    seen: set[str] = set()
    for entry, line in zip(entries, _entry_lines(text, len(entries))):
        metric, found = _build_metric(entry, line, repo_root, file, seen)
        problems.extend(found)
        if metric:
            metrics.append(metric)
    return metrics, problems


def read_snapshots(repo_root: Path, metric: WatchedMetric) -> tuple[list[SnapshotRow], list[Problem]]:
    """Valid rows (latest capture per period+segment), sorted by period then segment, plus a Problem per skipped row."""
    path = Path(repo_root) / PRODUCT_ROOT / metric.snapshot
    file = (PRODUCT_ROOT / metric.snapshot).as_posix()
    if not path.exists():
        return [], []
    problems: list[Problem] = []
    best: dict[tuple[str, str], SnapshotRow] = {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in SNAPSHOT_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            return [], [Problem(file, 1, f"missing column(s): {', '.join(missing)}")]
        for raw in reader:
            line = reader.line_num
            period = (raw.get("period") or "").strip()
            segment = (raw.get("segment") or "").strip() or "all"
            captured_at = (raw.get("captured_at") or "").strip()
            if not PERIOD[metric.cadence].match(period):
                problems.append(Problem(file, line, f"period {period!r} does not match {metric.cadence} cadence"))
                continue
            try:
                value = float((raw.get("value") or "").strip())
                if value != value or value in (float("inf"), float("-inf")):
                    raise ValueError
            except ValueError:
                problems.append(Problem(file, line, f"value {raw.get('value')!r} is not a plain number; row skipped"))
                continue
            try:
                _date.fromisoformat(captured_at[:10])
            except ValueError:
                problems.append(Problem(file, line, f"captured_at {captured_at!r} must start with YYYY-MM-DD"))
                continue
            row = SnapshotRow(period, segment, value, captured_at, (raw.get("captured_by") or "").strip())
            current = best.get((period, segment))
            if current is None or row.captured_at >= current.captured_at:
                best[(period, segment)] = row
    return [best[k] for k in sorted(best)], problems


def _satisfies(target: Target, value: float) -> bool:
    return {
        ">": value > target.value,
        ">=": value >= target.value,
        "<": value < target.value,
        "<=": value <= target.value,
    }[target.op]


def evaluate(metric: WatchedMetric, rows: list[SnapshotRow]) -> list[Hit]:
    """Hits for the latest period of each segment. Rules that lack data are skipped, never errors."""
    by_segment: dict[str, list[SnapshotRow]] = {}
    for row in sorted(rows, key=lambda r: r.period):
        by_segment.setdefault(row.segment, []).append(row)

    hits: list[Hit] = []
    for segment in sorted(by_segment):
        series = by_segment[segment]
        latest = series[-1]
        previous = series[-2] if len(series) > 1 else None
        for rule in metric.rules:
            if rule["type"] == "below-target":
                if metric.target is not None and not _satisfies(metric.target, latest.value):
                    hits.append(Hit("below-target", latest.period, segment, latest.value,
                                    latest.captured_at, latest.captured_by))
            elif previous is not None and previous.value != 0:
                pct = (latest.value - previous.value) / abs(previous.value) * 100
                threshold, direction = rule["threshold_pct"], rule["direction"]
                moved = (
                    pct <= -threshold if direction == "down"
                    else pct >= threshold if direction == "up"
                    else abs(pct) >= threshold
                )
                if moved:
                    hits.append(Hit("change", latest.period, segment, latest.value, latest.captured_at,
                                    latest.captured_by, previous.period, previous.value, pct))
    return hits


def hit_to_signal(metric: WatchedMetric, hit: Hit) -> dict:
    """A row ready for `signals.add`. The period is in the summary so each period is a new signal."""
    value = f"{hit.value:g}{metric.unit}"
    where = f"{hit.period} ({hit.segment})"
    if hit.rule == "below-target":
        summary = f"{metric.name} was {value} in {where}, missing target {metric.target.text}"
        detail = f"{metric.name} ({metric.id}): latest {value} in {hit.period} for segment {hit.segment}; target {metric.target.text}."
    else:
        verb = "rose" if hit.pct > 0 else "fell"
        summary = f"{metric.name} {verb} {abs(hit.pct):.1f}% to {value} in {hit.period} vs {hit.previous_period} ({hit.segment})"
        detail = (f"{metric.name} ({metric.id}): {hit.previous_value:g}{metric.unit} in {hit.previous_period} -> "
                  f"{value} in {hit.period} for segment {hit.segment}.")
    detail += f" Captured {hit.captured_at} by {hit.captured_by or 'unknown'}."
    if hit.captured_by == EXAMPLE_DATA:
        detail += " Seeded example data, not a real measurement."
    return {
        "date": hit.captured_at[:10],
        "source_type": "analytics",
        "source_ref": (PRODUCT_ROOT / metric.snapshot).as_posix(),
        "account": "",
        "summary": summary,
        "detail": detail,
        "tags": metric.id,
    }


# ---- Reports -------------------------------------------------------------------

REPORT_DIRS = {"experiments": "experiment", "investigations": "analytics"}  # folder -> source_type
DATE_FIELDS = ("Experiment End", "Run Date", "Date")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _plain(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("**", "").replace("`", "")).strip()


def _header_region(text: str) -> str:
    """Lines before the first heading after the title; field-like lines in the body must not match."""
    out: list[str] = []
    seen_title = False
    for line in text.splitlines():
        if HEADING.match(line):
            if seen_title:
                break
            seen_title = True
        out.append(line)
    return "\n".join(out)


def header_field(text: str, name: str) -> str | None:
    """Value of a header field in any of the three styles; None if absent.

    `| **Name** | v |`, `| Name | v |` and `**Name:** v` (also `**Name**: v`).
    """
    n = re.escape(name)
    region = _header_region(text)
    table = re.search(rf"^\s*\|\s*\**{n}\**\s*\|(.*?)\|?\s*$", region, re.I | re.M)
    inline = re.search(rf"^\s*\*\*{n}(?::\*\*|\*\*\s*:)\s*(.*?)\s*$", region, re.I | re.M)
    match = table or inline
    return _plain(match.group(1)) if match else None


def _sections(text: str) -> list[tuple[int, str, list[str]]]:
    """(level, heading text, body lines up to the next heading of the same or higher level); skips code fences."""
    lines, fenced, heads = text.splitlines(), False, []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        m = None if fenced else HEADING.match(line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    out = []
    for k, (i, level, title) in enumerate(heads):
        end = len(lines)
        for j, lvl, _ in heads[k + 1:]:
            if lvl <= level:
                end = j
                break
        out.append((level, title, lines[i + 1:end]))
    return out


def _find_section(text: str, match) -> list[str] | None:
    for _, title, body in _sections(text):
        if match(title.lower()):
            return body
    return None


def _first_paragraph(body: list[str]) -> str:
    para: list[str] = []
    for line in body:
        stripped = line.strip()
        if not stripped or stripped.startswith("---") or HEADING.match(line):
            if para:
                break
            continue
        para.append(stripped)
    return _plain(" ".join(para))


def _first_bold_sentence(body: list[str]) -> str:
    """Bold text that opens a non-table line, e.g. `**Users churn 3x more.** More words.`"""
    for line in body:
        m = re.match(r"^\s*\*\*(.+?)\*\*", line)
        if m:
            return _plain(m.group(1))
    return ""


def _cap(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def _summary_source(text: str) -> tuple[str, list[str] | None]:
    """(summary, the section it came from): TL;DR, else Findings, else Question, else the H1."""
    tldr = _find_section(text, lambda t: t.replace(" ", "") == "tl;dr")
    if tldr is not None and _first_paragraph(tldr):
        return _first_paragraph(tldr), tldr
    findings = _find_section(text, lambda t: "finding" in t)
    if findings is not None and _first_bold_sentence(findings):
        return _first_bold_sentence(findings), findings
    question = _find_section(text, lambda t: t == "question")
    if question is not None and _first_paragraph(question):
        return _first_paragraph(question), question
    for line in text.splitlines():
        m = re.match(r"^#\s+(.*?)\s*$", line)
        if m:
            return _plain(m.group(1)), None
    return "", None


def report_summary(text: str) -> str:
    return _cap(_summary_source(text)[0], SUMMARY_MAX)


def _report_detail(text: str) -> str:
    summary, section = _summary_source(text)
    body = "\n".join(section).strip() if section else summary
    return _cap(body, DETAIL_MAX)


def _report_files(repo_root: Path):
    base = Path(repo_root) / ANALYTICS
    for folder, source_type in REPORT_DIRS.items():
        for path in sorted((base / folder).rglob("*.md")):
            if path.name.lower() != "claude.md" and not path.name.startswith("_"):
                yield folder, source_type, path


def _scan_reports(repo_root: Path) -> tuple[list[dict], list[Problem]]:
    rows: list[dict] = []
    problems: list[Problem] = []
    for folder, source_type, path in _report_files(repo_root):
        ref = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8")
        status = header_field(text, "Status")
        if status is None or status.lower() != "complete":
            continue
        raw_date = next((v for v in (header_field(text, f) for f in DATE_FIELDS) if v and ISO_DATE.search(v)), None)
        if raw_date is None:
            problems.append(Problem(ref, 1, f"no usable date in {', '.join(DATE_FIELDS)}; report not swept"))
            continue
        area = path.parent.relative_to(Path(repo_root) / ANALYTICS / folder).as_posix().replace("/", "-")
        tags = [t for t in ("investigation" if folder == "investigations" else "", "" if area == "." else area) if t]
        rows.append({
            "date": ISO_DATE.search(raw_date).group(0),
            "source_type": source_type,
            "source_ref": ref,
            "account": "",
            "summary": report_summary(text),
            "detail": _report_detail(text),
            "tags": ";".join(tags),
        })
    return rows, problems


def scan_reports(repo_root: Path) -> list[dict]:
    """Signal rows for `Complete` experiments and investigations."""
    return _scan_reports(repo_root)[0]


# ---- Sweep ---------------------------------------------------------------------

def collect(repo_root: Path) -> tuple[list[dict], list[Problem]]:
    """Every signal row the inputs currently justify, plus problems found reading them."""
    metrics, problems = load_watch(repo_root)
    rows: list[dict] = []
    for metric in metrics:
        snapshot_rows, found = read_snapshots(repo_root, metric)
        problems.extend(found)
        rows.extend(hit_to_signal(metric, hit) for hit in evaluate(metric, snapshot_rows))
    report_rows, found = _scan_reports(repo_root)
    return rows + report_rows, problems + found


def _dry_add(repo_root: Path, rows: list[dict]) -> tuple[AddResult, list[dict]]:
    """What `signals.add` would do, without writing."""
    existing = signals.load(repo_root)
    seen = {(s.source_ref, s.summary) for s in existing}
    number = signals._next_number(existing)
    result, new = AddResult(written=[], skipped=0, invalid={}), []
    for index, row in enumerate(rows):
        bad = signals.validate(row, repo_root)
        if bad:
            result.invalid[index] = bad
        elif (row["source_ref"], row["summary"]) in seen:
            result.skipped += 1
        else:
            seen.add((row["source_ref"], row["summary"]))
            result.written.append(f"SIG-{number:03d}")
            number += 1
            new.append(row)
    return result, new


def _run(repo_root: Path, dry_run: bool) -> tuple[AddResult, list[dict], list[Problem]]:
    rows, problems = collect(repo_root)
    if dry_run:
        result, new = _dry_add(repo_root, rows)
        return result, new, problems
    return signals.add(repo_root, rows), [], problems


def sweep(repo_root: Path, dry_run: bool = False) -> AddResult:
    return _run(Path(repo_root), dry_run)[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="analytics_sweep.py", description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--dry-run", action="store_true", help="list what would be added; write nothing")
    args = parser.parse_args(argv)
    try:
        result, would_add, problems = _run(args.repo_root, args.dry_run)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for row in would_add:
        print(f"would add [{row['source_type']}] {row['summary']}")
    for problem in problems:
        print(f"problem: {problem}", file=sys.stderr)
    for index, messages in result.invalid.items():
        for message in messages:
            print(f"error: row {index}: {message}", file=sys.stderr)
    print(f"{len(result.written)} new, {result.skipped} existing, {len(result.invalid)} invalid, {len(problems)} problems")
    return 1 if result.invalid else 0


if __name__ == "__main__":
    sys.exit(main())
