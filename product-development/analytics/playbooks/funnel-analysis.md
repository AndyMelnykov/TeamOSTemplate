# Funnel Analysis Playbook

A repeatable methodology for investigating conversion funnels in example_product.

## When to Use This Playbook

- A funnel metric (e.g., setup completion rate, fork-to-deploy conversion) drops below target
- Product or engineering requests a funnel investigation for a new or changed flow
- You need to identify the highest-leverage drop-off point to improve

## Step-by-Step Methodology

### 1. Define the Funnel Steps
- Identify the discrete steps in the user flow
- Map each step to a measurable event in Segment or Snowflake
- Example: Domain setup funnel → `created` → `dns_instructions_viewed` → `dns_configured` → `dns_verified` → `ssl_provisioned` → `live`

### 2. Pull the Funnel Data
- Query the event tables for each step over the analysis window
- Use a CTE-based approach to count unique users at each step:

```sql
WITH funnel AS (
    SELECT
        user_id,
        MIN(CASE WHEN event = 'step_1' THEN timestamp END) AS step_1_at,
        MIN(CASE WHEN event = 'step_2' THEN timestamp END) AS step_2_at,
        MIN(CASE WHEN event = 'step_3' THEN timestamp END) AS step_3_at
    FROM analytics.example_product.events
    WHERE timestamp BETWEEN :start_date AND :end_date
    GROUP BY user_id
)
SELECT
    COUNT(step_1_at) AS step_1_users,
    COUNT(step_2_at) AS step_2_users,
    COUNT(step_3_at) AS step_3_users,
    ROUND(COUNT(step_2_at) / NULLIF(COUNT(step_1_at), 0) * 100, 1) AS step_1_to_2_pct,
    ROUND(COUNT(step_3_at) / NULLIF(COUNT(step_2_at), 0) * 100, 1) AS step_2_to_3_pct
FROM funnel;
```

### 3. Identify the Largest Drop-off
- Calculate step-to-step conversion rates
- Flag the step with the largest absolute drop-off
- Segment by cohort (tier, platform, referral source) to see if the drop-off is universal or concentrated

### 4. Investigate Root Causes
- Join with session recordings (Amplitude) to observe user behavior at the drop-off step
- Check for error events or timeout patterns near the drop-off
- Look at time-between-steps to identify where users stall vs. abandon

### 5. Quantify the Opportunity
- Calculate the impact of closing the gap: "If we improved step X conversion from Y% to Z%, we'd gain N additional completions per week"
- Tie to business metrics (revenue, retention, expansion)

### 6. Recommend and Track
- Propose specific interventions (UX changes, better error messages, async retry)
- Set up a monitoring query to track the metric post-intervention
- Document findings in an investigation file under `investigations/{product-area}/`

## Example

See the [Custom Domain Adoption Funnel Investigation](../investigations/deployment/2026-03-18-custom-domain-adoption-funnel.md) for a complete worked example of this playbook applied to the domain setup flow.

## Related Resources

| Resource | Path |
|----------|------|
| Example investigation | [Custom domain funnel](../investigations/deployment/2026-03-18-custom-domain-adoption-funnel.md) |
| Related metrics | [Custom domains metrics](../metrics/deployment/custom-domains-metrics.md) |
| Related query | [Domain setup completion](../queries/deployment/domain-setup-completion.sql) |
