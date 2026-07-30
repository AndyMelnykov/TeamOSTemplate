# Product OS Example Repo

This repo is a complete example of a Product OS, the shared knowledge base.

The core idea: the repo is the team's shared brain. Rather than one person holding context and answering the same questions, every artifact a product team produces is committed as Markdown, structured so an agent starting a cold session already knows the product, the people, the vocabulary, and where things live. No source code — the deliverable is context itself.

Six structural moves that make it work
1. Progressive disclosure through nested routers. 34 CLAUDE.md files, one per meaningful folder. The root holds only what's universally needed (team roster with GitHub/tracker/Slack IDs, channels, top-level doc index); each level down describes its own contents and links deeper. An agent walks the tree instead of loading 192 files.

2. A function × product-area matrix. Functions are the top axis (product/, engineering/, analytics/, data-engineering/, design/). Once you know the pattern, you can guess any path.

3. One join table to defeat the matrix. That grid scatters a single feature across ~8 folders, so feature-index.yaml reassembles it: per feature, the PRD, eng RFC + plan, data-eng RFC + plan, Figma link, tickets, table schemas, queries, dashboards, experiments, and bug investigations. Root CLAUDE.md tells agents to check it first. This is the keystone — it's what lets the strict folder taxonomy coexist with feature-shaped questions.

4. Naming conventions as an addressing scheme. {feature}-prd.md, {feature}-rfc.md, {feature}.md for plans, bug-MM-DD-YYYY-{desc}/investigation-plan.md, YYYY-MM-DD.md for dated docs. Lookups become constructible rather than searched.

5. Shared vocabulary defined once. Terminology tables (Project, Generation, Iteration), metric definitions with targets (GSR > 92%, TTD < 15 min, PCR > 60%), segment definitions, customer categories (paying / pilot / pipeline / free tier). Every downstream doc cites these instead of re-defining them.

6. Raw kept beside derived. calls/transcripts/ sits next to calls/summaries/; meetings/*/docs/ next to summaries/. Provenance survives, so a claim can always be traced to its source.


Processes are executable, not just written down
.claude/ turns recurring work into runnable units: an onboarding agent (asks role → loads general + role guide → tracks the checklist), a /customer-call command, and a customer-call-summary skill that carries a style guide plus a worked example as the quality bar.

Bigger processes get decomposed into ordered step files. The bi-weekly update is the model: a workflow-spec.md plus five numbered steps, each with an automated half (gather, draft) and an interactive half (PM reviews, approves), writing sections incrementally so progress is visible. It explicitly separates what changes every cycle (eng status, call synthesis) from what carries forward (OKR structure, customer background), names special cases ("new pilot?", "archive stale customer?"), and points at reference/2026-02-11.md as the canonical good output.

Throughout, external systems are pointed at, not mirrored — Figma, Linear/Jira/Asana, Snowflake, Segment, Amplitude, Stripe, Sigma/Mode are listed with purpose and access path. Only what benefits from version control lives here; design/ is deliberately a one-page stub for exactly that reason.

## License

This work is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). See [LICENSE](LICENSE) for details.
