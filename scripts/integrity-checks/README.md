# Integrity Checks

Config-driven Python checks for structural/process integrity across the discovery -> PRD -> engineering -> decision pipeline (e.g. hypotheses with no supporting signal, PRDs missing required sections, feature-index.yaml drift, stale backlog entries). See `docs/architecture.md` for how this fits the repo's deterministic-policy-layer pattern.

## Run locally

```bash
pip install -r scripts/integrity-checks/requirements.txt
python scripts/integrity-checks/run_checks.py
python scripts/integrity-checks/summarize.py
cat scripts/integrity-checks/reports/summary.md
```

`run_checks.py` exits 1 if any check has an open finding and `fail-on-findings: true` in `config.yaml` (the default) -- same convention as `scripts/check-references.ps1`.

## Enable / disable a check

Edit `config.yaml`'s `checks:` map -- `true` runs it, `false` skips it. Thresholds (staleness day counts) live in the same file under `thresholds:`.

`feature-index-broken-tickets` ships disabled: this template repo's example ticket numbers aren't real GitHub issues. Flip it to `true` once your `feature-index.yaml` has real ticket references and `gh` is authenticated against your real repo.

## How staleness is tracked

Every run reads `reports/status.json` from the previous run, so a finding that already existed keeps its original `first_detected` date instead of resetting to today. A finding no longer produced by any check is dropped (treated as resolved) rather than kept around. `summarize.py` reads the same file and computes "days open" from `first_detected`. Both `reports/status.json` and `reports/summary.md` are committed back to the repo by the GitHub Actions workflow, so they're visible in a normal `git log`/diff without any external system.

## Setting up the GitHub Actions cron

1. This repo's `.github/workflows/integrity-checks.yml` already defines the schedule (`0 8 * * *`, i.e. 08:00 UTC daily) and a `workflow_dispatch` trigger for running it on demand from the Actions tab.
2. **One manual setting is required**, because a workflow can't grant itself permission to push commits: go to **Settings -> Actions -> General -> Workflow permissions** and select **"Read and write permissions"**, then Save. Without this, the "Commit updated reports" step fails with a 403.
3. No secrets need to be added by hand -- `secrets.GITHUB_TOKEN` is provided automatically by GitHub Actions and is enough for both `git push` and the `gh` CLI calls used by `feature-index-broken-tickets` (once enabled).
4. To change the schedule, edit the `cron:` line (standard 5-field cron, UTC). To run it immediately without waiting for the schedule, use **Actions -> Integrity Checks -> Run workflow**.
5. Posting `reports/summary.md` anywhere outside this repo (Slack, email, etc.) is intentionally not built here -- a red workflow run in the Actions tab is the only built-in signal. Add a separate step (or a Claude Code scheduled routine that reads `reports/summary.md`) if you want that.
