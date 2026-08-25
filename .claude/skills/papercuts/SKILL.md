---
name: papercuts
description: Use immediately whenever you hit friction in this repo that isn't the task itself — a dead-end or misleading tool call, a broken link, a wrong or confusing doc, a footgun config, a missing helper script, an error or workaround that cost real time. Trigger the instant you notice yourself silently working around something broken instead of reporting it. Not for bugs the user explicitly asked you to investigate or fix — only for incidental friction hit en route to something else.
---

# Papercuts

## Overview

Agents hit friction constantly and silently push through — the signal evaporates. This is the one-line complaint box: when this repo's tooling, docs, or config wastes your time, log it and keep moving. A human (or another agent) reviews the backlog later and fixes the real problems.

## When to use

Fire the moment you notice any of:
- A command, script, or tool call that fails, misleads, or needs a workaround
- A doc, link, or comment that's wrong, stale, or missing what you needed
- A config that's a footgun (surprising default, wrong-by-default path, silent failure)
- A missing helper you had to work around or improvise
- Anything that cost more than a few seconds of confusion

**Don't use it for:** bugs or issues the user directly asked you to investigate or fix — those go through this repo's normal issue tracker, not here. This is for friction *around* the task, not the task itself.

## What to do

1. **Don't stop working, and don't ask.** Filing is a normal edit, like reading a file — not a suggestion to run past anyone. The moment you notice the friction, append the line yourself, then keep going.
2. Append one line to the **Log** section of `PAPERCUTS.md` at the repo root, in the format documented there:
   ```
   - **YYYY-MM-DD** [tag] What you hit, and what would have prevented it. (severity, unresolved)
   ```
   Pick a short free-form `tag` (`tooling`, `docs`, `config`, `build`, `test`, ...) and a `severity`: `minor` (annoyance) / `major` (time sink) / `blocker` (hard wall).
3. Continue the original task.

## Red flags — you should have filed one already

- You worked around a broken command instead of just running it
- You thought "this doc is wrong" and moved on without noting it
- You improvised a helper because no existing one worked
- `PAPERCUTS.md` is unedited and the friction is only in your head or your final summary
- You're about to *tell the user* about the friction, or ask if you should log it, instead of just editing the file — asking is stalling; the edit is the action

Any of these mid-task: stop, file the papercut yourself, then resume. No exceptions:
- Don't wait for the user to say "yes, log it"
- Don't defer it to "I'll mention it in my summary"
- Don't skip it because the task is almost done — the edit costs one tool call
