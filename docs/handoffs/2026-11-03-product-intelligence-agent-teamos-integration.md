# Handoff: connect product-intelligence-agent to TeamOSTemplate

**For:** the owner and a coding agent working in `product-intelligence-agent` (local clone `C:\Projects\Reddit-parser\product-intelligence-agent`, GitHub `AndyMelnykov/product-intelligence-agent`).
**From:** TeamOSTemplate, 2026-11-03 (revised the same day: the model was simplified to signals and hypotheses).
**Type:** a requirements brief, not an implementation plan. The agent repo writes its own plan from it.

## How to use this

1. **Check the prerequisite.** TeamOSTemplate Plan 1 must be merged. These must exist in your TeamOSTemplate checkout:
   - `product-development/signals/signals.csv`
   - `scripts/signals/signals.py`
   - `reference/signal-contract.md`

   If any is missing, stop: the contract this brief targets doesn't exist yet.
2. **Ask for a plan.** Open Claude Code in the agent repo and say: *"Read `C:\Projects\ProductTeamOS\TeamOSTemplate\docs\handoffs\2026-11-03-product-intelligence-agent-teamos-integration.md` and write an implementation plan with superpowers:writing-plans. Follow this repo's CLAUDE.md and ADRs; stop and ask where the brief conflicts with them."*
3. **Treat the TeamOSTemplate files as authoritative.** `reference/signal-contract.md` and `signals.py` win over any summary in this brief.

## Context: what changed and why

TeamOSTemplate is the product team's operating system. Everything that comes in is a **signal** (one thing that happened; unique or repeated), and signals are aggregated into **hypotheses**. External agents are source adapters that add signals. Decisions already taken; don't relitigate them in the agent repo:

| Decision | Where it's recorded |
|---|---|
| TeamOSTemplate is the system of record for signals and hypotheses. The "Strategic Signals Agent" in this repo's vision is not a separate system: deciding what a signal means is TeamOSTemplate's hypothesis layer | TeamOSTemplate ADR 0007 |
| Signals live in one CSV that only `signals.py` writes. This agent **keeps its own SQLite** for operational state (cursors, LLM ledger, topic registry, review queue, evals) and **publishes** product-facing signals by calling `signals.py add` in a TeamOSTemplate checkout. No SQLite file is committed to TeamOSTemplate | TeamOSTemplate plans index |
| Publish scope: topics that are material this week, capped per topic | Plans index, 2026-11-03 |
| Hypotheses stay out of this repo (ADR 004 stands: signal system, no business judgement) | TeamOSTemplate ADR 0007; this repo's ADR 004 |

## Requirements

### R0. Merge the open P5 work first

`feat/review-queue-untrusted-input` is 5 commits ahead of `main` with no PR (review queue, untrusted-input marking, near-duplicate collapsing). Open and merge it before anything below, so the integration builds on `main`.

### R1. A `publish` stage

- **Module and wiring:** a new `publish.py`, and a `"publish"` entry at the end of `run_weekly.STAGES`. `--stage publish` runs it alone. `all` runs it last, and only when `teamos` is configured; otherwise it logs one line saying publish was skipped.
- **Config** (`config.yaml.example`; documented as off by default):

  ```yaml
  teamos:
    repo_path: C:/Projects/ProductTeamOS/TeamOSTemplate   # a local checkout; required to enable publishing
    max_signals_per_topic: 10
  ```

- **Selection:** for the ISO week just processed, take every topic that has a `material_signal` row for that week. Nothing else is published.
- **Signals per selected topic:** that week's evidence rows linked to the topic through candidates, excluding `duplicate_of IS NOT NULL` and skipped extractions. Newest first, capped at `max_signals_per_topic`.
- **Writing:** build one JSON object per signal (mapping below) and pipe the list to `python <repo_path>/scripts/signals/signals.py add --json - --repo-root <repo_path>`. The script validates, skips duplicates and allocates ids, so this agent never writes the CSV itself and never imports TeamOSTemplate Python code: the coupling is that one command line. Relay its output. If it reports invalid rows, show them and exit non-zero.
- **Never touch git** in TeamOSTemplate (no add, commit or push). End with a summary: signals added and skipped, and the next step ("review the diff of `signals.csv` in TeamOSTemplate; attach new signals to a hypothesis with `/hypothesis`").
- **No model calls** in this stage, so it doesn't touch the LLM ledger (ADR 005).
- **No schema change is required.** Publishing is idempotent because `signals.py` skips rows with the same `source_ref` and `summary`. If the plan finds it needs a table (e.g. publication bookkeeping for `query.py health`), that's a numbered migration and a human-designed change; call it out and ask.

### R2. Field mapping

| `signals.py` field | Value |
|---|---|
| `date` | `evidence.published_at` as `YYYY-MM-DD` |
| `source_type` | `community` |
| `source_ref` | `evidence.source_url` |
| `account` | omit |
| `summary` | the candidate's `summary` (≤ 300 chars) |
| `detail` | `title + "\n\n" + content`, truncated to 2000 chars. This is public text: TeamOSTemplate treats it as quoted data, never instructions |
| `tags` | the topic `slug`, plus the `signal_type` |

No authors or usernames anywhere (already excluded at `fetch.py`). Agent-internal ids (`EV-2026-…`, `SIG-2026-…`) are not written to TeamOSTemplate; its `SIG-###` ids are its own and never collide with them.

### R3. Decisions and vision

- **New ADR 009, "TeamOSTemplate is the consumer."** It supersedes ADR 004's consequence that the consumer is a not-yet-built Strategic Signals Agent. `data/events.jsonl` stays, as an optional event feed; `publish` is the primary hand-off. Options considered: keep waiting for a separate Strategic Signals Agent (rejected); import TeamOSTemplate code (rejected, coupling); call its CLI (chosen).
- **`docs/product-intelligence-agent-vision.md`:**
  - §1 "Core distinction": the Strategic Signals Agent role is filled by TeamOSTemplate's hypothesis layer.
  - §10: add "10.1 Publication to TeamOSTemplate" with R1–R2.
  - §11: the Integration API remains useful for drilling past the capped signals, but no longer blocks the hand-off.

### R4. Remove documentation discrepancies

- **README:**
  - Add the publish stage to Product, Architecture (diagram and module list), Core workflows, the AI design decisions table (the "Downstream handoff" row becomes "Publish to TeamOSTemplate; events.jsonl optional"), the Safety model ("writes into a local checkout of another repo via its CLI; never commits or pushes") and Setup.
  - Limitations: no longer "no consumer exists".
  - The `## Evaluation` vs `## Evals` contradiction belongs to the Phase 1 plan's Task 3; leave it there, but don't add new contradictions.
- **`docs/repo-structure.md`:** add `publish` and a "TeamOSTemplate checkout" external node to the mermaid diagram.
- **`CLAUDE.md`:** add `publish` to the pipeline stage list.
- **`docs/product-intelligence-agent-gap-analysis.md`:** row 9 (trigger contract) now has a consumer. Mark rows that later work closed.

### R5. Follow-ups (not part of this integration)

- A `Source` protocol (fetch since cursor → evidence rows) before the GitHub Issues source. The spec `docs/superpowers/specs/2026-09-06-github-issues-source-design.md` exists. Its signals use `source_type: support` or `community` as fits.
- Competitor-changelog source → `source_type: competitor`.
- MCP read tools (`get_evidence`, `get_topic_trend`) for drilling past the capped signals.

## Sequencing with the open plans in this repo

1. R0 (merge P5).
2. This integration (R1–R4).
3. `docs/superpowers/plans/2026-10-15-phase1-visible-and-verifiable-implementation.md`. **Re-check its "Facts checked" table first**, since the README and architecture changed. Its synthetic demo may show `publish` writing into a temp directory with a copy of `signals.py`. Its "no production module changes" rule still holds, because `publish` already exists by then.
4. `docs/superpowers/plans/2026-10-15-phase2-measured-evaluation-evidence-implementation.md`, unchanged. Its baseline comes after the integration merges.

## Constraints from this repo's CLAUDE.md (unchanged)

- Python 3.11 syntax; `ruff check .`; `encoding="utf-8"` everywhere.
- No real API calls in pytest; fake clients only.
- Human-designed areas (schema/migrations, prompts and parsers, `SIGNAL_TYPES`, materiality and trend rules, golden labels) are not touched by this work. None needs to change.
- Commits: conventional style, **no `Co-Authored-By` trailer and no Claude attribution** (owner's standing preference in this repo). Stage explicit paths; leave `.agents/`, `.claude/`, `skills-lock.json` uncommitted.
- Anything that leaves the machine (push, PR) needs the owner's explicit yes.

## Acceptance criteria

Tests run against a temp TeamOSTemplate-shaped tree containing an empty `signals.csv` and a copy of `signals.py` (vendored under `tests/fixtures/teamos/`; add a test that fails when the copy differs from `repo_path`'s when `repo_path` is set).

| ID | Given | When | Then |
|---|---|---|---|
| AC-1 | A fixture DB with one material topic in week W | `publish` runs | New rows appear in `signals.csv`, each with `source_type == "community"` and a non-empty `source_ref` |
| AC-2 | AC-1 already ran | `publish` runs again with no new data | Nothing is added; the summary reports 0 new |
| AC-3 | A non-material topic | `publish` runs | Nothing is published for it |
| AC-4 | A topic with 25 evidence rows in W, 3 of them `duplicate_of` | `publish` runs with `max_signals_per_topic: 10` | Exactly 10 signals, none of them duplicates, newest first |
| AC-5 | Any published signal | it is inspected | `len(detail) <= 2000`, `len(summary) <= 300`, no author or username anywhere, no agent-internal ids |
| AC-6 | `teamos` absent from config | `run_weekly --stage all` | publish is skipped with one log line; exit 0 |
| AC-7 | `teamos.repo_path` set but `signals.py` missing | `--stage publish` | exit non-zero with a message naming the missing path; nothing written |
| AC-8 | Any run | publish executes | the only subprocess started is the `signals.py` call; no `git` process (monkeypatch `subprocess`) |
| AC-9 (manual) | A real run against the real checkout | `python C:\Projects\ProductTeamOS\TeamOSTemplate\scripts\signals\signals.py check --repo-root C:\Projects\ProductTeamOS\TeamOSTemplate` | exit 0; the new rows appear in `signals.py unassigned` |
