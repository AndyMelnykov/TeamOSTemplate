---
name: to-prd
description: Turn the current conversation into a Product Requirements Document and publish it under product-development/product/PRDs/ — no interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

This skill takes the current conversation context and product understanding and produces a **PRD** — the product-facing document that precedes engineering work. Do NOT interview the user — just synthesize what you already know.

## Where this sits in the pipeline

A PRD covers the same three opening stages as an engineering spec — Problem Statement, Solution, User Stories — but for a different audience and a different destination:

- **`/to-prd`** (this skill) writes them for stakeholders: the problem in market/customer terms, the solution as scope, metrics, and launch plan, user stories backed by an ID'd acceptance-criteria table. It publishes to `product-development/product/PRDs/`, not the issue tracker.
- **`/to-spec`** writes the same three stages for engineers handing off to implementation, then continues into **Implementation Decisions** and **Testing Decisions** that a PRD deliberately omits.

Run `/to-prd` first for any product-requirement-driven feature. Once it exists, `/to-spec` should take the PRD as input — reading its Problem, Why Now, User Stories and Acceptance Criteria rather than re-deriving them — and add only the engineering-specific sections.

## Process

1. Explore the repo to understand the current state, if you haven't already:
   - `product-development/product/PRDs/CLAUDE.md` for the canonical PRD template, acceptance-criteria rules, Execution Path rule, and the current PRD roster.
   - `product-development/product/CLAUDE.md` for pillars and terminology — use it throughout (Workflow, Automation Run, Refinement, ESR, TTP, WCR, etc.) rather than redefining it.
   - An existing PRD in the same product area (`product/PRDs/<area>/`) to match tone and section depth.

2. Confirm the product area and feature slug with the user if not already clear from the conversation. The area is one of the top-level keys of `product-development/feature-index.yaml` (read the list there; it changes) or a new one. The filename follows the convention in `PRDs/CLAUDE.md`: `[feature-name]-prd.md`.

3. Write the PRD using the canonical template in `product-development/product/PRDs/CLAUDE.md`, all sections in that order. Map what you know from the conversation onto the canonical sections:

   | Conversation content | Canonical section |
   |---|---|
   | The problem from the user's perspective (numbered pain points where there are several) | `### Problem` |
   | Forcing functions: competitive pressure, request volume, unblocked dependency, leaking metric; verbatim customer requests with source and date | `### Why Now` (cite each in `## Sources`) |
   | Business case and goals, with current value and target | `### Goals & Success Metrics` table (`Source` column says where each metric is measured; names match `reference/metrics.md`) |
   | What this deliberately does not cover, and where deferred scope is tracked | `### Non-Goals` |
   | Actors and capabilities (`As a … I want to … so that …`) | `## User Stories`, numbered `Story 1`, `Story 2`, … |
   | Testable conditions you would have written as per-story bullets | rows of `## Acceptance Criteria` (step 4), not bullets under the story |
   | Scope in priority order | `## Requirements` tables with ids `P0-n`, `P1-n`, `P2-n` |
   | Phased rollout, gates, rollback plan | `## Launch Plan` |
   | Unresolved items | `## Open Questions` after `## Sources` |

   Fill every section with real content. Where the conversation does not support a section, say what is unknown in `## Open Questions` rather than inventing content.

4. Derive acceptance criteria. Follow "Writing acceptance criteria" in `PRDs/CLAUDE.md`:
   - Every user story is covered by at least one AC row (`Covers` lists `Story N`).
   - Every P0 requirement is covered by at least one AC row. Re-read the P0 table and tick each id off against the `Covers` column before moving on.
   - Edge and error cases get their own rows. Give each row exactly one `Verify by` value.
   - A requirement too vague to test goes to `## Open Questions`.

5. Set the two header fields:
   - `**Hypothesis**`: the `HYP-…` id of the hypothesis file that justifies this feature (look in `PRDs/` and `feature-index.yaml`), or `none — <reason>`.
   - `**Execution Path**`: apply the rule in "Execution Path" in `PRDs/CLAUDE.md`. Also set `**Review Tier**` using that file's "Review Tier" criteria.

6. Save and register:
   - Save to `product/PRDs/<area>/<feature-name>-prd.md`.
   - Add a row to the "Current PRDs" table in `product-development/product/PRDs/CLAUDE.md`.
   - Add or update the feature's entry in `product-development/feature-index.yaml` under its area, with a `prd:` key pointing at the new file.
   - Leave `eng-rfc` / `eng-plan` unset in the index — those arrive later, from the engineering flow this PRD feeds.

7. Run the CPO check: perform every check in Step 6 of `.claude/commands/prd.md` against the file you wrote, and fix failures before reporting the PRD as done. Tell the user which checks you ran and the result.

Do NOT include specific file paths or code snippets in the body prose. They go stale fast, and a PRD's job is to describe the product, not the implementation. (Markdown links in `## Sources` are the exception.)
