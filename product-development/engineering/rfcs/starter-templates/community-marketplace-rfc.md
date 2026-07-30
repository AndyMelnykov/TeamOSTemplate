# RFC: Community Marketplace

**Author:** Sam Chen, Engineer
**Status:** Draft
**Last Updated:** 2026-03-22
**Related PRD:** [`product/PRDs/starter-templates/community-marketplace-prd.md`](../../../product/PRDs/starter-templates/community-marketplace-prd.md)
**Related Plan:** [`engineering/plans/starter-templates/community-marketplace.md`](../../plans/starter-templates/community-marketplace.md)

---

## Table of Contents

1. [Summary](#summary)
2. [Motivation](#motivation)
3. [Proposed Design](#proposed-design)
4. [Database Schema](#database-schema)
5. [API Design](#api-design)
6. [Frontend Components](#frontend-components)
7. [Key Queries](#key-queries)
8. [Security Considerations](#security-considerations)
9. [Rollout Plan](#rollout-plan)

---

## Summary

The Community Marketplace is a platform feature that enables example_product users to publish their projects as reusable templates and discover templates created by other users. The marketplace surfaces ratings and usage statistics to help users find high-quality starting points for their projects. This creates a user-generated content flywheel where the template catalog grows organically without requiring internal effort for every new template.

## Motivation

Today, all templates in the example_product template library are created and maintained internally by the example_product team. This creates several problems:

1. **Limited catalog size.** The internal team can only produce a handful of templates per quarter, leaving gaps in coverage for niche use cases (e.g., restaurant ordering systems, nonprofit donor portals, fitness tracking apps).
2. **Users want to share.** In customer calls and feature requests, users consistently ask for a way to publish their projects as templates so others can benefit from their work. Approximately 34% of feature requests in Q1 2026 referenced template sharing or discovery.
3. **No network effects.** The current template system is a static asset. A marketplace transforms it into a network where each new published template increases the value of the platform for all users.
4. **Quality signal is missing.** Without community ratings and usage data, there is no way to surface which templates are genuinely useful versus which simply exist.

The Community Marketplace addresses all of these by allowing any example_product user to publish a template, browse and fork community templates, and rate them after use.

## Proposed Design

The implementation is divided into three phases:

### Phase 1: Publish and Browse (Weeks 1-3)

- Add "Publish as Template" flow in project settings
- Build the `published_templates` database table and publishing API
- Create the `MarketplaceBrowser` component with grid layout and category filtering
- Implement the `GET /api/marketplace` and `GET /api/marketplace/:id` endpoints
- Add manual review queue for submitted templates (admin panel)

### Phase 2: Fork and Use (Weeks 4-5)

- Implement the `POST /api/marketplace/:id/use` endpoint to fork a template into the user's projects
- Track fork events in the `template_forks` analytics table
- Display fork count on template cards
- Add "Used by X people" social proof badges

### Phase 3: Ratings and Discovery (Weeks 6-8)

- Add the `template_ratings` table and `POST /api/marketplace/:id/rate` endpoint
- Build the rating prompt widget (triggered after using a forked template for >10 minutes)
- Implement sort-by options: popular (fork count), new (created_at), top-rated (avg_rating)
- Add full-text search across template titles and descriptions
- Build personalized recommendation engine based on user's project history and category preferences

## Database Schema

### `published_templates`

```sql
CREATE TABLE published_templates (
    id              VARCHAR(36) PRIMARY KEY DEFAULT UUID_GENERATE_V4(),
    source_project_id VARCHAR(36) NOT NULL REFERENCES projects(id),
    author_id       VARCHAR(36) NOT NULL REFERENCES users(id),
    title           VARCHAR(200) NOT NULL,
    description     TEXT NOT NULL,
    category        VARCHAR(50) NOT NULL CHECK (category IN (
                        'saas', 'portfolio', 'e-commerce', 'landing-page', 'internal-tool'
                    )),
    preview_images  JSONB NOT NULL DEFAULT '[]'::JSONB,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN (
                        'pending', 'approved', 'rejected'
                    )),
    fork_count      INTEGER NOT NULL DEFAULT 0,
    avg_rating      NUMERIC(3, 2) DEFAULT NULL,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_published_templates_category ON published_templates(category);
CREATE INDEX idx_published_templates_status ON published_templates(status);
CREATE INDEX idx_published_templates_author ON published_templates(author_id);
CREATE INDEX idx_published_templates_fork_count ON published_templates(fork_count DESC);
CREATE INDEX idx_published_templates_avg_rating ON published_templates(avg_rating DESC NULLS LAST);
CREATE INDEX idx_published_templates_created_at ON published_templates(created_at DESC);
```

The `preview_images` JSONB column stores an array of objects with the structure:

```json
[
  {
    "url": "https://cdn.example_productlabs.dev/templates/abc123/preview-1.png",
    "alt": "Dashboard overview screen",
    "order": 1
  }
]
```

### `template_ratings`

```sql
CREATE TABLE template_ratings (
    id              VARCHAR(36) PRIMARY KEY DEFAULT UUID_GENERATE_V4(),
    template_id     VARCHAR(36) NOT NULL REFERENCES published_templates(id) ON DELETE CASCADE,
    user_id         VARCHAR(36) NOT NULL REFERENCES users(id),
    rating          INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(template_id, user_id)
);

CREATE INDEX idx_template_ratings_template ON template_ratings(template_id);
```

A trigger on `template_ratings` INSERT recalculates and updates `published_templates.avg_rating`:

```sql
CREATE OR REPLACE FUNCTION update_avg_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE published_templates
    SET avg_rating = (
        SELECT ROUND(AVG(rating)::NUMERIC, 2)
        FROM template_ratings
        WHERE template_id = NEW.template_id
    ),
    updated_at = NOW()
    WHERE id = NEW.template_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_avg_rating
    AFTER INSERT ON template_ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_avg_rating();
```

## API Design

### `GET /api/marketplace`

Browse published templates with filtering and sorting.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | (all) | Filter by category: `saas`, `portfolio`, `e-commerce`, `landing-page`, `internal-tool` |
| `sort` | string | `popular` | Sort order: `popular` (fork_count desc), `new` (created_at desc), `top-rated` (avg_rating desc) |
| `search` | string | (none) | Full-text search across title and description |
| `page` | integer | 1 | Page number for pagination |
| `per_page` | integer | 24 | Results per page (max 100) |

**Success Response (200):**

```json
{
  "templates": [
    {
      "id": "abc-123",
      "title": "SaaS Admin Dashboard",
      "description": "A complete admin dashboard with user management, analytics charts, and settings panels.",
      "category": "saas",
      "author": {
        "id": "user-456",
        "username": "janedoe",
        "avatar_url": "https://cdn.example_productlabs.dev/avatars/user-456.jpg"
      },
      "preview_images": [
        { "url": "https://cdn.example_productlabs.dev/templates/abc-123/preview-1.png", "alt": "Dashboard overview", "order": 1 }
      ],
      "fork_count": 142,
      "avg_rating": 4.6,
      "created_at": "2026-03-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 24,
    "total_count": 87,
    "total_pages": 4
  }
}
```

**Error Responses:**

| Status | Condition | Body |
|--------|-----------|------|
| 400 | Invalid `category` or `sort` value | `{ "error": "invalid_parameter", "message": "Invalid category. Must be one of: saas, portfolio, e-commerce, landing-page, internal-tool" }` |
| 500 | Database error | `{ "error": "internal_error", "message": "An unexpected error occurred" }` |

---

### `GET /api/marketplace/:id`

Get full details for a single published template.

**Success Response (200):**

```json
{
  "id": "abc-123",
  "title": "SaaS Admin Dashboard",
  "description": "A complete admin dashboard with user management, analytics charts, and settings panels.",
  "category": "saas",
  "author": {
    "id": "user-456",
    "username": "janedoe",
    "avatar_url": "https://cdn.example_productlabs.dev/avatars/user-456.jpg"
  },
  "preview_images": [
    { "url": "https://cdn.example_productlabs.dev/templates/abc-123/preview-1.png", "alt": "Dashboard overview", "order": 1 },
    { "url": "https://cdn.example_productlabs.dev/templates/abc-123/preview-2.png", "alt": "User management page", "order": 2 }
  ],
  "source_project_id": "proj-789",
  "fork_count": 142,
  "avg_rating": 4.6,
  "rating_count": 38,
  "status": "approved",
  "created_at": "2026-03-15T10:30:00Z",
  "updated_at": "2026-03-18T14:22:00Z"
}
```

**Error Responses:**

| Status | Condition | Body |
|--------|-----------|------|
| 404 | Template not found or not approved | `{ "error": "not_found", "message": "Template not found" }` |
| 500 | Database error | `{ "error": "internal_error", "message": "An unexpected error occurred" }` |

---

### `POST /api/marketplace`

Publish a project as a community template. Requires authentication.

**Request Body:**

```json
{
  "source_project_id": "proj-789",
  "title": "SaaS Admin Dashboard",
  "description": "A complete admin dashboard with user management, analytics charts, and settings panels.",
  "category": "saas",
  "preview_images": [
    { "url": "https://cdn.example_productlabs.dev/templates/abc-123/preview-1.png", "alt": "Dashboard overview", "order": 1 }
  ]
}
```

**Success Response (201):**

```json
{
  "id": "abc-123",
  "status": "pending",
  "message": "Template submitted for review. You will be notified when it is approved."
}
```

**Error Responses:**

| Status | Condition | Body |
|--------|-----------|------|
| 400 | Missing required fields or invalid category | `{ "error": "validation_error", "message": "Title is required and must be under 200 characters" }` |
| 401 | Not authenticated | `{ "error": "unauthorized", "message": "Authentication required" }` |
| 403 | User does not own the source project | `{ "error": "forbidden", "message": "You can only publish templates from your own projects" }` |
| 409 | This project is already published as a template | `{ "error": "conflict", "message": "This project has already been published as a template" }` |
| 500 | Database error | `{ "error": "internal_error", "message": "An unexpected error occurred" }` |

---

### `POST /api/marketplace/:id/use`

Fork a published template into the user's projects. Creates an independent copy. Requires authentication.

**Success Response (201):**

```json
{
  "project_id": "proj-new-456",
  "message": "Template forked successfully. Opening your new project.",
  "redirect_url": "/projects/proj-new-456"
}
```

**Error Responses:**

| Status | Condition | Body |
|--------|-----------|------|
| 401 | Not authenticated | `{ "error": "unauthorized", "message": "Authentication required" }` |
| 404 | Template not found or not approved | `{ "error": "not_found", "message": "Template not found" }` |
| 429 | Rate limit exceeded (max 10 forks per hour) | `{ "error": "rate_limited", "message": "Too many fork requests. Please try again later." }` |
| 500 | Fork operation failed | `{ "error": "internal_error", "message": "An unexpected error occurred" }` |

Side effects on success:
- Increments `published_templates.fork_count` by 1
- Inserts a row into `template_forks` analytics table
- Fires `template.forked` Segment event

---

### `POST /api/marketplace/:id/rate`

Rate a template. Requires authentication. User must have previously forked the template.

**Request Body:**

```json
{
  "rating": 4
}
```

**Success Response (200):**

```json
{
  "message": "Rating submitted. Thank you for your feedback.",
  "new_avg_rating": 4.5
}
```

**Error Responses:**

| Status | Condition | Body |
|--------|-----------|------|
| 400 | Rating not between 1 and 5 | `{ "error": "validation_error", "message": "Rating must be an integer between 1 and 5" }` |
| 401 | Not authenticated | `{ "error": "unauthorized", "message": "Authentication required" }` |
| 403 | User has not forked this template | `{ "error": "forbidden", "message": "You must use a template before rating it" }` |
| 404 | Template not found | `{ "error": "not_found", "message": "Template not found" }` |
| 409 | User has already rated this template | `{ "error": "conflict", "message": "You have already rated this template" }` |
| 500 | Database error | `{ "error": "internal_error", "message": "An unexpected error occurred" }` |

## Frontend Components

### MarketplaceBrowser

The primary marketplace view, accessible at `/templates/marketplace`. Layout:

```
┌──────────────────────────────────────────────────────────┐
│  Search Bar [🔍 Search templates...]                     │
├────────────┬─────────────────────────────────────────────┤
│            │  Sort: [Popular ▾] [New] [Top Rated]        │
│  Category  │─────────────────────────────────────────────│
│  Sidebar   │  ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│            │  │ Template │ │ Template │ │ Template │      │
│  ○ All     │  │  Card 1  │ │  Card 2  │ │  Card 3  │      │
│  ○ SaaS    │  └─────────┘ └─────────┘ └─────────┘      │
│  ○ Portfol │  ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  ○ E-comm  │  │ Template │ │ Template │ │ Template │      │
│  ○ Landing │  │  Card 4  │ │  Card 5  │ │  Card 6  │      │
│  ○ Interna │  └─────────┘ └─────────┘ └─────────┘      │
│            │                                             │
│            │  [Load More]                                │
├────────────┴─────────────────────────────────────────────┤
│  Pagination: ← 1 2 3 4 →                                │
└──────────────────────────────────────────────────────────┘
```

**Component:** `src/components/templates/MarketplaceBrowser.tsx`

- Fetches from `GET /api/marketplace` with current filter/sort/search state
- Debounced search input (300ms)
- URL query params synced with filter state for shareability
- Responsive grid: 3 columns on desktop, 2 on tablet, 1 on mobile

### TemplateCard

Individual template card displayed in the grid.

**Component:** `src/components/templates/TemplateCard.tsx`

Contents:
- Preview image (first from `preview_images` array, with lazy loading)
- Title (truncated to 2 lines)
- Author name and avatar
- Category badge
- Fork count (e.g., "142 uses")
- Star rating (e.g., "4.6 ★")
- "Use Template" button (triggers fork flow)

### CategorySidebar

**Component:** `src/components/templates/CategorySidebar.tsx`

Categories with counts:
- **All** - Total approved templates
- **SaaS** - Admin dashboards, SaaS tools, subscription platforms
- **Portfolio** - Personal sites, developer portfolios, creative showcases
- **E-commerce** - Online stores, product catalogs, checkout flows
- **Landing Page** - Marketing pages, product launches, waitlists
- **Internal Tool** - Admin panels, CRMs, inventory systems

### RatingWidget

**Component:** `src/components/templates/RatingWidget.tsx`

- 5-star interactive rating input
- Appears as a bottom sheet/modal after the user has been working in a forked project for >10 minutes
- Shows current average rating and total rating count
- Disabled state if user has already rated
- Submits to `POST /api/marketplace/:id/rate`

### PublishTemplateDialog

**Component:** `src/components/templates/PublishTemplateDialog.tsx`

- Triggered from project settings ("Publish as Template" button)
- Form fields: title, description, category dropdown, preview image upload (up to 5 images)
- Preview of how the template card will look
- Submit sends to `POST /api/marketplace`
- Success state shows "Submitted for review" confirmation

## Key Queries

### Browse templates by category

```sql
SELECT pt.id, pt.title, pt.description, pt.category,
       pt.preview_images, pt.fork_count, pt.avg_rating, pt.created_at,
       u.username, u.avatar_url
FROM published_templates pt
JOIN users u ON u.id = pt.author_id
WHERE pt.status = 'approved'
  AND ($1::VARCHAR IS NULL OR pt.category = $1)
ORDER BY
    CASE WHEN $2 = 'popular' THEN pt.fork_count END DESC,
    CASE WHEN $2 = 'new' THEN pt.created_at END DESC,
    CASE WHEN $2 = 'top-rated' THEN pt.avg_rating END DESC NULLS LAST
LIMIT $3 OFFSET $4;
```

### Full-text search

```sql
SELECT pt.id, pt.title, pt.description, pt.category,
       pt.fork_count, pt.avg_rating,
       ts_rank(to_tsvector('english', pt.title || ' ' || pt.description), plainto_tsquery('english', $1)) AS rank
FROM published_templates pt
WHERE pt.status = 'approved'
  AND to_tsvector('english', pt.title || ' ' || pt.description) @@ plainto_tsquery('english', $1)
ORDER BY rank DESC
LIMIT $2 OFFSET $3;
```

### Top templates by category (for homepage widgets)

```sql
SELECT category,
       id, title, preview_images, fork_count, avg_rating
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY fork_count DESC) AS rn
    FROM published_templates
    WHERE status = 'approved'
) ranked
WHERE rn <= 3
ORDER BY category, rn;
```

## Security Considerations

### Review Queue

All published templates go through a manual review process before appearing in the marketplace:

1. User submits template via `POST /api/marketplace` -- status is set to `pending`
2. Template appears in the admin review queue at `/admin/marketplace/review`
3. Reviewer checks for:
   - Appropriate content (no offensive material, spam, or copyrighted content)
   - Working code (template can be forked and renders correctly)
   - Accurate metadata (title and description match the actual template)
4. Reviewer approves or rejects with an optional note sent to the author
5. Only `approved` templates are returned by `GET /api/marketplace`

### Abuse Prevention

- **Rate limiting:** Users can publish a maximum of 5 templates per day and fork a maximum of 10 templates per hour.
- **Spam detection:** Automated check on submission for duplicate content, keyword stuffing in descriptions, and suspiciously similar templates from the same author.
- **Report button:** Each template card includes a "Report" option that flags the template for review. Templates accumulate reports and are automatically hidden after 3 unique reports pending re-review.
- **Author reputation:** Accounts must have at least one deployed project and be older than 7 days to publish templates.
- **Content scanning:** Preview images are scanned for inappropriate content using an automated moderation service before approval.

### Data Access

- `published_templates` rows with status `pending` or `rejected` are only visible to the author and admins.
- The `source_project_id` is stored for provenance but the source project's code is snapshotted at publish time -- the fork operation copies from the snapshot, not the live project.
- Rating is restricted to users who have forked the template (verified via `template_forks` table).

## Rollout Plan

### Phase 1: Internal Beta (Week 9)

- Deploy behind the `marketplace-beta` feature flag
- Enable for internal example_product team members and 20 invited beta users
- Seed marketplace with 15-20 high-quality templates from the internal library
- Monitor review queue volume, fork success rate, and page load performance

### Phase 2: Limited GA (Week 10)

- Enable for all example_product Pro and Teams users
- Publish announcement in-app and via email
- Monitor for abuse patterns and review queue throughput
- Collect feedback on discovery and publishing UX

### Phase 3: Full GA (Week 12)

- Enable for all users including free tier
- Add marketplace link to main navigation
- Feature top community templates on the example_product homepage
- Launch "Template of the Week" editorial spotlight
