# Gap analysis: the product discovery and delivery loop vs. TeamOSTemplate + product-intelligence-agent

> **Note (2026-11-03, later):** the model in this analysis was simplified after owner review: a **signal** is one event (unique or repeated, no separate "evidence"), and signals are aggregated into **hypotheses** (an "opportunity" is a hypothesis's first status). Where this document says evidence, signal and opportunity separately, the [plans index](superpowers/plans/2026-11-03-product-loop-plans-index.md) wins.

**Date:** 2026-11-03
**Compares:** the loop described by the owner on 2026-11-03 (signals → hypotheses → validation → prototypes → PRDs → engineering → rollout → back to signals, all plug-and-play) against:

- **TeamOSTemplate** on branch `docs/reconcile-roadmap-integrity-checks` at `66bab53`, plus the uncommitted rename of `reference/01-ai-native-product-os.md` to `reference/ai-native-product-os.md`.
- **product-intelligence-agent**, local clone at `C:\Projects\Reddit-parser\product-intelligence-agent`, branch `feat/review-queue-untrusted-input` at `64bc782`. That branch is 5 commits ahead of `main` (P5: review queue, untrusted input, near-duplicate collapsing) and has no PR yet. The two 2026-10-15 plans are untracked files.

This is a snapshot. Retire or update rows as gaps close.

---

## 1. The direct question: is the signal/hypothesis store in the wrong repo?

**No. The hypothesis layer is already in TeamOSTemplate, and the agent never had one.** The agent has no hypothesis concept anywhere: every `grep -i hypothes` hit is the Hypothesis property-testing library. Its ADR 004 ("materiality-gated event emission boundary") explicitly stops at emitting `product_intelligence.signal.material` and refuses to interpret it. Hypotheses live in TeamOSTemplate: `templates/hypothesis.md`, `templates/opportunity.md`, `reference/discovery-artifact-types.md`, ADR 0005, worked example `product-development/product/PRDs/extraction-quality/`.

**The real problem is that there are two signal stores with the same shape and no bridge between them:**

| Concept | product-intelligence-agent (SQLite) | TeamOSTemplate (CSV) |
|---|---|---|
| One observation | `evidence` row (`EV-…`) | `sources.csv` row (`SRC-###`) |
| A recurring pattern | `canonical_topic` (+ versions, lineage, merge/split) | `insights.csv` row (`INS-###`) |
| Weight | `topic_weekly_mentions`, trend, materiality | count of `sources.csv` rows (derived) |
| "Worth a human's attention" | `material_signal` + `events.jsonl` | `status: new → validated` (manual) |

Neither repo mentions the other: `git grep -i "intelligence-agent\|Strategic Signals"` in TeamOSTemplate returns nothing. Reddit appears in both, as `customer-research-reddit` rows hand-entered in `sources.csv` and as the agent's only live source, with no shared IDs.

**Recommendation.** Keep the split you have, but name it and wire it:

- **TeamOSTemplate owns the canonical signal registry (`insights.csv` / `sources.csv`) and everything after it.** It is the integration layer, so every source has to land in one place there.
- **product-intelligence-agent is one signal adapter.** It is a heavy one: it does dedup, trend and materiality for high-volume public sources. It should stay ignorant of hypotheses, as ADR 004 says.
- **Redefine the "Strategic Signals Agent."** The agent's vision puts a separate, unbuilt Strategic Signals Agent downstream (SIGNAL → ASSESS → THREAT/OPPORTUNITY/WATCH → RESPONSE). In your loop, that role *is* TeamOSTemplate's insight → opportunity → hypothesis stage. Building a third repo for it would duplicate the OS. Update the agent's vision doc and ADR 004 so the event consumer is TeamOSTemplate.
- **Build the bridge.** Write an importer skill in TeamOSTemplate that reads `events.jsonl`, or the agent's future MCP `get_signal` / `get_evidence`, and *proposes* `sources.csv` rows plus either a match to an existing `INS-###` or a new one. A human accepts each proposal, the same pattern as the agent's own `review.py` queue. Store the agent's `signal_id` / `evidence_id` in `source_ref` so provenance survives the hop.

One sub-question stays open. CSV is fine at 20 rows and probably at a few hundred. Many-to-many links between signals and hypotheses, plus scoring and status history, will eventually want a real store. Decide whether that is SQLite in TeamOSTemplate, or YAML files per insight that keep git diffs reviewable, before the importer starts writing volume into the CSVs.

---

## 2. The loop at a glance

Legend: ● implemented and wired · ◐ partial (artifacts or docs exist, no workflow or no link) · ○ missing.

| # | Stage | TeamOSTemplate | Agent | Main gap |
|---|---|---|---|---|
| 1a | Signals: support tickets | ○ | ○ | No adapter, no folder (`Insights/customer-support/` is documented but doesn't exist) |
| 1b | Signals: customer meetings | ◐ `/customer-call` | ○ (vision lists "manually supplied interview summaries", not built) | Calls write account summaries and GitHub issues, **never `insights.csv`**; transcripts are pasted by hand, no CRM/Gong adapter |
| 1c | Signals: competitive | ◐ static `competitive-research/` | ◐ Reddit only; competitor-changelog source unbuilt | Agent output never reaches the OS |
| 1d | Signals: product analytics | ◐ rich static `analytics/` (metrics, investigations, experiments) | ○ (no metric-change signal type) | No path from an analytics finding to a signal row; `AN-###` IDs are cited by both templates but defined nowhere |
| 1e | Signal aggregation in one place | ◐ `insights.csv` / `sources.csv` | ◐ own SQLite registry | Two registries, no bridge (§1) |
| 2 | Hypotheses | ◐ OPP/HYP templates, one worked example, integrity checks | n/a (correctly) | No scoring (reach, confidence, validation cost); hypothesis → signal links are one-directional |
| 3 | Validation | ◐ `## Test` + `## Success criteria` in HYP; experiment write-ups in `analytics/experiments/` | n/a | No routing of cheap ideas to A/B and complex ones to survey/prototype; experiment files don't cite `HYP-` ids; validation results don't come back as signals |
| 4 | Prototyping | ◐ `prototype` skill | n/a | The skill is **throwaway by design**, which contradicts "reuse prototype front-end in production"; no shared design system; `design/` is a Figma pointer |
| 5 | PRDs for agents | ◐ `/prd` (7 sections, CPO check, Review Tier), `/to-prd`, `/to-spec`, `/to-tickets` | n/a | Two PRD templates disagree; no acceptance-criteria section in `/prd`; no "agent-executable vs. engineering-mediated" field; acceptance criteria aren't designed as test sources |
| 6 | Engineering | out of scope (by design) | n/a | Fine. The PRD → ticket hand-off contract is the only part this repo needs to own |
| 7 | Rollout | ◐ PRD "Launch Plan"; experiments name feature flags | n/a | No rollout record per feature, no post-launch metric review, no feedback into signals: **the loop doesn't close** |
| — | Plug-and-play / tool-agnostic | ◐ | ◐ | No adapter contract on either side; GitHub Issues is hard-wired; agent's `fetch.py` is hard-wired to PRAW |

The repo is strongest in the middle of the loop: navigation, the PRD and its review, and integrity checks. It is weakest at both ends, where signals come in and where results come back. Those two ends are what make it a loop and not a document store.

---

## 3. Stage-by-stage gaps

### Stage 1: Input signals

**What exists.** `Insights/insights.csv` + `sources.csv` with a clean, source-agnostic schema (`source_type` is open-ended), derived weight, and a `new → validated → actioned → archived` status. `/customer-call` turns a pasted transcript into a summary, a raw transcript and GitHub feature-request issues. The agent turns Reddit into deduplicated, trend-scored, materiality-gated signals, with evals, a durable ledger and a review queue. That is far more mature than anything on the OS side.

**Gaps.**

1. **No source-adapter contract.** Nothing defines what a source must deliver to become a `sources.csv` row: required fields, provenance, idempotency key, how it proposes an `insight_id`. Each existing path is bespoke. *This is the single most important missing piece for "plug and play."* Write it as `reference/signal-source-contract.md`, so every future MCP-backed source (Zendesk, Intercom, Gong, a CRM, Amplitude) is a small adapter skill against one contract.
2. **Customer calls bypass the signal registry.** `/customer-call` Step 5 writes `customers/accounts/{slug}/calls/summaries/` and files GitHub issues. It never adds `sources.csv` rows, so call evidence carries no weight in `insights.csv` and can't be cited by an opportunity except as a file path.
3. **Support tickets: nothing.** No adapter, no example data, and `Insights/CLAUDE.md` documents a `customer-support/` folder that doesn't exist (logged in `PAPERCUTS.md`).
4. **Analytics isn't a signal source.** `analytics/investigations/` and `analytics/experiments/` contain real findings, such as "low-balance banner cut churn 21.6%", that never become signal rows. The templates cite `AN-###` IDs, but no file defines or allocates them. Either define the scheme or drop it in favour of file paths.
5. **Competitive research is static.** `competitive-research/competitors/*/` holds pricing pages and TL;DRs. Nothing turns a competitor change into a signal. The agent's competitor-changelog source would fill this, but it is unbuilt, has no design spec, and has no route into the OS.
6. **No aggregation workflow.** There is no recurring "sweep" that pulls from all sources, proposes matches against existing `INS-###` rows, and asks a PM to accept them. The agent has this loop internally (`match.py` plus `review.py`). The OS needs the same loop *across* sources.

### Stage 2: Hypotheses

**What exists.** `OPP-` and `HYP-` files next to the PRD they feed, wired into `feature-index.yaml`, with integrity checks for orphan hypotheses, orphan sources, promotion status, stale insights and ID collisions (`scripts/integrity-checks/checks/insights_discovery.py`).

**Gaps.**

1. **No evaluation fields.** You asked for three things per hypothesis: how many customers are affected (reach), how certain we are the metric moves (confidence), and how it can be validated (method and cost). The template has only `Test` and `Success criteria`. Add `Reach` (count, segment, and the signal rows behind it), `Confidence` (enum from `reference/`), `Target metric` (must exist in `reference/metrics.md`, which the PRD CPO check already enforces for PRDs) and `Validation cost` (cheap or expensive, which drives stage 3 routing). Keep the scoring framework pluggable: name the fields, and let a team choose RICE, ICE or its own method in `reference/`.
2. **Many-to-many is half-modelled.** A hypothesis lists `INS-` ids under `Supporting evidence` and must reference exactly one `OPP-`. The reverse direction ("which hypotheses does INS-003 support?") exists only if something scans the files. Generate a derived index from the integrity-check run so both directions can be looked up.
3. **No hypothesis lifecycle.** `Result` is `pending | supported | not supported`. There is no `proposed → in-validation → validated/invalidated → in-PRD → shipped → measured` status, so you can't ask "what are we currently testing?"
4. **No generation workflow.** No skill reads a cluster of signals and drafts opportunities or hypotheses for a PM to review. That is the core AI-assist moment of the discovery half, and today it is entirely manual.
5. **Only one worked example**, `HYP-EXTRACT-001`, still `pending`. Nothing demonstrates a full pass from signal to hypothesis to validated result to PRD.

### Stage 3: Hypothesis validation

**What exists.** Experiment write-ups with hypothesis, setup, feature flag, statistics and a recommendation (`analytics/experiments/**`). The HYP `Test` section names a method.

**Gaps.**

1. **No routing rule.** Nothing encodes "cheap to build → ship behind a flag and A/B test; expensive → survey, prototype or interviews first." Make it a field-driven decision in the hypothesis template, plus a short `reference/validation-methods.md`.
2. **Experiments aren't linked to hypotheses.** Experiment files have a free-text `## Hypothesis` section with no `HYP-` id, and HYP files don't link to experiments until someone fills in `Result` by hand.
3. **Validation evidence doesn't flow back as signals.** Survey responses, prototype feedback and interview reactions should become `sources.csv` rows (`source_type: prototype-feedback`, `survey`, …) attached to the hypothesis's insights. Nothing does this, and `/to-questionnaire` exists without being wired to it.

### Stage 4: Prototyping

**What exists.** The `prototype` skill (logic and UI branches), the Figma pointer in `design/CLAUDE.md`, and `figma:` keys in `feature-index.yaml`.

**Gaps.**

1. **Philosophy conflict.** The vendored `prototype` skill says "throwaway code that answers a question" and keeps the prototype on a throwaway branch. Your vision is that prototype front-end gets reused in production to save time and tokens. Only `LOGIC.md` hints at reuse ("a small, pure module that could be lifted out"). You need a second, high-fidelity mode: built on the production design system, in the production component library, intended to be promoted. Keep the throwaway mode for low-fidelity questions.
2. **No shared design system or shared skills.** `design/CLAUDE.md` says the folder "will hold" design-system changelogs and holds nothing. There is no design-token file, component inventory or "build with our design system" skill that both PMs and front-end engineers load. Decide where it lives: most likely the product's frontend repo, referenced from here, the same "pointed at, not mirrored" rule the README applies to Figma.
3. **No prototype record.** There is no artifact type for a prototype: what question it answers, which `HYP-` it tests, who saw it, what feedback came back, and where the code lives. Add a `prototype:` key to `feature-index.yaml` and a small template.

### Stage 5: PRDs as instructions for agents

**What exists.** `/prd` with a 7-section template, Review Tier, the Step 6 CPO check (metrics validated against `reference/metrics.md`, sources resolve), and feature-index wiring. `/to-prd` → `/to-spec` → `/to-tickets` (`ready-for-agent` tickets with acceptance criteria) → `/implement`.

**Gaps.**

1. **Two PRD templates that disagree.** `/prd` (via `PRDs/CLAUDE.md`) uses Overview / User Stories / Requirements / Design / Technical / Launch Plan / Sources. `/to-prd` uses Overview / Problem / Business Opportunity / Why Now / Customer Requests / Goals & Metrics / Non-Goals / User Stories / Requirements P0–P2 / Launch Plan / Open Questions. It has no `Sources` and no Review Tier, so a `/to-prd` PRD fails the CPO check. Pick one template and make the other entry point produce it.
2. **No acceptance-criteria section in the PRD.** Acceptance criteria appear only in `/to-tickets` output and ad hoc in three PRDs. Your vision makes them first-class: testable, written as given/when/then or an equivalent, and the declared source for automated test generation. Add the section, and make the CPO check reject a PRD without it.
3. **No complexity / executor field.** Nothing in the PRD says "a PM can hand this straight to an agent" vs. "engineering must turn this into agent instructions." Review Tier is about *strategy* review, not *execution* path. Add an `Execution Path` field (`agent-direct` | `engineering-mediated`) with criteria in `reference/`, and branch the hand-off on it: `agent-direct` goes to `/to-tickets`, `engineering-mediated` goes to `/to-spec` with an engineer as owner.
4. **No traceability back to the hypothesis.** The PRD template has no `Hypothesis:` field. `Sources` can cite `INS-`, but nothing ties the PRD's success metric to the `HYP-`'s success criteria, so you can't later check whether the shipped result matches what was bet.

### Stage 6: Engineering

Out of scope by design, and correctly so. The one thing this repo needs to own is the **hand-off contract**: what a ticket must contain (acceptance criteria, PRD link, metric to instrument) and how status flows back (merged → released). Today `docs/agents/issue-tracker.md` covers tracker *mechanics* only.

### Stage 7: Rollout and closing the loop

**What exists.** PRD `Launch Plan`, feature-flag names in experiments, `launch-emails/`, dashboards per feature.

**Gaps.**

1. **No rollout record.** There is no per-feature artifact saying how it shipped (continuous / release / A/B), when, behind which flag, and to which segment.
2. **No post-launch review.** Nothing schedules "N weeks after launch, compare the PRD's success metrics to actuals." `reference/status-definitions.md` has statuses, but no `Measured` step after `Shipped`.
3. **The loop doesn't close.** A/B results, metric shifts and post-launch tickets should land as new `sources.csv` rows and update the originating `HYP-` result. This is the whole point of the loop, and it's the biggest gap after the source contract.

---

## 4. Cross-cutting gaps

1. **Tool-agnosticism is claimed but not structured.**
   - TeamOSTemplate hard-wires GitHub Issues (`docs/agents/issue-tracker.md`). The vendored `setup-matt-pocock-skills` already ships GitHub, GitLab and local variants, which is the right pattern. Extend it to Jira and Azure DevOps, and have every skill say "publish to the issue tracker" rather than calling `gh`. `/feature-request-intake` and `/to-tickets` should be checked for direct `gh` calls.
   - The root `CLAUDE.md` team table already has a "Linear / Jira / Asana ID" column, so the intent exists.
   - The same pattern is needed for support desk, CRM / call recorder and analytics: one `docs/agents/<capability>.md` per capability, naming which MCP server fills it in this install. ROADMAP's "Example integrations with Linear, Jira, GitHub, or Figma" item should become "capability adapters," with one real reference implementation.
2. **The agent isn't plug-and-play internally either.** `fetch.py` imports PRAW directly, and `run_weekly.py` assumes one source. Its own GitHub Issues spec (2026-09-06) adds a second fetcher but no source interface. Introduce a minimal `Source` protocol (fetch since cursor → evidence rows) before writing the second source, not after.
3. **The agent's taxonomy has no slot for internal signals.** `SIGNAL_TYPES` covers customer-market signals from public text. If the agent is ever to process support tickets or call summaries, which its own vision lists as later sources, the taxonomy and the prompt must handle private data with different trust and PII rules. Otherwise, keep private sources in TeamOSTemplate adapters and leave the agent for public sources only. Decide which, and write it down as an ADR in both repos.
4. **The README doesn't describe the loop.** TeamOSTemplate's README frames the repo as a knowledge-navigation reference architecture, which is how it started. It doesn't present the discovery → delivery loop, and it omits shipped pieces:
   - Core workflows omit `/feature-request-intake`, the opportunity/hypothesis layer, the `prototype` skill and `/to-spec` → `/to-tickets` → `/implement`.
   - AI design decisions stop at ADR 0004; 0005 (opportunity/hypothesis) and 0006 (two-track review) are missing.
   - Observability mentions only `check-references.ps1`, not `scripts/integrity-checks/` or its daily workflow.
   - Two claims are now stale: "PAPERCUTS.md is currently empty" (it has entries), and "nothing forces a new PRD into `feature-index.yaml`" (the `feature-index-join-completeness` check now detects it).
   - The product-intelligence-agent isn't mentioned at all.
5. **Uncommitted rename will break a link.** `ROADMAP.md` line 3 links `reference/01-ai-native-product-os.md#suggested-future-extensions`. The working tree renames that file to `reference/ai-native-product-os.md`. Update the link when you commit the rename. `check-references.ps1` should catch it, but only if run.
6. **The vision doc itself predates the loop.** `reference/ai-native-product-os.md` describes context architecture (progressive disclosure, join table, provenance) and three workflows. It doesn't describe signals, hypotheses, validation, prototypes or rollout feedback. The loop you described should become that document's spine, or a new `reference/product-loop.md` that the README links first.
7. **`CONTEXT-MAP.md` is referenced but missing** (root `CLAUDE.md` "Domain docs"). Logged in `PAPERCUTS.md`.

---

## 5. product-intelligence-agent: where the two 2026-10-15 plans fit

Both plans are untracked, and neither has started: there is no `demo/`, `docs/demo/` or `docs/evidence/`.

| Plan | What it delivers | Relation to the loop |
|---|---|---|
| Phase 1, "Launch checks" | Credential-free synthetic demo calling the real stage functions; README contradictions fixed (the `## Evaluation` vs `## Evals` conflict is still live); setup docs repaired; GitHub About/topics | **Credibility of the adapter**, not loop capability. Cheap and independent; worth finishing first because the README currently says both "no eval harness" and documents one |
| Phase 2, "Measured evaluation evidence" | Reviewed golden labels, holdout, pinned live baseline, one gated improvement, case study | **Trust in the signals the OS will import.** Matters more once the bridge in §1 exists, since bad extraction then pollutes `insights.csv`. Human gates G1–G7 make it slow by design |

Things the plans don't cover that the loop needs from the agent, in order:

1. **Merge P5** (`feat/review-queue-untrusted-input`, 5 commits ahead of `main`, no PR) before starting Phase 1. Phase 1 Task 1 baselines from `main`, and Phase 2 baselines must follow the durability work.
2. **Integration API / MCP toolset** (`get_signal`, `get_evidence`, `get_topic_trend`, `search_feedback`). This is what the TeamOSTemplate importer calls, and it is the agent's own roadmap Phase 5. In loop terms it matters more than more sources.
3. **Re-point ADR 004's consumer** from "Strategic Signals Agent (separate, not built)" to "TeamOSTemplate signal importer" (§1).
4. **Source protocol, then GitHub Issues** (spec exists), then **competitor changelogs** (needs a spec). The changelog source finally exercises `entity` / `effective_date` and the dead competitive constants in `materiality.py`.
5. Trend states (`sharply_rising`, `resurfacing`, `dormant`) and scheduling are useful but don't block the loop.

Note: the Phase 2 plan records your standing preference of **no `Co-Authored-By` trailer** in that repo. Keep that in mind when an agent commits there.

---

## 6. Suggested sequence

Ordered by what unblocks the loop end-to-end, not by size.

1. **Write the loop down.** Add `reference/product-loop.md` with your seven stages and the plug-and-play principle. Rewrite the README around it, fix the stale claims (§4.4) and the ROADMAP link (§4.5). Add an ADR recording the §1 decision in both repos: TeamOSTemplate owns signals and hypotheses; the agent is an adapter; the Strategic Signals Agent role is absorbed.
2. **Signal source contract** (`reference/signal-source-contract.md`), then make `/customer-call` write `sources.csv` rows through it. That gives the first internal source and proves the contract.
3. **Hypothesis template v2**: reach, confidence, target metric, validation cost, lifecycle status, a `HYP-` id in experiment files. Add a derived signal ↔ hypothesis index from the integrity-check run.
4. **Agent bridge**: merge P5, build the agent's MCP read tools, then an importer skill in TeamOSTemplate with human accept/reject.
5. **PRD v2**: unify `/prd` and `/to-prd`; add acceptance criteria, `Execution Path`, and a `Hypothesis` link; extend the CPO check.
6. **Close the loop**: rollout record, post-launch metric review, a `Measured` status, and experiment / post-launch results written back as signals and HYP results.
7. **Prototype v2 and design system**: a promotable high-fidelity prototype mode against a shared design-system skill. This is last because it depends on a real frontend repo to point at.
8. **Capability adapters for trackers and tools** (Jira / Azure DevOps / support desk / CRM), each a thin `docs/agents/<capability>.md` plus one reference adapter.
9. In parallel, on the agent side: Phase 1 plan, then Phase 2 plan, then the source protocol and new sources.
