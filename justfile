set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the SOTA Industrial Dashboard
default:
    @$lines = Get-Content '{{justfile()}}'; \
    Write-Host ' [SOTA] PyWinAuto MCP Industrial Dashboard v1.4.2' -ForegroundColor White -BackgroundColor Cyan; \
    Write-Host '' ; \
    $currentCategory = ''; \
    foreach ($line in $lines) { \
        if ($line -match '^# ── ([^─]+) ─') { \
            $currentCategory = $matches[1].Trim(); \
            Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
            Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
        } elseif ($line -match '^# ([^─].+)') { \
            $desc = $matches[1].Trim(); \
            $idx = [array]::IndexOf($lines, $line); \
            if ($idx -lt $lines.Count - 1) { \
                $nextLine = $lines[$idx + 1]; \
                if ($nextLine -match '^([a-z0-9-]+):') { \
                    $recipe = $matches[1]; \
                    $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                    Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
                    Write-Host "$pad$desc" -ForegroundColor Gray; \
                } \
            } \
        } \
    } \
    Write-Host "`n  [System State: PROD/INDUSTRIAL]" -ForegroundColor DarkGray; \
    Write-Host ''

# ── Operations ────────────────────────────────────────────────────────────────

# Initialize environment and synchronize dependencies
install:
    uv sync

# Start the full orchestration (Vite + FastAPI)
start:
    pwsh -File .\start.ps1

# Start backend in development mode (reload enabled)
dev:
    $env:PYTHONPATH = "src"; uv run uvicorn pywinauto_mcp.server:app --reload --port 10789

# Launch Microsoft Paint and draw a SOTA Landscape Masterpiece directly via tool calls
paint-demo:
    @$env:PYWINAUTO_MCP_BYPASS_HITL = "1"; \
    Write-Host "🎨 Starting Industrial Paint Demo (Justfile/PowerShell Orchestrated)" -ForegroundColor Cyan; \
    Start-Process "mspaint.exe"; \
    Start-Sleep -Seconds 3; \
    Write-Host "[INIT] Locating Paint window..." -ForegroundColor Gray; \
    $win = uv run -q python -c "import json; from pywinauto_mcp.tools.portmanteau_windows import automation_windows; print(json.dumps(automation_windows('find', class_name='MSPaintApp')))" | ConvertFrom-Json; \
    if (-not $win.success) { Write-Host "[ERROR] Paint not found" -ForegroundColor Red; exit 1 }; \
    $handle = $win.windows[0].handle; \
    Write-Host "[INIT] Maximizing Paint (HWND: $handle)..." -ForegroundColor Gray; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_windows import automation_windows; automation_windows('maximize', handle=$handle)"; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_windows import automation_windows; automation_windows('activate', handle=$handle)"; \
    Write-Host "[INIT] Discovering Canvas element..." -ForegroundColor Gray; \
    $canvas = uv run -q python -c "import json; from pywinauto_mcp.tools.portmanteau_elements import automation_elements; print(json.dumps(automation_elements('rect', window_handle=$handle, auto_id='image')))" | ConvertFrom-Json; \
    if (-not $canvas.success) { \
        Write-Host "[WARN] Canvas ID 'image' not found, searching by type..." -ForegroundColor Yellow; \
        $canvas = uv run -q python -c "import json; from pywinauto_mcp.tools.portmanteau_elements import automation_elements; print(json.dumps(automation_elements('rect', window_handle=$handle, control_type='Image')))" | ConvertFrom-Json; \
    }; \
    if (-not $canvas.success) { Write-Host "[ERROR] Could not find canvas" -ForegroundColor Red; exit 1 }; \
    $cx = $canvas.left; $cy = $canvas.top; $cw = $canvas.width; $ch = $canvas.height; \
    Write-Host "[DRAW] Drawing Meadow (Green)..." -ForegroundColor Green; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_elements import automation_elements; automation_elements('click', window_handle=$handle, title='Green', exact_match=False)"; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_mouse import automation_mouse; automation_mouse('drag', x=$($cx+10), y=$($cy+$ch-100), x2=$($cx+$cw-10), y2=$($cy+$ch-100), duration=1.5)"; \
    Write-Host "[DRAW] Drawing Sky (Blue)..." -ForegroundColor Blue; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_elements import automation_elements; automation_elements('click', window_handle=$handle, title='Blue', exact_match=False)"; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_mouse import automation_mouse; automation_mouse('drag', x=$($cx+10), y=$($cy+100), x2=$($cx+$cw-10), y2=$($cy+100), duration=1.5)"; \
    Write-Host "[DRAW] Drawing Sun (Red)..." -ForegroundColor Red; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_elements import automation_elements; automation_elements('click', window_handle=$handle, title='Red', exact_match=False)"; \
    $sx = $cx + $cw - 150; $sy = $cy + 150; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_mouse import automation_mouse; automation_mouse('drag', x=$sx, y=$sy, x2=$($sx+50), y2=$($sy+50), duration=0.5)"; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_mouse import automation_mouse; automation_mouse('drag', x=$($sx+50), y=$($sy+50), x2=$sx, y2=$($sy+100), duration=0.5)"; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_mouse import automation_mouse; automation_mouse('drag', x=$sx, y=$($sy+100), x2=$($sx-50), y2=$($sy+50), duration=0.5)"; \
    uv run -q python -c "from pywinauto_mcp.tools.portmanteau_mouse import automation_mouse; automation_mouse('drag', x=$($sx-50), y=$($sy+50), x2=$sx, y2=$sy, duration=0.5)"; \
    Write-Host "✅ Industrial Painting Complete!" -ForegroundColor Cyan

# Launch Notepad and render SOTA ASCII Art
text-demo:
    @echo "📝 Executing Text ASCII Demo (HITL Bypassed)..."
    $env:PYWINAUTO_MCP_BYPASS_HITL = "1"; uv run python scripts/text_demo.py

# ── Demos (examples/*.py) ─────────────────────────────────────────────────────

# Run Python example demos in sequence: mouse dance, nine Notepads in a 3x3 grid, typewriter
demo:
    @Write-Host "[1/3] Mouse dance..." -ForegroundColor Cyan
    uv run python examples/demo_mouse_dance.py --seconds 8
    @Write-Host "[2/3] Notepad 3x3 grid..." -ForegroundColor Cyan
    uv run python examples/demo_notepad_grid.py --auto --dwell 5
    @Write-Host "[3/3] Notepad typewriter..." -ForegroundColor Cyan
    uv run python examples/demo_notepad_typewriter.py
    @Write-Host "All demos finished." -ForegroundColor Green

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute full test suite with coverage
test:
    uv run pytest --cov=src --cov-report=term-missing

# Execute Ruff SOTA v13.1 linting
lint:
    uv run ruff check .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .

# Format code with ruff
format:
    uv run ruff format .

# Type check code
type-check:
    uv run mypy src

# Run all quality checks and tests
check: lint format type-check test

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    uv run safety check

# ── Maintenance ───────────────────────────────────────────────────────────────

# Remove build artifacts and temporary files
clean:
    if (Test-Path "dist") { Remove-Item -Recurse -Force dist }
    if (Test-Path "build") { Remove-Item -Recurse -Force build }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force htmlcov }
    if (Test-Path ".coverage") { Remove-Item .coverage }
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force .pytest_cache }
    if (Test-Path "src/pywinauto_mcp.egg-info") { Remove-Item -Recurse -Force src/pywinauto_mcp.egg-info }
    Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
