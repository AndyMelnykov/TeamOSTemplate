# Feature Request Intake

You are turning a raw feature ask into a structured, routed GitHub issue.

**Field, evidence-search, and format details:** read `.claude/skills/feature-request-intake/SKILL.md` before starting Step 3.

## Task Overview

Process a feature request by:
1. Gathering the raw ask and reporter
2. Checking for an existing entry (feature-index and open `feature-request` issues)
3. Searching for supporting evidence in customer call summaries
4. Classifying the request by function
5. Looking up the SLA target
6. Filing the GitHub issue

## Step 1: Gather the Raw Ask

Ask the user for:
- A short title
- The full description (paste, forward, or paraphrase)
- Who raised it — a named customer account (check `product-development/product/customers/CLAUDE.md` for the current list) or an internal reporter

## Step 2: Check for an Existing Entry

Run the Dedup Check from `.claude/skills/feature-request-intake/SKILL.md` against both `product-development/feature-index.yaml` and open `feature-request`-labeled issues. If a match is found, tell the user and stop.

## Step 3: Search for Evidence

Run the Evidence Search from the skill file against `product-development/product/customers/accounts/*/calls/summaries/`. Present any matches to the user and ask which, if any, are actually related before including them.

## Step 4: Gather Frequency and Impact

Ask the user directly for:
- **Frequency** — how many times/accounts this has come up
- **Impact** — `High`, `Medium`, or `Low` (see `reference/sla-policy.md` for definitions)

Do not infer either value from the evidence search in Step 3.

## Step 5: Classify by Function

Read the root `CLAUDE.md` Team table's `Function` column and pick the closest match, per the skill file's Function Classification section. Confirm the choice with the user if it's ambiguous.

## Step 6: Look Up the SLA

Look up the stated Impact level in `reference/sla-policy.md` and compute the "respond by" date.

## Step 7: File the Issue

Compose the issue per the skill file's Issue Format section and create it:

```bash
gh issue create --title "[Feature Request] {title}" --label "feature-request" --label "area:{function}" --body "{body}"
```

Use a heredoc for the body per `docs/agents/issue-tracker.md`'s conventions. Report the created issue's number and URL to the user. The issue starts unlabeled for triage state — `.claude/skills/triage/SKILL.md` picks it up from `needs-triage` onward; this command's job ends once the issue exists.
