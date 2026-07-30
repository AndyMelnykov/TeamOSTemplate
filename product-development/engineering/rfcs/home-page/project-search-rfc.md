# RFC: Project Search (Cmd+K)

**Author:** Jordan Kim, Engineer
**Status:** Draft
**Last Updated:** 2026-03-22
**Related PRD:** `product/PRDs/home-page/project-search-prd.md`
**Related Plan:** `engineering/plans/home-page/project-search.md`

---

## Table of Contents

1. [Summary](#summary)
2. [Motivation](#motivation)
3. [Proposed Design](#proposed-design)
   - [Phase 1: Database Schemas](#phase-1-database-schemas)
   - [Phase 2: API Layer](#phase-2-api-layer)
   - [Phase 3: Frontend](#phase-3-frontend)
4. [Filters](#filters)
5. [Key Queries](#key-queries)
6. [Security Considerations](#security-considerations)
7. [Rollout Plan](#rollout-plan)

---

## Summary

This RFC proposes a global search modal triggered by Cmd+K (Ctrl+K on Windows/Linux) that allows users to quickly find projects, templates, and recent actions from anywhere in the example_product application. The search system will consist of a full-text search index backed by PostgreSQL, a lightweight API endpoint optimized for typeahead latency, and a keyboard-navigable modal component rendered as a global overlay.

## Motivation

example_product users accumulate projects quickly. Power users on our Teams and Enterprise tiers regularly maintain 50+ active projects, and template exploration is a core part of the onboarding flow. Today, finding a specific project requires scrolling through the home page project grid or relying on browser history. There is no way to search across templates or jump to recent actions (e.g., last deployment, last edited project).

Customer interviews surface this pain consistently:

- *"I have 80 projects and no way to find the one I worked on last Tuesday."* -- Acme Corp, Enterprise
- *"I know there's a SaaS dashboard template but I can't remember where I saw it."* -- Free-tier user in onboarding session

A global search modal is a well-understood UX pattern (VS Code, Slack, Linear, Notion) that directly addresses discoverability without disrupting existing navigation. It also creates a foundation for future extensibility: searching documentation, team members, or settings.

## Proposed Design

### Phase 1: Database Schemas

We introduce two tables: `search_index` for the denormalized searchable content, and `search_events` for analytics on search behavior.

#### `search_index`

Stores a flattened, searchable representation of all content types. Updated asynchronously via database triggers on source tables.

```sql
CREATE TABLE search_index (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type    VARCHAR(30) NOT NULL,          -- 'project', 'template', 'action'
    content_id      UUID NOT NULL,                  -- FK to source record
    user_id         UUID NOT NULL,                  -- Owner / actor
    org_id          UUID,                           -- NULL for free-tier users
    title           TEXT NOT NULL,                   -- Display title
    description     TEXT,                            -- Subtitle / secondary text
    search_vector   TSVECTOR NOT NULL,              -- Full-text search column
    metadata        JSONB DEFAULT '{}',             -- Flexible attributes (tags, framework, status)
    last_accessed   TIMESTAMP WITH TIME ZONE,       -- For recency ranking
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_search_index_content UNIQUE (content_type, content_id, user_id)
);

CREATE INDEX idx_search_index_vector ON search_index USING GIN (search_vector);
CREATE INDEX idx_search_index_user ON search_index (user_id, content_type);
CREATE INDEX idx_search_index_org ON search_index (org_id) WHERE org_id IS NOT NULL;
CREATE INDEX idx_search_index_last_accessed ON search_index (user_id, last_accessed DESC NULLS LAST);
```

#### `search_events`

Captures every search interaction for analytics and relevance tuning.

```sql
CREATE TABLE search_events (
    event_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    session_id          VARCHAR(64) NOT NULL,
    query_text          TEXT NOT NULL,
    query_length        INTEGER NOT NULL,
    result_count        INTEGER NOT NULL DEFAULT 0,
    clicked_result_id   UUID,                       -- NULL if no click
    clicked_result_type VARCHAR(30),                -- 'project', 'template', 'action'
    clicked_position    INTEGER,                    -- 1-indexed position in result list
    filters_applied     JSONB DEFAULT '{}',         -- e.g. {"type": "project", "date_range": "7d"}
    time_to_click_ms    INTEGER,                    -- NULL if no click
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_search_events_user ON search_events (user_id, created_at DESC);
CREATE INDEX idx_search_events_session ON search_events (session_id);
CREATE INDEX idx_search_events_created ON search_events (created_at);
```

The `search_vector` column on `search_index` is populated by a trigger:

```sql
CREATE OR REPLACE FUNCTION update_search_vector() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.metadata::text, '')), 'C');
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_search_vector_update
    BEFORE INSERT OR UPDATE ON search_index
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();
```

### Phase 2: API Layer

#### `GET /api/search`

Single endpoint serving both typeahead (as-you-type) and full search results.

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | -- | Search query string (min 1 char) |
| `type` | string | No | `all` | Filter by content type: `projects`, `templates`, `actions`, `all` |
| `date_from` | string | No | -- | ISO 8601 date, lower bound for `last_accessed` |
| `date_to` | string | No | -- | ISO 8601 date, upper bound for `last_accessed` |
| `limit` | integer | No | `10` | Max results per content type (max 25) |
| `offset` | integer | No | `0` | Pagination offset |

**Success Response (200):**

```json
{
  "query": "dashboard",
  "total_count": 14,
  "results": {
    "projects": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "title": "SaaS Dashboard v2",
        "description": "Admin dashboard with analytics charts",
        "content_type": "project",
        "last_accessed": "2026-03-21T14:30:00Z",
        "metadata": {
          "framework": "next.js",
          "status": "active",
          "deploy_count": 3
        },
        "highlight": {
          "title": "SaaS <mark>Dashboard</mark> v2",
          "description": "Admin <mark>dashboard</mark> with analytics charts"
        }
      }
    ],
    "templates": [
      {
        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "title": "Analytics Dashboard Starter",
        "description": "Pre-built dashboard template with chart components",
        "content_type": "template",
        "last_accessed": null,
        "metadata": {
          "category": "business",
          "popularity_rank": 5
        },
        "highlight": {
          "title": "Analytics <mark>Dashboard</mark> Starter",
          "description": "Pre-built <mark>dashboard</mark> template with chart components"
        }
      }
    ],
    "actions": [
      {
        "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
        "title": "Deployed SaaS Dashboard v2",
        "description": "Deployed to production 2 hours ago",
        "content_type": "action",
        "last_accessed": "2026-03-22T10:15:00Z",
        "metadata": {
          "action_type": "deploy",
          "project_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        },
        "highlight": {
          "title": "Deployed SaaS <mark>Dashboard</mark> v2"
        }
      }
    ]
  },
  "timing_ms": 42
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_QUERY` | Query parameter `q` is missing or empty |
| 400 | `INVALID_TYPE_FILTER` | `type` is not one of `projects`, `templates`, `actions`, `all` |
| 400 | `INVALID_DATE_RANGE` | `date_from` is after `date_to` or dates are malformed |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 429 | `RATE_LIMITED` | User exceeded 60 requests/minute search rate limit |
| 500 | `SEARCH_ERROR` | Internal search failure (logged, triggers alert) |

**Implementation notes:**

- The endpoint is implemented in `src/routes/search.ts`.
- PostgreSQL `ts_rank_cd` is used for relevance scoring, combined with a recency boost: `score = ts_rank * 0.7 + recency_score * 0.3`.
- Queries under 3 characters use prefix matching (`query:*`) for typeahead feel.
- Response time target: < 200ms p95.
- Rate limited at 60 req/min per user via existing rate limiter middleware.

### Phase 3: Frontend

#### SearchModal Component

Located at `src/components/search/SearchModal.tsx`. The modal is a global overlay rendered at the app root level via a React portal.

**Component tree:**

```
SearchModal
├── SearchInput          -- Auto-focused text input with clear button
├── FilterBar            -- Type filter chips (All, Projects, Templates, Actions)
├── ResultSections       -- Grouped result lists
│   ├── RecentSearches   -- Shown when input is empty
│   ├── ProjectResults   -- Project result cards
│   ├── TemplateResults  -- Template result cards
│   └── ActionResults    -- Action result cards
└── SearchFooter         -- Keyboard shortcut hints (arrows, enter, esc)
```

**Keyboard Navigation:**

| Key | Behavior |
|-----|----------|
| `Cmd+K` / `Ctrl+K` | Open search modal (global shortcut registered in `src/hooks/useKeyboardShortcuts.ts`) |
| `Escape` | Close modal |
| `Arrow Down` | Move highlight to next result |
| `Arrow Up` | Move highlight to previous result |
| `Enter` | Navigate to highlighted result |
| `Tab` | Cycle through filter chips |

**Result Sections:**

1. **Recent Searches** -- Displayed when the input is empty. Pulled from localStorage (`example_product:recent-searches`). Stores the last 5 queries as an array of `{ query: string, timestamp: number }` objects.
2. **Projects** -- Shows project name, framework badge, last-accessed timestamp, and deploy count.
3. **Templates** -- Shows template name, category tag, and popularity indicator.
4. **Actions** -- Shows action description, action type icon (deploy, edit, generate), and relative timestamp.

**Debouncing:** Input is debounced at 200ms before triggering API calls. A loading skeleton is shown during the request. If the user clears the input or types a new query before the previous response arrives, the stale response is discarded via an AbortController.

**Recent Searches (localStorage):**

```typescript
interface RecentSearch {
  query: string;
  timestamp: number;
}

// Key: 'example_product:recent-searches'
// Max entries: 5
// Written on search execution (Enter key or result click)
// Read on modal open when input is empty
```

## Filters

The search modal supports two filter dimensions:

### Type Filter

A row of chip buttons above the results. Options:

| Value | Label | Searches |
|-------|-------|----------|
| `all` | All | Projects + Templates + Actions |
| `projects` | Projects | User-owned and shared projects |
| `templates` | Templates | Public and org-private templates |
| `actions` | Actions | Recent deployments, edits, generations |

Type filter is passed as the `type` query parameter to `GET /api/search`. Default is `all`.

### Date Range Filter

Available when a type filter other than `all` is active. Options:

| Value | Label | Behavior |
|-------|-------|----------|
| `any` | Any time | No date constraint (default) |
| `7d` | Last 7 days | `date_from = NOW() - 7 days` |
| `30d` | Last 30 days | `date_from = NOW() - 30 days` |
| `90d` | Last 90 days | `date_from = NOW() - 90 days` |

Passed as `date_from` and `date_to` parameters to the API.

## Key Queries

**Full-text search with ranking:**

```sql
SELECT
    si.content_type,
    si.content_id,
    si.title,
    si.description,
    si.metadata,
    si.last_accessed,
    ts_rank_cd(si.search_vector, plainto_tsquery('english', :query)) * 0.7
        + COALESCE(EXTRACT(EPOCH FROM si.last_accessed) / EXTRACT(EPOCH FROM NOW()), 0) * 0.3
        AS score
FROM search_index si
WHERE si.user_id = :user_id
  AND si.search_vector @@ plainto_tsquery('english', :query)
  AND (:type = 'all' OR si.content_type = :type)
  AND (:date_from IS NULL OR si.last_accessed >= :date_from)
  AND (:date_to IS NULL OR si.last_accessed <= :date_to)
ORDER BY score DESC
LIMIT :limit OFFSET :offset;
```

**Prefix search for short queries (< 3 chars):**

```sql
SELECT
    si.content_type,
    si.content_id,
    si.title,
    si.description,
    si.metadata,
    si.last_accessed
FROM search_index si
WHERE si.user_id = :user_id
  AND si.search_vector @@ to_tsquery('english', :query || ':*')
ORDER BY si.last_accessed DESC NULLS LAST
LIMIT :limit;
```

**Recent searches cleanup (cron, weekly):**

```sql
DELETE FROM search_events
WHERE created_at < NOW() - INTERVAL '90 days';
```

## Security Considerations

1. **Tenant Isolation:** Every query includes `user_id` (and optionally `org_id`) in the WHERE clause. There is no cross-tenant data leakage path. The `search_index` table enforces row-level filtering at the application layer, and we will add a PostgreSQL RLS policy as defense-in-depth.

2. **Query Injection:** All user input is parameterized. The `plainto_tsquery` function sanitizes input by stripping operators, preventing tsquery injection. Raw query text is never interpolated into SQL.

3. **Rate Limiting:** The search endpoint is rate-limited at 60 requests/minute per authenticated user. Unauthenticated requests return 401 before any database query executes.

4. **PII in Search Events:** The `search_events` table stores `query_text`, which may contain user-generated content. This table is classified as PII-containing and will be:
   - Excluded from analytics data warehouse exports until the query text is hashed or redacted.
   - Subject to 90-day retention with automated deletion.
   - Accessible only to the analytics team via role-restricted views.

5. **localStorage Security:** Recent searches stored in localStorage are scoped to the application origin. They contain only query strings, not result data. localStorage is cleared on user logout.

6. **Input Sanitization:** The `q` parameter is trimmed, limited to 200 characters, and stripped of control characters before processing.

## Rollout Plan

| Phase | Scope | Timeline | Feature Flag |
|-------|-------|----------|--------------|
| 1 | Internal dogfooding -- example_product Labs team only | Week 1 | `search_modal_internal` |
| 2 | Beta -- 10% of Pro and Teams users | Week 2-3 | `search_modal_beta` |
| 3 | GA -- All authenticated users | Week 4 | `search_modal_enabled` (default on) |

**Phase 1 success criteria:**
- p95 latency < 200ms on production database
- No tenant isolation bugs in security review
- Team feedback incorporated into UX polish

**Phase 2 success criteria:**
- Search usage rate > 15% of DAU
- Zero-results rate < 20%
- Click-through rate > 40%
- No P0/P1 bugs reported

**Phase 3 GA:**
- Remove beta flag, enable for all users
- Publish help center article
- Track metrics via `search_events` pipeline (see `data-engineering/rfcs/home-page/search-events-pipeline-rfc.md`)

**Rollback:** Disable via feature flag. The search_index table and API endpoint remain deployed but unreachable from the frontend. No data migration required for rollback.
