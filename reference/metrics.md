# Metrics

Canonical metric definitions and targets for example_product. Every dashboard, experiment, and PRD should reference this file instead of restating a target inline.

| Metric | Definition | Target |
|--------|------------|--------|
| **Generation Success Rate (GSR)** | Percentage of generations that produce working, error-free code | > 92% |
| **Time-to-Deploy (TTD)** | Median elapsed time from first generation to production deployment | < 15 min |
| **Project Completion Rate (PCR)** | Percentage of projects that reach at least one deployment | > 60% |
| **User Retention (D7)** | Percentage of new users who return within 7 days | > 45% |
| **Iteration Depth** | Average number of follow-up generations per project | Tracking (higher = engagement) |
| **Deploy Frequency** | Average deploys per active project per week | > 2 |
| **Error Recovery Rate** | Percentage of failed generations that succeed on retry/iteration | > 80% |

Data sources and dashboards for these metrics: [`product-development/analytics/CLAUDE.md`](../product-development/analytics/CLAUDE.md).
