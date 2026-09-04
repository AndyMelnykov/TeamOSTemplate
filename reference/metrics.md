# Metrics

Canonical metric definitions and targets for example_product. Every dashboard, experiment, and PRD should reference this file instead of restating a target inline.

| Metric | Definition | Target |
|--------|------------|--------|
| **Extraction Success Rate (ESR)** | Percentage of automation runs that extract all required fields without manual correction | > 92% |
| **Time-to-Publish (TTP)** | Median elapsed time from first workflow draft to published/live | < 15 min |
| **Workflow Completion Rate (WCR)** | Percentage of workflows that reach at least one publish | > 60% |
| **User Retention (D7)** | Percentage of new users who return within 7 days | > 45% |
| **Refinement Depth** | Average number of follow-up edits per workflow | Tracking (higher = engagement) |
| **Publish Frequency** | Average publishes per active workflow per week | > 2 |
| **Error Recovery Rate** | Percentage of failed automation runs that succeed on retry/correction | > 80% |

Data sources and dashboards for these metrics: [`product-development/analytics/CLAUDE.md`](../product-development/analytics/CLAUDE.md).
