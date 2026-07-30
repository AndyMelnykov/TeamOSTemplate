# RFC: Custom Domains

**Author:** Morgan Wu, Engineer
**Status:** Draft
**Last Updated:** 2026-03-22
**Related PRD:** [`product/PRDs/deployment/custom-domains-prd.md`](../../../product/PRDs/deployment/custom-domains-prd.md)
**Related Plan:** [`engineering/plans/deployment/custom-domains.md`](../../plans/deployment/custom-domains.md)

---

## Table of Contents

1. [Summary](#summary)
2. [Motivation](#motivation)
3. [Proposed Design](#proposed-design)
4. [Database Schema](#database-schema)
5. [API Design](#api-design)
6. [Frontend](#frontend)
7. [Key Queries](#key-queries)
8. [Security Considerations](#security-considerations)
9. [Rollout Plan](#rollout-plan)

---

# Summary

Allow example_product users to connect custom domains to their deployed projects with automatic SSL certificate provisioning via Let's Encrypt. Instead of sharing a `project-name.example_productapp.dev` URL, users will be able to serve their project from any domain they own (e.g., `app.acmecorp.com`). The system handles DNS verification, certificate issuance, renewal, and edge routing transparently.

# Motivation

Today every deployed example_product project is served from a `*.example_productapp.dev` subdomain. This works for prototyping, but falls short the moment a user wants to share something that looks professional:

- **Brand credibility.** Clients, investors, and end-users expect to see the company's own domain, not a platform subdomain. A `example_productapp.dev` URL signals "demo," not "product."
- **Paid conversion lever.** Custom domains are a natural upgrade trigger. Users on Free can prototype; users who need a polished public presence convert to Pro. In competitive analysis, every peer platform (Vercel, Netlify, Render) offers custom domains on paid tiers.
- **Table stakes for business users.** Enterprise and Teams accounts frequently cite custom domains as a blocker in procurement conversations. Without this, example_product is limited to internal prototyping rather than customer-facing deployments.
- **Top-requested feature.** Custom domains is the number one requested deployment feature based on customer feedback and feature request volume (EXAMPLE_PRODUCT-980, EXAMPLE_PRODUCT-1012, EXAMPLE_PRODUCT-1044).

# Proposed Design

The implementation is split into three phases:

## Phase 1: Domain Registration and DNS Verification

1. User adds a custom domain via the `DomainSettings` panel.
2. Backend generates a unique CNAME target (e.g., `cname.example_productapp.dev`) and a verification token.
3. User configures a CNAME record at their DNS registrar pointing their domain to the CNAME target.
4. A background worker polls DNS every 30 seconds for the CNAME record, for up to 48 hours.
5. Once the CNAME resolves correctly, `dns_status` transitions from `pending` to `verified`.
6. If 48 hours elapse without verification, `dns_status` transitions to `failed` and the user is notified.

## Phase 2: Automatic SSL Provisioning

1. After DNS verification, the system initiates a Let's Encrypt ACME challenge (HTTP-01) for the domain.
2. On success, the certificate and private key are stored encrypted in `domain_certificates`.
3. `ssl_status` transitions from `pending` to `provisioned`, and the domain is marked `live`.
4. A cron job runs daily to check certificates expiring within 30 days and triggers renewal.
5. Renewal follows the same ACME flow; on success, the certificate row is updated. On failure, `ssl_status` moves to `failed` and an alert fires.

## Phase 3: Edge Routing and Serving

1. The edge proxy (Caddy/nginx) is configured to route incoming requests on custom domains to the correct project's deployment.
2. A lookup table in Redis maps custom domains to project IDs and certificate paths for sub-millisecond routing.
3. On domain removal, the certificate is revoked, the Redis mapping is cleared, and the DNS verification record is deleted.

# Database Schema

## `custom_domains`

```sql
CREATE TABLE custom_domains (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id),
    domain          VARCHAR(253) NOT NULL UNIQUE,
    dns_status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (dns_status IN ('pending', 'verified', 'failed')),
    ssl_status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (ssl_status IN ('pending', 'provisioned', 'expired', 'failed')),
    cname_target    VARCHAR(253) NOT NULL,
    verification_token VARCHAR(64) NOT NULL,
    certificate_id  UUID REFERENCES domain_certificates(id),
    expires_at      TIMESTAMP WITH TIME ZONE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX idx_custom_domains_project ON custom_domains(project_id);
CREATE INDEX idx_custom_domains_domain ON custom_domains(domain);
CREATE INDEX idx_custom_domains_dns_status ON custom_domains(dns_status);
```

## `domain_certificates`

```sql
CREATE TABLE domain_certificates (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id               UUID NOT NULL REFERENCES custom_domains(id) ON DELETE CASCADE,
    provider                VARCHAR(50) NOT NULL DEFAULT 'letsencrypt',
    issued_at               TIMESTAMP WITH TIME ZONE,
    expires_at              TIMESTAMP WITH TIME ZONE,
    auto_renew              BOOLEAN NOT NULL DEFAULT true,
    last_renewal_attempt    TIMESTAMP WITH TIME ZONE,
    status                  VARCHAR(20) NOT NULL DEFAULT 'pending'
                                CHECK (status IN ('pending', 'active', 'expired', 'revoked', 'failed')),
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX idx_domain_certificates_domain ON domain_certificates(domain_id);
CREATE INDEX idx_domain_certificates_expires ON domain_certificates(expires_at);
CREATE INDEX idx_domain_certificates_status ON domain_certificates(status);
```

# API Design

All endpoints require authentication. Domain operations are scoped to the authenticated user's projects.

## `POST /api/projects/:id/domains`

Register a custom domain for a project.

**Request body:**

```json
{
  "domain": "app.acmecorp.com"
}
```

**Success response (201):**

```json
{
  "id": "d1a2b3c4-...",
  "domain": "app.acmecorp.com",
  "dns_status": "pending",
  "ssl_status": "pending",
  "cname_target": "d1a2b3c4.cname.example_productapp.dev",
  "verification_token": "example_product-verify-a1b2c3d4e5f6",
  "created_at": "2026-03-22T10:00:00Z"
}
```

**Error responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_DOMAIN` | Domain format is invalid or is a reserved TLD |
| 409 | `DOMAIN_ALREADY_REGISTERED` | Domain is already connected to another example_product project |
| 403 | `PLAN_LIMIT_REACHED` | Free-tier users cannot add custom domains; Pro allows 3, Teams 10, Enterprise unlimited |
| 404 | `PROJECT_NOT_FOUND` | Project does not exist or user lacks access |

## `GET /api/projects/:id/domains`

List all custom domains for a project.

**Success response (200):**

```json
{
  "domains": [
    {
      "id": "d1a2b3c4-...",
      "domain": "app.acmecorp.com",
      "dns_status": "verified",
      "ssl_status": "provisioned",
      "cname_target": "d1a2b3c4.cname.example_productapp.dev",
      "expires_at": "2026-06-20T10:00:00Z",
      "created_at": "2026-03-22T10:00:00Z"
    }
  ]
}
```

**Error responses:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `PROJECT_NOT_FOUND` | Project does not exist or user lacks access |

## `DELETE /api/projects/:id/domains/:domainId`

Remove a custom domain. Revokes the SSL certificate, clears the edge routing entry, and deletes the DNS verification record.

**Success response (204):** No content.

**Error responses:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `DOMAIN_NOT_FOUND` | Domain does not exist on this project |
| 403 | `FORBIDDEN` | User does not own this project |

## `POST /api/projects/:id/domains/:domainId/verify`

Manually trigger a DNS verification check. Useful if the user has just configured their DNS and does not want to wait for the next polling interval.

**Success response (200):**

```json
{
  "id": "d1a2b3c4-...",
  "domain": "app.acmecorp.com",
  "dns_status": "verified",
  "ssl_status": "pending",
  "message": "DNS verified. SSL certificate provisioning has started."
}
```

**Failure response (200, DNS not yet propagated):**

```json
{
  "id": "d1a2b3c4-...",
  "domain": "app.acmecorp.com",
  "dns_status": "pending",
  "ssl_status": "pending",
  "message": "DNS record not found. Changes can take up to 48 hours to propagate."
}
```

**Error responses:**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `DOMAIN_NOT_FOUND` | Domain does not exist on this project |
| 409 | `ALREADY_VERIFIED` | Domain DNS has already been verified |

### DNS Propagation Polling

The backend runs a recurring worker (`DnsVerificationWorker`) that:

1. Queries all domains with `dns_status = 'pending'` and `created_at` within the last 48 hours.
2. For each domain, performs a CNAME lookup via `dns.resolveCname()`.
3. If the CNAME points to the expected `cname_target`, sets `dns_status = 'verified'` and enqueues an SSL provisioning job.
4. If the 48-hour window has elapsed, sets `dns_status = 'failed'` and sends a notification email.
5. Runs every 30 seconds via a BullMQ repeatable job.

### SSL Provisioning State Machine

```
pending --> provisioning --> provisioned --> expired
    |            |                             |
    v            v                             v
  failed      failed                       renewed (-> provisioned)
```

- `pending`: Domain verified, certificate not yet requested.
- `provisioning`: ACME challenge in progress (typically 10-60 seconds).
- `provisioned`: Certificate issued and active. Edge proxy updated.
- `expired`: Certificate passed its `expires_at` without renewal.
- `failed`: ACME challenge failed (logged with error reason). Retries up to 3 times with exponential backoff.

# Frontend

## DomainSettings Panel

Located at `src/components/deploy/DomainSettings.tsx`. Rendered within the project deployment settings page.

**Layout:**

- Header: "Custom Domains" with a brief description.
- Input field for entering a new domain, with an "Add Domain" button.
- List of connected domains, each showing:
  - Domain name (linked, clickable when live).
  - Status badge: `Pending DNS` (yellow), `Verified` (blue), `SSL Provisioning` (blue, animated), `Live` (green), `Failed` (red).
  - "Verify Now" button (visible only when `dns_status = 'pending'`).
  - "Remove" button with trash icon.
- Empty state: illustration with text "Connect your own domain for a professional URL."

## DNS Instructions Component

Located at `src/components/deploy/DnsInstructions.tsx`. Displayed after the user adds a domain.

**Tabbed interface with registrar-specific instructions:**

### GoDaddy Tab

1. Log in to your GoDaddy account and go to **My Products**.
2. Find your domain and click **DNS**.
3. Click **Add** under the Records section.
4. Set Type to **CNAME**, Name to your subdomain (e.g., `app`), and Value to `{cname_target}`.
5. Set TTL to **1 Hour** and click **Save**.

### Namecheap Tab

1. Log in to Namecheap and go to **Domain List**.
2. Click **Manage** next to your domain, then **Advanced DNS**.
3. Click **Add New Record**.
4. Select **CNAME Record**, enter the Host (e.g., `app`) and Target (`{cname_target}`).
5. Click the green checkmark to save.

### Cloudflare Tab

1. Log in to Cloudflare and select your domain.
2. Go to **DNS** > **Records** and click **Add record**.
3. Set Type to **CNAME**, Name to your subdomain (e.g., `app`), and Target to `{cname_target}`.
4. Toggle the **Proxy status** to **DNS only** (gray cloud) for initial verification.
5. Click **Save**.

Each tab includes a copy-to-clipboard button for the CNAME target value.

## Status Indicators

Visual progression shown as a stepper component:

```
[1. DNS Pending] --> [2. DNS Verified] --> [3. SSL Provisioning] --> [4. Live]
```

- Each step shows a checkmark when complete, a spinner when in progress, and an X on failure.
- Clicking a failed step shows the error details and a retry option.

## Remove Confirmation

A modal dialog triggered by the "Remove" button:

- Title: "Remove {domain}?"
- Body: "This will disconnect the domain from your project. Your DNS records will no longer point to example_product and any SSL certificates will be revoked. This action cannot be undone."
- Actions: "Cancel" (secondary) and "Remove Domain" (destructive red).

# Key Queries

**All domains pending DNS verification (worker query):**

```sql
SELECT id, domain, cname_target, created_at
FROM custom_domains
WHERE dns_status = 'pending'
  AND created_at > now() - INTERVAL '48 hours';
```

**Certificates expiring within 30 days (renewal cron):**

```sql
SELECT dc.id, cd.domain, dc.expires_at, dc.last_renewal_attempt
FROM domain_certificates dc
JOIN custom_domains cd ON cd.id = dc.domain_id
WHERE dc.status = 'active'
  AND dc.auto_renew = true
  AND dc.expires_at < now() + INTERVAL '30 days';
```

**Domain status summary for a project:**

```sql
SELECT
    cd.domain,
    cd.dns_status,
    cd.ssl_status,
    dc.expires_at AS cert_expires_at,
    dc.status AS cert_status
FROM custom_domains cd
LEFT JOIN domain_certificates dc ON dc.id = cd.certificate_id
WHERE cd.project_id = :project_id
ORDER BY cd.created_at DESC;
```

# Security Considerations

## Domain Ownership Validation

- The CNAME verification flow ensures only the domain owner can connect it. Without control of the DNS zone, a user cannot create the required CNAME record.
- The `verification_token` is a cryptographically random 64-character hex string, preventing guessing or brute-force attacks.
- If a domain is removed and re-added, a new token and CNAME target are generated.

## Certificate Storage

- Private keys for SSL certificates are encrypted at rest using AES-256-GCM before storage.
- The encryption key is stored in AWS Secrets Manager, not in the application database.
- Certificate rows in `domain_certificates` store only metadata; the actual PEM files are stored in an S3 bucket with server-side encryption (SSE-KMS).
- Access to the S3 certificate bucket is restricted to the edge proxy service account via IAM policy.

## Domain Hijacking Prevention

- A domain can only be connected to one project at a time (enforced by the `UNIQUE` constraint on `custom_domains.domain`).
- When a domain is removed, its certificate is revoked immediately via the ACME revocation endpoint.
- Stale domains (DNS changed away from example_product) are detected by a weekly health check that verifies CNAME records are still valid. If a domain fails three consecutive health checks, it is automatically disconnected and the user is notified.

## Rate Limiting

- Domain addition is rate-limited to 10 domains per project per hour to prevent abuse.
- DNS verification polling is rate-limited per domain, not per user, to avoid excessive DNS queries.

# Rollout Plan

## Phase 1: Internal Beta (Week 1-2)

- Deploy behind `custom-domains` feature flag.
- Enable for example_product team internal projects.
- Validate DNS verification flow, SSL provisioning, and edge routing end-to-end.

## Phase 2: Limited Beta (Week 3-4)

- Enable for 50 selected Pro/Teams customers who requested the feature.
- Monitor domain setup completion rates and SSL provision success rates.
- Collect feedback on DNS instructions clarity and registrar coverage.

## Phase 3: General Availability (Week 5-6)

- Remove feature flag and enable for all Pro, Teams, and Enterprise tiers.
- Publish help center documentation with video walkthroughs.
- Add in-app upsell for Free users who attempt to add a domain.
- Announce via changelog and email campaign.

## Monitoring

- **Datadog alerts:** SSL provisioning failure rate > 5%, DNS verification timeout rate > 20%, certificate expiry within 7 days without successful renewal.
- **Dashboard:** Custom Domains health dashboard tracking setup funnel, active domains, certificate status distribution.
