# PyWinAuto MCP

**Let an AI assistant control real Windows apps** — through a single MCP server that wraps window, UI, mouse, keyboard, screenshots, OCR, and optional face checks behind a small set of **portmanteau** tools (many operations, few entry points so models stay focused).

**Stack:** v0.3.2 · FastMCP 3.1+ · Python 3.12+ · Windows 10/11  

**Web dashboard (optional):** This repo ships **`web_sota`** — a local browser UI (Vite; default **http://localhost:10788**) that talks to the same backend as the REST API (**http://127.0.0.1:10789**). Use it for a **tools hub**, safety/help pages, **local LLM chat** (Ollama or LM Studio), **camera** selection, biometrics, and overview — run **`web_sota/start.ps1`**. You do **not** need the webapp for normal MCP **stdio** use in an IDE; it is an extra operator surface.

**Important:** This is **not** a browser sandbox. It runs in **your** desktop session and can move the real cursor, type into real windows, and drive the same UI you see. Read **[docs/SAFETY.md](docs/SAFETY.md)** before you wire it into an IDE. For throwaway desktops (Windows Sandbox, VMs, mapped folders), use **[virtualization-mcp](https://github.com/sandraschi/virtualization-mcp)** alongside this project. Fleet notes: `mcp-central-docs/patterns/PYWINAUTO_MCP_SAFETY.md`. Optional **face** features are off until you opt in — see **SAFETY §5** and `PYWINAUTO_MCP_ENABLE_FACE`.

### Discovery (GitHub, Glama, MCP catalogs)

- **Safety:** [`docs/SAFETY.md`](docs/SAFETY.md) — kill switch, rate limits, HITL, dry-run.
- **Isolation:** **Windows Sandbox** / VM via [`virtualization-mcp`](https://github.com/sandraschi/virtualization-mcp). Repo stars are **not** a safety guarantee.

### Product & docs

- **PRD / index:** [`docs/PRD.md`](docs/PRD.md) · [`docs/README.md`](docs/README.md)
- **Web dashboard:** [`web_sota/`](web_sota/) — `start.ps1` (ports **10788** / **10789**)

### Prompts, skills, MCPB

- **MCP prompts:** `desktop_automation_operator_protocol`, `desktop_automation_runbook` — [`src/pywinauto_mcp/prompts.py`](src/pywinauto_mcp/prompts.py).
- **Cursor skill:** [`skills/desktop-automation-protocol/SKILL.md`](skills/desktop-automation-protocol/SKILL.md).
- **Foreground:** [`docs/OPERATOR_PROTOCOL.md`](docs/OPERATOR_PROTOCOL.md) — keep the target app focused during automation.
- **MCPB:** [`mcpb/manifest.json`](mcpb/manifest.json) packages the server; prompts come from the running process unless you extend the pack.

### Planned / todo

- **Optional voice (STT / keyword / speaker-adjacent):** Not implemented. Would mirror face: **env + optional extra**, local-first, same HITL/safety docs — not authentication.

## Examples

- [examples/notepad_basic.py](examples/notepad_basic.py) — simple window flow.
- [examples/calculator_advanced.py](examples/calculator_advanced.py) — element tree.
- [examples/system_monitoring.py](examples/system_monitoring.py) — processes / tray.

Latency depends on the host, target app, and backends (OCR, etc.); treat any old benchmark tables as obsolete.

## Tools (portmanteau)

Seven core interfaces plus **`get_desktop_state`**, and **optional** `automation_face` when enabled:

| Tool | Operations | Description |
|------|------------|-------------|
| `automation_windows` | 11 | Window management (list, find, maximize, etc.) |
| `automation_elements` | 14 | UI element interaction (click, hover, text, etc.) |
| `automation_mouse` | 9 | Mouse (HITL may apply) |
| `automation_keyboard` | 4 | Keyboard (HITL may apply) |
| `automation_visual` | 4 | Screenshot, OCR, find image |
| `automation_face` | 5 | Face (opt-in: env + `face` extra) |
| `automation_system` | — | status, **help**, wait, info, clipboard, processes, start_app |
| `get_desktop_state` | 1 | UI tree / discovery |

---

## Usage snippets

### `automation_windows`

```python
automation_windows("find", title="Notepad", partial=True)
automation_windows("maximize", handle=12345)
```

### `automation_elements`

```python
automation_elements("click", window_handle=12345, control_id="btnOK")
automation_elements("set_text", window_handle=12345, control_id="Edit1", text="Hello!")
```

### `automation_visual`

```python
automation_visual("extract_text", image_path="screen.png")
automation_visual("find_image", template_path="button.png", threshold=0.8)
```

---

## Installation

**Prerequisites:** [uv](https://docs.astral.sh/uv/) recommended · Python 3.12+ · Windows 10/11 · Tesseract optional (visual/OCR).

**Run with uvx (published package):**

```bash
uvx pywinauto-mcp
```

**Claude Desktop (example):**

```json
"mcpServers": {
  "pywinauto-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/pywinauto-mcp", "run", "pywinauto-mcp"]
  }
}
```

**Install from source:**

```powershell
uv pip install -e .
```

**MCPB:**

```powershell
mcpb install pywinauto-mcp
```

---

## Safety

**Canonical:** [`docs/SAFETY.md`](docs/SAFETY.md) — two-server model with **`virtualization-mcp`**, HITL, env vars, fleet docs.

Desktop automation is **not** browser-sandboxed. **Sampling** and long agent loops can multiply tool calls.

### Human-in-the-loop

- **`approve_automation(duration_minutes=...)`** before mutating **mouse** / **keyboard**, or tools return `clarification_needed`.
- **`automation_mouse("position")`** is read-only and skips approval.

### Environment variables

| Env | Purpose |
|-----|---------|
| `PYWINAUTO_MCP_KILL_SWITCH=1` | Blocks mutating mouse/keyboard (after HITL path). |
| `PYWINAUTO_MCP_MAX_ACTIONS_PER_MINUTE` | Default `120` — rolling 60s cap for mutating actions. |
| `PYWINAUTO_MCP_DRY_RUN=1` | Count actions without sending input (`dry_run` in results). |
| `PYWINAUTO_MCP_ENABLE_FACE=1` | Allows registering **`automation_face`** (needs `face` extra). |
| `PYWINAUTO_LLM_BASE_URL` | Default OpenAI-compatible root for the **web_sota** local-LLM proxy (e.g. Ollama `http://127.0.0.1:11434/v1`, LM Studio `http://127.0.0.1:1234/v1`). The UI can override per session. |
| `PYWINAUTO_MCP_CAMERA_MAX_INDEX` | Max OpenCV index to probe for **`GET /api/v1/cameras/`** (default `10`, capped at 32). |

**`automation_safety(operation="status"|"reset_counters")`** — counters and flags. **`automation_system("help")`** returns a structured overview (version, tools, safety keys, doc paths).

**Fleet:** `mcp-central-docs` → `patterns/PYWINAUTO_MCP_SAFETY.md`.

---

## Testing (CI vs local)

See **[docs/TESTING.md](docs/TESTING.md)** — environment-aware markers (`requires_hardware`, `destructive`, …) aligned with **mcp-central-docs** `standards/testing-environment-aware.md`. In CI, hardware-marked tests are skipped; run locally on Windows to exercise OpenCV / real window flows.

## Maintenance

- Documentation should match **implemented** tools and env vars.
- **`glama.json`:** update when releasing or when marketplace metadata changes.

## License

MIT — Copyright (c) 2026 Sandra Schipal.

---

## Web dashboard (`web_sota`)

Optional Vite UI + local backend. Default ports from **`web_sota/start.ps1`**: frontend **10788**, backend **10789**.

```powershell
Set-Location web_sota
.\start.ps1
```

Open `http://localhost:10788` — **Help** route documents safety, env vars, and tool overview (same themes as `automation_system("help")`).

**Local LLM chat** (`/chat`): proxies to **Ollama** or **LM Studio** (OpenAI-compatible `/v1` on localhost only). Pick a model, optional **personas**, **prompt refiner**, and **repo knowledge** pre-prompt (`src/pywinauto_mcp/llm_repo_context.py`) for questions like “can I click and drag?”. Start Ollama or LM Studio first; then **Refresh models**.
