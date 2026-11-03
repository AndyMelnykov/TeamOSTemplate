"""Guard: the stage status table in reference/product-loop.md stays well-formed and honest."""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOOP_DOC = REPO_ROOT / "reference" / "product-loop.md"

STAGES = ["1. Input signals", "2. Hypotheses", "3. Validation", "4. Prototyping",
          "5. PRDs", "6. Engineering", "7. Rollout and measurement", "Loop closure"]
STATUSES = {"implemented", "partial", "planned", "out-of-scope"}


def _rows():
    lines = LOOP_DOC.read_text(encoding="utf-8").splitlines()
    start = lines.index("## Stage status")
    rows = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] in ("Stage",) or set(cells[0]) <= {"-", ":", " "}:
            continue
        rows.append(cells)
    return rows


def test_stage_table_lists_every_stage_in_order():
    assert [r[0] for r in _rows()] == STAGES


def test_every_status_is_valid():
    for stage, status, *_ in _rows():
        assert status in STATUSES, f"{stage}: invalid status {status!r}"


def test_implemented_or_partial_rows_cite_existing_paths():
    for stage, status, delivered, *_ in _rows():
        if status not in ("implemented", "partial"):
            continue
        paths = re.findall(r"`([^`]+)`", delivered)
        assert paths, f"{stage}: {status} row cites no paths"
        for p in paths:
            assert (REPO_ROOT / p).exists(), f"{stage}: cited path does not exist: {p}"


def test_planned_rows_name_a_plan():
    for stage, status, delivered, *_ in _rows():
        if status == "planned":
            assert "Plan " in delivered, f"{stage}: planned row must name a plan"
