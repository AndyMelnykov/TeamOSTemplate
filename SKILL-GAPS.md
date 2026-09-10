# Skill Gaps

A running log of manual, multi-step "recipes" an agent performed by hand that had no skill or command backing them — the mirror image of `PAPERCUTS.md`: papercuts logs things that are *broken*, this logs things that work fine but keep getting redone from scratch because nothing has turned the recipe into a reusable skill yet.

This is not a queue of feature ideas — it only holds recipes an agent actually performed, not proposals. An entry is evidence a real session hit this shape of task, not a wish.

## How agents use this

See [.claude/skills/skill-gap-detection/SKILL.md](.claude/skills/skill-gap-detection/SKILL.md) — it fires when an agent notices it is hand-executing a multi-step task that resembles one it (or a prior logged entry) has already done, with no `.claude/skills/` or `.claude/commands/` entry covering it. Short version: don't stop to build a skill on the spot, don't ask permission, append one line under **Log** below (or bump an existing matching entry's count), then keep going.

## Entry format

```
- **YYYY-MM-DD** [area] What manual recipe was performed (rough inputs → outputs), and why no existing skill covered it. (seen-Nx, status)
```

- **area** — free-form, e.g. `product`, `customers`, `analytics`, `process`
- **seen-Nx** — how many times this exact shape of recipe has been logged; bump the count and refresh the date on the existing line instead of adding a duplicate when the same shape recurs
- **status** — `unresolved` when filed; `resolved` once someone turns it into an actual skill/command, noting which one

## Reviewing the backlog

Periodically skim **Log** below. Any entry at `seen-2x` or higher is a real signal — draft a skill for it (see `superpowers:writing-skills`), then flip the entry to `resolved` and name the skill it became.

## Log

<!-- Newest entries at the bottom. Append here, or bump an existing matching entry's count and date — do not remove existing entries. -->
