# Clause & Field Block Library - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-17 |
| **Related Plan** | `engineering/plans/prototyping/component-library.md` |

---

## Overview

A shared clause and field block library lets users compose workflows from a shared set of pre-built clauses and field groups instead of re-extracting or re-defining equivalent structure from scratch on every workflow, reducing automation-run volume and improving consistency across a user's workflows.

## Problem Statement

Users currently rebuild near-identical structure (standard payment-terms clauses, limitation-of-liability clauses, signature blocks, address field groups) from scratch on every new workflow, which increases both extraction cost and Time-to-Publish (TTP) — see `reference/metrics.md` for the TTP target.

## User Stories

- As a user starting a new workflow, I want to pull in a pre-built clause or field block instead of defining one from scratch, so that I reach a working preview faster.

## Requirements

- A browsable library of common clauses and field blocks (payment-terms clause, limitation-of-liability clause, signature block, address field group, W-9 field group).
- Inserting a block from the library does not require a new automation run.
- Blocks respect the workflow's existing template and branding.

## Design

See `engineering/plans/prototyping/component-library.md` for implementation scope.

## Technical Considerations

Depends on the same workflow/extraction data model used elsewhere in `prototyping/` — no new schema required for v1.

## Launch Plan

Ship as an opt-in panel in the existing workflow builder; no gating by tier.
