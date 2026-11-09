from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "signals"))

import analytics_sweep  # noqa: E402  (scripts/signals/analytics_sweep.py, the sweep's only reader)
import signals  # noqa: E402
from common import Finding  # noqa: E402


def check_watch_invalid(repo_root: Path, thresholds: dict) -> list[Finding]:
    """Every problem the sweep hits reading the watch file and snapshots, plus a missing snapshot file."""
    metrics, problems = analytics_sweep.load_watch(repo_root)
    watch_file = analytics_sweep.WATCH_FILE.as_posix()
    for metric in metrics:
        _, found = analytics_sweep.read_snapshots(repo_root, metric)
        problems.extend(found)
        snapshot = Path(repo_root) / analytics_sweep.PRODUCT_ROOT / metric.snapshot
        if not snapshot.is_file():
            problems.append(analytics_sweep.Problem(
                watch_file, metric.line, f"{metric.id}: snapshot file {metric.snapshot} not found"))

    # One finding per file:line, so several problems on one watch entry do not overwrite each other.
    grouped: dict[str, list[str]] = {}
    files: dict[str, str] = {}
    for p in problems:
        key = f"{p.file}:{p.line}"
        grouped.setdefault(key, []).append(p.message)
        files[key] = p.file
    return [Finding("analytics-watch-invalid", key, f"{key}: {'; '.join(messages)}", files[key])
            for key, messages in grouped.items()]


def check_unswept_reports(repo_root: Path, thresholds: dict) -> list[Finding]:
    """A `Complete` experiment or investigation that no signal's source_ref points at."""
    swept = {s.source_ref for s in signals.load(repo_root)}
    return [Finding("analytics-unswept-reports", ref,
                    f"{ref} is Complete but no signal cites it; run /analytics-sweep", ref)
            for ref in analytics_sweep.complete_reports(repo_root) if ref not in swept]


CHECKS = {
    "analytics-watch-invalid": check_watch_invalid,
    "analytics-unswept-reports": check_unswept_reports,
}
