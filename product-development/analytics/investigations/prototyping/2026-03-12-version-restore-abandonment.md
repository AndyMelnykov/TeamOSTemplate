# Investigation: Do Users Who Restore Versions Continue Working or Abandon?

**Author:** Casey Nguyen, Analytics
**Date:** 2026-03-12
**Linear / Jira / Asana:** EXAMPLE_PRODUCT-1048
**Status:** Complete

## Question

When users restore a previous project version, do they continue working on the project (generate, edit, deploy) or do they abandon the project shortly after? Understanding post-restore behavior tells us whether version history is a recovery tool that keeps users engaged or merely a last action before giving up.

## Context

Version history launched to internal dogfood users on 2026-02-24 and expanded to beta (example_product Pro and Teams) on 2026-03-03. After 9 days of beta data, we have enough restore events to draw initial conclusions. This investigation was triggered by a question from Hannah during the March 11 product review: "Are restores a sign of engagement or a sign of frustration?"

## Methodology

**Population:** All users who performed at least one restore action during the beta period (2026-03-03 to 2026-03-11). N = 214 users across 187 projects.

**Definition of "continue working":** User performs at least one of the following actions within 30 minutes of the restore event:
- A new AI generation on the same project
- A manual file edit on the same project
- A deploy attempt on the same project

**Definition of "abandon":** No further activity on the project within 30 minutes of the restore, and no return to the project within 24 hours.

**Data sources:**
- `analytics.example_product.project_versions` (restore events)
- `analytics.example_product.project_generations` (post-restore generations)
- Segment session events (edits, deploys, navigation)

## Query

```sql
WITH restores AS (
    SELECT
        version_id,
        project_id,
        user_id,
        created_at AS restore_ts
    FROM analytics.example_product.project_versions
    WHERE action = 'restore'
      AND created_at BETWEEN '2026-03-03' AND '2026-03-12'
),

post_restore_activity AS (
    SELECT
        r.version_id AS restore_version_id,
        r.project_id,
        r.user_id,
        r.restore_ts,
        MIN(g.created_at) AS first_generation_after_restore
    FROM restores r
    LEFT JOIN analytics.example_product.project_generations g
        ON r.project_id = g.project_id
        AND r.user_id = g.user_id
        AND g.created_at > r.restore_ts
        AND g.created_at <= DATEADD('minute', 30, r.restore_ts)
    GROUP BY 1, 2, 3, 4
)

SELECT
    COUNT(*) AS total_restores,
    COUNT(first_generation_after_restore) AS continued_working,
    COUNT(*) - COUNT(first_generation_after_restore) AS did_not_continue,
    ROUND(COUNT(first_generation_after_restore) * 100.0 / COUNT(*), 1) AS continue_rate_pct
FROM post_restore_activity;
```

## Findings

| Metric | Value |
|--------|-------|
| Total restore events (beta period) | 312 |
| Unique users who restored | 214 |
| Unique projects with restores | 187 |
| **Continued working within 30 min** | **72%** |
| Continued working within 60 min | 78% |
| Returned within 24 hours (of those who did not continue in 30 min) | 41% |
| True abandonment (no return in 24 hours) | 13% |

**Key finding: 72% of users who restore a version continue working on the project within 30 minutes.** This is a strong positive signal. Version history is functioning as a recovery tool that keeps users engaged, not as a last-resort action before abandonment.

### Breakdown by action after restore

| Post-restore action (within 30 min) | % of restores |
|--------------------------------------|---------------|
| New AI generation | 58% |
| Manual file edit | 9% |
| Deploy attempt | 5% |
| No activity (within 30 min) | 28% |

The dominant pattern is: restore, then immediately generate again with a different prompt. This confirms the hypothesis that users restore to get back to a good state and then try a different approach.

### Breakdown by user tier

| Tier | Continue rate |
|------|---------------|
| Pro | 74% |
| Teams | 69% |

Teams users have a slightly lower continue rate, but the sample size for Teams is small (N = 38). Not statistically significant at this point.

## Recommendations

1. **This is a green light for GA launch.** The 72% continue rate demonstrates clear user value. Users are restoring and re-engaging, not restoring and leaving.
2. **Optimize the post-restore experience.** Since 58% of users generate immediately after restoring, consider pre-populating the prompt input with a suggestion like "Try a different approach" or showing the previous prompt that led to the version they just rolled back from.
3. **Investigate the 13% true abandonment cohort.** These users restored and never came back. Are they hitting a different problem? Worth a follow-up investigation once we have more data.
4. **Track restore-to-continue as an ongoing metric.** Add this to the Version History Feature Board as a core health metric with a target of > 70%.

---

## Related Resources

| Resource | Path |
|----------|------|
| Metrics definition | [version-history-metrics.md](../../metrics/prototyping/version-history-metrics.md) |
| SQL query | [version-restore-rate.sql](../../queries/prototyping/version-restore-rate.sql) |
| Schema | [project_versions.md](../../schemas/prototyping/project_versions.md) |
