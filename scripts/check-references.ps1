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
    [string]$RepoRoot
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    $toplevel = & git -C $scriptDir rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0 -and $toplevel) {
        $RepoRoot = ($toplevel -replace '/', '\')
    } else {
        $RepoRoot = (Get-Location).Path
    }
}

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
$mdRelPaths = & git -C $RepoRoot ls-files -co --exclude-standard -- '*.md'

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
