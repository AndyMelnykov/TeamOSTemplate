# Product loop plans — index (2026-11-03)

Plans that turn TeamOSTemplate into a plug-and-play product operating system for the loop **signal → hypothesis → validation → prototype → PRD → (engineering, out of scope) → rollout → measurement → signal**. Background: [`docs/gap-analysis-product-loop-2026-11-03.md`](../../gap-analysis-product-loop-2026-11-03.md) (written before the model below was simplified; where they differ, this index wins).

## The model

| Term | Meaning |
|---|---|
| **Signal** | One thing that happened, from any source: a customer quote, a forum thread, a support ticket, a metric miss, an A/B result. Unique or repeated; repeats are separate rows. |
| **Hypothesis** | The one discovery artifact. Aggregates signals. Its first status, `opportunity`, is what other tools call an opportunity. |

Nothing else is added to the model: no separate evidence layer, no separate opportunity artifact, no registry, no database.

## Decisions (owner, 2026-11-03)

| Decision | Choice |
|---|---|
| Signal store | One CSV, `product-development/signals/signals.csv`, written only through `scripts/signals/signals.py` |
| product-intelligence-agent | Keeps its own SQLite as private working state and adds signals by calling `signals.py add` in a TeamOSTemplate checkout |
| Hypothesis scoring | Derived reach (signal and account counts), human-set confidence and effort, a rule-based validation-path recommendation. No scoring framework |
| Prototyping | Unchanged: throwaway code. Design-system linkage is a later roadmap item |

## Plans and order

| # | Plan | Depends on | Branch |
|---|---|---|---|
| 0 | [Product loop vision in README and key docs](2026-11-03-plan0-product-loop-vision-docs.md) | — | `docs/product-loop-vision` |
| 1 | [Signals](2026-11-03-plan1-signals.md) | 0 | `feat/signals` |
| 2 | [Hypotheses](2026-11-03-plan2-hypotheses.md) | 1 | `feat/hypotheses` |
| 3 | [PRD acceptance criteria](2026-11-03-plan3-prd-acceptance-criteria.md) | 0 (2 for the `Hypothesis` field to cite real ids) | `feat/prd-acceptance-criteria` |
| 4 | [Analytics → signals](2026-11-03-plan4-analytics-signals.md) | 1 (2 for the hypothesis link) | `feat/analytics-signals` |
| 1a | [Handoff brief for product-intelligence-agent](../../handoffs/2026-11-03-product-intelligence-agent-teamos-integration.md) (input for the other repo, not a plan for this one) | 1 merged | in the agent repo |

Gap 4 (prototyping) has no plan by decision; Plan 0 records the stance and puts the design-system link in `ROADMAP.md` under "Later".

Plan 3 can run in parallel with Plans 1–2. Plans 2 and 4 can run in parallel once Plan 1 is merged. Superseded earlier drafts are kept in [`superseded/`](superseded/) for reference only.

Shared files to watch when running plans in parallel:
- `scripts/integrity-checks/checks/prd_content.py` is edited by Plan 1 Task 3 (citation ids) and Plan 3 Task 3 (acceptance criteria). Whichever merges second rebases and keeps both.
- `scripts/integrity-checks/config.yaml` and `run_checks.py` gain entries in every plan. The conflicts are additive.
- `reference/product-loop.md` and `README.md` get a status-row edit at the end of every plan.

## Conventions shared by every plan

- Tests: `pip install -r scripts/integrity-checks/requirements.txt` then `pytest -q` from the repo root (Plan 0 added the root `pytest.ini` so this one command covers every test directory).
- Integrity checks: `python scripts/integrity-checks/run_checks.py --repo-root .` — a plan may leave *content* findings open (e.g. Draft PRDs without acceptance criteria), never *code* failures.
- Links: `powershell -ExecutionPolicy Bypass -File scripts/check-references.ps1` must report `No broken references found.`
