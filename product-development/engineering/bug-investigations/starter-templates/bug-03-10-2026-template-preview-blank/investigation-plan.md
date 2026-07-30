# Template preview iframe blank on Safari

| Field | Value |
|-------|-------|
| Run Date | 2026-03-10 |
| Author | Sam Chen, Engineer |
| Status | Complete |
| Playbook | [Cross-Browser Issue Triage](https://playbooks.internal/cross-browser) |
| Google Doc | [Investigation: Safari Preview Blank](https://docs.google.com/document/d/1stu-safari-preview) |
| Related Tickets | EXAMPLE_PRODUCT-1015, EXAMPLE_PRODUCT-1019 |

## Objective
Investigate why template previews render as blank white iframes in Safari (macOS and iOS) while working correctly in Chrome and Firefox.

## Background
After launching the template customizer (v2.4.2), support received 8 tickets from Safari users unable to preview templates. The Templates tab shows template cards correctly, but clicking into a template preview shows a blank iframe. Chrome and Firefox users are unaffected.

## Impact Scope
- **Affected users:** ~2,100 users (14% of traffic from Safari)
- **Severity:** P2 — feature completely broken for Safari users, no workaround
- **Duration:** Since 2026-03-04 (template customizer launch)

## Infrastructure
- **Frontend:** React 18, Vite build, deployed on Vercel
- **Preview iframe:** Sandboxed iframe loading template from `preview.lovable.app` subdomain
- **CDN:** Vercel Edge Network
- **Affected browsers:** Safari 17.x (macOS), Safari iOS 17.x+

## Results
- Safari blocks the iframe due to cross-origin isolation policies
- The `preview.lovable.app` subdomain sets `Cross-Origin-Opener-Policy: same-origin` header
- Safari enforces this more strictly than Chrome — it refuses to render cross-origin iframes when COOP is set to `same-origin`
- Chrome and Firefox allow the iframe but isolate it; Safari blocks it entirely

## Analysis
1. Opened Safari Web Inspector — iframe shows `Blocked a frame with origin "https://lovable.dev" from accessing a cross-origin frame`
2. Checked response headers on `preview.lovable.app` — found `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`
3. These headers were added in the Vercel config for security hardening (PR #495) but weren't tested in Safari
4. Removed COOP header in staging — iframe renders correctly in Safari
5. Confirmed Chrome/Firefox already handle this via iframe sandboxing without needing COOP

## Root Cause
PR #495 added `Cross-Origin-Opener-Policy: same-origin` to the preview subdomain's Vercel headers config for security hardening. Safari interprets COOP more strictly than other browsers and refuses to render cross-origin iframes when the embedded page sets `same-origin` COOP. Chrome and Firefox are more permissive.

## Recommended Fix
1. Change COOP header on `preview.lovable.app` from `same-origin` to `same-origin-allow-popups`
2. Keep COEP header as-is — it's not causing the issue
3. Add `sandbox="allow-scripts allow-same-origin"` attribute to the preview iframe for defense-in-depth
4. Add Safari to the cross-browser test matrix for iframe-dependent features

## Cross-Validation
- Tested fix in staging on Safari 17.4 (macOS) and Safari iOS 17.4 — iframe renders correctly
- Verified Chrome and Firefox still work with the updated header
- Confirmed no security regression: iframe still properly sandboxed

## Data Examples

| Browser | Version | Preview Loads | Error |
|---------|---------|--------------|-------|
| Chrome | 122 | Yes | None |
| Firefox | 124 | Yes | None |
| Safari macOS | 17.4 | No | Cross-origin frame blocked |
| Safari iOS | 17.4 | No | Cross-origin frame blocked |
| Safari macOS (fix) | 17.4 | Yes | None |

## Executive Summary
Template previews are blank in Safari because a security header (`Cross-Origin-Opener-Policy: same-origin`) blocks cross-origin iframe rendering. Safari enforces this more strictly than Chrome/Firefox. Change the header to `same-origin-allow-popups` on the preview subdomain. One-line config change, no code changes needed. Add Safari to the iframe test checklist going forward.

## Appendix

### Query 1: Template preview usage by browser
```sql
SELECT
  browser_family,
  COUNT(*) as preview_attempts,
  COUNT(*) FILTER (WHERE loaded = true) as successful,
  ROUND(100.0 * COUNT(*) FILTER (WHERE loaded = true) / COUNT(*), 1) as success_rate
FROM template_preview_events
WHERE created_at > '2026-03-04'
GROUP BY browser_family
ORDER BY preview_attempts DESC;
```

### Query 2: Support tickets related to blank previews
```sql
SELECT t.id, t.user_id, t.subject, t.created_at, u.browser_info
FROM support_tickets t
JOIN users u ON u.id = t.user_id
WHERE t.subject ILIKE '%preview%blank%' OR t.subject ILIKE '%template%not loading%'
  AND t.created_at > '2026-03-04'
ORDER BY t.created_at;
```
