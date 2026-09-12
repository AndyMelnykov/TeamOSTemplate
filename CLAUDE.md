# example_product

## Team

| Function | Team Member | GitHub | Linear / Jira / Asana ID | Slack ID |
|----------|-------------|--------|-----------|----------|
| EM | Alex Rivera | `alexrivera` | `b2c3d4e5-f6a7-8901-bcde-f12345678901` | `U0B2C3D4E5F` |
| Engineering | Jordan Kim | `jordankim` | `c3d4e5f6-a7b8-9012-cdef-123456789012` | `U0C3D4E5F6A` |


## Teams Channels

| Channel | ID | Visibility | Purpose |
|---------|-----|------------|---------|
| #eng | `C0A1B2C3D4E` | Private | Engineering discussions, code reviews, deploys, incident response |
| #design | `C0B2C3D4E5F` | Private | Design critiques, asset reviews, UX research share-outs |
| #product | `C0C3D4E5F6A` | Private | PRD reviews, roadmap planning, feature prioritization |


## Doc Index

**When looking up artifacts for a specific feature (PRDs, RFCs, plans, schemas, dashboards, experiments, tickets), check `product-development/feature-index.yaml` first.** It maps every feature to all related artifacts in one place.

| Area | File | Description |
|------|------|-------------|
| Feature index | `product-development/feature-index.yaml` | Master lookup — every feature mapped to its PRDs, RFCs, plans, schemas, experiments, tickets |
| Reference | `reference/CLAUDE.md` | Canonical definitions — terminology, metrics, segments, statuses, decision types |
| Product | `product-development/product/CLAUDE.md` | Product context, pillars, segments, competitive landscape |
| PRDs | `product-development/product/PRDs/CLAUDE.md` | Product requirement documents index |
| Customer insights | `product-development/product/customers/CLAUDE.md` | Customer calls, account context, feature requests |
| Competitive research | `product-development/product/competitive-research/CLAUDE.md` | Competitor intel and feature comparisons |
| Strategy | `product-development/product/strategy/CLAUDE.md` | Roadmaps, vision, business context |
| Launches | `product-development/product/launch-emails/CLAUDE.md` | Launch communications |
| Sales enablement | `product-development/product/sales-enablement/CLAUDE.md` | Sales-facing docs and onboarding |
| Processes | `product-development/product/processes/CLAUDE.md` | Operational processes |
| Product context | `product-development/product/product-context/CLAUDE.md` | Reference docs for systems |
| Analytics | `product-development/analytics/CLAUDE.md` | Metrics glossary, data sources, common queries |
| Engineering | `product-development/engineering/CLAUDE.md` | Engineering plans, RFCs, bug investigations |
| Meetings | `product-development/product/meetings/CLAUDE.md` | Meeting docs, transcripts, summaries |
| Team | `team/` | Onboarding guide and team resources |
| Evaluation | `evaluation/CLAUDE.md` | Benchmark tasks + protocol for measuring whether the context architecture helps agents |
| Architecture | `docs/architecture.md` | How an agent moves through the repo tree; deterministic vs. human-approval policy layer |
| Roadmap | `ROADMAP.md` | What's next and why, not a feature wishlist |
| Decisions | `docs/adr/` | Repo-wide architecture decisions (retrieval strategy, join table, write approval, agent orchestration) |
| Adoption guides | [`docs/install-from-scratch.md`](docs/install-from-scratch.md), [`docs/install-existing-product.md`](docs/install-existing-product.md) | Step-by-step guides for introducing this practice to a team — greenfield vs. an existing product |

## Agent skills

### Papercuts

When you hit friction — a dead-end tool call, broken link, misleading doc, footgun config, missing helper, anything that cost you time or forced a workaround — file it yourself immediately, as part of doing the task, not after: append one line to the **Log** section of `PAPERCUTS.md` at the repo root:

    - **YYYY-MM-DD** [tag] What you hit, and what would have prevented it. (severity, unresolved)

`tag` is free-form (`tooling`, `docs`, `config`, `build`, `test`, ...); `severity` is `minor` / `major` / `blocker`. This edit is required, not optional: don't ask whether to log it, don't just mention it in your final summary or report it back to the user instead — those are not substitutes for writing the line. File it, then keep working. Full trigger conditions: `.claude/skills/papercuts/SKILL.md`.

### Skill gaps

When you catch yourself hand-executing a multi-step recipe that has no skill or command behind it — especially one that resembles something done before — log it immediately: append one line to the **Log** section of `SKILL-GAPS.md` at the repo root. Don't stop to build the skill on the spot, don't ask permission, just log and keep going. Full trigger conditions: `.claude/skills/skill-gap-detection/SKILL.md`.

### Issue tracker

Issues live in GitHub Issues for `AndyMelnykov/TeamOSTemplate`, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Multi-context layout — `CONTEXT-MAP.md` at the repo root, with a `CONTEXT.md` per functional area under `product-development/<area>/` and `team/`. See `docs/agents/domain.md`.

