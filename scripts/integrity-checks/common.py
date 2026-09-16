from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml


@dataclass
class Finding:
    check_id: str
    key: str
    message: str
    file: str = ""


def load_config(config_path: Path) -> dict:
    with config_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_status(status_path: Path) -> dict:
    if not status_path.exists():
        return {"generated_at": None, "findings": {}}
    with status_path.open(encoding="utf-8") as f:
        return json.load(f)


def write_status(status_path: Path, status: dict) -> None:
    status_path.parent.mkdir(parents=True, exist_ok=True)
    with status_path.open("w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, sort_keys=True)
        f.write("\n")


def merge_findings(previous: dict, current: list[Finding], today: date) -> dict:
    today_str = today.isoformat()
    merged: dict[str, dict] = {}
    for finding in current:
        record_key = f"{finding.check_id}::{finding.key}"
        prior = previous.get(record_key)
        first_detected = prior["first_detected"] if prior else today_str
        merged[record_key] = {
            "check_id": finding.check_id,
            "key": finding.key,
            "message": finding.message,
            "file": finding.file,
            "first_detected": first_detected,
            "last_seen": today_str,
        }
    return merged


def days_open(record: dict, today: date) -> int:
    return (today - date.fromisoformat(record["first_detected"])).days
