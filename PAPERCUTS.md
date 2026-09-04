# Papercuts

A running log of friction agents hit while working in this repo — dead-end tool calls, broken links, misleading docs, footgun configs, missing helpers. The point isn't to fix things in the moment; it's to leave a trail so a human (or another agent) can review the backlog later and fix what keeps costing time.

This is a markdown-only adaptation of the [papercuts](https://github.com/steveruizok) concept — an append-only log instead of a CLI + JSONL file, so it works in any repo with no install step. Copy this file and `.claude/skills/papercuts/` into another repo to reuse the practice there.

## How agents use this

See [.claude/skills/papercuts/SKILL.md](.claude/skills/papercuts/SKILL.md) — it fires automatically when an agent hits friction mid-task. Short version: don't stop to fix it, don't ask permission, append one line under **Log** below, then keep going.

## Entry format

```
- **YYYY-MM-DD** [tag] What you hit, and what would have prevented it. (severity, status)
```

- **tag** — free-form area, e.g. `tooling`, `docs`, `config`, `build`, `test`
- **severity** — `minor` (annoyance) / `major` (time sink) / `blocker` (hard wall, had to work around it)
- **status** — `unresolved` when filed; flip to `resolved` (never delete the entry) once someone fixes the underlying issue, ideally noting the fix

## Reviewing the backlog

Periodically skim **Log** below for repeat offenders — the same tag or file coming up more than once is a signal worth acting on. Fix the underlying problem, then flip the entry's status to `resolved`.

## Log

<!-- Newest entries at the bottom. Append here — do not edit or remove existing entries. -->

- **2026-08-31** [docs] `docs/agents/domain.md` documents a `docs/adr/` convention for repo-wide decisions, but nothing in the root `CLAUDE.md` doc index pointed to it before this entry — an agent writing its first ADR had to already know to open `domain-modeling/SKILL.md` to discover the path. Fixed by adding an explicit `docs/adr/` row to the root doc index. (minor, resolved)
- **2026-09-04** [docs] `product-development/product/strategy/plans/example_product-competitive-strategy-plan.md` referenced `strategy/vision/example_product-platform-vision.md` as a source file, but the actual file on disk is `strategy/vision/platform-vision.md` — a name that never existed. Fixed the reference while re-theming this file; would have cost the next agent that runs this plan a failed read. (minor, resolved)
