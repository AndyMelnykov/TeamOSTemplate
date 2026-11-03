# Product Loop

Canonical definition of the discovery → delivery loop this repo supports. Every other document links here instead of restating the stages or their status. Vocabulary is defined in [terminology.md](terminology.md).

## The loop

```
calls | tickets | analytics | research | external agents
          |
          v
+-------------------+     +-------------------+     +-------------------+
| 1. SIGNALS        |     | 2. HYPOTHESES     |     | 3. VALIDATION     |
| events from any   |---->| aggregate signals;|---->| A/B, survey,      |
| source, unique or |     | first status is   |     | interviews,       |
| repeated          |     | opportunity       |     | 4. prototype      |
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
2. **Hypotheses.** A hypothesis aggregates signals into a testable bet: what we believe, for whom, and what would change our mind. Its first status, `opportunity`, is the problem framed before a bet is chosen; there is no separate opportunity artifact.
3. **Validation.** A hypothesis is tested by the cheapest adequate **validation path**: cheap to build means build it and A/B test; complex means a prototype, survey or interviews first. Results come back as signals.
4. **Prototyping.** Prototypes answer a design question. They stay throwaway; they are not a path to production code.
5. **PRDs.** A validated hypothesis becomes a PRD with acceptance criteria that engineering can build against.
6. **Engineering.** Development, testing and deployment happen outside this repo. The repo owns only the PRD → ticket hand-off.
7. **Rollout and measurement.** The feature ships, and results (rollout outcomes, A/B results, metric shifts) are measured.

**Loop closure.** Rollout results, A/B outcomes and metric shifts are added as new signals, so the next pass through stage 1 starts from what the last release actually did.

## Plug-and-play principle

TeamOSTemplate is the integration layer and system of record for the loop.

- Every source adds signals the same way (planned, Plan 1).
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
| 1. Input signals | partial | `.claude/commands/customer-call.md`; `product-development/product/Insights/insights.csv` | Manual call and Reddit-research intake only, kept in `Insights/` until Plan 1 replaces it with `signals.csv`. Analytics feed: Plan 4. |
| 2. Hypotheses | partial | `templates/hypothesis.md`; `reference/discovery-artifact-types.md` | Hypotheses and a separate opportunity file exist today. Plan 2 makes opportunity a hypothesis status and adds derived reach and a validation recommendation. |
| 3. Validation | partial | `product-development/analytics/experiments/` | Experiments are recorded. Results as signals: Plans 1 and 4. |
| 4. Prototyping | partial | `.claude/skills/prototype/SKILL.md` | Throwaway by design. Linking prototypes to a shared design system is a Later roadmap item. |
| 5. PRDs | partial | `.claude/commands/prd.md`; `.claude/skills/to-prd/SKILL.md` | Acceptance criteria: Plan 3. |
| 6. Engineering | out-of-scope | `docs/agents/issue-tracker.md` | Only the PRD → ticket hand-off is owned here. |
| 7. Rollout and measurement | planned | Plan 4 | Metric and experiment results become signals. |
| Loop closure | planned | Plan 1; Plan 4 | Outcomes flow back as signals once signals have a single store and analytics feeds it. |
