# Roadmap

A roadmap of decisions, not a wishlist — each item states why it matters, not just what it is. Items are pulled from the open list in [`reference/ai-native-product-os.md`](reference/ai-native-product-os.md#suggested-future-extensions), filtered down to what's actually still missing. The product-loop work is organised by the plans in the [plans index](docs/superpowers/plans/2026-11-03-product-loop-plans-index.md); stage status lives in [`reference/product-loop.md`](reference/product-loop.md#stage-status).

## Now

### Run the evaluation protocol and publish real results
**Why:** `evaluation/task-set.md` and `evaluation/protocol.md` define a real methodology, but `evaluation/results/` is empty. Every claim in the README about the structure "helping" is currently a hypothesis with a defined test, not a measured result — this repo shouldn't claim reliability it hasn't measured.

### Plan 1 — Signals
**Why:** Every input to the loop (calls, research, tickets, analytics, external agents) needs to be added the same way, or "plug-and-play" is only a slogan. One store of signals, one script that writes it. See [plan 1](docs/superpowers/plans/2026-11-03-plan1-signals.md).

### Plan 3 — PRD acceptance criteria
**Why:** The PRD → ticket hand-off is the one engineering boundary this repo owns; without testable acceptance criteria it cannot be checked. See [plan 3](docs/superpowers/plans/2026-11-03-plan3-prd-acceptance-criteria.md).

## Next

### Plan 2 — Hypotheses
**Why:** A hypothesis should be the single discovery artifact: it aggregates signals, and shows its reach and a recommended validation path (A/B when cheap, prototype or survey when complex). See [plan 2](docs/superpowers/plans/2026-11-03-plan2-hypotheses.md).

### Plan 4 — Analytics → signals
**Why:** Measurement is stage 7 of the loop and currently has no path back into the loop; metric shifts and experiment outcomes should become signals. See [plan 4](docs/superpowers/plans/2026-11-03-plan4-analytics-signals.md).

### product-intelligence-agent integration
**Why:** The first external source adapter proves the signal script end to end. Work happens in the agent's repo; see the [handoff brief](docs/handoffs/2026-11-03-product-intelligence-agent-teamos-integration.md) and [ADR 0007](docs/adr/0007-teamos-is-the-integration-layer.md).

### Automatic feature-index maintenance
**Why:** `feature-index.yaml` is hand-maintained (see [ADR 0002](docs/adr/0002-feature-index-as-join-table.md)). The `feature-index-join-completeness` integrity check now detects unwired artifacts, but nothing writes the entries, so a new PRD or RFC can still sit outside the join table until a person notices.

### Canonical-document validation
**Why:** `reference/decision-types.md` defines a valid decision-file format, but nothing currently enforces it — a definition can get re-stated outside `reference/` and nothing catches it. (PRD-level validation — `Status` value, and metric name/target match against `reference/metrics.md` — is covered by `/prd`'s Step 6 CPO check; this item is scoped to decision files, and to enforcement outside of a PRD author's own `/prd` run, e.g. a PRD edited by hand after the fact.)

### Stale-context detection
**Why:** Nothing currently flags a decision file or reference definition that hasn't been touched since the artifacts depending on it changed underneath it.

### Conflict detection across decisions
**Why:** `reference/decision-types.md` defines the format for a decision file, but nothing checks two decision files against each other for contradictory claims.

## Later

### Prototype ↔ shared design system
**Why:** Prototypes stay throwaway by design (`.claude/skills/prototype/`). Linking them to a shared design system would stop design drift between prototype and product, but it is not needed to close the loop.

### Capability adapters for Jira, Azure DevOps and a support desk
**Why:** Capabilities are currently filled by GitHub Issues and manual paste ([`docs/agents/capabilities.md`](docs/agents/capabilities.md)). Demonstrating a second adapter per capability is what proves the swap story; today nothing in the repo shows a live link to those systems resolving.

### Agent-generated decision summaries
**Why:** Turning a closed debate (a PR thread, a meeting's outcome) into a dated decision file is still a fully manual step today.

### Hybrid retrieval for large, less-structured collections
**Why:** `product-development/product/competitive-research/` and the customer `Insights/` folder are the two places already flagged (in [ADR 0001](docs/adr/0001-structured-navigation-over-embeddings.md)) as closer to unstructured document piles than addressable tables — deterministic navigation is weakest there.

### Codex-compatible instructions
**Why:** The router-tree pattern (`CLAUDE.md` per folder) is currently coupled to Claude Code's file-naming convention. A parallel path (e.g. `AGENTS.md`) would let other coding agents use the same structure without a rename.

## Already shipped

*(Moved here from "future extensions" once actually built — kept so this list doesn't imply they're still missing.)*

- **Broken-reference checker** — `scripts/check-references.ps1` deterministically catches dead links in `feature-index.yaml` and Markdown files.
- **Role-specific onboarding agent** — `.claude/agents/onboarding.md`.
- **GitHub-based issue tracking** — `docs/agents/issue-tracker.md`.
- **A friction log with an auto-triggering skill** — `PAPERCUTS.md` plus `.claude/skills/papercuts/`, not on the original extensions list but built for the same reason: surface problems with the structure instead of letting agents silently work around them.
- **Hypothesis discovery layer** — `reference/discovery-artifact-types.md`, `templates/hypothesis.md`, worked example under `product-development/product/PRDs/extraction-quality/`. See [ADR 0008](docs/adr/0008-hypothesis-is-the-discovery-artifact.md) (supersedes [ADR 0005](docs/adr/0005-opportunity-hypothesis-layer.md)).
- **PRD self-review before sharing ("CPO check")** — `.claude/commands/prd.md` Step 6 validates section completeness, `Status` validity, metric name/target match against `reference/metrics.md`, and that `Sources` citations resolve, before a PRD is treated as ready. Scoped to PRDs only; decision-file validation remains open (see "Canonical-document validation" above).
- **Feature-request intake** — `.claude/commands/feature-request-intake.md` and `.claude/skills/feature-request-intake/SKILL.md` turn a raw ask into a structured, function-routed GitHub issue (dedup-checked against `feature-index.yaml` and open `feature-request` issues, evidence-searched against customer call summaries, SLA-assigned per `reference/sla-policy.md`). Filed issues start unlabeled for `.claude/skills/triage/SKILL.md` to pick up from `needs-triage`.
- **Two-track PRD review ("Review Tier")** — PRDs now carry a `**Review Tier**` field (`Local` | `Strategy Review`); `/prd`'s Step 6 CPO check holds a `Strategy Review`-tier PRD at `In Review` until a decision file resolving it exists under `product-development/product/strategy/`, which routes it through the existing human-approval gate in [ADR 0003](docs/adr/0003-human-approval-for-canonical-writes.md). See [ADR 0006](docs/adr/0006-two-track-prd-review.md).
- **Repo integrity checks** — `scripts/integrity-checks/` runs a config-driven suite of Python checks (Insights/Hypothesis chain integrity, feature-index.yaml join-table completeness, PRD content completeness and staleness, decision/ADR naming conventions, backlog staleness for bug investigations/PAPERCUTS.md/SKILL-GAPS.md) on a daily GitHub Actions schedule (`.github/workflows/integrity-checks.yml`), committing `reports/status.json` (first-detected tracking) and `reports/summary.md` back to the repo. See `scripts/integrity-checks/README.md`.
