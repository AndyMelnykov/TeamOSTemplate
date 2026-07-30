<#
.SYNOPSIS
    Replace the product name "Forge" with a placeholder across every text file in the repo.

.DESCRIPTION
    Runs a case-aware find/replace over all tracked text files, skipping .git and binary
    assets. Dry-run by default: it reports what WOULD change and writes nothing until you
    pass -Apply.

    Case handling (see $Replacements): "Forge" and "forge" both become "example_product",
    while "FORGE" becomes "EXAMPLE_PRODUCT" so uppercase ticket IDs (FORGE-1042) keep their
    shape. Pass -Uniform to force a single literal target for all three forms instead.

    File renames (-RenameFiles) are consistent with the content pass: rewriting "forge" to
    "example_product" inside documents also rewrites the paths that link to the renamed
    files, so cross-references survive.

.PARAMETER Apply
    Actually write changes. Without this, the script only reports.

.PARAMETER RenameFiles
    Also rename files/directories whose names contain "forge" (uses `git mv` when available
    so history follows the rename).

.PARAMETER Uniform
    Replace all case variants with -To verbatim, ignoring the case-aware mapping.

.PARAMETER From
    The product name to replace. Default "Forge".

.PARAMETER To
    The replacement. Default "example_product".

.PARAMETER Root
    Repo root to operate on. Defaults to the parent of this script's directory.

.EXAMPLE
    .\scripts\replace-product-name.ps1
    Dry run. Prints per-file counts and a total.

.EXAMPLE
    .\scripts\replace-product-name.ps1 -Apply -RenameFiles
    Rewrite file contents and rename the four forge-* files.

.EXAMPLE
    .\scripts\replace-product-name.ps1 -To "acme" -Apply
    Use a different placeholder.
#>

[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$RenameFiles,
    [switch]$Uniform,
    [string]$From = 'Forge',
    [string]$To   = 'example_product',
    [string]$Root
)

$ErrorActionPreference = 'Stop'

if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }
$Root = (Resolve-Path $Root).Path

# --- What gets replaced, in order. Longest/most-specific first. ---------------
# No cascade risk: none of the target strings contain the source strings.
if ($Uniform) {
    $Replacements = @(
        @{ Find = $From.ToUpper();   Replace = $To }
        @{ Find = $From;             Replace = $To }
        @{ Find = $From.ToLower();   Replace = $To }
    )
} else {
    $Replacements = @(
        @{ Find = $From.ToUpper();   Replace = $To.ToUpper() }   # FORGE-1042 -> EXAMPLE_PRODUCT-1042
        @{ Find = $From;             Replace = $To }             # Forge      -> example_product
        @{ Find = $From.ToLower();   Replace = $To }             # forge-app  -> example_product-app
    )
}
# De-dupe in case From is already single-case (e.g. -From FORGE makes all three identical).
# Must be an Ordinal comparison - Group-Object would fold Forge/forge/FORGE together.
$seen = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
$Replacements = @($Replacements | Where-Object { $seen.Add($_.Find) })

# --- Exclusions --------------------------------------------------------------
$ExcludedDirs = @('.git', 'node_modules', '.venv', 'dist', 'build')
$BinaryExt = @(
    '.png','.jpg','.jpeg','.gif','.webp','.ico','.svgz','.pdf','.zip','.gz','.tar',
    '.woff','.woff2','.ttf','.otf','.eot','.mp4','.mov','.mp3','.wav','.xlsx','.docx','.pptx',
    '.pen'   # encrypted Pencil design files - never touch as text
)

function Test-IsBinary {
    <# NUL byte in the first 8 KB is a reliable enough text/binary sniff. #>
    param([string]$Path)
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $buffer = New-Object byte[] 8192
        $read = $stream.Read($buffer, 0, $buffer.Length)
        for ($i = 0; $i -lt $read; $i++) { if ($buffer[$i] -eq 0) { return $true } }
        return $false
    } finally { $stream.Dispose() }
}

function Convert-Text {
    <#
      Applies every replacement in order; returns the new string plus per-pattern hit counts.
      Counts are an ordered ARRAY, not a hashtable: PowerShell hashtables are case-insensitive,
      which would fold Forge/forge/FORGE into a single key and undercount the total.
    #>
    param([string]$Text)
    $counts = New-Object System.Collections.ArrayList
    $result = $Text
    foreach ($r in $Replacements) {
        # Case-sensitive, literal (Ordinal) matching - not regex, not culture-aware.
        $hits = 0
        $idx = 0
        while (($idx = $result.IndexOf($r.Find, $idx, [System.StringComparison]::Ordinal)) -ge 0) {
            $hits++
            $idx += $r.Find.Length
        }
        if ($hits -gt 0) {
            [void]$counts.Add([pscustomobject]@{ Find = $r.Find; Hits = $hits })
            $result = $result.Replace($r.Find, $r.Replace)
        }
    }
    return [pscustomobject]@{ Text = $result; Counts = $counts }
}

$mode = if ($Apply) { 'APPLY' } else { 'DRY RUN' }
Write-Host ""
Write-Host "  $mode  -  '$From' -> '$To'" -ForegroundColor Cyan
Write-Host "  root: $Root"
Write-Host "  map:  $(($Replacements | ForEach-Object { "$($_.Find) -> $($_.Replace)" }) -join '  |  ')"
Write-Host ""

# --- Pass 1: file contents ---------------------------------------------------
$files = Get-ChildItem -Path $Root -Recurse -File -Force | Where-Object {
    $relative = $_.FullName.Substring($Root.Length).TrimStart('\', '/')
    $parts = $relative -split '[\\/]'
    -not ($parts | Where-Object { $ExcludedDirs -contains $_ }) -and
    ($BinaryExt -notcontains $_.Extension.ToLower()) -and
    # Skip this script: its own comments and default values contain the search strings.
    ($_.FullName -ne $PSCommandPath)
}

$changedFiles = 0
$totalHits = 0
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

foreach ($file in $files) {
    if (Test-IsBinary $file.FullName) { continue }

    # ReadAllText/WriteAllText preserve existing CRLF vs LF line endings verbatim.
    $original = [System.IO.File]::ReadAllText($file.FullName)
    $converted = Convert-Text $original
    if ($converted.Text -eq $original) { continue }

    $fileHits = ($converted.Counts | Measure-Object -Property Hits -Sum).Sum
    $changedFiles++
    $totalHits += $fileHits

    $relative = $file.FullName.Substring($Root.Length).TrimStart('\', '/')
    $detail = ($converted.Counts | ForEach-Object { "$($_.Find)x$($_.Hits)" }) -join ' '
    Write-Host ("  {0,5}  {1,-70} {2}" -f $fileHits, $relative, $detail)

    if ($Apply) { [System.IO.File]::WriteAllText($file.FullName, $converted.Text, $utf8NoBom) }
}

# --- Pass 2: file and directory names (opt-in) -------------------------------
$renamed = 0
if ($RenameFiles) {
    Write-Host ""
    Write-Host "  Renames:" -ForegroundColor Cyan

    $useGit = $false
    try { git -C $Root rev-parse --is-inside-work-tree | Out-Null; $useGit = $? } catch { $useGit = $false }

    # Deepest paths first so renaming a parent directory can't invalidate a queued child path.
    $targets = Get-ChildItem -Path $Root -Recurse -Force |
        Where-Object {
            $relative = $_.FullName.Substring($Root.Length).TrimStart('\', '/')
            $parts = $relative -split '[\\/]'
            -not ($parts | Where-Object { $ExcludedDirs -contains $_ })
        } |
        Where-Object { (Convert-Text $_.Name).Text -ne $_.Name } |
        Sort-Object { ($_.FullName -split '[\\/]').Count } -Descending

    if (-not $targets) { Write-Host "    (none)" }

    foreach ($item in $targets) {
        $newName = (Convert-Text $item.Name).Text
        $newPath = Join-Path $item.Directory.FullName $newName
        $relative = $item.FullName.Substring($Root.Length).TrimStart('\', '/')
        Write-Host ("    {0}  ->  {1}" -f $relative, $newName)
        $renamed++

        if ($Apply) {
            if (Test-Path -LiteralPath $newPath) { throw "Target already exists: $newPath" }
            if ($useGit) {
                git -C $Root mv --  $item.FullName $newPath
                if ($LASTEXITCODE -ne 0) { throw "git mv failed for $relative" }
            } else {
                Move-Item -LiteralPath $item.FullName -Destination $newPath
            }
        }
    }
}

# --- Summary -----------------------------------------------------------------
Write-Host ""
Write-Host "  $totalHits replacements across $changedFiles files$(if ($RenameFiles) { ", $renamed renames" })" -ForegroundColor Green
if (-not $Apply) {
    Write-Host "  Nothing written. Re-run with -Apply$(if ($RenameFiles) { ' -RenameFiles' }) to commit the changes." -ForegroundColor Yellow
}
Write-Host ""
