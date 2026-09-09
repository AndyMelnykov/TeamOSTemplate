# Evaluation

A small benchmark demonstrating whether this repo's context architecture measurably helps an agent answer real product questions, versus an unstructured baseline.

## Doc Index

| File | Description |
|------|--------------|
| `task-set.md` | Seven grounded tasks, each with a verifiable expected answer and source file |
| `protocol.md` | Baseline-vs-Product-OS methodology and the metrics to record |
| `skill-acceptance-protocol.md` | Paired before/after check for a *specific* new skill or reference doc — narrower than `protocol.md`, run before merging any addition |
| `papercuts-task-set.md` | Behavioral eval for the `papercuts` skill — positive cases where friction should be logged, negative cases where it shouldn't |
| `results/` | Dated run outputs (starts empty) |
