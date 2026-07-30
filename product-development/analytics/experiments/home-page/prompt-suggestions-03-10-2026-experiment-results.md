# Experiment: Personalized vs Generic Prompt Suggestions

| Field | Value |
|-------|-------|
| Run Date | 2026-03-10 |
| Author | Casey Nguyen, Analytics |
| Status | Complete |
| Related Ticket | EXAMPLE_PRODUCT-1040 |
| Duration | 2 weeks (2026-02-24 to 2026-03-09) |
| Split | 50/50 |
| Total Users | 8,412 (4,198 control / 4,214 treatment) |
| Platform | Web |

---

## TL;DR

Personalized prompt suggestions on the example_product home page increased prompt submission rate by 18% (32.1% vs 27.2%) and reduced median time-to-first-action by 11 seconds. The treatment group also showed a 6% lift in Day 7 retention. Recommendation: **Ship to 100% of users.**

---

## Hypothesis

Users who see prompt suggestions based on their project history and usage patterns will engage with the home page prompt input at a higher rate than users who see generic starter prompts, because personalized suggestions reduce the cognitive load of deciding what to build next.

## Control: Generic Prompt Suggestions

Users in the control group saw a fixed set of 4 generic starter prompts displayed below the home page prompt input:

| Prompt |
|--------|
| "Build a landing page for my startup" |
| "Create a SaaS dashboard with analytics" |
| "Design a portfolio website" |
| "Make an e-commerce product page" |

These prompts were static, identical for all users, and did not change between sessions.

## Treatment: Personalized Prompt Suggestions

Users in the treatment group saw up to 4 dynamically generated prompt suggestions based on:

1. **Recent project context:** Suggestions related to the user's last 3 projects (e.g., if the user recently built a dashboard, suggest "Add a settings page to your dashboard").
2. **Framework affinity:** Suggestions matching the user's most-used framework (e.g., Next.js users see Next.js-specific prompts).
3. **Progression signals:** For users who have generated but not deployed, suggest deployment-oriented prompts. For users who deployed, suggest iteration prompts.
4. **Fallback:** New users with no history received the same generic prompts as the control group.

Suggestions refreshed on each home page visit, with a maximum of 1 repeat suggestion across consecutive visits.

---

## Results

### Primary Metrics

| Metric | Control | Treatment | Delta | p-value | Significant |
|--------|---------|-----------|-------|---------|-------------|
| Prompt submission rate | 27.2% | 32.1% | +18.0% | 0.003 | Yes |
| Time-to-first-action (median) | 48s | 37s | -22.9% | 0.001 | Yes |
| Home page bounce rate | 41.3% | 38.7% | -6.3% | 0.042 | Yes |

### Secondary Metrics

| Metric | Control | Treatment | Delta | p-value | Significant |
|--------|---------|-----------|-------|---------|-------------|
| Suggestions clicked (% of impressions) | 14.8% | 22.6% | +52.7% | < 0.001 | Yes |
| Generations per session | 1.8 | 2.1 | +16.7% | 0.018 | Yes |
| Day 7 retention | 43.2% | 45.8% | +6.0% | 0.087 | No (marginal) |
| Deploy rate (within session) | 18.4% | 19.1% | +3.8% | 0.312 | No |
| Avg generation quality score | 7.2 | 7.3 | +1.4% | 0.624 | No |

### Segmentation

| Segment | Control Submission Rate | Treatment Submission Rate | Delta |
|---------|------------------------|--------------------------|-------|
| Free tier | 24.1% | 28.9% | +19.9% |
| Pro tier | 30.8% | 35.4% | +14.9% |
| Teams tier | 32.5% | 38.2% | +17.5% |
| New users (< 7 days) | 21.3% | 27.0% | +26.8% |
| Returning users (7+ days) | 31.4% | 35.6% | +13.4% |

The largest lift was observed in new users (< 7 days old), where personalized suggestions increased submission rate by 26.8%. This is partially explained by the fact that new users benefit most from guided prompts since they have less familiarity with what example_product can build.

---

## Learnings

1. **Personalization outperforms generic across all segments.** The lift was consistent across tiers and tenure, though strongest for new users. This validates the hypothesis that reducing cognitive load drives engagement.

2. **Framework affinity is the strongest signal.** Among the three personalization signals (recent projects, framework affinity, progression), framework-matched suggestions had the highest click rate (28.3% vs 19.1% for recent-project and 17.4% for progression-based suggestions).

3. **Time-to-first-action is a leading indicator.** The 11-second reduction in median time-to-first-action correlated with higher downstream generation counts. Users who act faster tend to iterate more within the same session.

4. **Deploy rate was not significantly affected.** Personalized suggestions increased generation engagement but did not meaningfully move deployment rates within the same session. Deployment is a downstream behavior with its own friction points unrelated to prompt suggestions.

5. **Day 7 retention showed a promising but non-significant signal.** The 6% lift (p=0.087) warrants monitoring post-launch. A longer observation window or larger sample may confirm this trend.

---

## Decision

**Ship to 100% of users.** The primary metrics showed statistically significant improvements with no degradation in guardrail metrics (generation quality, error rates, page load time). The feature flag `personalized_prompt_suggestions` will be set to `enabled` for all users starting 2026-03-12.

Follow-up work:
- Monitor Day 7 retention for 4 weeks post-launch to validate the marginal retention signal.
- Explore adding a 4th personalization signal based on template browsing history (EXAMPLE_PRODUCT-1062).
- A/B test suggestion count: 4 vs 6 suggestions to determine if more options improve or hurt engagement.

---

## Appendix

### Query A: Primary metric calculation

```sql
WITH experiment_users AS (
    SELECT
        user_id,
        variant,
        MIN(created_at) AS first_exposure
    FROM analytics.example_product.experiment_assignments
    WHERE experiment_id = 'prompt_suggestions_v1'
      AND created_at BETWEEN '2026-02-24' AND '2026-03-09'
    GROUP BY 1, 2
),

user_actions AS (
    SELECT
        eu.user_id,
        eu.variant,
        COUNT(DISTINCT CASE WHEN pg.created_at IS NOT NULL THEN pg.generation_id END) AS generations,
        MIN(pg.created_at) AS first_generation_at,
        eu.first_exposure
    FROM experiment_users eu
    LEFT JOIN analytics.example_product.project_generations pg
        ON eu.user_id = pg.user_id
        AND pg.created_at BETWEEN eu.first_exposure AND DATEADD('day', 1, eu.first_exposure)
    GROUP BY 1, 2
)

SELECT
    variant,
    COUNT(*) AS total_users,
    COUNT_IF(generations > 0) AS users_with_submission,
    ROUND(COUNT_IF(generations > 0) * 100.0 / COUNT(*), 2) AS submission_rate_pct,
    MEDIAN(DATEDIFF('second', first_exposure, first_generation_at)) AS median_time_to_first_action_s
FROM user_actions
GROUP BY 1
ORDER BY 1;
```

### Query B: Suggestion click-through by personalization type

```sql
WITH suggestion_events AS (
    SELECT
        se.user_id,
        se.suggestion_type,         -- 'recent_project', 'framework', 'progression', 'generic'
        se.variant,
        se.was_clicked
    FROM analytics.example_product.suggestion_impression_events se
    INNER JOIN analytics.example_product.experiment_assignments ea
        ON se.user_id = ea.user_id
        AND ea.experiment_id = 'prompt_suggestions_v1'
    WHERE se.created_at BETWEEN '2026-02-24' AND '2026-03-09'
)

SELECT
    variant,
    suggestion_type,
    COUNT(*) AS total_impressions,
    COUNT_IF(was_clicked = TRUE) AS clicks,
    ROUND(COUNT_IF(was_clicked = TRUE) * 100.0 / COUNT(*), 2) AS click_rate_pct
FROM suggestion_events
GROUP BY 1, 2
ORDER BY 1, click_rate_pct DESC;
```
