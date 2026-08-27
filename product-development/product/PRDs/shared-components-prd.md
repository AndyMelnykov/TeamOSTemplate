# Component Library - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-17 |
| **Related Plan** | `engineering/plans/prototyping/component-library.md` |

---

## Overview

A reusable component library lets users compose generated apps from a shared set of pre-built UI components instead of regenerating equivalent UI from scratch on every project, reducing generation volume and improving visual consistency across a user's projects.

## Problem Statement

Users currently regenerate near-identical UI (nav bars, auth forms, data tables) from scratch on every new project, which increases both generation cost and Time-to-Deploy (TTD) — see `reference/metrics.md` for the TTD target.

## User Stories

- As a user starting a new project, I want to pull in a pre-built component instead of prompting for one from scratch, so that I reach a working preview faster.

## Requirements

- A browsable library of common components (nav bar, auth form, data table, pricing card).
- Inserting a component from the library does not require a new generation call.
- Components respect the project's existing framework and styling.

## Design

See `engineering/plans/prototyping/component-library.md` for implementation scope.

## Technical Considerations

Depends on the same project/generation data model used elsewhere in `prototyping/` — no new schema required for v1.

## Launch Plan

Ship as an opt-in panel in the existing project editor; no gating by tier.
