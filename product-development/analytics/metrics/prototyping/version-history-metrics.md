# Version History - Metrics Definition

**Feature:** Version History
**Owner:** Hannah Stulberg, PM
**Analytics Lead:** Casey Nguyen

## Primary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Versions per project | Average number of version snapshots per active project (includes auto-snapshots, manual saves, and restores) | Tracking (higher = engagement) | `project_versions` table |
| Restore rate | % of active projects that have at least one restore event in a given period | > 15% within 60 days of launch | `project_versions` where action = 'restore' |
| Restore-to-continue rate | % of users who perform at least one additional generation within 30 minutes of a restore | > 70% | `project_versions` joined with `project_generations` on user_id and time window |

## Secondary Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| Version history panel open rate | % of active users who open the version history panel at least once per session | > 25% | Segment event `version_history.panel_opened` |
| Diff view usage rate | % of version history sessions where the user views at least one diff | > 40% | Segment event `version_history.diff_viewed` |
| Avg time to restore | Median time from opening version history panel to completing a restore | < 30s | Segment events `version_history.panel_opened` to `version_history.restore_completed` |
| Manual save rate | % of versions created via manual save (vs. auto-snapshot) | Tracking | `project_versions` where action = 'manual_save' |
| Post-restore abandonment | % of users who do not return to the project within 24 hours after a restore | < 10% | `project_versions` joined with session data |
| Snapshot storage per project | Average total_size_bytes across all versions for a project | Tracking (monitor for cost) | `project_versions` |

## Data Sources

- **`project_versions`** - Primary event table in Snowflake, populated via backend event logging through Snowpipe
- **`project_generations`** - Upstream generation data, used to measure restore-to-continue (did the user keep generating after restoring?)
- **`projects`** - Project metadata for filtering by framework, tier, and creation date
- **Segment events** - Client-side interaction events for panel opens, diff views, and UI engagement

## Dashboard Links

- [Version History Feature Board](https://app.mode.com/example_product-labs/reports/version-history) - Weekly metrics review
- [Version History Health](https://app.sigmacomputing.com/example_product-labs/workbook/version-history-health) - Real-time restore success rate and error monitoring

## Related Queries

| Query | Description |
|-------|-------------|
| [version-restore-rate.sql](../../queries/prototyping/version-restore-rate.sql) | Version restore rate and versions per project |

## Related Investigations

| Investigation | Date | Summary |
|--------------|------|---------|
| [2026-03-12-version-restore-abandonment.md](../../investigations/prototyping/2026-03-12-version-restore-abandonment.md) | 2026-03-12 | Version restore abandonment analysis |
