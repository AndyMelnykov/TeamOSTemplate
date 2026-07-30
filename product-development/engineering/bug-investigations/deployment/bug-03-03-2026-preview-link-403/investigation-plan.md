# Password-protected preview links returning 403 instead of password gate

| Field | Value |
|-------|-------|
| Run Date | 2026-03-03 |
| Author | Casey Nguyen, Analytics |
| Status | Complete |
| Playbook | [Preview Environment Debugging](https://playbooks.internal/preview-envs) |
| Google Doc | [Investigation: Preview 403 Errors](https://docs.google.com/document/d/1bcd-preview-403) |
| Related Tickets | EXAMPLE_PRODUCT-990, EXAMPLE_PRODUCT-994 |

## Objective
Investigate why password-protected preview links return a 403 Forbidden error instead of showing the password entry page, making it impossible for stakeholders to access shared previews.

## Background
Preview environments with optional password protection launched in v2.3.1. Users who enable password protection on a preview link report that visitors see a 403 error page instead of a password prompt. Previews without password protection work correctly.

## Impact Scope
- **Affected users:** ~90 users who enabled password protection on preview links
- **Stakeholder impact:** Unknown number of external stakeholders unable to view shared previews
- **Severity:** P2 — password-protected previews completely unusable
- **Duration:** Since 2026-02-22 (password protection feature launch)

## Infrastructure
- **Service:** `preview-gateway` (Vercel Edge Middleware)
- **Auth layer:** Edge middleware at `middleware.ts` in the preview app
- **Database:** Supabase PostgreSQL — `preview_deploys` table with `password_hash` column
- **Hosting:** Vercel preview deployments on `preview-*.lovable.app` subdomains

## Results
- The Vercel Edge Middleware checks for password protection before serving the preview
- When a preview has a password set, the middleware should serve the password gate page
- Instead, the middleware returns 403 because it checks `request.headers.get('x-preview-auth')` which is never set for first-time visitors
- The password gate page (which would set this header) never gets served because the 403 fires first

## Analysis
1. Traced the request flow in Vercel Edge Middleware logs
2. The middleware logic is: check `x-preview-auth` header → if missing and preview has password → return 403
3. The intended flow was: if no auth header and preview has password → serve password gate page → user submits password → set cookie → redirect with auth
4. The password gate page was implemented as a separate route (`/preview-auth`) but the middleware blocks ALL routes before the gate can load
5. The middleware was written with the assumption that the auth header would be pre-set by a client-side redirect, but no such redirect exists

## Root Cause
Circular dependency in the auth flow. The Edge Middleware requires an `x-preview-auth` header to serve any page (including the password gate page). But the password gate page is what sets this header. Since the middleware runs before any page loads, the gate page can never be reached — it's blocked by the same auth check it's supposed to satisfy.

## Recommended Fix
1. Exclude the `/preview-auth` route from the middleware auth check
2. Update middleware logic: if no auth and password required → redirect to `/preview-auth` (not 403)
3. Password gate page validates password against hash, sets `x-preview-auth` cookie, redirects back
4. Add integration test: unauthenticated request to password-protected preview → shows gate → submit password → preview loads

## Cross-Validation
- Reproduced in staging: create password-protected preview → visit link → 403 (confirmed)
- Applied middleware exclusion fix → password gate renders → submit password → preview loads
- Verified non-password previews still work without any auth flow

## Data Examples

| Preview ID | Password Protected | HTTP Response | Expected |
|-----------|-------------------|---------------|----------|
| prev_a1b2 | Yes | 403 Forbidden | Password gate page |
| prev_c3d4 | Yes | 403 Forbidden | Password gate page |
| prev_e5f6 | No | 200 OK | 200 OK (correct) |
| prev_g7h8 | Yes (after fix) | 302 → /preview-auth | Password gate page (correct) |

## Executive Summary
Password-protected preview links always return 403 because the Edge Middleware blocks the password gate page with the same auth check the gate is supposed to satisfy — a circular dependency. Fix by excluding the `/preview-auth` route from the middleware check and redirecting unauthenticated visitors to the gate instead of returning 403. Simple middleware config change, no architectural changes needed.

## Appendix

### Query 1: Password-protected previews and their access attempts
```sql
SELECT pd.id, pd.project_id, pd.password_hash IS NOT NULL as has_password,
       COUNT(al.id) as access_attempts,
       COUNT(al.id) FILTER (WHERE al.status_code = 403) as blocked_attempts
FROM preview_deploys pd
LEFT JOIN access_logs al ON al.preview_id = pd.id
WHERE pd.created_at > '2026-02-22'
GROUP BY pd.id, pd.project_id, has_password
ORDER BY blocked_attempts DESC;
```

### Query 2: Preview feature adoption
```sql
SELECT
  COUNT(*) as total_previews,
  COUNT(*) FILTER (WHERE password_hash IS NOT NULL) as password_protected,
  COUNT(*) FILTER (WHERE password_hash IS NULL) as open_access,
  ROUND(100.0 * COUNT(*) FILTER (WHERE password_hash IS NOT NULL) / COUNT(*), 1) as pct_protected
FROM preview_deploys
WHERE created_at > '2026-02-22'
  AND expires_at > NOW();
```
