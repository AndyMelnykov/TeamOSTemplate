# Installing this practice on a new product

For a product with no existing knowledge base yet — no PRD backlog to migrate, no scattered
docs to reconcile. You're choosing the shape from day one instead of retrofitting it later
(if that's not your situation, see [`install-existing-product.md`](install-existing-product.md)
instead).

This repo is the reference implementation, populated with a fictional example
(`example_product`). Installing the practice means copying its *shape*, then replacing the
example content with your own — not copying `example_product`'s specific pillars or team
structure verbatim (see the README's [Limitations](../README.md#limitations): the taxonomy is
tuned to one team's shape, and adopting it elsewhere means adapting it).

## 1. Copy the skeleton

Bring over the structural files, not the example content:

```
CLAUDE.md                          # rewrite — see step 2
CONTEXT-MAP.md
PAPERCUTS.md
ROADMAP.md                         # optional, but useful from day one
reference/
product-development/CLAUDE.md
product-development/feature-index.yaml   # truncate to an empty table, see step 4
templates/
team/
docs/adr/
docs/agents/
docs/architecture.md
scripts/check-references.ps1
.claude/agents/onboarding.md
.claude/commands/
.claude/skills/papercuts/
.claude/skills/domain-modeling/   # if using the domain-modeling skill (step 6)
```

Leave `product-development/product/PRDs/`, `customers/`, `strategy/`, etc. as empty
directories (or delete their `example_product`-specific files) — you'll populate them as real
work happens, not by adapting the example's content.

## 2. Rewrite the root `CLAUDE.md`

This is the entry point every agent session and every new hire starts from. Replace:

- **Team table** — your actual roster, GitHub handles, issue-tracker IDs, Slack IDs
- **Channels table** — your actual Slack/Teams channels
- **Doc Index** — keep the shape (one row per function/area, pointing at that area's
  `CLAUDE.md`), but only list folders that actually exist for you. Don't pre-create rows for
  functions you don't have (e.g. drop `data-engineering` if there's no data-eng team yet) —
  add the row when the function and its folder both exist.

## 3. Write `reference/` before anything else

Every other artifact in this repo is supposed to *cite* `reference/` rather than redefine
terms locally — so it has to exist first, even in a thin form. At minimum, write down:

- **Terminology** — the 5-10 terms your team already argues about the definition of
- **Metrics** — your north-star metric and its current target
- **Segments** — how you currently split customers/users, if you do
- **Statuses** — the lifecycle a PRD/RFC moves through (`Draft` → `Shipped`, or whatever you
  use)
- **Decision types** — see `reference/decision-types.md` in this repo for the convention

Thin and real beats comprehensive and speculative. Add terms as they come up in practice
rather than trying to enumerate the whole domain upfront.

## 4. Adapt the function × product-area matrix

Decide your top-level axis under `product-development/` — it should match how your team is
actually organized (product/engineering/design/analytics/data-engineering is this repo's
shape, not a requirement). Create one folder per function, each with its own `CLAUDE.md`
router describing what's inside.

Then set up `feature-index.yaml` as an **empty table** with the right columns for your
functions — don't backfill entries for features that don't exist yet. Add a row the first time
a feature gets a PRD, RFC, or ticket, per [ADR 0002](adr/0002-feature-index-as-join-table.md).

## 5. Wire up the deterministic checks

- Run `scripts/check-references.ps1` locally once you have a handful of internal links, and
  add it as a pre-commit hook or CI check from the start — it's much cheaper to keep links
  correct as you go than to clean up a backlog of rot later.
- Keep `PAPERCUTS.md` and its skill (`.claude/skills/papercuts/`) active from day one, even
  though the structure is new — friction found while a team is *building* the practice is the
  most valuable friction to capture.

## 6. Set up the agent tooling

- `.claude/agents/onboarding.md` — point new hires at it; it reads `team/onboarding-guides/`
  and tracks their checklist. Write the general guide plus one per function before your first
  hire needs it.
- `.claude/commands/` — bring over the commands relevant to your workflows (e.g.
  `customer-call.md`, `prd.md`), or write new ones the same way once you have a recurring task
  worth turning into a skill/command.
- `docs/agents/domain.md` + `CONTEXT-MAP.md` — only needed once you're ready to start
  capturing architecture decisions and a glossary per functional area; the domain-modeling
  skill creates `CONTEXT.md` files lazily, so it's fine to leave this until the first decision
  actually needs recording.
- `docs/agents/issue-tracker.md` — point it at wherever your issues actually live (GitHub,
  Linear, Jira).

## 7. Socialize it

The practice only works if agents *and* humans treat the root `CLAUDE.md` as the starting
point instead of Slack or someone's head:

- Tell every team member (and every coding-agent session) to start from `CLAUDE.md` at the
  repo root, not from searching the tree.
- The first few PRDs/RFCs/decisions written this way will feel slower than the old habit —
  that's expected. The payoff shows up on the second and third time someone needs the same
  context.
- Optionally, adapt `evaluation/task-set.md` and `evaluation/protocol.md` to a handful of your
  own real questions, and run them periodically as a sanity check that the structure is still
  answering things correctly as it grows.

## Done when

- `reference/` has real (if thin) content for terminology, metrics, and statuses
- Every team member's first agent session starts from the root `CLAUDE.md`
- `feature-index.yaml` has at least one real entry
- `scripts/check-references.ps1` runs clean and is wired into pre-commit or CI
- `PAPERCUTS.md` has at least one entry (a sign the log is actually being used)
