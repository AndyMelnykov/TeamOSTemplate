# Investigation: Template Fork-to-Publish Conversion

**Author:** Casey Nguyen, Analytics
**Date:** 2026-03-08
**Linear / Jira / Asana Ticket:** EXAMPLE_PRODUCT-1020
**Status:** Complete

## Question

What percentage of forked templates reach publish? How does fork-to-publish conversion compare to blank-workflow publish conversion, and what factors influence whether a forked template gets published?

## Context

The Community Marketplace is launching soon and we need a baseline understanding of how template-based workflows perform relative to blank-start workflows. The product team needs this data to set realistic targets for the fork-to-publish conversion metric and to identify which categories or template characteristics predict publish success.

The analysis uses data from the internal template library (pre-marketplace), which has been available since January 2026. While the community marketplace will introduce user-created templates, the internal templates provide the best available proxy for expected behavior.

## Methodology

- **Time window:** 2026-01-01 to 2026-03-07 (66 days)
- **Population:** All workflows created during the window, split into two cohorts:
  - **Template cohort:** Workflows created by forking an internal template (N = 1,247)
  - **Blank cohort:** Workflows created from scratch with no template (N = 3,891)
- **Publish definition:** At least one `publish_events` record with `status = 'completed'` within 30 days of workflow creation
- **Excluded:** Workflows from internal example_product team accounts, workflows deleted within 24 hours of creation

## Key Findings

### Finding 1: Forked templates publish at 41% vs 28% for blank workflows

| Cohort | Workflows | Published | Publish Rate |
|--------|----------|----------|-------------|
| Template fork | 1,247 | 511 | **41.0%** |
| Blank workflow | 3,891 | 1,089 | **28.0%** |

Template-based workflows publish at a **46% higher rate** (41% vs 28%) than blank workflows. This gap is statistically significant (p < 0.001, chi-square test).

### Finding 2: Publish rate varies by template category

| Category | Forks | Publish Rate |
|----------|-------|-------------|
| Invoices | 387 | 52.7% |
| Purchase Orders | 201 | 44.3% |
| Vendor Onboarding | 312 | 38.1% |
| Intake Forms | 198 | 34.8% |
| NDAs / Sales Contracts | 149 | 30.9% |

Invoice templates have the highest publish rate, likely because they are simpler and closer to "done" out of the box. NDA and sales-contract templates have the lowest, possibly because users customize clauses heavily before publishing.

### Finding 3: Customization correlates with higher publish rates

| Customized? | Forks | Publish Rate |
|-------------|-------|-------------|
| Yes (edited within first session) | 823 | 47.6% |
| No (used as-is or abandoned) | 424 | 28.3% |

Users who apply customizations to a forked template are significantly more likely to publish. This suggests that engagement with the template (not just forking it) is the real predictor of publish success.

### Finding 4: Time-to-publish is faster for template forks

| Cohort | Median Time-to-Publish |
|--------|-----------------------|
| Template fork | 22 minutes |
| Blank workflow | 48 minutes |

Template forks reach publish in roughly half the time, reinforcing the value proposition of starting from a template.

## Implications

1. **Set fork-to-publish target at 40%.** The 41% baseline from internal templates is a reasonable starting target for the community marketplace. Community templates may perform slightly differently due to varying quality, so 40% is a safe initial goal.
2. **Invoice and purchase-order categories should be prioritized for marketplace seeding.** These categories have the highest publish rates and represent the most immediately useful templates.
3. **Customization is a leading indicator.** Tracking `customizations_applied` in `template_forks` will be a strong early signal of whether a fork will convert to publish. Consider using this as a trigger for engagement nudges.
4. **Template quality matters more than quantity.** The 13 percentage point gap between template forks and blank workflows is meaningful, but only when users actually engage with the template. Low-quality templates that users fork and abandon will drag down the overall conversion rate.

## SQL

```sql
-- Fork-to-publish conversion by cohort
WITH workflows AS (
    SELECT
        p.workflow_id,
        CASE WHEN tf.fork_id IS NOT NULL THEN 'template_fork' ELSE 'blank_workflow' END AS cohort,
        p.created_at AS workflow_created_at
    FROM analytics.example_product.workflows p
    LEFT JOIN analytics.example_product.template_forks tf ON tf.workflow_id = p.workflow_id
    WHERE p.created_at BETWEEN '2026-01-01' AND '2026-03-07'
      AND p.user_id NOT IN (SELECT user_id FROM analytics.example_product.internal_users)
      AND p.deleted_at IS NULL OR DATEDIFF('hour', p.created_at, p.deleted_at) > 24
),
publish_status AS (
    SELECT
        pr.workflow_id,
        pr.cohort,
        MAX(CASE WHEN de.status = 'completed' THEN 1 ELSE 0 END) AS was_published
    FROM workflows pr
    LEFT JOIN analytics.example_product.publish_events de
        ON de.workflow_id = pr.workflow_id
        AND de.created_at <= DATEADD('day', 30, pr.workflow_created_at)
    GROUP BY 1, 2
)
SELECT
    cohort,
    COUNT(*) AS total_workflows,
    SUM(was_published) AS published,
    ROUND(SUM(was_published) * 100.0 / COUNT(*), 1) AS publish_rate_pct
FROM publish_status
GROUP BY 1;
```

## Next Steps

- Share findings with Hannah Stulberg (PM) to inform marketplace launch targets
- Build the fork-to-publish conversion query into the Community Marketplace Dashboard (Sigma)
- Revisit this analysis 30 days post-marketplace-launch to compare community template performance against internal template baseline

---

## Related Resources

| Resource | Path |
|----------|------|
| Metrics definition | [marketplace-metrics.md](../../metrics/starter-templates/marketplace-metrics.md) |
| SQL query | [template-fork-rate.sql](../../queries/starter-templates/template-fork-rate.sql) |
| Schema | [template_forks.md](../../schemas/starter-templates/template_forks.md) |
