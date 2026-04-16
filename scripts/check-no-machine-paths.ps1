#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Find machine-specific absolute paths (fixed drive + Dev\repos-style trees) that break on other PCs.

.DESCRIPTION
    Scans text files for patterns like Windows drive + Dev\repos, and file:/// URIs with drive letters.
    Default scope is strict: src/ and a few repo-root files. Use -FullRepo to scan the whole tree
    (expect many hits under docs/ until those are cleaned or excluded).

.PARAMETER FullRepo
    Scan all *.md, *.py, *.ps1, *.json, *.toml, *.yaml, *.yml, .cursorrules under the repo (minus excluded dirs).

.PARAMETER NoFail
    Print matches but exit 0 (useful while fixing legacy docs).

.EXAMPLE
    .\scripts\check-no-machine-paths.ps1
    # Strict scan; exit 1 if any match

.EXAMPLE
    .\scripts\check-no-machine-paths.ps1 -FullRepo -NoFail
    # See everything without failing the pipeline
#>

param(
    [switch]$FullRepo,
    [switch]$NoFail
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

Set-Location $repoRoot

$excludeDirPattern = '(\\|/)(\.git|node_modules|htmlcov|dist|build|__pycache__|\.venv|\.pytest_cache)(\\|/|$)'

function Test-ExcludedPath([string]$fullPath) {
    return $fullPath -match $excludeDirPattern
}

# Patterns: developer drive layouts and file:// with drive letter (portable clones should use env or placeholders).
$patterns = @(
    @{ Name = 'Drive Dev\repos style'; Regex = '[A-Za-z]:[/\\][Dd]ev[/\\][Rr]epos' }
    @{ Name = 'file URI with drive'; Regex = 'file:///[a-zA-Z]:/' }
)

$hits = [System.Collections.Generic.List[object]]::new()

function Add-Hit($relPath, $lineNum, $line) {
    $hits.Add([pscustomobject]@{ Path = $relPath; Line = $lineNum; Text = $line.TrimEnd() })
}

function Search-FileMachinePathPatterns($fullPath) {
    if (Test-ExcludedPath $fullPath) { return }
    $rel = $fullPath.Substring($repoRoot.Path.Length).TrimStart('\', '/')
    $n = 0
    foreach ($raw in [System.IO.File]::ReadLines($fullPath)) {
        $n++
        foreach ($p in $patterns) {
            if ($raw -match $p.Regex) {
                Add-Hit $rel $n $raw
                break
            }
        }
    }
}

if ($FullRepo) {
    $ext = @('*.md', '*.py', '*.ps1', '*.json', '*.toml', '*.yaml', '*.yml')
    foreach ($g in $ext) {
        Get-ChildItem -Path $repoRoot -Recurse -File -Filter $g -ErrorAction SilentlyContinue | ForEach-Object {
            if (-not (Test-ExcludedPath $_.FullName)) { Search-FileMachinePathPatterns $_.FullName }
        }
    }
    if (Test-Path (Join-Path $repoRoot '.cursorrules')) {
        Search-FileMachinePathPatterns (Join-Path $repoRoot '.cursorrules')
    }
}
else {
    # Strict: implementation + common copy-paste surfaces
    $rootFiles = @(
        'README.md', 'llms.txt', 'glama.json', 'pyproject.toml', 'mcpb.json',
        'AGENT_PROTOCOLS.md', 'CONTRIBUTING.md'
    )
    foreach ($f in $rootFiles) {
        $p = Join-Path $repoRoot $f
        if (Test-Path $p) { Search-FileMachinePathPatterns $p }
    }
    $src = Join-Path $repoRoot 'src'
    if (Test-Path $src) {
        Get-ChildItem -Path $src -Recurse -File -Filter *.py | ForEach-Object { Search-FileMachinePathPatterns $_.FullName }
    }
    Get-ChildItem -Path (Join-Path $repoRoot 'scripts') -File -Filter *.ps1 -ErrorAction SilentlyContinue |
        ForEach-Object { Search-FileMachinePathPatterns $_.FullName }
}

if ($hits.Count -eq 0) {
    Write-Host "OK: no machine-specific path patterns in scanned files." -ForegroundColor Green
    exit 0
}

Write-Host "Found $($hits.Count) line(s) matching machine-path patterns:" -ForegroundColor Yellow
$hits | ForEach-Object {
    Write-Host "$($_.Path):$($_.Line): $($_.Text)" -ForegroundColor Gray
}
if (-not $NoFail) {
    exit 1
}
exit 0
