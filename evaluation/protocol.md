# Evaluation Protocol

## Method

Run each task in `task-set.md` twice against a fresh agent session with no prior conversation context:

1. **Baseline** — agent receives the repo with all `CLAUDE.md` router files, `reference/`, and `feature-index.yaml` removed (or ignored), so it must search the raw content tree unassisted.
2. **Product OS** — agent receives the repo as-is, and is told to start from the root `CLAUDE.md`.

## Metrics to Record

| Metric | How to measure |
|--------|-----------------|
| Task completion accuracy | Does the answer match `task-set.md`'s expected answer? |
| Wrong-source rate | Did the agent cite a file other than the expected source, or an outdated/duplicate definition? |
| Context tokens consumed | Total tokens read across the session for this task |
| Files opened | Count of distinct files the agent read |
| Time to answer | Wall-clock time from prompt to final answer |
| Citation accuracy | Does the agent's answer include a correct file path citation? |

## Reporting

Record one row per task per condition (baseline / Product OS) in `evaluation/results/YYYY-MM-DD-run.md` (create this file per run; the folder starts empty — see `results/.gitkeep`). Summarize aggregate deltas (accuracy, files opened, tokens) between conditions at the top of each run's file.
