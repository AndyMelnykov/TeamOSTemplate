# Investigation: Template Fork-to-Deploy Conversion

**Author:** Casey Nguyen, Analytics
**Date:** 2026-03-08
**Linear / Jira / Asana Ticket:** EXAMPLE_PRODUCT-1020
**Status:** Complete

## Question

What percentage of forked templates reach deployment? How does fork-to-deploy conversion compare to blank-project deploy conversion, and what factors influence whether a forked template gets deployed?

## Context

The Community Marketplace is launching soon and we need a baseline understanding of how template-based projects perform relative to blank-start projects. The product team needs this data to set realistic targets for the fork-to-deploy conversion metric and to identify which categories or template characteristics predict deployment success.

The analysis uses data from the internal template library (pre-marketplace), which has been available since January 2026. While the community marketplace will introduce user-created templates, the internal templates provide the best available proxy for expected behavior.

## Methodology

- **Time window:** 2026-01-01 to 2026-03-07 (66 days)
- **Population:** All projects created during the window, split into two cohorts:
  - **Template cohort:** Projects created by forking an internal template (N = 1,247)
  - **Blank cohort:** Projects created from scratch with no template (N = 3,891)
- **Deploy definition:** At least one `deploy_events` record with `status = 'completed'` within 30 days of project creation
- **Excluded:** Projects from internal example_product team accounts, projects deleted within 24 hours of creation

## Key Findings

### Finding 1: Forked templates deploy at 41% vs 28% for blank projects

| Cohort | Projects | Deployed | Deploy Rate |
|--------|----------|----------|-------------|
| Template fork | 1,247 | 511 | **41.0%** |
| Blank project | 3,891 | 1,089 | **28.0%** |

Template-based projects deploy at a **46% higher rate** (41% vs 28%) than blank projects. This gap is statistically significant (p < 0.001, chi-square test).

### Finding 2: Deploy rate varies by template category

| Category | Forks | Deploy Rate |
|----------|-------|-------------|
| Landing Page | 387 | 52.7% |
| Internal Tool | 201 | 44.3% |
| SaaS | 312 | 38.1% |
| E-commerce | 198 | 34.8% |
| Portfolio | 149 | 30.9% |

Landing page templates have the highest deploy rate, likely because they are simpler and closer to "done" out of the box. Portfolio templates have the lowest, possibly because users customize them heavily before deploying.

### Finding 3: Customization correlates with higher deploy rates

| Customized? | Forks | Deploy Rate |
|-------------|-------|-------------|
| Yes (edited within first session) | 823 | 47.6% |
| No (used as-is or abandoned) | 424 | 28.3% |

Users who apply customizations to a forked template are significantly more likely to deploy. This suggests that engagement with the template (not just forking it) is the real predictor of deployment success.

### Finding 4: Time-to-deploy is faster for template forks

| Cohort | Median Time-to-Deploy |
|--------|-----------------------|
| Template fork | 22 minutes |
| Blank project | 48 minutes |

Template forks reach deployment in roughly half the time, reinforcing the value proposition of starting from a template.

## Implications

1. **Set fork-to-deploy target at 40%.** The 41% baseline from internal templates is a reasonable starting target for the community marketplace. Community templates may perform slightly differently due to varying quality, so 40% is a safe initial goal.
2. **Landing page and internal tool categories should be prioritized for marketplace seeding.** These categories have the highest deploy rates and represent the most immediately useful templates.
3. **Customization is a leading indicator.** Tracking `customizations_applied` in `template_forks` will be a strong early signal of whether a fork will convert to deployment. Consider using this as a trigger for engagement nudges.
4. **Template quality matters more than quantity.** The 13 percentage point gap between template forks and blank projects is meaningful, but only when users actually engage with the template. Low-quality templates that users fork and abandon will drag down the overall conversion rate.

## SQL

```sql
-- Fork-to-deploy conversion by cohort
WITH projects AS (
    SELECT
        p.project_id,
        CASE WHEN tf.fork_id IS NOT NULL THEN 'template_fork' ELSE 'blank_project' END AS cohort,
        p.created_at AS project_created_at
    FROM analytics.example_product.projects p
    LEFT JOIN analytics.example_product.template_forks tf ON tf.project_id = p.project_id
    WHERE p.created_at BETWEEN '2026-01-01' AND '2026-03-07'
      AND p.user_id NOT IN (SELECT user_id FROM analytics.example_product.internal_users)
      AND p.deleted_at IS NULL OR DATEDIFF('hour', p.created_at, p.deleted_at) > 24
),
deploy_status AS (
    SELECT
        pr.project_id,
        pr.cohort,
        MAX(CASE WHEN de.status = 'completed' THEN 1 ELSE 0 END) AS was_deployed
    FROM projects pr
    LEFT JOIN analytics.example_product.deploy_events de
        ON de.project_id = pr.project_id
        AND de.created_at <= DATEADD('day', 30, pr.project_created_at)
    GROUP BY 1, 2
)
SELECT
    cohort,
    COUNT(*) AS total_projects,
    SUM(was_deployed) AS deployed,
    ROUND(SUM(was_deployed) * 100.0 / COUNT(*), 1) AS deploy_rate_pct
FROM deploy_status
GROUP BY 1;
```

## Next Steps

- Share findings with Hannah Stulberg (PM) to inform marketplace launch targets
- Build the fork-to-deploy conversion query into the Community Marketplace Dashboard (Sigma)
- Revisit this analysis 30 days post-marketplace-launch to compare community template performance against internal template baseline

---

## Related Resources

| Resource | Path |
|----------|------|
| Metrics definition | [marketplace-metrics.md](../../metrics/starter-templates/marketplace-metrics.md) |
| SQL query | [template-fork-rate.sql](../../queries/starter-templates/template-fork-rate.sql) |
| Schema | [template_forks.md](../../schemas/starter-templates/template_forks.md) |
