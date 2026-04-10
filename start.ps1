# root start.ps1: Orchestrate PyWinAuto MCP Frontend (10788) and Backend (10789)
$WebPort = 10788
$BackendPort = 10789
$PSScriptRoot = Get-Location

# 1. Kill any process squatting on the ports (Atomic Loop)
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
for ($i=0; $i -lt 3; $i++) {
    $pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
    if (-not $pids) { break }
    foreach ($p in $pids) {
        Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
        try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
    }
    Start-Sleep -Seconds 1 # Give OS time to release sockets
}

# 2. Setup
Write-Host "Synchronizing dependencies..." -ForegroundColor Cyan
uv sync

if (-not (Test-Path "web_sota/node_modules")) { 
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Set-Location "web_sota"
    npm install
    Set-Location ..
}

# 3. Start the Python backend (Background)
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan

# Set PYTHONPATH explicitly for the child process
$backendCmd = "`$env:PYTHONPATH = 'src'; uv run uvicorn pywinauto_mcp.server:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $backendCmd -WorkingDirectory $PSScriptRoot -WindowStyle Normal

# Staggered startup: Give uvicorn a moment to bind its socket before Vite starts its proxy
Start-Sleep -Seconds 2

# 4. Start the Frontend (Vite dev)
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green

# 4b. Launch background task to open browser once frontend is ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process pwsh -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen -WorkingDirectory $PSScriptRoot

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
Set-Location "web_sota"
npm run dev -- --port $WebPort --host 127.0.0.1
