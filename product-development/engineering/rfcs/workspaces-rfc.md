# Team Workspaces - Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Riley Patel (Engineer) |
| **Status** | Draft |
| **Last Updated** | 2026-03-19 |
| **Related PRD** | `product/PRDs/team-workspaces-prd.md` |

---

## Summary

Introduces a workspace entity that groups document automation workflows under a team, with role-based permissions (member/manager/admin) and a manager review flag on each workflow.

## Motivation

See `product/PRDs/team-workspaces-prd.md`.

## Proposed Design

- New `workspace` entity owning a set of `workflow` records (currently owned directly by `account`).
- `workspace_membership` join table carrying a `role` enum (`member`, `manager`, `admin`).
- `workflow.reviewed_at` / `workflow.reviewed_by` columns to support the manager review flow (e.g., a manager sign-off before a vendor contract workflow is published).

## Alternatives Considered

- Reusing the existing account-level permission model instead of a new workspace entity: rejected — accounts can contain multiple teams (e.g., legal and finance both automating documents under one account), and permissions need to scope below the account level.

## Rollout Plan

Ship to Acme Corp as design partner first, then general availability for Growth and Enterprise tiers.
