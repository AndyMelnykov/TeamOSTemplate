# Project Search (Cmd+K) PRD

**Author:** Hannah Stulberg, PM
**Status:** Draft
**Last Updated:** 2026-03-22
**Related RFC:** `engineering/rfcs/home-page/project-search-rfc.md`
**Related Plan:** `engineering/plans/home-page/project-search.md`

---

## Overview

Project Search introduces a global search modal (Cmd+K / Ctrl+K) that lets users instantly find projects, templates, and recent actions from anywhere in example_product. As users accumulate projects and explore templates, the current browse-only navigation becomes a bottleneck. A keyboard-driven search modal is the most requested navigation improvement and a table-stakes feature for power users coming from tools like VS Code, Notion, and Linear.

## Problem Statement

example_product users have no way to search across their projects, templates, or recent activity. The home page displays projects in a grid sorted by last-modified date, but offers no search, filtering, or quick-jump capability. This creates three specific pain points:

1. **Project discovery degrades with scale.** Free-tier users average 5-8 projects and can scan visually. Pro users average 25+ projects; Teams and Enterprise accounts can have 100+. Scrolling through a grid is not viable at this scale.

2. **Template exploration is disconnected.** Templates live on a separate page with their own browse flow. Users cannot search across projects and templates simultaneously, leading to context switches during the ideation phase.

3. **No path to recent actions.** Users frequently want to return to something they just deployed or edited. Today this requires remembering the project name or relying on browser history. There is no in-app concept of "recent activity" that is searchable.

## Business Opportunity

- **Activation:** Users who find relevant templates faster complete onboarding at higher rates. Reducing friction in the "find a starting point" phase directly impacts Day 1 activation.
- **Retention:** Power users on Pro and Teams tiers are most likely to churn when navigation overhead grows. Search reduces the friction tax on high-volume users.
- **Expansion signal:** Search query data reveals what users are looking for but not finding, providing a direct signal for template gaps and feature requests.

## Why Now

- The home page redesign (Q1 2026) established the layout foundation. Search is the next logical investment in the home page surface.
- Customer escalations around project discovery have increased 3x quarter-over-quarter as average project counts grow.
- Competitors Lovable and v0 both shipped global search in the past 6 months. Users switching from those tools explicitly cite search as an expected capability.
- The prompt suggestions experiment (EXAMPLE_PRODUCT-1040) validated that surfacing relevant content on the home page increases engagement. Search extends this principle to user-initiated discovery.

## Customer Requests

| Customer | Tier | Verbatim |
|----------|------|----------|
| Acme Corp | Enterprise | "I have 80 projects and no way to find the one I worked on last Tuesday. I end up using browser history which is embarrassing." |
| Bright Studios | Teams | "We need Cmd+K. Every tool I use has it. I keep pressing it in example_product and nothing happens." |
| Solo Dev (free-tier) | Free | "I tried a bunch of templates last week and now I can't remember which one had the e-commerce layout." |
| DataFlow Inc | Pro | "Our team shares 40+ projects. Finding the right one takes longer than it should." |
| NovaTech | Enterprise | "Search is the #1 thing blocking us from recommending example_product to more teams internally." |

---

## Goals & Success Metrics

### Goals

1. Give every example_product user a fast, keyboard-driven way to find any project, template, or recent action in under 3 seconds.
2. Reduce the navigation overhead for power users with large project portfolios.
3. Capture search behavior data to inform template strategy and content gaps.

### Success Metrics

| Metric | Definition | Target | Timeframe |
|--------|-----------|--------|-----------|
| Search usage rate | % of DAU who use search at least once per day | > 20% | 30 days post-GA |
| Zero-results rate | % of searches that return no results | < 15% | 30 days post-GA |
| Click-through rate (CTR) | % of searches where the user clicks a result | > 45% | 30 days post-GA |
| Time-to-result | Median time from modal open to result click | < 4 seconds | 30 days post-GA |
| Search-to-project-open rate | % of search sessions that lead to a project being opened | > 35% | 30 days post-GA |

### Guardrail Metrics

| Metric | Definition | Threshold |
|--------|-----------|-----------|
| Home page engagement | Existing home page project card clicks should not decline | No regression > 5% |
| Page load time | Adding the search modal should not impact initial page load | p95 < 50ms increase |

---

## User Stories

### US-1: Find a project by name
**As a** example_product user with many projects,
**I want to** press Cmd+K and type a project name,
**So that** I can navigate directly to it without scrolling through the project grid.

**Acceptance criteria:**
- Cmd+K opens the search modal from any page in example_product.
- Typing a project name shows matching projects within 300ms.
- Pressing Enter on a highlighted project navigates to it.
- The modal closes after navigation.

### US-2: Search for a template
**As a** user exploring templates,
**I want to** search for templates by name or category from the search modal,
**So that** I can find relevant starting points without leaving my current context.

**Acceptance criteria:**
- Templates appear in search results alongside projects.
- Each template result shows the template name and category.
- Clicking a template result opens the template detail/preview page.

### US-3: Return to a recent action
**As a** user who recently deployed or edited a project,
**I want to** search for recent actions like "deployed" or find recent activity,
**So that** I can quickly return to what I was working on.

**Acceptance criteria:**
- Recent actions (deploys, edits, generations) appear in search results.
- Actions show the action type, associated project name, and relative timestamp.
- Clicking an action navigates to the relevant project.

### US-4: Filter search results by type
**As a** user looking for a specific type of content,
**I want to** filter search results to only show projects, templates, or actions,
**So that** I can narrow down results quickly.

**Acceptance criteria:**
- Filter chips for All, Projects, Templates, and Actions are visible in the modal.
- Selecting a filter updates results immediately.
- The active filter persists within the search session.

### US-5: Access recent searches
**As a** returning user,
**I want to** see my recent searches when I open the search modal,
**So that** I can repeat common searches without retyping.

**Acceptance criteria:**
- Opening the search modal with an empty input shows up to 5 recent searches.
- Clicking a recent search populates the input and triggers the search.
- Recent searches are stored locally and persist across sessions (but not across devices).

### US-6: Keyboard-only navigation
**As a** keyboard-centric user,
**I want to** navigate search results entirely with arrow keys and Enter,
**So that** I never need to reach for the mouse during search.

**Acceptance criteria:**
- Arrow Down/Up moves the highlight through results.
- Enter navigates to the highlighted result.
- Tab cycles through filter chips.
- Escape closes the modal.

---

## Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-1 | Global keyboard shortcut (Cmd+K / Ctrl+K) opens search modal from any page | P0 |
| FR-2 | Full-text search across project names, descriptions, template titles, and action descriptions | P0 |
| FR-3 | Results grouped by type: Projects, Templates, Actions | P0 |
| FR-4 | Keyboard navigation through results (arrow keys, Enter, Escape) | P0 |
| FR-5 | Matching text highlighted in results | P0 |
| FR-6 | Type filter chips (All, Projects, Templates, Actions) | P0 |
| FR-7 | Recent searches displayed on empty input (up to 5, stored in localStorage) | P1 |
| FR-8 | Date range filter (Last 7 days, 30 days, 90 days) | P1 |
| FR-9 | Result metadata: framework badge, deploy count, category tag, action type icon | P1 |
| FR-10 | Search event tracking for analytics (query, result count, click position) | P1 |
| FR-11 | Click-outside or Escape to dismiss modal | P0 |
| FR-12 | Loading skeleton during search request | P1 |
| FR-13 | Empty state with helpful message when no results found | P1 |

## Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR-1 | Search API response time | < 200ms p95 |
| NFR-2 | Input debounce interval | 200ms |
| NFR-3 | Modal render time (open to interactive) | < 100ms |
| NFR-4 | Search index freshness (new project appears in search) | < 30 seconds |
| NFR-5 | Tenant isolation (users can only see their own content and shared projects) | 100% enforced |
| NFR-6 | Rate limiting | 60 requests/min per user |
| NFR-7 | Accessibility: ARIA labels, focus management, screen reader support | WCAG 2.1 AA |
| NFR-8 | Mobile responsive: modal adapts to viewport < 768px | Functional (not just hidden) |

---

## Launch Plan

| Phase | Audience | Duration | Entry Criteria |
|-------|----------|----------|----------------|
| Internal dogfood | example_product Labs team | 1 week | Feature complete, passing tests |
| Beta | 10% of Pro and Teams users | 2 weeks | No P0/P1 bugs from dogfood, p95 < 200ms |
| GA | All authenticated users | Ongoing | Beta success metrics met, security review passed |

**Feature flags:**
- `search_modal_internal` -- Phase 1
- `search_modal_beta` -- Phase 2
- `search_modal_enabled` -- Phase 3 (default on)

**Launch communications:**
- In-app tooltip on first exposure: "Press Cmd+K to search your projects, templates, and more."
- Changelog entry on GA launch.
- Help center article with keyboard shortcuts and search tips.

**Rollback plan:** Disable via feature flag. No data migration required.

---

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Should search include shared projects from other org members, or only the user's own projects? | Hannah Stulberg | Open |
| 2 | Do we want to support searching within project file contents (code search) in a future phase? | Jordan Kim | Open |
| 3 | Should recent searches sync across devices via the backend, or remain localStorage-only? | Hannah Stulberg | Open |
| 4 | What is the right empty-state experience: show trending templates, or just a "no results" message? | Taylor Brooks | Open |
| 5 | Should we add analytics for search queries that produce zero results to feed into template gap analysis? | Casey Nguyen | Open -- leaning yes |
