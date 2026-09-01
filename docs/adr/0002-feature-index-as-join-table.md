# feature-index.yaml as the single join table across functions

Product knowledge is organized by function first (`product/`, `engineering/`, `analytics/`, `data-engineering/`, `design/`), which fragments any single feature across as many as eight files. Rather than restructuring around features (losing the ownership clarity function-first folders give each team) or duplicating feature summaries into every folder, we maintain one YAML file per feature that reassembles the scattered artifacts by reference.

## Considered Options

- Feature-first folder structure (one folder per feature, functions nested inside).
- Duplicate a feature summary into each function's folder.

Both rejected: the first sacrifices the ownership clarity a function-first structure gives each team; the second requires keeping N copies in sync by hand, which is worse than the one-copy problem this decision solves.

## Consequences

`feature-index.yaml` is hand-maintained — a new PRD or RFC can ship without ever being wired into the join table, silently reintroducing the fragmentation problem the index exists to solve (see `ROADMAP.md`, "Automatic feature-index maintenance").
