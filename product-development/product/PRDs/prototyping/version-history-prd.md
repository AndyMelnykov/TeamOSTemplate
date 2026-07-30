# Version History PRD

**Author:** Hannah Stulberg, PM
**Status:** Draft
**Last Updated:** 2026-03-22
**Related RFC:** [`engineering/rfcs/prototyping/version-history-rfc.md`](../../../engineering/rfcs/prototyping/version-history-rfc.md)
**Related Plan:** [`engineering/plans/prototyping/version-history.md`](../../../engineering/plans/prototyping/version-history.md)

---

## Problem Statement

example_product users have no reliable way to recover previous project states when AI generations go wrong. The current single-step undo only reverts the most recent change, which is insufficient when users want to roll back multiple iterations or compare how their project evolved over time.

This creates three compounding problems:

1. **Users lose work permanently.** When a user iterates three or four times and realizes version two was the best one, there is no way to get back to it. The work is gone.
2. **Users avoid experimentation.** Because there is no safety net, users stick to conservative, incremental prompts instead of trying bold ideas. This limits the creative potential of the platform and reduces the value users get from AI-assisted generation.
3. **Users abandon projects after bad generations.** Internal data shows that 18% of users who experience a generation that makes their project worse abandon the project entirely instead of trying to recover. This is a direct hit to Project Completion Rate (PCR) and downstream conversion.

## Business Opportunity

Version history directly addresses the abandonment-after-bad-generation problem, which is one of our largest measurable leaks in the project completion funnel.

**Current state:**
- 18% of users abandon projects after a bad generation (no recovery path)
- PCR sits at 58%, below our 60% target
- Churn surveys consistently rank "lost work / can't undo" in the top 3 frustrations

**Expected impact:**
- Reducing post-bad-generation abandonment by even 30% would lift PCR by approximately 3 percentage points
- Users who complete projects are 4.2x more likely to upgrade to example_product Pro
- Estimated revenue impact: $180K-$240K incremental ARR in the first 6 months based on improved PCR-to-conversion flow

## Why Now

Three factors make this the right time to build version history:

1. **Competitive pressure.** Lovable shipped version history and rollback in Q1 2026. It is already appearing in their marketing materials and competitor comparison pages. We are losing evaluation deals where version history is a checkbox item on the buyer's feature matrix. Two enterprise prospects (Meridian Corp and DataStack) specifically cited this gap in their evaluation feedback in February 2026.

2. **Foundation is ready.** The generation pipeline work from Q4 2025 already captures the data we need (generation IDs, file tree state, prompt history). Building version snapshots on top of this is incremental, not greenfield.

3. **User demand is at a peak.** Version history / undo / rollback has been the number one feature request for three consecutive months in our in-app feedback widget. It is time to stop noting the request and start shipping the solution.

## Customer Requests

| Source | Date | Verbatim |
|--------|------|----------|
| In-app feedback | 2026-03-15 | "I accidentally made my app worse with a prompt and now I can't go back. This is incredibly frustrating." |
| In-app feedback | 2026-03-08 | "Please add version history. I need to be able to see what changed and roll back." |
| Customer call - Meridian Corp | 2026-02-22 | "Version control is table stakes for us. We can't adopt a tool where one bad generation wipes out an hour of work." |
| Customer call - DataStack | 2026-02-18 | "Lovable has rollback. If example_product doesn't, that's a dealbreaker for our team." |
| Support ticket #4821 | 2026-03-01 | "Is there any way to undo multiple generations? I need to go back 3 steps." |
| Support ticket #4903 | 2026-03-10 | "I lost my entire project layout after a generation. Ctrl+Z only undoes the last change. I need full version history." |
| NPS survey (detractor) | 2026-02-28 | "Love the AI but terrified to use it aggressively because there's no safety net." |
| Slack community #example_product-feedback | 2026-03-12 | "Any ETA on version history? This is the one thing keeping me on Lovable for serious projects." |

## Goals

| Goal | Metric | Target |
|------|--------|--------|
| Reduce post-bad-generation abandonment | % of users who abandon after a bad generation | < 12% (from 18%) |
| Improve project completion rate | PCR | > 62% |
| Drive version history adoption | % of active projects with at least one version restore | > 15% within 60 days |
| Increase experimentation confidence | Average iterations per project | +20% lift |
| Zero data loss on restore | Restore operations that complete without error | > 99.5% |

## User Stories

### Core user stories

1. **As a user**, I want every AI generation to automatically save a version of my project so that I always have a recovery point without needing to remember to save manually.

2. **As a user**, I want to browse a chronological list of all my project versions so that I can see how my project evolved and find the version I want to return to.

3. **As a user**, I want to compare any two versions side-by-side so that I can understand exactly what changed between them before deciding whether to restore.

4. **As a user**, I want to restore a previous version with one click so that I can quickly recover from a bad generation without losing my current state.

5. **As a user**, I want restoring a version to be non-destructive so that I can always get back to any point in my project's history, including the state I restored from.

### Secondary user stories

6. **As a user**, I want to search my version history by prompt text so that I can quickly find the version where I made a specific change.

7. **As a user**, I want to filter my version history by date range so that I can narrow down versions to a specific work session.

8. **As a user**, I want to see a summary of what changed in each version (files added, modified, removed) so that I can scan the list without opening every version.

9. **As a team member on a shared project**, I want to see who created each version so that I can understand my teammates' changes.

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | System automatically creates a version snapshot after every successful AI generation | P0 |
| FR-2 | Users can manually save a named version at any time | P1 |
| FR-3 | Version history panel displays all versions for a project in reverse chronological order | P0 |
| FR-4 | Each version entry shows: version number, prompt snippet, timestamp, and file change summary | P0 |
| FR-5 | Users can compare any two versions in a side-by-side diff view | P0 |
| FR-6 | Diff view shows line-level additions, deletions, and modifications with syntax highlighting | P0 |
| FR-7 | Users can restore any previous version with a single confirmation step | P0 |
| FR-8 | Restore is non-destructive: current state is saved as a new version before the restore is applied | P0 |
| FR-9 | Users can filter versions by date range | P1 |
| FR-10 | Users can search versions by prompt text | P1 |
| FR-11 | Version list supports pagination for projects with many versions | P1 |
| FR-12 | Restore confirmation dialog clearly explains that current state will be preserved | P0 |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Version list loads in under 500ms for projects with up to 200 versions | P0 |
| NFR-2 | Diff computation completes in under 2 seconds for typical projects (< 50 files) | P0 |
| NFR-3 | Snapshot storage does not degrade editor performance | P0 |
| NFR-4 | Snapshots are retained for the lifetime of the project | P0 |
| NFR-5 | Restore success rate exceeds 99.5% | P0 |
| NFR-6 | Version history is accessible on tablet-sized viewports (1024px+) | P1 |

## Launch Plan

### Phase 1: Internal dogfood (Week 1)
- Deploy behind `version_history_internal` feature flag
- example_product Labs team uses the feature on internal projects
- Collect UX feedback, identify edge cases, validate snapshot reliability
- Success gate: zero data loss incidents, team feedback is positive

### Phase 2: Beta (Weeks 2-3)
- Expand to example_product Pro and Teams customers behind `version_history_beta` flag
- Opt-in via settings panel
- Monitor restore success rate, storage growth, and performance metrics
- Run onboarding tooltip experiment (see experiment doc)
- Success gate: restore success rate > 99.5%, no P0 bugs, adoption > 10% of eligible projects

### Phase 3: General availability (Week 4)
- Enable for all users by default via `version_history_ga` flag
- Publish help center article and changelog post
- Launch email to all users highlighting the feature
- Begin tracking long-term metrics (restore-to-continue rate, PCR impact)

### Rollback plan
- Feature flags allow instant disable without a deploy
- Existing snapshots are preserved even if the feature is turned off
- Users who created versions during beta will retain access to their history when GA launches

## Open Questions

| Question | Owner | Status |
|----------|-------|--------|
| Should we cap the number of versions per project for free-tier users? | Hannah Stulberg | Open |
| Do we need version branching (fork from an old version) in v1, or is linear history sufficient? | Morgan Wu | Decided: linear history for v1 |
| What is the expected storage cost per project at 100+ versions? | Sam Chen | Investigating |
