# New Feature Intake Workflow Spec

## Overview

This workflow takes a raw feature idea — from a customer call, an internal proposal, or a support-ticket pattern — through to either a PRD-ready intent or a documented decision not to pursue it. It runs interactively: each step has an automated part (gathering, checking) and an interactive part (PM judgment).

---

## Process Flow

```
1. Capture the problem
2. Identify supporting evidence
3. Check product-development/feature-index.yaml for an existing entry
4. Draft intent
5. Resolve constraints
6. Create PRD only after approval
```

---

## Step 1: Capture the Problem

Ask the requester (PM, or an agent processing a customer call) to state the problem in one or two sentences: who has it, what they're trying to do, and what's currently stopping them. Do not accept a solution ("build X") as the problem statement — restate it as the underlying need if necessary.

## Step 2: Identify Supporting Evidence

Gather what evidence already exists:
- Customer call summaries mentioning this problem (`product-development/product/customers/accounts/*/calls/summaries/`)
- Support ticket patterns or investigation docs (`product-development/analytics/investigations/`, `product-development/engineering/bug-investigations/`)
- Competitive pressure (`product-development/product/competitive-research/`)

If no evidence exists beyond a single request, say so explicitly rather than treating one data point as validated demand.

## Step 3: Check for an Existing Entry

Search `product-development/feature-index.yaml` for a feature that already covers this problem, by product area and by keyword. If a matching entry exists, this is not new intake — route the requester to the existing PRD/RFC/plan instead of starting a duplicate.

## Step 4: Draft Intent

Write a one-paragraph statement of intent: the problem, the evidence, and the product area it belongs to (`home-page`, `billing`, `prototyping`, `starter-templates`, or `deployment` — see `product-development/feature-index.yaml` for the current set). This is not a PRD — it's the artifact a PM reviews to decide whether a PRD is warranted.

## Step 5: Resolve Constraints

Before drafting a PRD, confirm with the PM:
- Which of the Five Core Pillars (`product-development/product/CLAUDE.md`) this serves.
- Whether it depends on unshipped work (check `product-development/feature-index.yaml` for the relevant product area).
- Rough sizing judgment — is this PRD-worthy, or small enough to go straight to an engineering plan without a PRD.

If the PM declines to proceed, record why in a decision file per `reference/decision-types.md` (type: Product decision) rather than silently dropping the idea.

## Step 6: Create PRD Only After Approval

Once the PM approves, use the `/prd` command to create the PRD in `product-development/product/PRDs/{product-area}/{feature-name}-prd.md`, and add a new entry to `product-development/feature-index.yaml` under the relevant product area with at minimum the `prd` key populated, `**Status**` set to `Draft` per `reference/status-definitions.md`.

---

## Conventions

- One feature idea per intake run — do not batch multiple unrelated ideas into one pass.
- Step 4's draft intent is disposable if the PM declines in Step 5 — it does not need to be preserved as a file unless the PM asks for a record of why it was declined (see Step 5).
- This workflow does not replace the customer-call processing workflow (`.claude/commands/customer-call.md`) — a customer call is processed first, and if it surfaces a feature request worth pursuing, that request becomes this workflow's Step 1 input.
