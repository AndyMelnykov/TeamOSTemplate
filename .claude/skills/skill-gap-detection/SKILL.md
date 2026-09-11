---
name: skill-gap-detection
description: Use immediately whenever you catch yourself hand-executing a multi-step recipe (3+ mechanical steps with a recognizable input → transform → output shape) that has no `.claude/skills/` or `.claude/commands/` entry covering it, especially when it resembles something done before. Trigger the instant you notice you're improvising a repeatable recipe instead of following a named one. Not for genuinely one-off requests, trivial 1-2 step tasks, anything an existing skill/command already covers, or anything the user has explicitly said not to log.
---

# Skill Gap Detection

## Overview

Skills only get written when someone notices a pattern repeating. Left to chance, that noticing happens in a human's head, days later, from memory — this is the one-line complaint box that catches it in the moment instead: when a recipe-shaped task has no skill behind it, log it and keep moving. A human (or another agent, per `superpowers:writing-skills`) reviews the backlog later and promotes repeat offenders into real skills.

## When to use

Fire the moment you notice any of:
- You're about to hand-write the same multi-step sequence (gather X → transform Y → write Z in format W) you recall performing in this session or a prior one
- The user says something like "same as last time," "like we did for X," or "again"
- You're doing 3+ mechanical, nameable steps ad hoc and nothing under `.claude/skills/` or `.claude/commands/` already covers this shape of task

**Don't use it for:**
- A task an existing skill/command already covers — invoke that skill instead of logging a gap. (If you did the work by hand because you didn't realize the skill existed, that's a `PAPERCUTS.md` discoverability entry, not a skill gap.)
- A genuinely one-off request, especially one the user explicitly frames as non-recurring ("just this once")
- Trivial 1-2 step tasks — not every repeated action deserves a skill
- Anything the user has explicitly asked you not to log — user instructions override this skill, same as any other

## What to do

1. **Don't stop working, and don't ask.** Filing is a normal edit, like reading a file — not a suggestion to run past anyone.
2. Check `SKILL-GAPS.md` for an existing entry matching this recipe's shape.
   - If one exists: bump its count (`seen-1x` → `seen-2x`, etc.) and refresh the date.
   - If none exists: append a new line under **Log**:
     ```
     - **YYYY-MM-DD** [area] What manual recipe was performed (rough inputs → outputs), and why no existing skill covered it. (seen-1x, unresolved)
     ```
3. Continue the original task.

## Red flags — you should have logged one already

- You improvised the same shape of multi-step task you remember doing in an earlier turn or session, and didn't check `SKILL-GAPS.md`
- You thought "I keep doing this by hand" and moved on without noting it
- `SKILL-GAPS.md` is unedited and the repetition is only in your head or your final summary
- You're about to *tell the user* you keep redoing this, or ask if you should log it, instead of just editing the file

Any of these mid-task: stop, log it yourself, then resume. No exceptions.
