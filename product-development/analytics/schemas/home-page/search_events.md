# Schema: `analytics.example_product.search_events`

Event-level table capturing every search interaction in the example_product platform. One row per search query execution. Tracks what users search for, how many results are returned, and which results (if any) are clicked.

**Database:** `ANALYTICS`
**Schema:** `EXAMPLE_PRODUCT`
**Table:** `SEARCH_EVENTS`
**Refresh:** Streaming (near real-time via Snowpipe)
**Retention:** 2 years

# Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `event_id` | VARCHAR(36) | No | Unique identifier for the search event (UUID) |
| `user_id` | VARCHAR(36) | No | User who performed the search |
| `org_id` | VARCHAR(36) | Yes | Organization ID (null for free-tier users) |
| `session_id` | VARCHAR(64) | No | Browser session identifier for grouping searches within a visit |
| `query_text` | TEXT | No | The search string entered by the user |
| `query_length` | INTEGER | No | Character count of the query string |
| `result_count` | INTEGER | No | Total number of results returned across all content types |
| `result_count_projects` | INTEGER | No | Number of project results returned |
| `result_count_templates` | INTEGER | No | Number of template results returned |
| `result_count_actions` | INTEGER | No | Number of action results returned |
| `clicked_result_id` | VARCHAR(36) | Yes | ID of the result the user clicked (null if no click) |
| `clicked_result_type` | VARCHAR(30) | Yes | Content type of the clicked result: `project`, `template`, `action` |
| `clicked_position` | INTEGER | Yes | 1-indexed position of the clicked result in the list |
| `filters_applied` | VARIANT | Yes | JSON object of active filters (e.g., `{"type": "project", "date_range": "7d"}`) |
| `time_to_click_ms` | INTEGER | Yes | Milliseconds from search execution to result click (null if no click) |
| `is_zero_results` | BOOLEAN | No | Whether the search returned zero results |
| `search_latency_ms` | INTEGER | No | Server-side response time for the search query in milliseconds |
| `subscription_tier` | VARCHAR(20) | No | User's subscription tier at time of search: `free`, `pro`, `teams`, `enterprise` |
| `platform` | VARCHAR(20) | No | Client platform: `web`, `desktop_app` |
| `created_at` | TIMESTAMP_NTZ | No | When the search event occurred (UTC) |

# Indexes & Clustering

- Clustered on `(created_at, user_id)`
- Commonly filtered on `is_zero_results`, `subscription_tier`, `clicked_result_type`

# Common Joins

- `users` on `user_id` -- User profile, account details, signup date
- `organizations` on `org_id` -- Organization metadata and plan information
- `projects` on `clicked_result_id` WHERE `clicked_result_type = 'project'` -- Project details for click-through analysis
- `templates` on `clicked_result_id` WHERE `clicked_result_type = 'template'` -- Template metadata
- `subscriptions` on `user_id` -- Billing and plan tier history

# Notes

- `clicked_result_id`, `clicked_result_type`, `clicked_position`, and `time_to_click_ms` are all null when the user does not click any result (abandons the search or closes the modal).
- `query_text` is classified as PII-adjacent. Use hashed or aggregated forms for reporting outside the analytics team. The raw text is available for zero-results analysis and relevance tuning only.
- `filters_applied` is a VARIANT column containing the JSON representation of any active filters. Empty object `{}` indicates no filters were applied.
- `is_zero_results` is a derived boolean for efficient filtering; it is equivalent to `result_count = 0` but avoids a scan.
- Events are deduplicated by `event_id` during Snowpipe ingestion. Duplicate events within a 5-minute window for the same `session_id` and `query_text` are dropped.
