# Product OS Gap Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the gaps between `01-ai-native-product-os.md` (the reference-architecture spec) and this repo's current state, so the repo fully demonstrates every principle the spec describes — not just most of them.

**Architecture:** This repo (`TeamOSTemplate`) is already a substantially complete implementation of the spec: 34 `CLAUDE.md` routers, a function × product-area matrix, and `feature-index.yaml` as the join table all exist and work. This plan does **not** rebuild any of that. It closes five specific, verified gaps: (1) no centralized `reference/` vocabulary layer — terms/metrics/segments are duplicated inline across CLAUDE.md files instead of defined once; (2) seven dangling file references inside `feature-index.yaml` plus stale/inconsistent paths in `.claude/commands/customer-call.md` and a missing worked example in the `customer-call-summary` skill; (3) only 2 of the spec's 3 example workflows exist — "new feature intake" is missing; (4) no automated broken-reference checker, so the dangling refs in (2) went undetected; (5) no evaluation benchmark, despite the spec calling one out as a required signal of whether the architecture actually helps.

**Tech Stack:** Markdown + YAML content files; one Windows PowerShell 5.1 script (`scripts/check-references.ps1`) for reference-integrity verification, matching the existing `scripts/replace-product-name.ps1` convention. No application code, no test framework — this repo's "tests" are content-integrity checks (the checker script) and content-provenance checks (grep/diff against source-of-truth tables), consistent with the repo's own nature as a documentation/context system rather than an application.

**Spec:** `01-ai-native-product-os.md` (provided in conversation; not currently checked into the repo — Task 14 adds it to `reference/` as the architecture's own canonical source document).

## Global Constraints

- Every new or edited file must use the existing placeholder product name `example_product` / `EXAMPLE_PRODUCT` — never reintroduce the pre-rebrand name `Forge` (see `scripts/replace-product-name.ps1` and commit `bdbae7b`).
- Every new `CLAUDE.md` router must follow the existing pattern: short purpose statement, then a table-based doc index — no prose essays (see any existing folder `CLAUDE.md` for the house style).
- Never delete or overwrite raw source evidence (call transcripts, meeting transcripts) — this repo's provenance pattern (`calls/transcripts/` beside `calls/summaries/`) is load-bearing per the spec's Principle 6 and must be preserved by every task.
- New dated artifacts follow the repo's existing naming conventions verbatim: `{feature}-prd.md`, `{feature}-rfc.md`, `{feature}.md` (plans), `bug-{MM-DD-YYYY}-{desc}/investigation-plan.md`, `YYYY-MM-DD.md` (dated docs). Do not invent new naming schemes.
- After every task that touches a path referenced elsewhere in the repo, re-run `scripts/check-references.ps1` (built in Task 1) and confirm it reports no *new* broken references versus the previous run's baseline.
- This is a demo/template repo (`example_product` is a placeholder, per README.md and the rebrand script) — new content must be realistic and internally consistent with existing fabricated facts (e.g., Acme Corp = Growth segment, Derek/Priya as Acme contacts, GSR/TTD/PCR targets), not generic filler.

---

## Task 1: Build the broken-reference checker

**Files:**
- Create: `scripts/check-references.ps1`

**Interfaces:**
- Produces: an exit-code-0/1 script every later task re-runs to verify it hasn't introduced (Task-1-forward) or hasn't left unfixed (Tasks 8-10) a dangling reference. Invocation: `powershell -File scripts/check-references.ps1` from repo root, or `.\scripts\check-references.ps1` from inside `scripts/`.

- [ ] **Step 1: Write the script**

```powershell
<#
.SYNOPSIS
    Scans product-development/feature-index.yaml and all Markdown files for
    references to local files/paths that do not resolve on disk.
.DESCRIPTION
    Two passes:
      1. feature-index.yaml — flags any token ending in .md/.sql/.yaml (relative
         to product-development/) that does not exist.
      2. Every *.md file known to git (tracked, plus untracked-but-not-ignored)
         — flags any [text](relative/path) Markdown link (relative to the
         linking file's own directory) that does not resolve. External links
         (http/https/mailto) and anchor-only links (#foo) are ignored.
    Pass 2 is scoped via `git ls-files` rather than a recursive filesystem walk,
    so it only ever sees files this repo actually tracks (or is about to) and
    can't wander into unrelated paths elsewhere on disk.
    Exit code 0 = no broken references. Exit code 1 = one or more found.
.EXAMPLE
    powershell -File scripts/check-references.ps1
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
)

$ErrorActionPreference = 'Stop'
$broken = New-Object System.Collections.Generic.List[string]

function Test-IsExternalRef {
    param([string]$Ref)
    # http(s)/mailto/anchor-only links are external; a ref containing {...} is a
    # documented naming-pattern illustration (e.g. "../transcripts/{date}.md"),
    # not a literal path, so it's skipped too.
    return $Ref -match '^(https?://|mailto:|#)' -or $Ref -match '\{[^}]*\}'
}

function Resolve-RefPath {
    param([string]$BaseDir, [string]$Ref)
    $clean = ($Ref -split '#')[0].Trim()
    if ([string]::IsNullOrWhiteSpace($clean)) { return $null }
    $joined = Join-Path $BaseDir $clean
    try { return (Resolve-Path -LiteralPath $joined -ErrorAction Stop).Path }
    catch { return $null }
}

# Pass 1: product-development/feature-index.yaml
$featureIndex = Join-Path $RepoRoot 'product-development\feature-index.yaml'
$featureIndexDir = Join-Path $RepoRoot 'product-development'
if (Test-Path $featureIndex) {
    $lineNum = 0
    Get-Content $featureIndex | ForEach-Object {
        $lineNum++
        $line = $_
        if ($line -match '^\s*#') { return }
        $tokenMatches = [regex]::Matches($line, '[\w][\w./-]*\.(?:md|sql|yaml)')
        foreach ($tm in $tokenMatches) {
            $ref = $tm.Value
            $resolved = Resolve-RefPath -BaseDir $featureIndexDir -Ref $ref
            if (-not $resolved) {
                $broken.Add("${featureIndex}:${lineNum}: $ref")
            }
        }
    }
}

# Pass 2: every git-known Markdown file's relative links
$mdRelPaths = git -C $RepoRoot ls-files -co --exclude-standard -- '*.md'

foreach ($relPath in $mdRelPaths) {
    $fullPath = Join-Path $RepoRoot $relPath
    if (-not (Test-Path -LiteralPath $fullPath)) { continue }
    $dir = Split-Path -Parent $fullPath
    $lines = Get-Content -LiteralPath $fullPath -ErrorAction SilentlyContinue
    $inFence = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $lineNum = $i + 1
        if ($line -match '^\s*```') {
            $inFence = -not $inFence
            continue
        }
        if ($inFence) { continue }
        $linkMatches = [regex]::Matches($line, '\[[^\]]*\]\(([^)]+)\)')
        foreach ($m in $linkMatches) {
            $ref = $m.Groups[1].Value
            if (Test-IsExternalRef $ref) { continue }
            $resolved = Resolve-RefPath -BaseDir $dir -Ref $ref
            if (-not $resolved) {
                $broken.Add("${fullPath}:${lineNum}: $ref")
            }
        }
    }
}

if ($broken.Count -gt 0) {
    Write-Host "Broken references found:" -ForegroundColor Red
    $broken | Sort-Object | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    Write-Host "`n$($broken.Count) broken reference(s)." -ForegroundColor Red
    exit 1
} else {
    Write-Host "No broken references found." -ForegroundColor Green
    exit 0
}
```

- [ ] **Step 2: Run it against the repo as-is and confirm it catches the known-bad state**

Run: `powershell -File scripts/check-references.ps1`

Expected: exit code 1, with these seven `feature-index.yaml` lines among the reported broken references (do not proceed until all seven appear — if any is missing, the regex in Step 1 needs adjustment before continuing):

```
product-development\feature-index.yaml:81: product/PRDs/sso-prd.md
product-development\feature-index.yaml:82: engineering/rfcs/sso-rfc.md
product-development\feature-index.yaml:113: product/PRDs/shared-components-prd.md
product-development\feature-index.yaml:127: product/PRDs/ai-gen-v3-prd.md
product-development\feature-index.yaml:128: engineering/rfcs/gen-v3-rfc.md
product-development\feature-index.yaml:134: product/PRDs/team-workspaces-prd.md
product-development\feature-index.yaml:135: engineering/rfcs/workspaces-rfc.md
```

This is the plan's "red" state — proof the checker works, established using the repo's real, already-known-broken data rather than a synthetic fixture. Save the full output to `scratch-baseline.txt` (repo root, untracked) for comparison after Task 8.

- [ ] **Step 3: Commit**

```bash
git add scripts/check-references.ps1
git commit -m "Add broken-reference checker for feature-index.yaml and Markdown links"
```

---

## Task 2: Canonical terminology (`reference/terminology.md`)

**Files:**
- Create: `reference/terminology.md`
- Modify: `product-development/product/CLAUDE.md` (remove both terminology tables, replace with a pointer)

**Interfaces:**
- Produces: `reference/terminology.md`, linked from `product-development/product/CLAUDE.md`'s Key Documents table and (once Task 7 exists) from `reference/CLAUDE.md`.

- [ ] **Step 1: Create `reference/terminology.md`**, consolidating the two tables currently in `product-development/product/CLAUDE.md` lines 64-87 (verbatim rows, minus the GSR/TTD/PCR rows, which move to `reference/metrics.md` in Task 3):

```markdown
# Terminology

Canonical vocabulary for example_product Labs and the example_product product. Every document in this repo should link here instead of redefining these terms locally.

For metric definitions and targets (GSR, TTD, PCR, etc.), see [metrics.md](metrics.md).
For customer segment and lifecycle-stage definitions, see [segments.md](segments.md).

## example_product Labs Terminology

| Term | Definition |
|------|------------|
| example_product Pro | example_product Pro tier - always capitalized (product name) |
| example_product Teams | example_product Teams tier - always capitalized (product name) |
| example_product Enterprise | example_product Enterprise tier - always capitalized (product name) |
| Dashboard | Customer-facing project dashboard - always capitalized when referring to the product surface |

## example_product Product Terminology

| Term | Definition |
|------|------------|
| Project | A customer workspace containing generated code, configuration, and deployment settings |
| Generation | A single AI code generation event (prompt in, code out) |
| Template | A pre-built starting point for common app types (SaaS dashboard, landing page, e-commerce, etc.) |
| Preview | The live rendered output of generated code before deployment |
| Deploy | Publishing a project to production infrastructure |
| Iteration | A follow-up generation that modifies existing project code |
| Prompt | The natural language input a customer provides to generate or iterate on code |
| Competitors | Lovable, Google Stitch, v0, Replit, Figma Make, Bolt (see `../product-development/product/competitive-research/CLAUDE.md`) |
```

- [ ] **Step 2: Edit `product-development/product/CLAUDE.md`**, replacing lines 64-87 (the two terminology tables) with:

```markdown
## Terminology

Canonical term definitions, metric definitions, and segment definitions live in [reference/](../../reference/CLAUDE.md), not here — see [reference/terminology.md](../../reference/terminology.md).
```

- [ ] **Step 3: Verify the dedup and no new breakage**

Run: `Select-String -Path "product-development\product\CLAUDE.md" -Pattern "GSR|Generation Success Rate"` — expect no matches (confirms the metric rows were fully removed from this file, not just the terminology rows).

Run: `powershell -File scripts/check-references.ps1` — expect the same 7 broken references as Task 1's baseline, no more, no fewer.

- [ ] **Step 4: Commit**

```bash
git add reference/terminology.md product-development/product/CLAUDE.md
git commit -m "Extract canonical terminology into reference/terminology.md"
```

---

## Task 3: Canonical metrics (`reference/metrics.md`)

**Files:**
- Create: `reference/metrics.md`
- Modify: `product-development/analytics/CLAUDE.md` (Core Metrics table becomes a pointer)

**Interfaces:**
- Consumes: none.
- Produces: `reference/metrics.md`, the sole source of truth for GSR/TTD/PCR/etc. definitions and targets — Task 2 already removed the duplicate copy from `product/CLAUDE.md`.

- [ ] **Step 1: Create `reference/metrics.md`**, using the Core Metrics table currently at `product-development/analytics/CLAUDE.md` lines 31-41 verbatim (this table has targets; it is the more complete of the two duplicate copies, so it becomes canonical) plus the GSR/TTD/PCR one-line definitions salvaged from `product/CLAUDE.md`'s now-removed table (folded into the `Definition` column):

```markdown
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
```

- [ ] **Step 2: Edit `product-development/analytics/CLAUDE.md`**, replacing the "Core Metrics" section (lines 31-41) with:

```markdown
## Core Metrics

Canonical metric definitions and targets live in [reference/metrics.md](../../reference/metrics.md), not here.
```

- [ ] **Step 3: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect the same 7 broken references as baseline.

- [ ] **Step 4: Commit**

```bash
git add reference/metrics.md product-development/analytics/CLAUDE.md
git commit -m "Extract canonical metric definitions into reference/metrics.md"
```

---

## Task 4: Canonical segments and customer lifecycle (`reference/segments.md`)

**Files:**
- Create: `reference/segments.md`
- Modify: `product-development/product/customers/CLAUDE.md` (Segments table becomes a pointer)
- Modify: `product-development/product/workflows/bi-weekly-update/workflow-spec.md` (Customer Categorization becomes a pointer)

**Interfaces:**
- Produces: `reference/segments.md`, consolidating two vocabularies that are currently defined in two unrelated files and never cross-referenced: account segments (`customers/CLAUDE.md`) and call-synthesis lifecycle categories (`workflow-spec.md`).

- [ ] **Step 1: Create `reference/segments.md`**, using the Segments table from `product-development/product/customers/CLAUDE.md` lines 7-11 and the Customer Categorization list from `product-development/product/workflows/bi-weekly-update/workflow-spec.md` lines 49-54, verbatim:

```markdown
# Customer Segments & Lifecycle Stages

## Account Segments

| Segment | Description |
|---------|--------------|
| Enterprise | Managed accounts with complex needs (SSO, compliance, dedicated support) |
| Growth | Mid-market accounts with expansion potential |
| Self-serve | Long-tail, no individual account management |

Only named/managed accounts get a folder under `product-development/product/customers/accounts/`. Self-serve customers are tracked through aggregate analytics only.

## Customer Lifecycle Stage

Used in the bi-weekly update's call-synthesis table (see `product-development/product/workflows/bi-weekly-update/workflow-spec.md`) to categorize where a customer sits in the relationship:

| Stage | Description |
|-------|--------------|
| Paying customer | Signed and paying |
| Pilot | Active pilot, not yet paying |
| Pipeline | In pipeline, being pitched |
| Free tier | On free plan, potential upsell |
```

- [ ] **Step 2: Edit `product-development/product/customers/CLAUDE.md`**, replacing the `## Segments` section (lines 5-13) with:

```markdown
## Segments

Canonical segment and lifecycle-stage definitions live in [reference/segments.md](../../../reference/segments.md), not here.

Only named/managed accounts get folders. Self-serve customers are tracked through aggregate analytics.
```

- [ ] **Step 3: Edit `product-development/product/workflows/bi-weekly-update/workflow-spec.md`**, replacing the `### Customer Categorization` subsection (lines 49-54) with:

```markdown
### Customer Categorization

Each customer in the call synthesis table gets one of the stages defined in [reference/segments.md](../../../../reference/segments.md#customer-lifecycle-stage).
```

- [ ] **Step 4: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect the same 7 broken references as baseline (confirms the new relative links in Steps 2-3 resolve correctly; the depth-5 `../../../../../` in Step 3 is easy to get wrong — the checker will catch it if so).

- [ ] **Step 5: Commit**

```bash
git add reference/segments.md product-development/product/customers/CLAUDE.md product-development/product/workflows/bi-weekly-update/workflow-spec.md
git commit -m "Extract canonical segment and lifecycle-stage definitions into reference/segments.md"
```

---

## Task 5: Canonical status definitions (`reference/status-definitions.md`)

**Files:**
- Create: `reference/status-definitions.md`
- Modify: `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md:6` (Status field)
- Modify: `product-development/engineering/rfcs/billing/credit-usage-dashboard-rfc.md:6` (Status field)

**Interfaces:**
- Produces: `reference/status-definitions.md` — the first time this repo's existing but undefined `**Status**` field (present in every PRD/RFC/roadmap header table, e.g. `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md:6`) gets a defined value set.

The gap here is real and verified, not hypothetical: every PRD and RFC in the repo already carries a `| **Status** | Value |` row in its header table, but no file anywhere defines what values are valid — so every example artifact currently says `Draft`, including `credit-usage-dashboard`, which already has a downstream eng-plan, dashboards, and shipped experiments and should not read as a draft.

- [ ] **Step 1: Create `reference/status-definitions.md`**:

```markdown
# Status Definitions

Canonical status values for the `**Status**` field used in PRD and RFC header tables (see any file under `product-development/product/PRDs/` or `product-development/engineering/rfcs/`).

| Status | Meaning |
|--------|---------|
| Draft | Being written; not yet shared for feedback |
| In Review | Shared for feedback; open questions being resolved |
| Approved | Reviewers signed off; implementation may begin or is in progress |
| Shipped | Feature is live in production |
| Archived | Superseded, cancelled, or no longer relevant; kept for history |

Use exactly one of these five values in the `**Status**` field. Update it as the artifact's real-world state changes — do not leave it at `Draft` once work has progressed past that stage.
```

- [ ] **Step 2: Correct the two artifacts already known to be inconsistent** — `credit-usage-dashboard` has a completed eng-plan, live dashboards (`analytics/dashboards/billing/credit-usage-dashboards.md`), and a completed experiment (`analytics/experiments/billing/low-balance-warning-03-05-2026-experiment-results.md`), so its PRD and RFC should read `Shipped`, not `Draft`:

Edit `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md:6`:
```
| **Status** | Shipped |
```

Edit `product-development/engineering/rfcs/billing/credit-usage-dashboard-rfc.md:6`:
```
| **Status** | Shipped |
```

- [ ] **Step 3: Add a pointer from the two consuming folders**

Edit `product-development/product/PRDs/CLAUDE.md`, adding after the `## Purpose` section:

```markdown
Valid `**Status**` values are defined in [reference/status-definitions.md](../../../reference/status-definitions.md).
```

Edit `product-development/engineering/CLAUDE.md`, adding after the `## Folders` table:

```markdown
## Status

RFCs carry a `**Status**` field in their header table. Valid values are defined in [reference/status-definitions.md](../../../reference/status-definitions.md).
```

- [ ] **Step 4: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect the same 7 broken references as baseline.

- [ ] **Step 5: Commit**

```bash
git add reference/status-definitions.md product-development/product/PRDs/billing/credit-usage-dashboard-prd.md product-development/engineering/rfcs/billing/credit-usage-dashboard-rfc.md product-development/product/PRDs/CLAUDE.md product-development/engineering/CLAUDE.md
git commit -m "Add reference/status-definitions.md and correct credit-usage-dashboard status"
```

---

## Task 6: Canonical decision types (`reference/decision-types.md`)

**Files:**
- Create: `reference/decision-types.md`

**Interfaces:**
- Produces: `reference/decision-types.md` — establishes the taxonomy and naming convention the spec calls for (`YYYY-MM-DD-{topic}-decision.md`) so future decisions have somewhere to go. This repo has no decision-log folder or dated decision file today; this task defines the vocabulary and convention without retroactively fabricating a fake decision history (that would misrepresent the repo's real timeline).

- [ ] **Step 1: Create `reference/decision-types.md`**:

```markdown
# Decision Types

Canonical decision categories for this repo. A decision file is named `YYYY-MM-DD-{topic}-decision.md` and placed in the folder matching its type, alongside the artifacts it affects (there is no separate top-level decision archive — decisions live next to what they decided).

| Type | Where it's recorded | Example location |
|------|---------------------|-------------------|
| Product decision | `product-development/product/strategy/` or the relevant feature's PRD folder | `product-development/product/strategy/2026-04-01-q3-priorities-decision.md` |
| Technical/architecture decision | `product-development/engineering/rfcs/{product-area}/` | `product-development/engineering/rfcs/billing/2026-04-01-ledger-storage-decision.md` |
| Process decision | `product-development/product/processes/` | `product-development/product/processes/2026-04-01-prd-review-cadence-decision.md` |

A decision file should state: the question being decided, the options considered, the decision, who made it, and the date. It should link back to the PRD, RFC, or feature-index entry it affects, and forward to any decision it supersedes.

Only the decision itself is durable and belongs here — see Principle 7 (Durable vs. transient context) in `01-ai-native-product-os.md`. Working hypotheses and unapproved alternatives stay out of this pattern.
```

- [ ] **Step 2: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect the same 7 broken references as baseline (this file has no outbound links to check beyond the prose mention of `01-ai-native-product-os.md`, which is not a Markdown link and so isn't scanned — Task 14 wires that in as a real link).

- [ ] **Step 3: Commit**

```bash
git add reference/decision-types.md
git commit -m "Add reference/decision-types.md"
```

---

## Task 7: `reference/CLAUDE.md` router and root doc-index wiring

**Files:**
- Create: `reference/CLAUDE.md`
- Modify: `CLAUDE.md` (root — add a Doc Index row)

**Interfaces:**
- Consumes: `reference/terminology.md`, `reference/metrics.md`, `reference/segments.md`, `reference/status-definitions.md`, `reference/decision-types.md` (Tasks 2-6).
- Produces: the routing entry point an agent reaches from the root, per the spec's Principle 2 (progressive disclosure) — every meaningful folder needs a router, and `reference/` was the one top-level folder in the spec's recommended structure this repo was missing entirely.

- [ ] **Step 1: Create `reference/CLAUDE.md`**:

```markdown
# Reference

Canonical, single-source-of-truth definitions for example_product. Every other document in this repo should link here instead of redefining a term, metric, segment, status, or decision type locally.

## Doc Index

| File | Description |
|------|--------------|
| `terminology.md` | Product and company terminology (Project, Generation, tier names, etc.) |
| `metrics.md` | Metric definitions and targets (GSR, TTD, PCR, D7 retention, etc.) |
| `segments.md` | Customer account segments and call-synthesis lifecycle stages |
| `status-definitions.md` | Valid `**Status**` values for PRDs and RFCs |
| `decision-types.md` | Decision categories and the `YYYY-MM-DD-{topic}-decision.md` naming convention |
```

- [ ] **Step 2: Edit root `CLAUDE.md`**, adding a row to the `## Doc Index` table (insert after the `Feature index` row, before `| Product |`):

```markdown
| Reference | `reference/CLAUDE.md` | Canonical definitions — terminology, metrics, segments, statuses, decision types |
```

- [ ] **Step 3: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect the same 7 broken references as baseline.

- [ ] **Step 4: Commit**

```bash
git add reference/CLAUDE.md CLAUDE.md
git commit -m "Add reference/CLAUDE.md router and wire it into the root doc index"
```

---

## Task 8: Fix the seven dangling `feature-index.yaml` references

**Files:**
- Create: `product-development/product/PRDs/sso-prd.md`
- Create: `product-development/engineering/rfcs/sso-rfc.md`
- Create: `product-development/product/PRDs/ai-gen-v3-prd.md`
- Create: `product-development/engineering/rfcs/gen-v3-rfc.md`
- Create: `product-development/product/PRDs/team-workspaces-prd.md`
- Create: `product-development/engineering/rfcs/workspaces-rfc.md`
- Create: `product-development/product/PRDs/shared-components-prd.md`

**Interfaces:**
- Consumes: `reference/status-definitions.md` (Task 5) for the `**Status**` field value; existing facts from `product-development/product/CLAUDE.md` (Five Core Pillars — Enterprise pillar covers SSO; Collaboration pillar covers team workspaces) and `product-development/product/customers/accounts/meridian-health/` and `axiom-logistics/` (both Enterprise-segment accounts, the natural SSO requesters, per `reference/segments.md`).
- Produces: seven files that make all seven `feature-index.yaml` entries resolve. Note the paths are irregular versus the naming convention documented in `product-development/product/PRDs/CLAUDE.md` (`sso-prd.md` instead of `billing/sso-integration-prd.md`) — `feature-index.yaml` is the source of truth for the actual path, so these tasks match `feature-index.yaml` exactly rather than "fixing" the naming, which would just move the breakage to `feature-index.yaml` itself.

- [ ] **Step 1: Create `product-development/product/PRDs/sso-prd.md`**:

```markdown
# SSO Integration - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-20 |
| **Related RFC** | `engineering/rfcs/sso-rfc.md` |

---

## Overview

SSO Integration lets example_product Enterprise customers authenticate through their own identity provider (Okta, Azure AD, Google Workspace) instead of example_product-managed credentials, satisfying a hard procurement requirement for regulated-industry buyers.

## Problem Statement

Enterprise prospects in regulated industries require SSO before they will sign. Meridian Health and Crestview Financial (both Enterprise-segment, both under active evaluation) have each flagged SSO as a blocker in their security review. Without it, example_product cannot close deals that require centralized identity management and deprovisioning.

## User Stories

- As an Enterprise admin, I want to provision and deprovision example_product access through our existing identity provider, so that offboarding is instant and auditable.
- As an Enterprise security reviewer, I want SAML-based SSO, so that example_product meets our procurement security checklist.

## Requirements

- Support SAML 2.0 with Okta, Azure AD, and Google Workspace as initial providers.
- Just-in-time user provisioning on first SSO login.
- Deprovisioning via IdP-initiated logout revokes the example_product session within 5 minutes.
- SSO is an example_product Enterprise-tier-only capability.

## Design

Admin-facing SSO configuration lives under Enterprise account settings. See Figma link in `feature-index.yaml` (`billing.sso-integration.figma`).

## Technical Considerations

See `engineering/rfcs/sso-rfc.md` for the SAML implementation design.

## Launch Plan

Enterprise-tier gated rollout, starting with Meridian Health and Crestview Financial as design partners.
```

- [ ] **Step 2: Create `product-development/engineering/rfcs/sso-rfc.md`**:

```markdown
# SSO Integration - Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Riley Patel (Engineer) |
| **Status** | Draft |
| **Last Updated** | 2026-03-20 |
| **Related PRD** | `product/PRDs/sso-prd.md` |

---

## Summary

Adds SAML 2.0-based SSO for example_product Enterprise accounts, with just-in-time provisioning and IdP-initiated deprovisioning.

## Motivation

Enterprise procurement reviews at Meridian Health and Crestview Financial both list SSO as a blocking requirement. See `product/PRDs/sso-prd.md` for the full business case.

## Proposed Design

- Integrate a SAML 2.0 library on the auth service; support Okta, Azure AD, and Google Workspace as IdPs.
- On first SSO login, just-in-time provision a example_product user scoped to the Enterprise account's workspace.
- Subscribe to IdP-initiated logout webhooks where supported (Okta, Azure AD); poll session validity every 5 minutes as a fallback for providers without webhook support.

## Alternatives Considered

- OIDC instead of SAML: rejected for v1 because both target accounts' security teams specifically require SAML in their procurement checklist.

## Rollout Plan

Enterprise-tier feature flag, enabled per-account starting with Meridian Health and Crestview Financial.
```

- [ ] **Step 3: Create `product-development/product/PRDs/ai-gen-v3-prd.md`**:

```markdown
# AI Generation v3 - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-18 |
| **Related RFC** | `engineering/rfcs/gen-v3-rfc.md` |

---

## Overview

AI Generation v3 upgrades example_product's core code-generation pipeline to the next-generation model, targeting a material lift in Generation Success Rate (GSR) — see `reference/metrics.md` for the metric definition and current target (> 92%).

## Problem Statement

GSR has plateaued below target on multi-file generations involving less common framework combinations. Support tickets and the `analytics/investigations/` history show generation failures concentrated in these cases, directly suppressing Project Completion Rate (PCR).

## User Stories

- As a user generating a multi-file app, I want a higher first-try success rate, so that I spend fewer iterations recovering from broken generations.

## Requirements

- Migrate the generation pipeline to the v3 model.
- Maintain framework-detection accuracy at or above the current baseline while improving GSR.
- Ship behind a gradual rollout so GSR can be monitored per cohort before full cutover.

## Design

No user-facing UI changes; this is a backend model upgrade. See `engineering/rfcs/gen-v3-rfc.md`.

## Technical Considerations

See `engineering/rfcs/gen-v3-rfc.md` and the `table-schemas` entry in `feature-index.yaml` (`prototyping.ai-generation-v3.table-schemas`) for the generation-event schema this feature depends on.

## Launch Plan

Staged rollout by cohort, monitored against the GSR target in `reference/metrics.md`.
```

- [ ] **Step 4: Create `product-development/engineering/rfcs/gen-v3-rfc.md`**:

```markdown
# AI Generation v3 - Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Riley Patel (Engineer) |
| **Status** | Draft |
| **Last Updated** | 2026-03-18 |
| **Related PRD** | `product/PRDs/ai-gen-v3-prd.md` |

---

## Summary

Migrates the generation pipeline to the v3 model to improve Generation Success Rate (GSR) on multi-file, mixed-framework generations.

## Motivation

See `product/PRDs/ai-gen-v3-prd.md` — GSR is below target specifically on less-common framework combinations.

## Proposed Design

- Stand up the v3 model behind the existing generation-service interface so no downstream caller changes.
- Log generation outcomes to the `project-generations` table (`analytics/schemas/prototyping/project-generations.md`) with a model-version column so v2 vs v3 GSR can be compared per cohort.
- Roll out by percentage cohort, gated on GSR staying at or above the v2 baseline at each step.

## Alternatives Considered

- Full cutover without a staged rollout: rejected — insufficient signal to catch a regression before it affects all users.

## Rollout Plan

5% -> 25% -> 100% cohort rollout, each stage gated on GSR (`reference/metrics.md`) staying at or above baseline for 3 consecutive days.
```

- [ ] **Step 5: Create `product-development/product/PRDs/team-workspaces-prd.md`**:

```markdown
# Team Workspaces - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-19 |
| **Related RFC** | `engineering/rfcs/workspaces-rfc.md` |

---

## Overview

Team Workspaces gives Growth and Enterprise accounts a shared project namespace with role-based permissions, moving example_product from an individual prototyping tool toward a team-wide dev platform — directly under the "Collaboration" pillar (see `product-development/product/CLAUDE.md`, Five Core Pillars).

## Problem Statement

Acme Corp's account team (see `product-development/product/customers/accounts/acme-corp/calls/summaries/`) has already asked for manager-level review workflows over shared projects, and assigned internal owners to plan a rollout before the feature ships — a strong signal of validated demand ahead of any commitment from example_product.

## User Stories

- As a team lead, I want a shared workspace where my team's projects live, so that I don't need to track individual members' projects manually.
- As an engineering lead, I want to review my team's projects on a recurring cadence, so that I can ensure quality and catch issues early.

## Requirements

- Workspace-scoped project namespace, shared across team members.
- Role-based permissions: member, manager, admin.
- Manager review flow: a manager can mark a project "reviewed" with a timestamp.

## Design

See Figma link in `feature-index.yaml` (`prototyping.team-workspaces.figma`).

## Technical Considerations

See `engineering/rfcs/workspaces-rfc.md`.

## Launch Plan

Design-partner rollout with Acme Corp given their existing internal rollout planning.
```

- [ ] **Step 6: Create `product-development/engineering/rfcs/workspaces-rfc.md`**:

```markdown
# Team Workspaces - Engineering RFC

| Field | Value |
|-------|-------|
| **Author** | Riley Patel (Engineer) |
| **Status** | Draft |
| **Last Updated** | 2026-03-19 |
| **Related PRD** | `product/PRDs/team-workspaces-prd.md` |

---

## Summary

Introduces a workspace entity that groups projects under a team, with role-based permissions (member/manager/admin) and a manager review flag on each project.

## Motivation

See `product/PRDs/team-workspaces-prd.md`.

## Proposed Design

- New `workspace` entity owning a set of `project` records (currently owned directly by `account`).
- `workspace_membership` join table carrying a `role` enum (`member`, `manager`, `admin`).
- `project.reviewed_at` / `project.reviewed_by` columns to support the manager review flow.

## Alternatives Considered

- Reusing the existing account-level permission model instead of a new workspace entity: rejected — accounts can contain multiple teams, and permissions need to scope below the account level.

## Rollout Plan

Ship to Acme Corp as design partner first, then general availability for Growth and Enterprise tiers.
```

- [ ] **Step 7: Create `product-development/product/PRDs/shared-components-prd.md`**:

```markdown
# Component Library - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | Hannah Stulberg (PM) |
| **Status** | Draft |
| **Last Updated** | 2026-03-17 |
| **Related Plan** | `engineering/plans/prototyping/component-library.md` |

---

## Overview

A reusable component library lets users compose generated apps from a shared set of pre-built UI components instead of regenerating equivalent UI from scratch on every project, reducing generation volume and improving visual consistency across a user's projects.

## Problem Statement

Users currently regenerate near-identical UI (nav bars, auth forms, data tables) from scratch on every new project, which increases both generation cost and Time-to-Deploy (TTD) — see `reference/metrics.md` for the TTD target.

## User Stories

- As a user starting a new project, I want to pull in a pre-built component instead of prompting for one from scratch, so that I reach a working preview faster.

## Requirements

- A browsable library of common components (nav bar, auth form, data table, pricing card).
- Inserting a component from the library does not require a new generation call.
- Components respect the project's existing framework and styling.

## Design

See `engineering/plans/prototyping/component-library.md` for implementation scope.

## Technical Considerations

Depends on the same project/generation data model used elsewhere in `prototyping/` — no new schema required for v1.

## Launch Plan

Ship as an opt-in panel in the existing project editor; no gating by tier.
```

- [ ] **Step 8: Confirm all seven references now resolve**

Run: `powershell -File scripts/check-references.ps1`

Expected: exit code 0, "No broken references found." — this is the plan's "green" state for the checker built in Task 1. If any of the seven original lines still appears, re-check the file was created at the exact path `feature-index.yaml` expects (paths are relative to `product-development/`, e.g. `product/PRDs/sso-prd.md` resolves to `product-development/product/PRDs/sso-prd.md`).

- [ ] **Step 9: Commit**

```bash
git add product-development/product/PRDs/sso-prd.md product-development/engineering/rfcs/sso-rfc.md product-development/product/PRDs/ai-gen-v3-prd.md product-development/engineering/rfcs/gen-v3-rfc.md product-development/product/PRDs/team-workspaces-prd.md product-development/engineering/rfcs/workspaces-rfc.md product-development/product/PRDs/shared-components-prd.md
git commit -m "Author the 7 PRD/RFC files feature-index.yaml already pointed to"
```

---

## Task 9: Fix `.claude/commands/customer-call.md` — stale, pre-rebrand paths

**Files:**
- Modify: `.claude/commands/customer-call.md` (full rewrite of Steps 1, 2, and 5c)

**Interfaces:**
- Consumes: the actual, correct process already documented in `product-development/product/customers/CLAUDE.md` lines 40-46 ("Processing Customer Calls").

The command currently describes a "product area" (`AI Prototyping (example_product)` / `example_product Studio` / `example_product Deploy` / `example_product Analytics`) folder scheme with a `feature-requests.md` tracker file — none of which exists anywhere in the repo. The real, current process is account-based (`product-development/product/customers/accounts/{slug}/`) with feature requests logged to Linear/Jira/Asana, not a markdown tracker. This task aligns the command to reality.

- [ ] **Step 1: Replace Step 1 of `.claude/commands/customer-call.md`** (lines 16-30) with:

```markdown
## Step 1: Identify the Customer Account

Ask the user which named account this call is for, or infer it from context. Check `product-development/product/customers/CLAUDE.md` for the current list of named accounts.

If the account has no existing folder under `product-development/product/customers/accounts/`, tell the user this is a new account and confirm the segment (Enterprise / Growth / Self-serve — see `reference/segments.md`) before creating `product-development/product/customers/accounts/{slug}/`.

Base path for this account's calls: `product-development/product/customers/accounts/{slug}/calls/`
```

- [ ] **Step 2: Replace Step 2** (lines 42-54) with:

```markdown
## Step 2: Check for Existing Customer Files

**ALWAYS check both folders before creating new files:**

1. Search `product-development/product/customers/accounts/{slug}/calls/summaries/` for an existing entry covering this call's topic.
2. Search `product-development/product/customers/accounts/{slug}/calls/transcripts/` similarly.

Each call gets its own dated file in each folder (`{date}.md`), not one running file per customer — see the naming convention in `product-development/product/customers/CLAUDE.md`.

**If files for this date already exist:** confirm with the user before overwriting.
**If no files exist for this date:** create new dated files in both folders.
```

- [ ] **Step 3: Replace Step 5c** (lines 167-179) with:

```markdown
### 5c. Log Feature Requests

Feature requests are tracked in Linear / Jira / Asana, not in a repository file — see `product-development/product/customers/CLAUDE.md`, "Finding Customer Data."

For each feature request identified in Step 4, log it in Linear / Jira / Asana with the customer's account label. Do not write feature requests to a Markdown tracker file.
```

- [ ] **Step 4: Update file-path references throughout the rest of the document** — every remaining occurrence of `[product-area]/customer-calls/summaries/[CustomerName].md` and `[product-area]/customer-calls/transcripts/[CustomerName].md` (Steps 4, 5a, 5b, and the "Important Notes" section) becomes `product-development/product/customers/accounts/{slug}/calls/summaries/{date}.md` and `.../calls/transcripts/{date}.md` respectively. Search the file for `[product-area]` and `[CustomerName].md` and replace each occurrence in place, keeping the surrounding instructions (Granola handling, chunked transcript writing, anchor-link format, quality checklist) unchanged — those parts are still accurate.

- [ ] **Step 5: Verify**

Run: `Select-String -Path ".claude\commands\customer-call.md" -Pattern "product areas|feature-requests\.md|\[CustomerName\]"` — expect no matches (confirms every stale reference was replaced).

Run: `powershell -File scripts/check-references.ps1` — expect exit 0 (this file has no Markdown-link-style references, so it shouldn't change the count, but confirm nothing regressed).

- [ ] **Step 6: Commit**

```bash
git add .claude/commands/customer-call.md
git commit -m "Fix customer-call command to match the actual account-based folder structure"
```

---

## Task 10: Fix the missing `customer-call-summary` skill example

**Files:**
- Create: `.claude/skills/customer-call-summary/examples/acme-01-27-26.md`

**Interfaces:**
- Consumes: the Acme Corp narrative already established in `.claude/skills/customer-call-summary/SKILL.md` lines 152-218 (the Slack Summary worked example) and `product-development/product/customers/accounts/acme-corp/` (the real named account this example must be consistent with).
- Produces: the file `SKILL.md` already references twice (lines 10 and 279) but that does not exist — the skill is currently unusable as documented, since Step 4 of `.claude/commands/customer-call.md` instructs reading this file "for expected level of detail" before every call summary.

- [ ] **Step 1: Create `.claude/skills/customer-call-summary/examples/acme-01-27-26.md`**, building out all six sections defined in `SKILL.md`'s "Summary Structure," reusing the facts already established in `SKILL.md`'s own Slack Summary example (Derek and Priya as Acme contacts, the 5 template fast-follows, the 40% template-to-deploy conversion rate, the access-controls/team-workspaces enthusiasm, the deployment-visibility gap) so the new file is consistent with, not invented against, the existing worked example:

```markdown
# Acme Corp - Meeting Summary

## Open Action Items

### example_product Labs
| Action Item | Owner | From Meeting |
|-------------|-------|--------------|
| Ship 5 template fast-follows (versioning, metadata display, failed-generations tab, project detail link-outs, view-deployment button) | Sam, Jordan | 01/27/26 |
| Scope Access Controls + Team Workspaces manager review flow | Product | 01/27/26 |
| Bring Deployment Dashboard into example_product | Engineering | 01/27/26 |

### Acme Corp
| Action Item | Owner | From Meeting |
|-------------|-------|--------------|
| Draft internal rollout plan for Access Controls / Team Workspaces | Priya, Tom | 01/27/26 |

## Completed Action Items

### example_product Labs
| Action Item | Owner | From Meeting | Completed |
|-------------|-------|--------------|-----------|

### Acme Corp
| Action Item | Owner | From Meeting | Completed |
|-------------|-------|--------------|-----------|

---

# 01/27/26 - Bi-Weekly Check-in

**Date:** January 27, 2026
**Participants:** Derek (Acme), Priya (Acme), Tom (Acme), Hannah (example_product)
**Transcript:** [View transcript](../../../../../../product-development/product/customers/accounts/acme-corp/calls/transcripts/2026-01-27.md)

## Executive Summary

Shared project templates continue to perform well since launch, with 91 projects created from templates to date. *"We are digging it. It's off to a great start and it's something that we've been looking forward to having for so long."* - Derek

This call focused on two areas: (1) template fast-follows identified from early usage, and (2) a preview of the upcoming Access Controls and Team Workspaces feature.

**Template Fast-Follows**

Acme flagged five issues with the current template experience, all scoped into sprint planning this week: template versioning orphaning old projects, misleading "generated by example_product" metadata on hand-customized templates, no visibility into which template configs produce low-quality output, missing environment indicators on generated project cards, and no in-product way to check deploy status.

**How Acme is Using Templates & Generation Deflection**

Acme has driven strong adoption of shared templates internally, with a 40% template-to-deploy conversion rate. Derek called out template coverage across their tech stack (React/Vue/Svelte) as the biggest remaining bottleneck, alongside the CI/CD integration still in progress on Acme's side.

**Opportunity Areas**

Access Controls and Team Workspaces represent a step-change opportunity: Derek's reaction to the preview was immediate, and he's already asked for a structured weekly manager-review process built around example_product, not just basic access gating. This would shift example_product from an individual prototyping tool to a team-wide workflow within the account.

**Key Product Gaps**
- **Deployment visibility:** Priya manually checks the AWS console to confirm whether a project is already deployed before spinning up new infrastructure, risking duplicate environments. Implies example_product needs to surface deployment status directly.
- **Template quality signal:** No way for Acme to see which template configurations are producing low-quality generations, so they can't tell where to focus internal template curation.

## Insights / Learnings

### Template Adoption

Summary: Templates are seeing healthy usage, with a clear bottleneck around framework coverage.

| Insight | Details |
|---------|---------|
| **40% template-to-deploy conversion** | Acme is converting a meaningful share of template-started projects to deploys, which the team is treating as a floor, not a ceiling.<br><br>*"Biggest bottleneck to delivering greater value is template coverage across their tech stack." - Derek* |
| **CI/CD integration still WIP** | A significant portion of Acme's projects require automated testing before launch; once CI/CD integration ships, expect a material increase in production deploys.<br><br>*"There's been a noticeable decrease in the time from idea to working prototype." - Derek* |

### Access Controls & Team Workspaces Validation

Summary: This call provided strong unprompted evidence validating the Team Workspaces strategy (see `product-development/product/PRDs/team-workspaces-prd.md`).

| Insight | Details |
|---------|---------|
| **Unprompted internal rollout planning** | Derek assigned Priya and Tom to draft an internal rollout plan before the feature has even shipped, and asked for a structured weekly manager-review process, not just access gating.<br><br>*"You had me at hello, Hannah... What would really be helpful would be like if you guys created some sort of process where our engineering leads had to sign in once a week and review their team's projects and click complete." - Derek* |

## Feature Requests

### Deployment Visibility

Summary: Acme wants deployment status surfaced inside example_product instead of checking AWS directly.

| Feature | Details |
|---------|---------|
| **In-product deployment status** | Priya checks the AWS console before spinning up new environments to avoid duplicating infrastructure that's already running through example_product Teams.<br><br>*"There is a high chance that if it's a project deployed through example_product Teams, it's already running on our infrastructure. So we're not spinning up duplicate instances." - Priya* |

### Template Quality Signal

Summary: Acme wants visibility into which template configurations underperform.

| Feature | Details |
|---------|---------|
| **Failed-generations tab** | A view showing which template configs are producing low-quality output and why, so Acme's team can prioritize curation. |

## Next Steps

### Template Fast-Follows
- Fix template versioning orphaning - Sam
- Fix misleading template metadata display - Jordan
- Add failed-generations tab - Sam
- Add project detail link-outs and environment indicators - Jordan
- Add view-deployment button on generated projects - Sam

### Access Controls & Team Workspaces
- Draft internal rollout plan - Priya, Tom (Acme)
- Scope manager weekly-review flow - Product (example_product Labs)

## Follow-up Email

**To:** Derek
**Subject:** Bi-Weekly Check-in Recap + Action Items

Hi Derek,

Thanks for the great discussion today! Here's a quick recap:

**What we covered:**
- Template fast-follows from early usage (5 fixes now in sprint planning)
- Access Controls and Team Workspaces preview

**Action items for you:**
- [ ] Share internal rollout plan draft once Priya and Tom have it

**From our side:**
- [ ] Ship the 5 template fast-follows this sprint
- [ ] Scope the manager weekly-review flow for Access Controls / Team Workspaces
- [ ] Bring deployment status into the example_product project view

Let me know if I missed anything!

Best,
Hannah

## Slack Summary

Great bi-weekly sync with Acme today! Full recap here.

Project Templates
Shared templates are off to a strong start - 91 projects created from templates
since launch. Derek gave a shoutout to the team: "We are digging it. It's off
to a great start and it's something that we've been looking forward to having
for so long." Acme flagged several issues, and we broke them down in sprint
planning into five template fast follows assigned to Sam and Jordan this week.

Access Controls, Team Workspaces, and Usage Analytics will be a major value
unlock for Acme. Derek's reaction to the access permissions preview was
immediate and enthusiastic, and he's already assigned Priya and Tom to
develop an internal rollout plan before the feature even ships.

Linear issues to come for all items raised above.
```

- [ ] **Step 2: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect exit 0. This specifically checks the new file's own relative transcript link (`../../../../../../product-development/...`) resolves; if it doesn't, count the actual directory depth from `.claude/skills/customer-call-summary/examples/` to repo root (6 levels: `examples` → `customer-call-summary` → `skills` → `.claude` → repo root, i.e. 4 levels, not 6 — recompute and correct the relative path before committing) and fix the link accordingly.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/customer-call-summary/examples/acme-01-27-26.md
git commit -m "Add the worked example the customer-call-summary skill already referenced"
```

---

## Task 11: New Feature Intake workflow

**Files:**
- Create: `product-development/product/workflows/new-feature-intake/CLAUDE.md`
- Create: `product-development/product/workflows/new-feature-intake/workflow-spec.md`
- Create: `product-development/product/workflows/CLAUDE.md` (new — router for the `workflows/` folder, which previously had no index of its own)

**Interfaces:**
- Consumes: `product-development/feature-index.yaml` (the "check for existing feature/problem entries" step reads this file), `reference/status-definitions.md` and `reference/decision-types.md` (Tasks 5-6), the `/prd` command (Task 12, invoked in this workflow's final step).
- Produces: the third of the spec's three example workflows (customer interview and bi-weekly update already existed; this closes the gap), modeled on the existing `bi-weekly-update/` file pattern (`workflow-spec.md` + `CLAUDE.md`) per this repo's own established convention rather than inventing a new one.

- [ ] **Step 1: Create `product-development/product/workflows/new-feature-intake/workflow-spec.md`**, following the spec's six intake steps (Section "New feature intake" in `01-ai-native-product-os.md`) and the same automated/interactive split used by `bi-weekly-update/workflow-spec.md`:

```markdown
# New Feature Intake Workflow Spec

## Overview

This workflow takes a raw feature idea — from a customer call, an internal proposal, or a support-ticket pattern — through to either a PRD-ready intent or a documented decision not to pursue it. It runs interactively: each step has an automated part (gathering, checking) and an interactive part (PM judgment).

---

## Process Flow

```
1. Capture the problem
2. Identify supporting evidence
3. Check product-development/feature-index.yaml for an existing entry
4. Draft intent
5. Resolve constraints
6. Create PRD only after approval
```

---

## Step 1: Capture the Problem

Ask the requester (PM, or an agent processing a customer call) to state the problem in one or two sentences: who has it, what they're trying to do, and what's currently stopping them. Do not accept a solution ("build X") as the problem statement — restate it as the underlying need if necessary.

## Step 2: Identify Supporting Evidence

Gather what evidence already exists:
- Customer call summaries mentioning this problem (`product-development/product/customers/accounts/*/calls/summaries/`)
- Support ticket patterns or investigation docs (`product-development/analytics/investigations/`, `product-development/engineering/bug-investigations/`)
- Competitive pressure (`product-development/product/competitive-research/`)

If no evidence exists beyond a single request, say so explicitly rather than treating one data point as validated demand.

## Step 3: Check for an Existing Entry

Search `product-development/feature-index.yaml` for a feature that already covers this problem, by product area and by keyword. If a matching entry exists, this is not new intake — route the requester to the existing PRD/RFC/plan instead of starting a duplicate.

## Step 4: Draft Intent

Write a one-paragraph statement of intent: the problem, the evidence, and the product area it belongs to (`home-page`, `billing`, `prototyping`, `starter-templates`, or `deployment` — see `product-development/feature-index.yaml` for the current set). This is not a PRD — it's the artifact a PM reviews to decide whether a PRD is warranted.

## Step 5: Resolve Constraints

Before drafting a PRD, confirm with the PM:
- Which of the Five Core Pillars (`product-development/product/CLAUDE.md`) this serves.
- Whether it depends on unshipped work (check `product-development/feature-index.yaml` for the relevant product area).
- Rough sizing judgment — is this PRD-worthy, or small enough to go straight to an engineering plan without a PRD.

If the PM declines to proceed, record why in a decision file per `reference/decision-types.md` (type: Product decision) rather than silently dropping the idea.

## Step 6: Create PRD Only After Approval

Once the PM approves, use the `/prd` command to create the PRD in `product-development/product/PRDs/{product-area}/{feature-name}-prd.md`, and add a new entry to `product-development/feature-index.yaml` under the relevant product area with at minimum the `prd` key populated, `**Status**` set to `Draft` per `reference/status-definitions.md`.

---

## Conventions

- One feature idea per intake run — do not batch multiple unrelated ideas into one pass.
- Step 4's draft intent is disposable if the PM declines in Step 5 — it does not need to be preserved as a file unless the PM asks for a record of why it was declined (see Step 5).
- This workflow does not replace the customer-call processing workflow (`.claude/commands/customer-call.md`) — a customer call is processed first, and if it surfaces a feature request worth pursuing, that request becomes this workflow's Step 1 input.
```

- [ ] **Step 2: Create `product-development/product/workflows/new-feature-intake/CLAUDE.md`**, matching `bi-weekly-update/CLAUDE.md`'s short-overview pattern:

```markdown
# New Feature Intake Workflow

## Purpose

Takes a raw feature idea from any source (customer call, internal proposal, support pattern) through evidence-gathering and constraint-resolution to either a PRD-ready intent or a documented pass.

## What This Workflow Does

1. Captures the problem and its supporting evidence.
2. Checks `product-development/feature-index.yaml` to avoid duplicating an existing feature.
3. Drafts intent for PM review.
4. Only creates a PRD (via the `/prd` command) after PM approval.

See `workflow-spec.md` for the full step-by-step process.
```

- [ ] **Step 3: Create `product-development/product/workflows/CLAUDE.md`** (this folder previously had no router of its own — it was only described inline in `product/CLAUDE.md`'s folder-structure diagram):

```markdown
# Workflows

Executable process specs for example_product's recurring product workflows.

## Doc Index

| Workflow | Description |
|----------|--------------|
| [bi-weekly-update/](bi-weekly-update/CLAUDE.md) | Generates the bi-weekly product review document |
| [new-feature-intake/](new-feature-intake/CLAUDE.md) | Takes a raw feature idea through evidence-gathering to PRD-ready intent |
```

- [ ] **Step 4: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect exit 0.

- [ ] **Step 5: Commit**

```bash
git add product-development/product/workflows/new-feature-intake/CLAUDE.md product-development/product/workflows/new-feature-intake/workflow-spec.md product-development/product/workflows/CLAUDE.md
git commit -m "Add the New Feature Intake workflow (spec's third example workflow)"
```

---

## Task 12: `/prd` command

**Files:**
- Create: `.claude/commands/prd.md`

**Interfaces:**
- Consumes: the PRD Template Sections already documented in `product-development/product/PRDs/CLAUDE.md` (Overview, User Stories, Requirements, Design, Technical Considerations, Launch Plan).
- Produces: the command `product-development/product/PRDs/CLAUDE.md` already told readers to use ("Use the `/prd` command to create new PRDs") but that didn't exist, and the command Task 11's workflow-spec Step 6 invokes.

- [ ] **Step 1: Create `.claude/commands/prd.md`**:

```markdown
# PRD Writing

You are an expert at writing example_product Product Requirement Documents.

## Task Overview

Create a new PRD by:
1. Confirming the feature name and product area
2. Checking `product-development/feature-index.yaml` for an existing entry (do not create a duplicate PRD for a feature that already has one)
3. Gathering the required content for each template section
4. Writing the PRD file with the correct name and location
5. Updating `product-development/feature-index.yaml` with the new PRD's path

## Step 1: Confirm Feature Name and Product Area

Ask the user for the feature name and which product area it belongs to (`home-page`, `billing`, `prototyping`, `starter-templates`, or `deployment` — see `product-development/feature-index.yaml` for the current set).

## Step 2: Check for an Existing Entry

Search `product-development/feature-index.yaml` under the given product area for an existing feature with this name or a close match. If found, tell the user and offer to edit the existing PRD instead of creating a new one.

## Step 3: Gather Content

For each of the six sections defined in `product-development/product/PRDs/CLAUDE.md` ("PRD Template Sections"), ask the user for the relevant content, or draft it from context already available (feature-index entries, customer call summaries under `product-development/product/customers/accounts/`, competitive research) and confirm with the user before finalizing:

1. **Overview** - Problem statement, goals, success metrics (cite `reference/metrics.md` for any metric target referenced)
2. **User Stories** - Who benefits and how
3. **Requirements** - Functional and non-functional
4. **Design** - UX flows, wireframes (link the Figma file if one exists)
5. **Technical Considerations** - Architecture, dependencies; link the related RFC if one exists or is planned
6. **Launch Plan** - Rollout strategy, feature flags

## Step 4: Write the PRD

Use the header table format from any existing PRD (e.g. `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md`):

```markdown
# [Feature Name] - Product Requirements Document

| Field | Value |
|-------|-------|
| **Author** | [Name] (PM) |
| **Status** | Draft |
| **Last Updated** | [YYYY-MM-DD] |
| **Related RFC** | `engineering/rfcs/{product-area}/{feature-name}-rfc.md` (once it exists) |
```

`**Status**` starts at `Draft` per `reference/status-definitions.md` and should be updated as the PRD progresses.

Write the file to `product-development/product/PRDs/{product-area}/{feature-name}-prd.md`, following the naming convention in `product-development/product/PRDs/CLAUDE.md`.

## Step 5: Update the Feature Index

Add or update the entry in `product-development/feature-index.yaml` under the correct product area, setting the `prd` key to the new file's path (relative to `product-development/`).
```

- [ ] **Step 2: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect exit 0.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/prd.md
git commit -m "Add /prd command referenced by PRDs/CLAUDE.md and the new-feature-intake workflow"
```

---

## Task 13: Evaluation benchmark

**Files:**
- Create: `evaluation/CLAUDE.md`
- Create: `evaluation/task-set.md`
- Create: `evaluation/protocol.md`
- Create: `evaluation/results/.gitkeep`

**Interfaces:**
- Consumes: real, verifiable facts from across the repo (this task's entire value depends on every "expected answer" being independently checkable against a real file — an ungrounded benchmark is worse than none, since it would appear rigorous while testing nothing).
- Produces: the benchmark the spec's own "Evaluation ideas" section calls a required deliverable ("This project should include a small benchmark showing whether the context architecture actually helps").

- [ ] **Step 1: Create `evaluation/task-set.md`**, using the spec's own seven example tasks, each grounded in a real, checkable answer from this repo:

```markdown
# Evaluation Task Set

Each task has a real, verifiable expected answer and expected source file(s) in this repo, as of 2026-08-26. Run each task against an agent that has this repo in context, and record: did it reach the correct answer, did it cite the correct source, how many files did it open, and how many tokens did it consume.

## 1. Find the current definition of a metric

**Prompt:** "What is the current target for Generation Success Rate (GSR)?"
**Expected answer:** > 92%
**Expected source:** `reference/metrics.md`

## 2. Locate all artifacts related to one feature

**Prompt:** "What artifacts exist for the credit-usage-dashboard feature?"
**Expected answer:** PRD, eng RFC, eng plan, data-eng RFC, data-eng plan, Figma link, 3 tickets, 1 table schema, 1 query, 1 dashboard doc, 1 experiment result, 1 investigation, 1 bug investigation.
**Expected source:** `product-development/feature-index.yaml`, `billing.credit-usage-dashboard`

## 3. Identify the approved product decision

**Prompt:** "What is example_product's Status field convention, and what does 'Shipped' mean?"
**Expected answer:** Five defined values (Draft, In Review, Approved, Shipped, Archived); Shipped = feature is live in production.
**Expected source:** `reference/status-definitions.md`

## 4. Summarize customer evidence behind a roadmap item

**Prompt:** "What customer evidence supports building Team Workspaces?"
**Expected answer:** Acme Corp's account team requested manager-level review workflows and assigned internal owners to plan a rollout before the feature shipped.
**Expected source:** `product-development/product/PRDs/team-workspaces-prd.md`, `product-development/product/customers/accounts/acme-corp/`

## 5. Find the latest experiment result

**Prompt:** "What was the result of the low-balance-warning experiment?"
**Expected answer:** A 22% reduction in churn-from-depletion (cited in the credit-usage-dashboard PRD's Business Opportunity section).
**Expected source:** `product-development/analytics/experiments/billing/low-balance-warning-03-05-2026-experiment-results.md`, cross-referenced from `product-development/product/PRDs/billing/credit-usage-dashboard-prd.md`

## 6. Identify conflicting or outdated context

**Prompt:** "Is there any inconsistency in how customer segments are defined across this repo?"
**Expected answer:** Before this plan's Task 4, segments were defined independently in `product-development/product/customers/CLAUDE.md` and customer-lifecycle categories in `product-development/product/workflows/bi-weekly-update/workflow-spec.md`, with no cross-reference. After Task 4, both point to `reference/segments.md`.
**Expected source:** `reference/segments.md`

## 7. Generate a bi-weekly product update

**Prompt:** "Generate this cycle's bi-weekly product update."
**Expected answer:** A document following the structure in `product-development/product/workflows/bi-weekly-update/workflow-spec.md`, written to `product-development/product/meetings/team-bi-weekly/docs/`.
**Expected source:** `product-development/product/workflows/bi-weekly-update/workflow-spec.md`, `product-development/product/workflows/bi-weekly-update/reference/2026-02-11.md` (canonical good output)
```

- [ ] **Step 2: Create `evaluation/protocol.md`**:

```markdown
# Evaluation Protocol

## Method

Run each task in `task-set.md` twice against a fresh agent session with no prior conversation context:

1. **Baseline** — agent receives the repo with all `CLAUDE.md` router files, `reference/`, and `feature-index.yaml` removed (or ignored), so it must search the raw content tree unassisted.
2. **Product OS** — agent receives the repo as-is, and is told to start from the root `CLAUDE.md`.

## Metrics to Record

| Metric | How to measure |
|--------|-----------------|
| Task completion accuracy | Does the answer match `task-set.md`'s expected answer? |
| Wrong-source rate | Did the agent cite a file other than the expected source, or an outdated/duplicate definition? |
| Context tokens consumed | Total tokens read across the session for this task |
| Files opened | Count of distinct files the agent read |
| Time to answer | Wall-clock time from prompt to final answer |
| Citation accuracy | Does the agent's answer include a correct file path citation? |

## Reporting

Record one row per task per condition (baseline / Product OS) in `evaluation/results/YYYY-MM-DD-run.md` (create this file per run; the folder starts empty — see `results/.gitkeep`). Summarize aggregate deltas (accuracy, files opened, tokens) between conditions at the top of each run's file.
```

- [ ] **Step 3: Create `evaluation/CLAUDE.md`**:

```markdown
# Evaluation

A small benchmark demonstrating whether this repo's context architecture measurably helps an agent answer real product questions, versus an unstructured baseline.

## Doc Index

| File | Description |
|------|--------------|
| `task-set.md` | Seven grounded tasks, each with a verifiable expected answer and source file |
| `protocol.md` | Baseline-vs-Product-OS methodology and the metrics to record |
| `results/` | Dated run outputs (starts empty) |
```

- [ ] **Step 4: Create `evaluation/results/.gitkeep`** (empty file, matching the existing pattern at `team/retros/.gitkeep` and `product-development/product/workflows/bi-weekly-update/output/.gitkeep`).

- [ ] **Step 5: Verify**

Run: `powershell -File scripts/check-references.ps1` — expect exit 0.

- [ ] **Step 6: Commit**

```bash
git add evaluation/
git commit -m "Add evaluation benchmark (task set, protocol, results folder)"
```

---

## Task 14: Final wiring and full-repo verification

**Files:**
- Modify: `CLAUDE.md` (root — add an Evaluation row to the Doc Index; add `reference/decision-types.md`'s naming convention note)
- Create: `01-ai-native-product-os.md` → copy into `reference/01-ai-native-product-os.md` (the spec becomes part of the reference layer it inspired, so it's discoverable in-repo, not only in conversation history)

**Interfaces:**
- Consumes: every file created in Tasks 1-13.
- Produces: the fully wired root doc index, and the final proof — one checker run across the whole, completed change set.

- [ ] **Step 1: Copy the spec into the repo**

Write the full contents of `01-ai-native-product-os.md` (the document provided in this conversation) to `reference/01-ai-native-product-os.md`, unmodified.

- [ ] **Step 2: Edit root `CLAUDE.md`**, adding a row to the `## Doc Index` table (insert after the `Team` row):

```markdown
| Evaluation | `evaluation/CLAUDE.md` | Benchmark tasks + protocol for measuring whether the context architecture helps agents |
```

- [ ] **Step 3: Edit `reference/CLAUDE.md`** (from Task 7), adding a row for the newly-copied spec:

```markdown
| `01-ai-native-product-os.md` | The architecture spec this repo implements — the source of truth for *why* the repo is structured this way |
```

- [ ] **Step 4: Run the full verification**

Run: `powershell -File scripts/check-references.ps1`

Expected: exit code 0, "No broken references found." This is the final proof that every gap opened by this plan's own new content (Tasks 2-13) resolves correctly, and that the seven originally-broken `feature-index.yaml` references from Task 1's baseline are still fixed.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md reference/CLAUDE.md reference/01-ai-native-product-os.md
git commit -m "Wire reference/ and evaluation/ into the root doc index; add spec as reference/01-ai-native-product-os.md"
```

---

## Self-Review Notes

**Spec coverage:**
- Principle 2 (progressive disclosure) — Tasks 7, 11 (new `reference/CLAUDE.md`, `workflows/CLAUDE.md` routers).
- Principle 5 (shared vocabulary defined once) — Tasks 2-7 (the core gap; this was the spec's most-violated principle in the current repo, since terminology/metrics were duplicated, not centralized).
- Principle 6 (provenance) — no changes needed; already correctly implemented (verified in the initial repo survey), so no task touches it.
- Principle 7 (durable vs. transient) — Task 6 (`decision-types.md` explicitly cites this principle).
- "New feature intake" workflow — Task 11.
- "Evaluation ideas" section — Task 13.
- "Suggested future extensions" → "automated broken-link checks" — Task 1.
- Naming conventions (`YYYY-MM-DD-{topic}-decision.md`) — Task 6.

**Not in scope, and why:** stale-context detection, conflict detection across decisions, and agent-generated decision summaries (also listed under "Suggested future extensions") are explicitly framed by the spec as *future* extensions, not core requirements — building them now would be scope creep beyond what the spec's core principles and "Avoid" section call for. The broken-link checker (Task 1) is the one future extension promoted into this plan because it was the only one with a concrete, already-verified failure mode (7 real dangling references) to fix.
