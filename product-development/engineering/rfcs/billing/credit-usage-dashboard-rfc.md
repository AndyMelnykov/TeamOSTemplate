# Credit Usage Dashboard - Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Riley Patel (Engineer) |
| **Status** | Draft |
| **Last Updated** | 2026-03-22 |
| **Related PRD** | `product/PRDs/billing/credit-usage-dashboard-prd.md` |
| **Related Plan** | `engineering/plans/billing/credit-usage-dashboard.md` |

---

## Table of Contents

1. [Summary](#summary)
2. [Motivation](#motivation)
3. [Proposed Design](#proposed-design)
   - [Phase 1: Database Schemas](#phase-1-database-schemas)
   - [Phase 2: API Layer](#phase-2-api-layer)
   - [Phase 3: Frontend](#phase-3-frontend)
4. [Key Queries](#key-queries)
5. [Security Considerations](#security-considerations)
6. [Rollout Plan](#rollout-plan)

---

## Summary

This RFC proposes a Credit Usage Dashboard that gives example_product users full visibility into how they consume credits across generation, edit, and deploy operations. The dashboard will display a daily breakdown by category, real-time burn rate calculations, and projections for when credits will be exhausted at current consumption rates. Users will also be able to drill into per-project usage and filter by date range, category, and project.

## Motivation

Today, example_product users have no way to understand how they are spending credits until they receive a hard stop at the limit. This leads to several problems:

- **Surprise limit hits**: Users in the middle of a workflow are blocked without warning when credits run out. This is the number one billing-related complaint in support (averaging 47 tickets/week in Q1 2026).
- **No category visibility**: Users cannot tell whether their credits are going to generations, edits, or deploys. This prevents them from adjusting their workflow to stay within budget.
- **No burn rate awareness**: Users have no sense of how quickly they are consuming credits relative to their billing cycle, making it impossible to pace usage.
- **Upgrade friction**: Without usage data, users cannot make informed decisions about whether to upgrade. They either churn out of frustration or over-purchase credits they do not need.

A dashboard that surfaces this data will reduce surprise limit hits, decrease billing-related support volume, and create a natural upgrade path by showing users exactly where they stand.

## Proposed Design

### Phase 1: Database Schemas

The credit transaction ledger is the foundation of the dashboard. All credit movements are recorded as immutable rows in a single append-only table.

```sql
CREATE TABLE credit_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    amount          INTEGER NOT NULL,
    type            VARCHAR(10) NOT NULL CHECK (type IN ('debit', 'credit')),
    category        VARCHAR(20) NOT NULL CHECK (category IN ('generation', 'edit', 'deploy', 'refund', 'referral')),
    reference_id    UUID,
    project_id      UUID REFERENCES projects(id),
    balance_after   INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_user_created ON credit_transactions(user_id, created_at);
CREATE INDEX idx_credit_transactions_user_category ON credit_transactions(user_id, category);
CREATE INDEX idx_credit_transactions_project ON credit_transactions(project_id);
```

Design decisions:
- **Append-only**: Transactions are never updated or deleted. Corrections are modeled as new `credit` rows with category `refund`.
- **`balance_after`**: Denormalized running balance avoids expensive aggregation queries for the current balance. Maintained within a database transaction when inserting new rows.
- **`reference_id`**: Links back to the originating entity (e.g., the generation ID, deploy ID) for auditability.
- **`project_id`**: Nullable because some credit events (e.g., referral bonuses) are not tied to a project.

### Phase 2: API Layer

Two endpoints power the dashboard.

#### `GET /api/billing/usage`

Returns daily credit usage grouped by category for the authenticated user.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_date` | ISO 8601 date | 30 days ago | Start of date range |
| `end_date` | ISO 8601 date | today | End of date range |
| `category` | string | all | Filter to a single category |

**Success Response (200):**

```json
{
  "data": {
    "daily_usage": [
      {
        "date": "2026-03-20",
        "generation": 120,
        "edit": 45,
        "deploy": 30,
        "total": 195
      },
      {
        "date": "2026-03-21",
        "generation": 85,
        "edit": 60,
        "deploy": 15,
        "total": 160
      }
    ],
    "summary": {
      "total_used": 355,
      "current_balance": 1645,
      "cycle_start": "2026-03-01",
      "cycle_end": "2026-03-31",
      "burn_rate_per_day": 177.5,
      "projected_days_remaining": 9.3
    }
  }
}
```

**Error Responses:**

| Status | Body | Condition |
|--------|------|-----------|
| 401 | `{ "error": "unauthorized", "message": "Authentication required." }` | Missing or invalid auth token |
| 403 | `{ "error": "forbidden", "message": "You do not have permission to view this resource." }` | User attempting to access another user's data |

#### `GET /api/billing/usage/by-project`

Returns credit totals broken down by project for the authenticated user.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_date` | ISO 8601 date | 30 days ago | Start of date range |
| `end_date` | ISO 8601 date | today | End of date range |
| `sort_by` | string | `total_credits` | Sort field (`total_credits`, `project_name`, `last_activity`) |
| `sort_order` | string | `desc` | `asc` or `desc` |

**Success Response (200):**

```json
{
  "data": {
    "projects": [
      {
        "project_id": "a1b2c3d4-...",
        "project_name": "Marketing Site Redesign",
        "generation": 340,
        "edit": 120,
        "deploy": 55,
        "total_credits": 515,
        "last_activity": "2026-03-21T14:32:00Z"
      },
      {
        "project_id": "e5f6a7b8-...",
        "project_name": "Mobile App Prototype",
        "generation": 210,
        "edit": 85,
        "deploy": 30,
        "total_credits": 325,
        "last_activity": "2026-03-20T09:15:00Z"
      }
    ],
    "total_across_projects": 840
  }
}
```

**Error Responses:**

Same as `GET /api/billing/usage`.

### Phase 3: Frontend

The dashboard is implemented as a new page at `/billing/usage` composed of the following components:

#### UsageDashboard Page (`src/pages/billing/UsageDashboard.tsx`)

Top-level page component. Orchestrates data fetching, manages filter state, and renders the child components. On mount, it calls both API endpoints in parallel.

- **On API success**: Render the chart, summary cards, and project table with the returned data.
- **On API failure**: Show an error state with a descriptive message and a "Retry" button that re-fires the failed request.

#### UsageBarChart Component (`src/components/billing/UsageBarChart.tsx`)

Stacked bar chart using Recharts showing daily credit usage. Each bar is segmented by category with distinct colors:

- Generation: blue (`#3B82F6`)
- Edit: violet (`#8B5CF6`)
- Deploy: amber (`#F59E0B`)

The chart supports hover tooltips with exact values and click-to-filter by category.

#### UsageSummaryCards Component (`src/components/billing/UsageSummaryCards.tsx`)

Four summary cards displayed in a row above the chart:

| Card | Value | Subtext |
|------|-------|---------|
| Credits Used | Total debits this cycle | vs. previous cycle % change |
| Remaining | Current balance | of total allocation |
| Burn Rate | Credits per day (7-day avg) | trend arrow up/down |
| Projected Depletion | Estimated date | or "Safe through cycle end" |

#### ProjectBreakdownTable Component (`src/components/billing/ProjectBreakdownTable.tsx`)

Sortable table with columns: Project Name, Generations, Edits, Deploys, Total Credits, Last Activity. Rows are clickable and navigate to the project detail page.

#### LowBalanceBanner Component (`src/components/billing/LowBalanceBanner.tsx`)

Conditionally rendered when the user's remaining credits fall below 20% of their cycle allocation. Displayed as a yellow warning banner at the top of the home page and the dashboard page. Contains:

- Warning text: "You have {n} credits remaining ({pct}% of your plan). Credits reset on {date}."
- CTA button: "Upgrade Plan" linking to `/billing/plans`
- Dismiss button that suppresses the banner for 24 hours (stored in localStorage)

#### Filters

A filter bar sits between the summary cards and the chart:

- **Date range picker**: Preset options (7 days, 30 days, this cycle, custom range). Custom range uses a calendar popover.
- **Category filter**: Multi-select dropdown with options: Generation, Edit, Deploy. Defaults to all selected.
- **Project filter**: Searchable dropdown populated from the user's projects. Defaults to "All projects."

Filters update query parameters in the URL so the view is shareable and bookmarkable. Changing any filter triggers a new API call with the updated parameters.

## Key Queries

The following queries are critical for dashboard performance and should be optimized:

**Daily usage by category (powers the bar chart):**

```sql
SELECT
    DATE(created_at) AS usage_date,
    category,
    SUM(amount) AS total_amount
FROM credit_transactions
WHERE user_id = :user_id
    AND type = 'debit'
    AND created_at >= :start_date
    AND created_at < :end_date
GROUP BY DATE(created_at), category
ORDER BY usage_date;
```

**Per-project totals (powers the project table):**

```sql
SELECT
    ct.project_id,
    p.name AS project_name,
    SUM(CASE WHEN ct.category = 'generation' THEN ct.amount ELSE 0 END) AS generation_credits,
    SUM(CASE WHEN ct.category = 'edit' THEN ct.amount ELSE 0 END) AS edit_credits,
    SUM(CASE WHEN ct.category = 'deploy' THEN ct.amount ELSE 0 END) AS deploy_credits,
    SUM(ct.amount) AS total_credits,
    MAX(ct.created_at) AS last_activity
FROM credit_transactions ct
JOIN projects p ON ct.project_id = p.id
WHERE ct.user_id = :user_id
    AND ct.type = 'debit'
    AND ct.created_at >= :start_date
    AND ct.created_at < :end_date
    AND ct.project_id IS NOT NULL
GROUP BY ct.project_id, p.name
ORDER BY total_credits DESC;
```

**Burn rate calculation (7-day rolling average):**

```sql
SELECT
    SUM(amount)::FLOAT / 7 AS daily_burn_rate
FROM credit_transactions
WHERE user_id = :user_id
    AND type = 'debit'
    AND created_at >= now() - INTERVAL '7 days';
```

## Security Considerations

- **Row-level isolation**: All queries filter by the authenticated `user_id`. There is no admin endpoint that exposes other users' data through this API.
- **Rate limiting**: Both endpoints are rate-limited to 60 requests per minute per user to prevent abuse.
- **Input validation**: Date range parameters are validated server-side. Maximum range is 365 days. Category and sort parameters are validated against allowed enums.
- **Sensitive data**: Credit transaction amounts are not considered PII, but `user_id` and `project_id` references are. API responses never include data for users other than the authenticated user.
- **Audit logging**: All API calls to billing endpoints are logged with the requesting user ID, endpoint, and timestamp for compliance purposes.

## Rollout Plan

| Phase | Scope | Timeline | Gate |
|-------|-------|----------|------|
| 1 | Database schema migration and backfill | Week 1 | Schema deployed to staging, backfill verified against existing balance records |
| 2 | API endpoints with feature flag | Week 2 | Integration tests passing, load test at 2x expected traffic |
| 3 | Frontend dashboard behind feature flag | Weeks 3-4 | Design review sign-off, accessibility audit passed |
| 4 | Internal dogfood | Week 5 | Team uses dashboard for 1 week, no P0/P1 bugs |
| 5 | Beta rollout to 10% of Pro users | Week 6 | Error rate <0.1%, p95 latency <500ms |
| 6 | GA rollout to all users | Week 7 | Beta metrics stable, support team briefed |

Feature flag: `billing.usage_dashboard.enabled` in LaunchDarkly, controlled per user segment.
