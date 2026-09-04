# Team seat management

## Overview
Let Teams plan admins add and remove team seats, assign roles, and see per-seat usage from a single settings page.

## Steps
1. Add team member CRUD endpoints in `src/routes/team.ts`
   - `GET /api/team/members` — list members with role and usage stats
   - `POST /api/team/members` — invite by email, assign role (admin/member)
   - `DELETE /api/team/members/:id` — remove seat, transfer owned workflows
2. Create `TeamManagement` component in `src/components/settings/`
   - Member table: name, email, role, credits used, last active
   - Invite form with email input and role picker
   - Confirm dialog for seat removal with workflow transfer options
3. Add seat-based billing logic
   - Update Stripe subscription quantity on member add/remove
   - Prorate charges mid-cycle
   - Enforce seat limit based on plan tier
4. Add pending invite state
   - Track invites in `team_invites` table with expiry
   - Show pending invites in member list with resend/cancel actions
5. Add tests
   - Invite creates pending record and sends email
   - Seat removal triggers Stripe quantity update
   - Non-admins cannot access team management
