# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT-MAP.md`** at the repo root — points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`** — repo-wide decisions.
- Context-scoped decisions live in each area's own `docs/adr/` (see the map below).

If any of these files don't exist yet, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill creates them lazily when terms or decisions actually get resolved.

## File structure

This repo uses a **multi-context** layout, adapted for a docs/product-knowledge repo (no `src/`):

```
/
├── CONTEXT-MAP.md                          ← points to each area's CONTEXT.md
├── docs/adr/                               ← repo-wide decisions
├── product-development/
│   ├── product/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/
│   ├── engineering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/
│   ├── analytics/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/
│   ├── design/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/
│   └── data-engineering/
│       ├── CONTEXT.md
│       └── docs/adr/
└── team/
    ├── CONTEXT.md
    └── docs/adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in the relevant area's `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_
