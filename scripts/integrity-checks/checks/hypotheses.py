from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "signals"))

import hypotheses  # noqa: E402  (scripts/signals/hypotheses.py, the hypothesis parser)
from common import Finding  # noqa: E402


def _parsed(repo_root: Path):
    for path in hypotheses.hypothesis_files(repo_root):
        h = hypotheses.parse(path)
        yield h, h.hyp_id or path.relative_to(repo_root).as_posix(), path.relative_to(repo_root).as_posix()


def check_missing_fields(repo_root: Path, thresholds: dict) -> list[Finding]:
    return [
        Finding("hyp-missing-fields", key,
                f"{key} ({h.status or 'no status'}) is missing: {'; '.join(h.missing)}", rel)
        for h, key, rel in _parsed(repo_root) if h.missing
    ]


def _invalid_values(h) -> list[str]:
    problems = []
    if h.status and h.status not in hypotheses.STATUSES:
        problems.append(f"Status {h.status!r} is not one of {', '.join(hypotheses.STATUSES)}")
    # "?" is an honest placeholder at `proposed` and nowhere else; an unknown status gets no allowance.
    past_proposed = h.status != "proposed"
    for name, value, allowed in (("Confidence", h.confidence, hypotheses.CONFIDENCES),
                                 ("Effort", h.effort, hypotheses.EFFORTS)):
        if not value or value in allowed:
            continue  # empty is hyp-missing-fields' finding
        if value == "?":
            if past_proposed:
                problems.append(f"{name} is '?' at status {h.status or 'unknown'} (set one of {', '.join(allowed)})")
        else:
            problems.append(f"{name} {value!r} is not one of {', '.join(allowed)}")
    if h.validation_path and h.validation_path not in hypotheses.VALIDATION_PATHS:
        problems.append(f"Validation path {h.validation_path!r} is not one of {', '.join(hypotheses.VALIDATION_PATHS)}")
    return problems


def check_invalid_values(repo_root: Path, thresholds: dict) -> list[Finding]:
    findings = []
    for h, key, rel in _parsed(repo_root):
        problems = _invalid_values(h)
        if problems:
            findings.append(Finding("hyp-invalid-values", key, f"{key} has invalid values: {'; '.join(problems)}", rel))
    return findings


def check_stale_testing(repo_root: Path, thresholds: dict) -> list[Finding]:
    stale_days = thresholds.get("stale-testing-days", 30)
    today = date.today()
    findings = []
    for h, key, rel in _parsed(repo_root):
        if h.status != "testing":
            continue
        try:
            age = (today - date.fromisoformat(h.last_updated)).days
        except ValueError:
            continue  # a missing date is hyp-missing-fields' finding
        if age > stale_days:
            findings.append(Finding("hyp-stale-testing", key,
                f"{key} has been in testing since {h.last_updated} ({age}d, threshold {stale_days}d)", rel))
    return findings


CHECKS = {
    "hyp-missing-fields": check_missing_fields,
    "hyp-invalid-values": check_invalid_values,
    "hyp-stale-testing": check_stale_testing,
}
