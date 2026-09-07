# Introducing this practice on a product already in development

For a product that already has months or years of accumulated knowledge — PRDs in Notion,
decisions buried in Slack threads, a partial glossary someone wrote once and never finished.
The goal here is **incremental adoption that pays off before it's finished**, not a
big-bang migration (if you're starting a product with nothing yet, see
[`install-from-scratch.md`](install-from-scratch.md) instead — it's a much shorter path).

Do not attempt to migrate everything before anyone starts using the new structure. Every step
below is ordered so the practice starts paying off after a few hours of work, not after a
multi-week migration project.

## 1. Audit before you move anything

Spend an hour listing where knowledge currently lives: which Notion/Confluence spaces, which
Slack channels people actually search, where PRDs get written, where decisions get recorded
(if anywhere). You're not migrating this content yet — you're finding out what the doc index
in the new root `CLAUDE.md` needs to point at, and which of it is stale enough to just drop.

## 2. Start with `reference/` — highest leverage, lowest disruption

This is the step to do first, before touching any folder structure. Every team already has
terms whose definition drifts depending on who you ask ("active user," "shipped," "growth
tier"). Pick 5-10 of the ones that cause the most repeated arguments or the most re-explaining,
and write them down in `reference/`:

- `reference/terminology.md` (or whatever files this repo's `reference/CLAUDE.md` structures
  it as) — the terms themselves
- `reference/metrics.md` — your current north-star metric and target, as it actually is today,
  not an aspirational redefinition
- `reference/status-definitions.md` — the status vocabulary already in informal use (`Draft`,
  `Shipped`, etc.)

This alone is useful immediately — it stops drift on day one, without requiring anyone to
reorganize a single existing doc. Get a few people to actually cite `reference/` before moving
on to step 3.

## 3. Stand up the root `CLAUDE.md` pointing at what already exists

Don't wait until content is migrated to create the entry point. Write the root `CLAUDE.md` doc
index so it points at your *existing* locations first — a Notion link is a valid doc-index
entry if that's genuinely still where the content lives:

```
| PRDs | https://notion.so/team/prds | Product requirement documents (not yet migrated) |
```

This gives every agent session and every new hire one starting point immediately, even before
anything has moved into the repo. Migrate a doc-index row from an external link to an
in-repo `CLAUDE.md` router only when that area's content actually moves — don't create empty
routers ahead of the content.

## 4. Migrate one function at a time

Pick the function with the most active churn (usually product, since PRDs are being written
continuously) and migrate just that one folder first: create its `CLAUDE.md` router, move or
rewrite its highest-traffic docs into the new naming convention
(`{feature}-prd.md`, `YYYY-MM-DD-{topic}-decision.md`), and update the root doc index row for
it. Prove the pattern works for one function before asking another team to change their habits.

Leave everything else pointing at its old location until its turn comes. A half-migrated repo
with an accurate doc index is fine; a fully-migrated repo that's silently gone stale is not.

## 5. Build `feature-index.yaml` around what's active now, not the full backlog

Don't try to backfill every feature the product has ever shipped into the join table — start
with the 5-10 features currently in active development or under live discussion, per
[ADR 0002](adr/0002-feature-index-as-join-table.md). Add older features only when someone
actually needs to answer a question about one (lazily, on demand), or not at all if they're
truly done and unlikely to come up again.

## 6. Turn on the deterministic checks as soon as there's something to check

- `scripts/check-references.ps1` — run it as soon as `feature-index.yaml` and a handful of
  in-repo Markdown links exist. Fix what it finds before wiring it into CI, then keep it there
  so link rot can't reaccumulate during the rest of the migration.
- `PAPERCUTS.md` + `.claude/skills/papercuts/` — turn this on from the first day of migration,
  not after. Migration work is exactly when you'll hit broken assumptions, missing docs, and
  naming mismatches (see this repo's own log for examples) — capture that friction instead of
  quietly working around it.

## 7. Introduce the human-approval boundary before opening writes up broadly

Once `reference/` and `product/strategy/` hold real canonical content, put
[ADR 0003](adr/0003-human-approval-for-canonical-writes.md)'s approval gate in place *before*
you let agents or new team members write to those folders freely — the whole point of
`reference/` is that many future sessions trust it without re-verifying, so a bad edit there is
more expensive than a bad edit anywhere else in the tree.

## 8. Prove it before mandating it

Migrations stall when they're imposed top-down before anyone's seen the payoff. Two ways to
make the case with evidence instead of assertion:

- **Pilot with one PM or one pod first.** Let them run their next PRD and decision through the
  new structure, then ask what was faster or slower than their old process.
- **Run the evaluation protocol on a real question.** Adapt one or two tasks from
  `evaluation/task-set.md` to a question your team actually needs answered, and run it both
  ways — against the newly-migrated structure and against the old scattered docs — following
  `evaluation/protocol.md`. A concrete "this took 3 file reads instead of 20 minutes of
  searching Slack" is a stronger rollout argument than the structure alone.

Only after the pilot function is showing that payoff, migrate the next function and repeat
steps 4-6 for it.

## Done when (per function, not repo-wide)

- That function's `CLAUDE.md` router exists and the root doc index points at it, not at the
  old external location
- Its active features have real entries in `feature-index.yaml`
- `scripts/check-references.ps1` runs clean for its docs
- At least one person on that team has cited `reference/` instead of re-explaining a
  definition from memory
- `PAPERCUTS.md` has entries from the migration itself — evidence the log is actually catching
  friction, not just installed
