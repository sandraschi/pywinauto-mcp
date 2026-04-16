# root start.ps1: Orchestrate PyWinAuto MCP Frontend (10788) and Backend (10789)
$WebPort = 10788
$BackendPort = 10789
# Do not overwrite $PSScriptRoot — use repo directory (works when cwd is not the repo)
$RepoRoot = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }

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

$WebSota = Join-Path $RepoRoot "web_sota"
if (-not (Test-Path (Join-Path $WebSota "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Push-Location $WebSota
    npm install
    Pop-Location
}

# 3. Start the Python backend (Background)
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan

# Set PYTHONPATH explicitly for the child process
$backendCmd = "`$env:PYTHONPATH = 'src'; Set-Location '$RepoRoot'; uv run uvicorn pywinauto_mcp.server:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $backendCmd -WorkingDirectory $RepoRoot -WindowStyle Normal

# Wait until API accepts connections (uv sync / first import can exceed a fixed sleep)
$healthUrl = "http://127.0.0.1:$BackendPort/api/v1/health"
$ready = $false
for ($i = 0; $i -lt 90; $i++) {
    try {
        $null = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Write-Host "Backend did not respond at $healthUrl within 90s. Check the uvicorn window for import errors." -ForegroundColor Red
    exit 1
}
Write-Host "Backend is ready." -ForegroundColor Green

# 4. Start the Frontend (Vite dev)
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green

# 4b. Launch background task to open browser once frontend is ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process pwsh -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen -WorkingDirectory $RepoRoot

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
Push-Location $WebSota
npm run dev -- --port $WebPort --host 127.0.0.1
