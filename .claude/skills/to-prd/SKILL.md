---
name: to-prd
description: Turn the current conversation into a Product Requirements Document and publish it under product-development/product/PRDs/ — no interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

This skill takes the current conversation context and product understanding and produces a **PRD** — the product-facing document that precedes engineering work. Do NOT interview the user — just synthesize what you already know.

## Where this sits in the pipeline

A PRD covers the same three opening stages as an engineering spec — Problem Statement, Solution, User Stories — but for a different audience and a different destination:

- **`/to-prd`** (this skill) writes them for stakeholders: the problem in market/customer terms, the solution as scope, metrics, and launch plan, user stories as acceptance-tested requirements. It publishes to `product-development/product/PRDs/`, not the issue tracker.
- **`/to-spec`** writes the same three stages for engineers handing off to implementation, then continues into **Implementation Decisions** and **Testing Decisions** that a PRD deliberately omits.

Run `/to-prd` first for any product-requirement-driven feature. Once it exists, `/to-spec` should take the PRD as input — reading its Problem Statement/Business Opportunity and User Stories rather than re-deriving them — and add only the engineering-specific sections.

## Process

1. Explore the repo to understand the current state, if you haven't already:
   - `product-development/product/PRDs/CLAUDE.md` for the current PRD roster and naming convention.
   - `product-development/product/CLAUDE.md` for pillars and terminology — use it throughout (Project, Generation, Iteration, GSR, TTD, PCR, etc.) rather than redefining it.
   - An existing PRD in the same product area (`product/PRDs/<area>/`) to match tone and section depth.

2. Confirm the product area and feature slug with the user if not already clear from the conversation. The area matches an existing `PRDs/<area>/` subfolder (`billing`, `deployment`, `home-page`, `prototyping`, `starter-templates`) or is a new one. The filename follows the existing convention: `[feature-name]-prd.md`.

3. Write the PRD using the template below, then:
   - Save it to `product/PRDs/<area>/<feature-name>-prd.md`.
   - Add a row for it to the "Current PRDs" table in `product-development/product/PRDs/CLAUDE.md`.
   - Add or update the feature's entry in `product-development/feature-index.yaml` under its product area, with a `prd:` key pointing at the new file.
   - Leave `eng-rfc` / `eng-plan` unset in the index — those arrive later, from the engineering flow this PRD feeds.

Do NOT include specific file paths or code snippets in the body. They go stale fast, and a PRD's job is to describe the product, not the implementation.

<prd-template>

# <Feature Name> - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | <name>, PM |
| **Status** | Draft |
| **Last Updated** | <date> |
| **Related RFC** | _TBD — filled in once engineering scopes the RFC_ |
| **Related Plan** | _TBD — filled in once engineering scopes the plan_ |

## Overview

One paragraph: what this feature is and the outcome it produces for the user.

## Problem Statement

The problem, from the user's perspective. A numbered list of the compounding pain points where there is more than one.

## Business Opportunity

Why this is worth building, tied to metrics or revenue. Where the connection is quantifiable, use a table of conversion/retention/revenue levers.

## Why Now

The forcing function(s) — competitive pressure, request volume, a newly-unblocked dependency, or a metric actively leaking. A bullet list, each backed by a number or a date.

## Customer Requests

Verbatim customer requests, each attributed to a source (support ticket, sales/customer call, NPS, feature-request tool) and a date.

## Goals & Success Metrics

### Goals

Numbered list, each goal one sentence.

### Success Metrics

Table: Metric | Current | Target | Timeline.

### Non-Goals

Bullet list of what this explicitly does not cover. Point at where deferred scope IS tracked (a phase-2 note, a separate ticket) rather than leaving it silently dropped.

## User Stories

One `###` per story:

**As a** <actor>, **I want to** <capability>, **so that** <benefit>.

**Acceptance criteria:**
- Testable condition
- Testable condition

Cover the primary flows exhaustively — every acceptance criterion here is a requirement `/to-spec` will need to account for later.

## Requirements

### Must Have (P0)

Table: ID | Requirement.

### Should Have (P1)

Table: ID | Requirement.

### Nice to Have (P2)

Table: ID | Requirement.

## Launch Plan

Phased rollout (Internal Dogfood → Beta → General Availability): audience, gate criteria, and what ships at each phase. Include a rollback plan if the feature is flag-gated.

## Open Questions

Table: # | Question | Owner | Status.

</prd-template>
