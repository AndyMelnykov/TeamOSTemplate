# Product Loop

Canonical definition of the discovery → delivery loop this repo supports. Every other document links here instead of restating the stages or their status. Vocabulary is defined in [terminology.md](terminology.md).

## The loop

```
sources → evidence → signals → opportunities/hypotheses
  → validation (A/B | prototype | survey | interviews)
  → PRD → engineering (out of scope) → rollout → measurement → evidence
```

1. **Input signals.** Feedback, calls, tickets, analytics and external market intelligence arrive from many sources. Each observation from one source is **evidence**; a recurring pattern across evidence is a **signal**.
2. **Hypotheses.** Signals are framed as **opportunities** and testable **hypotheses**: what we believe, for whom, and what would change our mind.
3. **Validation.** A hypothesis is tested by the cheapest adequate **validation path**: an A/B experiment, a prototype, a survey or customer interviews.
4. **Prototyping.** Prototypes answer a design question. They stay throwaway; they are not a path to production code.
5. **PRDs.** A validated hypothesis becomes a PRD with acceptance criteria that engineering can build against.
6. **Engineering.** Development, testing and deployment happen outside this repo. The repo owns only the PRD → ticket hand-off contract.
7. **Rollout and measurement.** The feature ships, and results (rollout outcomes, A/B results, metric shifts) are measured.

**Loop closure.** Rollout results, A/B outcomes and metric shifts are written back as new evidence, so the next pass through stage 1 starts from what the last release actually did.

## Plug-and-play principle

TeamOSTemplate is the integration layer and system of record for the loop.

- Every source writes evidence through one contract (planned, Plan 1).
- Every external tool (issue tracker, support desk, CRM / call recorder, analytics warehouse, external intelligence, design tool) is a **capability** filled by a named adapter per install. See [../docs/agents/capabilities.md](../docs/agents/capabilities.md).
- No prioritisation framework, roadmap method or vendor is assumed. The defaults are named in `reference/` and are swappable.

## Ownership boundaries

| Lives here | Does not live here |
|---|---|
| Signals, evidence, opportunities, hypotheses, PRDs, rollout records, measurements | Engineering work (development, testing, deployment) |
| Pointers to external artifacts (tickets, dashboards, designs) | Raw data held by external tools |
| Prototype decisions and learnings | Prototype code |

product-intelligence-agent is a source adapter, not a part of this repo. See [ADR 0007](../docs/adr/0007-teamos-is-the-integration-layer.md).

## Stage status

Machine-checked by `tests/docs/test_product_loop.py`: every `implemented` or `partial` row must cite paths that exist, and every `planned` row must name a plan. Later plans edit this table as they land.

| Stage | Status | Delivered by | Notes |
|---|---|---|---|
| 1. Input signals | partial | `.claude/commands/customer-call.md`; `product-development/product/Insights/insights.csv` | Manual call and Reddit-research intake only. Source contract and store: Plans 1–2. Analytics adapter: Plan 6. |
| 2. Hypotheses | partial | `templates/hypothesis.md`; `reference/discovery-artifact-types.md` | Artifacts exist; scoring and evaluation: Plan 3. |
| 3. Validation | partial | `product-development/analytics/experiments/` | Experiments are recorded; routing a hypothesis to a validation path: Plan 3. |
| 4. Prototyping | partial | `.claude/skills/prototype/SKILL.md` | Throwaway by design. Linking prototypes to a shared design system is a Later roadmap item. |
| 5. PRDs | partial | `.claude/commands/prd.md`; `.claude/skills/to-prd/SKILL.md` | Acceptance criteria: Plan 5. |
| 6. Engineering | out-of-scope | `docs/agents/issue-tracker.md` | Only the PRD → ticket hand-off is owned here. |
| 7. Rollout and measurement | planned | Plan 6 | Plan 6 covers measurement; the rollout record is a Later roadmap item. |
| Loop closure | planned | Plan 2; Plan 3; Plan 6 | Outcomes flow back as evidence once the store and adapters exist. |
