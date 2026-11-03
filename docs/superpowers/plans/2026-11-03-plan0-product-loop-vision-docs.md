# Plan 0: Product Loop Vision in README and Key Docs — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repo describe itself as the product operating system the owner described: a plug-and-play integration layer for the discovery → delivery loop. Every stage's real status is stated honestly, and later plans have one place to update.

**Architecture:** A new canonical `reference/product-loop.md` defines the seven stages, the closing feedback edge, the plug-and-play principle, and a machine-checked stage-status table. README, architecture doc, vision doc, ROADMAP and root `CLAUDE.md` are rewritten to route through it. A new ADR records that TeamOSTemplate is the integration layer and external agents (product-intelligence-agent first) are source adapters. A small pytest guard keeps the status table valid.

**Tech Stack:** Markdown, Python 3.12, pytest.

**Spec:** the owner's loop description of 2026-11-03 (stages 1–7 and "The loop", quoted in the session) and [`docs/gap-analysis-product-loop-2026-11-03.md`](../../gap-analysis-product-loop-2026-11-03.md) §2, §4.4–§4.7. Decisions: [plans index](2026-11-03-product-loop-plans-index.md).

## Global Constraints

- Describe what exists as existing and what is planned as planned. Every "planned" capability names the plan that delivers it. Never describe a planned file as if it exists.
- `reference/` edits (`product-loop.md`, `terminology.md`, `CLAUDE.md`) need owner approval in the PR (ADR 0003). Say so in the PR body.
- The loop vocabulary is fixed here and reused by every later plan, and it is deliberately small: a **signal** is one thing that happened, from any source, unique or repeated (`SIG-###` once Plan 1 lands); a **hypothesis** aggregates signals, and its first status, `opportunity`, is what other tools call an opportunity. There is no separate evidence layer and no separate opportunity artifact. Plus: **source adapter** (anything that adds signals), **capability**, **validation path**, **prototype**, **PRD**, **rollout**, **measurement**. Do not add terms.
- Stage status values, exactly: `implemented`, `partial`, `planned`, `out-of-scope`.
- Prototyping stance, verbatim intent: prototypes stay throwaway (`.claude/skills/prototype/`); linking prototypes to a shared design system is a "Later" roadmap item.
- Engineering (development, testing, deployment) is out of scope. The repo owns only the PRD → ticket hand-off contract.
- Tool-agnostic principle: every external tool (issue tracker, support desk, CRM / call recorder, analytics warehouse, external intelligence) is a **capability** filled by a named adapter per install. Docs never assume a vendor.

## Review Focus

1. **A README claim about a planned feature written in present tense.** Expected: every not-yet-built capability says "planned (Plan N)". Pinned by Task 5 Step 3 (grep for planned paths that don't exist).
2. **The status table drifting from reality as later plans land.** Expected: the guard test fails if a row's `Delivered by` path does not exist while status is `implemented` or `partial`. Pinned in Task 1.
3. **The uncommitted rename of `reference/01-ai-native-product-os.md` leaving dangling links.** Expected: `check-references.ps1` clean. Pinned in Task 4 Step 5.
4. **`reference/` changes merged without owner sign-off.** Expected: the PR body lists every `reference/` file touched. Pinned in Task 5 Step 4.
5. **Vendor names leaking back in as assumptions** ("log it in Jira"). Expected: workflow docs say "the issue tracker (see `docs/agents/capabilities.md`)". Pinned in Task 2 Step 3.

---

## File Structure

| File | Responsibility |
|---|---|
| `reference/product-loop.md` (create) | Canonical loop definition + stage status table |
| `reference/terminology.md` (modify) | Add loop vocabulary |
| `reference/CLAUDE.md` (modify) | Route to `product-loop.md` |
| `tests/docs/test_product_loop.py` (create) | Guard: status table is well-formed and honest |
| `pytest.ini` (create) | `testpaths = tests` so `pytest -q` from root runs everything |
| `docs/adr/0007-teamos-is-the-integration-layer.md` (create) | TeamOSTemplate is the system of record and integration layer; external agents are adapters; the "Strategic Signals Agent" role is absorbed |
| `docs/agents/capabilities.md` (create) | Capability → configured adapter table |
| `README.md` (rewrite) | Loop-first README |
| `docs/architecture.md` (modify) | Add the adapter/integration layer |
| `reference/ai-native-product-os.md` (commit the rename; modify) | Add a "Product loop" section pointing at `product-loop.md` |
| `ROADMAP.md` (rewrite) | Now/Next/Later organised by the plans |
| `CLAUDE.md` (modify) | Doc index rows; fix "Domain docs" |
| `CONTEXT-MAP.md` (create) | Resolves the 2026-11-03 papercut |
| `PAPERCUTS.md` (modify) | Mark the `CONTEXT-MAP.md` papercut resolved |

---

### Task 1: Canonical loop document and its guard test

**Files:**
- Create: `reference/product-loop.md`, `tests/docs/test_product_loop.py`, `pytest.ini`
- Modify: `reference/terminology.md`, `reference/CLAUDE.md`

**Interfaces:**
- Produces: the stage table in `reference/product-loop.md` under the heading `## Stage status`, columns exactly `| Stage | Status | Delivered by | Notes |`, one row per stage in this order: `1. Input signals`, `2. Hypotheses`, `3. Validation`, `4. Prototyping`, `5. PRDs`, `6. Engineering`, `7. Rollout and measurement`, `Loop closure`. `Delivered by` holds `;`-separated repo-relative paths in backticks, or `Plan N` for planned rows. Every later plan edits this table.

- [ ] **Step 1: Write the failing test** in `tests/docs/test_product_loop.py`:

```python
STAGES = ["1. Input signals", "2. Hypotheses", "3. Validation", "4. Prototyping",
          "5. PRDs", "6. Engineering", "7. Rollout and measurement", "Loop closure"]
STATUSES = {"implemented", "partial", "planned", "out-of-scope"}

def test_stage_table_lists_every_stage_in_order(): ...      # rows == STAGES
def test_every_status_is_valid(): ...                        # each Status in STATUSES
def test_implemented_or_partial_rows_cite_existing_paths(): ...  # each backticked path exists under repo root
def test_planned_rows_name_a_plan(): ...                     # "Plan " in Delivered by
```

Parse the table with a regex over lines between `## Stage status` and the next `## `. Resolve paths from `Path(__file__).resolve().parents[2]`.

- [ ] **Step 2: Run it and confirm it fails** — `pytest tests/docs -q` → FAIL (file not found).

- [ ] **Step 3: Write `reference/product-loop.md`** with these sections:
  - `## The loop`: the owner's seven stages, one short paragraph each, plus the closing edge (rollout results, A/B outcomes and metric shifts become new signals). Include an ASCII box diagram of the seven stages with the loop-closure arrow.
  - `## Plug-and-play principle`: TeamOSTemplate is the integration layer and system of record. Every source adds signals the same way (Plan 1). Every tool is a capability (`docs/agents/capabilities.md`). No prioritisation framework, roadmap method or vendor is assumed; the defaults are named in `reference/` and swappable.
  - `## Ownership boundaries`: what lives here (signals, hypotheses, PRDs, measurements); what doesn't (engineering, raw tool data, prototype code); product-intelligence-agent is an adapter (ADR 0007).
  - `## Stage status`: the table. Initial values: `1. Input signals` partial (`.claude/commands/customer-call.md`; `product-development/product/Insights/insights.csv`; signal store Plan 1, analytics Plan 4). `2. Hypotheses` partial (`templates/hypothesis.md`; `reference/discovery-artifact-types.md`; opportunity folded into the hypothesis and derived reach, Plan 2). `3. Validation` partial (`product-development/analytics/experiments/`; results as signals, Plans 1 and 4). `4. Prototyping` partial (`.claude/skills/prototype/SKILL.md`; throwaway by design; design-system link Later). `5. PRDs` partial (`.claude/commands/prd.md`; `.claude/skills/to-prd/SKILL.md`; acceptance criteria Plan 3). `6. Engineering` out-of-scope (`docs/agents/issue-tracker.md`). `7. Rollout and measurement` planned (Plan 4). `Loop closure` planned (Plans 1 and 4).

- [ ] **Step 4: Add vocabulary** to `reference/terminology.md`: Signal, Hypothesis (including its `opportunity` status), Validation path, Source adapter, Capability. One line each, and each points to `reference/product-loop.md`. Add a row to `reference/CLAUDE.md` for `product-loop.md`.

- [ ] **Step 5: Create `pytest.ini`** with `[pytest]` / `testpaths = tests` / `pythonpath = scripts scripts/integrity-checks`. Then delete the `sys.path.insert` line from `tests/integrity_checks/conftest.py`, since `pythonpath` replaces it. If `conftest.py` is then empty, delete it.

- [ ] **Step 6: Run everything** — `pytest -q` → all pass (existing integrity-check tests included).

- [ ] **Step 7: Commit** — `git add reference/product-loop.md reference/terminology.md reference/CLAUDE.md tests/docs pytest.ini tests/integrity_checks/conftest.py` then `git commit -m "docs: define the product loop and its stage status table"`.

### Task 2: Integration-layer ADR and capability map

**Files:**
- Create: `docs/adr/0007-teamos-is-the-integration-layer.md`, `docs/agents/capabilities.md`
- Modify: `.claude/commands/customer-call.md`, `product-development/product/customers/CLAUDE.md`, `.claude/skills/feature-request-intake/SKILL.md` (vendor wording only)

- [ ] **Step 1: Write ADR 0007** in the house ADR style (see `docs/adr/0005-opportunity-hypothesis-layer.md`):
  - **Decision:** TeamOSTemplate is the system of record for signals, hypotheses and their outcomes. External agents and MCP-backed tools are source adapters that add signals. product-intelligence-agent is the first external adapter.
  - **Considered options:** a separate "Strategic Signals Agent" repo (rejected: it would duplicate the hypothesis layer); hypotheses inside the agent (rejected: discovery spans all sources, not just public text); this repo as adapter host (chosen).
  - **Consequences:** the agent's ADR 004 consumer becomes this repo (handoff 2a). Adapter authors follow Plan 1's signal contract.

- [ ] **Step 2: Write `docs/agents/capabilities.md`** with a table `| Capability | Used by | Configured adapter in this install | How to swap |`. Rows:
  - Issue tracker — GitHub Issues via `gh`, `docs/agents/issue-tracker.md`.
  - Support desk — none yet.
  - CRM / call recorder — manual paste into `/customer-call`.
  - Analytics warehouse — snapshot files (Plan 4).
  - External intelligence — product-intelligence-agent (handoff 2a).
  - Design tool — Figma links in `feature-index.yaml`.

  Add one paragraph: "A skill names the capability, never the vendor. To swap a vendor, change this table's row and the doc it points to."

- [ ] **Step 3: Remove vendor assumptions** from the three workflow files listed above, so they name the capability and link `docs/agents/capabilities.md`. Verify with `git grep -n -i "linear\|jira\|asana" -- .claude product-development/product/customers/CLAUDE.md`: the remaining hits are only the root `CLAUDE.md` team-table column header and example ticket keys.

- [ ] **Step 4: Commit** — `git commit -m "docs: ADR 0007 integration layer and capability map"`.

### Task 3: README rewrite

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README.md** with these sections, in order:
  1. One-paragraph positioning: a product operating system, an integration layer between all the tools a product team uses, built as version-controlled context with an example product.
  2. `## The loop`: a five-line summary and diagram linking `reference/product-loop.md`.
  3. `## How each stage is implemented`: a table mirroring the stage status table (stage, status, entry points), so README and reference agree. It must list these entry points: `/customer-call`, `/feature-request-intake`, the hypothesis template, `analytics/experiments/`, the `prototype` skill (throwaway), `/prd`, `/to-prd` → `/to-spec` → `/to-tickets` → `/implement`, and integrity checks.
  4. `## Plug-and-play`: the capability map and the one way to add a signal (planned, Plan 1), plus product-intelligence-agent as the reference external adapter, linking `https://github.com/AndyMelnykov/product-intelligence-agent`.
  5. `## Repository structure`: keep the router-tree, join-table, naming and `reference/` ideas from the old "Product" section, condensed.
  6. `## Demo`: keep the Team Workspaces walk-through. Add a second walk-through, "Why does HYP-EXTRACT-001 exist?" (hypothesis → its supporting signals `INS-002`, `INS-003` → Reddit sources; mention that the opportunity file is folded into the hypothesis by Plan 2), using today's IDs.
  7. `## AI design decisions`: ADRs 0001–0007 (add 0005, 0006, 0007).
  8. `## Human-agent boundary`: keep.
  9. `## Evaluation`: keep, and state honestly that no run has been recorded.
  10. `## Observability`: `check-references.ps1` **and** `scripts/integrity-checks/` with its daily workflow and `reports/summary.md`; `PAPERCUTS.md` / `SKILL-GAPS.md` as live logs. Delete the claim that the logs are empty.
  11. `## Adopting this on a real team`: keep.
  12. `## Limitations`: delete "feature-index.yaml is hand-maintained, nothing forces…" and write instead that `feature-index-join-completeness` detects unwired artifacts but nothing writes them automatically. Keep the evaluation and taxonomy limitations. Add: "the loop is open at both ends until Plans 1–6 land."
  13. `## Roadmap`: link `ROADMAP.md` and the plans index.
  14. `## License`: keep.

- [ ] **Step 2: Check no planned path is presented as existing** — run `git grep -n -E "product-development/signals|signal-contract|metric-watch|signals\.py" README.md`. Every hit must sit in a sentence containing "planned" or "Plan ".

- [ ] **Step 3: Commit** — `git commit -m "docs: rewrite README around the product loop"`.

### Task 4: Architecture, vision doc, ROADMAP, root router

**Files:**
- Modify: `docs/architecture.md`, `reference/ai-native-product-os.md` (and stage the deletion of `reference/01-ai-native-product-os.md`), `ROADMAP.md`, `CLAUDE.md`, `product-development/CLAUDE.md`, `PAPERCUTS.md`
- Create: `CONTEXT-MAP.md`

- [ ] **Step 1: `docs/architecture.md`.** Add a second diagram, "Integration layer": source adapters (product-intelligence-agent, `/customer-call`, the analytics sweep, MCP-backed adapters) → signals → hypotheses → PRD → tickets (external) → rollout → measurement → signals. In the vocabulary table, set Storage to "Git text files; signals move to a single `signals.csv` (Plan 1)" and Data sources to "the repo plus signals added by source adapters". Keep the existing read/write-path diagram.

- [ ] **Step 2: Vision doc.** Stage the rename: `git add -A reference/01-ai-native-product-os.md reference/ai-native-product-os.md`. Then add `## Product loop` right after `## Purpose`: two sentences plus a link to `product-loop.md`, saying context architecture serves the loop. In `## Suggested future extensions`, mark shipped items as shipped.

- [ ] **Step 3: ROADMAP.md.** Fix the line-3 link to `reference/ai-native-product-os.md#suggested-future-extensions`.
  - **Now:** Plans 1 and 3. **Next:** Plans 2 and 4, and the agent integration (1a).
  - **Later:** prototype ↔ shared design system; capability adapters for Jira / Azure DevOps / a support desk; hybrid retrieval; Codex-compatible instructions.
  - **Keep as-is:** run the evaluation protocol (Now); stale-context and conflict detection (Next).
  - Each item keeps its one-line **Why**.

- [ ] **Step 4: Root router.**
  - In `CLAUDE.md`'s Doc Index, add rows for `reference/product-loop.md`, `docs/agents/capabilities.md` and the plans index.
  - Create `CONTEXT-MAP.md`, following `docs/agents/domain.md` "File structure": list the two existing `CONTEXT.md` files (`product-development/product/PRDs/billing/CONTEXT.md`, `product-development/product/PRDs/extraction-quality/CONTEXT.md`) and say other areas add theirs when first needed.
  - Reword `CLAUDE.md` "Domain docs" to match.
  - In `PAPERCUTS.md`, flip the 2026-11-03 `CONTEXT-MAP.md` entry to `resolved` with a note.
  - In `product-development/CLAUDE.md`, add one line pointing at `reference/product-loop.md`.

- [ ] **Step 5: Verify links** — `powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1` → `No broken references found.` Then `pytest -q` → pass.

- [ ] **Step 6: Commit** — `git commit -m "docs: route architecture, vision, roadmap and router through the product loop"`.

### Task 5: Final verification and PR

- [ ] **Step 1:** `pytest -q` → pass. `python scripts/integrity-checks/run_checks.py --repo-root .` → no new check IDs failing because of this branch. Compare open-finding counts with `main`; content findings unchanged.
- [ ] **Step 2:** Re-read `README.md` top to bottom as a stranger. Every stage says what exists, what's planned, and which plan delivers it.
- [ ] **Step 3:** `git grep -n "01-ai-native-product-os"` → no hits outside `docs/superpowers/plans/` and `local_changed.txt`.
- [ ] **Step 4:** Ask the owner before pushing. The PR body lists the `reference/` files touched (ADR 0003 approval) and ends with the repo's attribution line.
