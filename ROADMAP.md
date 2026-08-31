# Roadmap

A roadmap of decisions, not a wishlist — each item states why it matters, not just what it is. Items are pulled from the open list in [`reference/01-ai-native-product-os.md`](reference/01-ai-native-product-os.md#suggested-future-extensions), filtered down to what's actually still missing.

## Now

### Run the evaluation protocol and publish real results
**Why:** `evaluation/task-set.md` and `evaluation/protocol.md` define a real methodology, but `evaluation/results/` is empty. Every claim in the README about the structure "helping" is currently a hypothesis with a defined test, not a measured result — this repo shouldn't claim reliability it hasn't measured.

### Automatic feature-index maintenance
**Why:** `feature-index.yaml` is hand-maintained (see [ADR 0002](docs/adr/0002-feature-index-as-join-table.md)). A new PRD or RFC can ship without ever being wired into the join table, silently reintroducing the exact cross-functional fragmentation the index exists to solve.

### Canonical-document validation
**Why:** `reference/status-definitions.md` and `reference/decision-types.md` define valid conventions, but nothing currently enforces them — a PRD can carry an invalid `Status` value or a definition can get re-stated outside `reference/` and nothing catches it.

## Next

### Stale-context detection
**Why:** Nothing currently flags a decision file or reference definition that hasn't been touched since the artifacts depending on it changed underneath it.

### Conflict detection across decisions
**Why:** `reference/decision-types.md` defines the format for a decision file, but nothing checks two decision files against each other for contradictory claims.

### Agent-generated decision summaries
**Why:** Turning a closed debate (a PR thread, a meeting's outcome) into a dated decision file is still a fully manual step today.

## Later

### Codex-compatible instructions
**Why:** The router-tree pattern (`CLAUDE.md` per folder) is currently coupled to Claude Code's file-naming convention. A parallel path (e.g. `AGENTS.md`) would let other coding agents use the same structure without a rename.

### Hybrid retrieval for large, less-structured collections
**Why:** `product-development/product/competitive-research/` and the customer `Insights/` folder are the two places already flagged (in [ADR 0001](docs/adr/0001-structured-navigation-over-embeddings.md)) as closer to unstructured document piles than addressable tables — deterministic navigation is weakest there.

### Example integrations with Linear, Jira, GitHub, or Figma
**Why:** Today those systems are described in prose (path + purpose, see the root `CLAUDE.md` doc index) but nothing in the repo demonstrates a live link actually resolving.

## Already shipped

*(Moved here from "future extensions" once actually built — kept so this list doesn't imply they're still missing.)*

- **Broken-reference checker** — `scripts/check-references.ps1` deterministically catches dead links in `feature-index.yaml` and Markdown files.
- **Role-specific onboarding agent** — `.claude/agents/onboarding.md`.
- **GitHub-based issue tracking** — `docs/agents/issue-tracker.md`.
- **A friction log with an auto-triggering skill** — `PAPERCUTS.md` plus `.claude/skills/papercuts/`, not on the original extensions list but built for the same reason: surface problems with the structure instead of letting agents silently work around them.
