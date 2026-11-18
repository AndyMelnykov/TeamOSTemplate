# Product Loop

Canonical definition of the discovery → delivery loop this repo supports. Every other document links here instead of restating the stages or their status. Vocabulary is defined in [terminology.md](terminology.md).

## The loop

```
calls | tickets | analytics | research | external agents
          |
          v
+-------------------+     +-------------------+     +-------------------+
| 1. SIGNALS        |     | 2. HYPOTHESES     |     | 3. VALIDATION     |
| events from any   |---->| aggregate signals |---->| A/B, survey,      |
| source, unique or |     | into a testable   |     | interviews,       |
| repeated          |     | bet               |     | 4. prototype      |
+-------------------+     +-------------------+     +-------------------+
          ^                                                   |
          |  rollout results become new signals               v
+-------------------+     +-------------------+     +-------------------+
| 7. ROLLOUT AND    |     | 6. ENGINEERING    |     | 5. PRD            |
| MEASUREMENT       |<----| (out of scope)    |<----| validated bet +   |
| results, metric   |     | repo owns only    |     | acceptance        |
| shifts            |     | the ticket handoff|     | criteria          |
+-------------------+     +-------------------+     +-------------------+
```

The flow reads left to right along the top row, then right to left along the bottom row. The upward arrow is the loop closure: rollout results become new signals at stage 1.

1. **Signals.** Anything that happens and might matter: a customer says something, a forum thread appears, a support ticket arrives, a metric misses, an A/B test finishes. A signal is one event from one source. It may be unique or it may repeat; repeats are separate signals.
2. **Hypotheses.** A hypothesis aggregates signals into a testable bet: what we believe, for whom, and what would change our mind. It starts as `proposed`: the problem and its signals, before a test is chosen.
3. **Validation.** A hypothesis is tested by the cheapest adequate **validation path**: cheap to build means build it and A/B test; complex means a prototype, survey or interviews first. Results come back as signals.
4. **Prototyping.** Prototypes answer a design question. They stay throwaway; they are not a path to production code.
5. **PRDs.** A validated hypothesis becomes a PRD with acceptance criteria that engineering can build against.
6. **Engineering.** Development, testing and deployment happen outside this repo. The repo owns only the PRD → ticket hand-off.
7. **Rollout and measurement.** The feature ships, and results (rollout outcomes, A/B results, metric shifts) are measured.

**Loop closure.** Rollout results, A/B outcomes and metric shifts are added as new signals, so the next pass through stage 1 starts from what the last release actually did.

## Plug-and-play principle

TeamOSTemplate is the integration layer and system of record for the loop.

- Every source adds signals the same way, through `scripts/signals/signals.py` ([`signal-contract.md`](signal-contract.md)).
- Every external tool (issue tracker, support desk, CRM / call recorder, analytics warehouse, external intelligence, design tool) is a **capability** filled by a named adapter per install. See [../docs/agents/capabilities.md](../docs/agents/capabilities.md).
- No prioritisation framework, roadmap method or vendor is assumed. The defaults are named in `reference/` and are swappable.

## Ownership boundaries

| Lives here | Does not live here |
|---|---|
| Signals, hypotheses, PRDs, measurements | Engineering work (development, testing, deployment) |
| Pointers to external artifacts (tickets, dashboards, designs) | Raw data held by external tools |
| Prototype decisions and learnings | Prototype code |

product-intelligence-agent is a source adapter, not a part of this repo. See [ADR 0007](../docs/adr/0007-teamos-is-the-integration-layer.md).

## Stage status

Machine-checked by `tests/docs/test_product_loop.py`: every `implemented` or `partial` row must cite paths that exist, and every `planned` row must name a plan. Later plans edit this table as they land.

| Stage | Status | Delivered by | Notes |
|---|---|---|---|
| 1. Input signals | partial | `.claude/commands/customer-call.md`; `product-development/signals/signals.csv`; `scripts/signals/signals.py`; `reference/signal-contract.md`; `product-development/analytics/metric-watch.yaml`; `scripts/signals/analytics_sweep.py` | One store and one entry point. Intake is manual (`/customer-call`, `/log-signal`), external agents calling the script, and the analytics sweep (watched metrics, completed experiments and investigations; weekly workflow or `/analytics-sweep`). Stays partial until a support-desk adapter exists. |
| 2. Hypotheses | implemented | `templates/hypothesis.md`; `scripts/signals/hypotheses.py`; `.claude/commands/hypothesis.md` | Header table; reach derived from cited signals; validation path recommended by a rule and chosen by a human; `hyp-*` integrity checks. |
| 3. Validation | implemented | `product-development/analytics/experiments/`; `scripts/signals/hypotheses.py`; `scripts/signals/analytics_sweep.py` | Experiments are recorded and the recommendation exists. Completed experiments become `experiment` signals through the analytics sweep; other validation results arrive through `/log-signal`. |
| 4. Prototyping | partial | `.claude/skills/prototype/SKILL.md` | Throwaway by design. Linking prototypes to a shared design system is a Later roadmap item. |
| 5. PRDs | implemented | `product-development/product/PRDs/CLAUDE.md`; `.claude/skills/to-prd/SKILL.md`; `.claude/commands/prd.md` | One canonical template; ID'd requirements and acceptance criteria that cover every P0; Execution Path and hand-off rules; `prd-acceptance-criteria` and `prd-execution-path` integrity checks apply from `In Review`. |
| 6. Engineering | out-of-scope | `docs/agents/issue-tracker.md` | Only the PRD → ticket hand-off is owned here. |
| 7. Rollout and measurement | partial | `product-development/analytics/metric-watch.yaml`; `product-development/analytics/snapshots/`; `scripts/signals/analytics_sweep.py`; `.github/workflows/analytics-sweep.yml` | Measurement is automated: snapshots are captured (`/analytics-snapshot`), and a metric that misses its target or moves sharply becomes a signal. Rollout outcomes beyond watched metrics are still logged by hand. Seeded snapshot rows are example data (`captured_by: example-data`). |
| Loop closure | partial | `scripts/signals/analytics_sweep.py`; `.claude/commands/analytics-sweep.md`; `product-development/signals/signals.csv` | Analytics and experiment results feed back as signals; linking them to the hypotheses they concern is a human step in `/analytics-sweep`. |
