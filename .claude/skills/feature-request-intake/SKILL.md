---
name: feature-request-intake
description: Turn a raw feature ask into a structured, function-routed GitHub issue.
---

# Feature Request Intake

This skill defines the fields, evidence-gathering method, and issue format used by `/feature-request-intake`. The command orchestrates the steps; this file is the format reference.

## Required Fields

Every intake produces an issue with these fields, all stated explicitly by whoever files the request — none of them are inferred from search results:

| Field | Description |
|-------|-------------|
| Title | Short, specific description of the ask |
| Description | The raw ask, in the requester's own words or paraphrased with their intent preserved |
| Reporter | Who raised it — a named customer account (see `product-development/product/customers/CLAUDE.md`) if applicable, or "internal" plus the person's name |
| Frequency | How many times/accounts this has come up, as stated by the person filing it |
| Impact | One of `High` / `Medium` / `Low` — see `reference/sla-policy.md` for definitions |

## Dedup Check

Before filing, check both:
1. `product-development/feature-index.yaml` for an existing feature entry with a matching or near-matching name (same search this repo's `/prd` Step 2 already does).
2. Open GitHub issues labeled `feature-request`: `gh issue list --label feature-request --state open --json number,title,body`.

If either surfaces a clear match, tell the user and stop — do not file a duplicate. Report where you looked either way, per the same convention `.claude/skills/triage/SKILL.md` uses for its own redundancy check.

## Evidence Search

Grep `product-development/product/customers/accounts/*/calls/summaries/` for keywords from the request's title/description:

```bash
grep -ril "keyword1\|keyword2" product-development/product/customers/accounts/*/calls/summaries/
```

List any matches with a one-line snippet and ask the person filing the request whether each is actually related before citing it in the issue body. This is supplementary evidence only — it never substitutes for the explicit Frequency/Impact fields above, and an unconfirmed match must not be cited.

## Function Classification

Read the `Function` column of the root `CLAUDE.md` Team table and classify the request into the function whose remit it best matches (e.g. `Engineering`, `EM`, or whatever rows exist in a given install). This is a category label, not a named-owner assignment — final named ownership is a human triage decision, not something this skill automates. Render the label as `area:<function, lowercased, spaces to hyphens>` (e.g. `area:engineering`).

## SLA Lookup

Look up the stated `Impact` value in `reference/sla-policy.md`'s table and record the resulting "Respond by" window as an explicit target date (today + the stated business-day window) in the issue body.

## Issue Format

- **Title:** `[Feature Request] {title}`
- **Labels:** `feature-request`, `area:<function>`
- **Body:**

```markdown
**Reporter:** {reporter}
**Frequency:** {frequency}
**Impact:** {impact} — respond by {computed date} (see `reference/sla-policy.md`)
**Function:** {function}

## Description

{description}

## Supporting Evidence

{confirmed evidence matches, each as a bullet with a link to the call summary file, or "None found / provided" if none}
```

An issue created this way carries no state label (no `needs-triage` label applied here) — it starts in the "unlabeled" bucket that `.claude/skills/triage/SKILL.md`'s discovery step already treats as needing first triage. Intake and triage are sequential: this skill files the issue; `/triage` moves it from there.
