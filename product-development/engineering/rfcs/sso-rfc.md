# SSO Integration - Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Riley Patel (Engineer) |
| **Status** | Draft |
| **Last Updated** | 2026-03-20 |
| **Related PRD** | `product/PRDs/sso-prd.md` |

---

## Summary

Adds SAML 2.0-based SSO for example_product Enterprise accounts, with just-in-time provisioning and IdP-initiated deprovisioning.

## Motivation

Enterprise procurement reviews at Meridian Health and Crestview Financial both list SSO as a blocking requirement. See `product/PRDs/sso-prd.md` for the full business case.

## Proposed Design

- Integrate a SAML 2.0 library on the auth service; support Okta, Azure AD, and Google Workspace as IdPs.
- On first SSO login, just-in-time provision a example_product user scoped to the Enterprise account's workspace.
- Subscribe to IdP-initiated logout webhooks where supported (Okta, Azure AD); poll session validity every 5 minutes as a fallback for providers without webhook support.

## Alternatives Considered

- OIDC instead of SAML: rejected for v1 because both target accounts' security teams specifically require SAML in their procurement checklist.

## Rollout Plan

Enterprise-tier feature flag, enabled per-account starting with Meridian Health and Crestview Financial.
