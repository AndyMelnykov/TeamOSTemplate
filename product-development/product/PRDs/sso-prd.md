# SSO Integration - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-20 |
| **Related RFC** | `engineering/rfcs/sso-rfc.md` |

---

## Overview

SSO Integration lets example_product Enterprise customers authenticate through their own identity provider (Okta, Azure AD, Google Workspace) instead of example_product-managed credentials, satisfying a hard procurement requirement for regulated-industry buyers.

## Problem Statement

Enterprise prospects in regulated industries require SSO before they will sign. Meridian Health and Crestview Financial (both Enterprise-segment, both under active evaluation) have each flagged SSO as a blocker in their security review. Without it, example_product cannot close deals that require centralized identity management and deprovisioning.

## User Stories

- As an Enterprise admin, I want to provision and deprovision example_product access through our existing identity provider, so that offboarding is instant and auditable.
- As an Enterprise security reviewer, I want SAML-based SSO, so that example_product meets our procurement security checklist.

## Requirements

- Support SAML 2.0 with Okta, Azure AD, and Google Workspace as initial providers.
- Just-in-time user provisioning on first SSO login.
- Deprovisioning via IdP-initiated logout revokes the example_product session within 5 minutes.
- SSO is an example_product Enterprise-tier-only capability.

## Design

Admin-facing SSO configuration lives under Enterprise account settings. See Figma link in `feature-index.yaml` (`billing.sso-integration.figma`).

## Technical Considerations

See `engineering/rfcs/sso-rfc.md` for the SAML implementation design.

## Launch Plan

Enterprise-tier gated rollout, starting with Meridian Health and Crestview Financial as design partners.
