# Team Workspaces - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-19 |
| **Related RFC** | `engineering/rfcs/workspaces-rfc.md` |

---

## Overview

Team Workspaces gives Growth and Enterprise accounts a shared workflow namespace with role-based permissions, moving example_product from an individual document-automation tool toward a team-wide ops platform — directly under the "Collaboration" pillar (see `product-development/product/CLAUDE.md`, Five Core Pillars).

## Problem Statement

Acme Corp's account team (see `product-development/product/customers/accounts/acme-corp/calls/summaries/`) has already asked for manager-level review workflows over their shared vendor-contract and employee-onboarding workflows, and assigned internal owners to plan a rollout before the feature ships — a strong signal of validated demand ahead of any commitment from example_product.

## User Stories

- As a team lead, I want a shared workspace where my team's workflows live, so that I don't need to track individual members' workflows manually.
- As an ops lead, I want to review my team's workflows on a recurring cadence, so that I can ensure quality and catch issues early.

## Requirements

- Workspace-scoped workflow namespace, shared across team members.
- Role-based permissions: member, manager, admin.
- Manager review flow: a manager can mark a workflow "reviewed" with a timestamp.

## Design

See Figma link in `feature-index.yaml` (`prototyping.team-workspaces.figma`).

## Technical Considerations

See `engineering/rfcs/workspaces-rfc.md`.

## Launch Plan

Design-partner rollout with Acme Corp given their existing internal rollout planning.
