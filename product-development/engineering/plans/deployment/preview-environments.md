# Preview environments

## Overview
Generate shareable preview links for each version of a workflow so users can share a work-in-progress signing/submission portal with stakeholders without publishing it live.

## Steps
1. Add preview publish pipeline
   - On "Share preview" action, publish current workflow state to an isolated preview environment
   - Generate unique URL: `preview-{hash}.example_productapp.dev`
   - Store in `preview_publishes` table with workflow_id, version, created_at, expires_at
2. Add `POST /api/workflows/:id/previews` endpoint in `src/routes/previews.ts`
   - Create preview publish and return shareable URL
   - `GET /api/workflows/:id/previews` — list active previews
   - `DELETE /api/workflows/:id/previews/:previewId` — tear down preview
3. Create `SharePreview` component in `src/components/builder/`
   - Button in workflow builder toolbar → generates preview link
   - Copy-to-clipboard with success toast
   - Show list of active previews with expiry countdown
4. Add preview expiry and cleanup
   - Previews expire after 7 days by default
   - User can extend or set to "never expire" (paid plans only)
   - Cron job tears down expired preview environments
5. Add optional password protection
   - Toggle to require a password to view the preview
   - Simple password gate page before rendering the preview
6. Add tests
   - Preview publish creates accessible URL
   - Expired previews return 410 Gone
   - Password-protected previews require correct password
