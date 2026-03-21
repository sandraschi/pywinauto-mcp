# Build MCPB Package Script for PyWinAuto MCP
# Builds the MCPB package for distribution

param(
    [switch]$NoSign,
    [string]$OutputDir = "dist"
)

$ErrorActionPreference = "Stop"

Write-Host "Building PyWinAuto MCP MCPB Package..." -ForegroundColor Cyan

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "  Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Node.js not found. Please install Node.js." -ForegroundColor Red
    exit 1
}

# Check MCPB CLI
try {
    $mcpbVersion = mcpb --version
    Write-Host "  MCPB CLI: $mcpbVersion" -ForegroundColor Green
} catch {
    Write-Host "  Installing MCPB CLI..." -ForegroundColor Yellow
    npm install -g @anthropic-ai/mcpb
    $mcpbVersion = mcpb --version
    Write-Host "  MCPB CLI installed: $mcpbVersion" -ForegroundColor Green
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.10+." -ForegroundColor Red
    exit 1
}

# Validate manifest
Write-Host "`nValidating manifest.json..." -ForegroundColor Yellow
try {
    mcpb validate manifest.json
    Write-Host "  Manifest validation passed" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Manifest validation failed" -ForegroundColor Red
    exit 1
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "  Created output directory: $OutputDir" -ForegroundColor Green
}

# Build package
Write-Host "`nBuilding MCPB package..." -ForegroundColor Yellow
try {
    if ($NoSign) {
        mcpb pack --output $OutputDir
    } else {
        mcpb pack --output $OutputDir
    }
    Write-Host "  Package built successfully" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Package build failed" -ForegroundColor Red
    exit 1
}

# Find the built package
$packageFile = Get-ChildItem -Path $OutputDir -Filter "*.mcpb" | Select-Object -First 1
if ($packageFile) {
    $packageSize = [math]::Round($packageFile.Length / 1MB, 2)
    Write-Host "`nPackage Details:" -ForegroundColor Cyan
    Write-Host "  File: $($packageFile.Name)" -ForegroundColor White
    Write-Host "  Size: $packageSize MB" -ForegroundColor White
    Write-Host "  Path: $($packageFile.FullName)" -ForegroundColor White
    Write-Host "`nBuild completed successfully!" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Could not find built package file" -ForegroundColor Yellow
}

