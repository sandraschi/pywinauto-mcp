# PyWinAuto MCP

**Let an AI assistant control real Windows apps**  through a single MCP server that wraps window, UI, mouse, keyboard, screenshots, OCR, and optional face checks behind a small set of **portmanteau** tools (many operations, few entry points so models stay focused).

**Stack:** v0.4.2  FastMCP 3.2+  Python 3.12+  Windows 10/11  

**Web dashboard (optional):** This repo ships **`web_sota`** — a local browser UI (Vite; default **http://localhost:10788**) that talks to the same backend as the REST API (**http://127.0.0.1:10789**). Use it for a **tools hub**, safety/help pages, **local LLM chat** (Ollama or LM Studio), **camera** selection, biometrics, and overview — run **`web_sota/start.ps1`**. You do **not** need the webapp for normal MCP **stdio** use in an IDE; it is an extra operator surface.

**Important:** This is **not** a browser sandbox. It runs in **your** desktop session and can move the real cursor, type into real windows, and drive the same UI you see. Read **[docs/SAFETY.md](docs/SAFETY.md)** before you wire it into an IDE. For **why hooks and full desktop control look “malware-adjacent”** and how this repo gates them (research, forensics, legitimate automation), see **[Dual-use tooling](docs/SAFETY.md#dual-use-tooling-research-forensics-and-guardrails)** in that doc. For throwaway desktops (Windows Sandbox, VMs, mapped folders), use **[virtualization-mcp](https://github.com/sandraschi/virtualization-mcp)** alongside this project. Fleet notes: `mcp-central-docs/patterns/PYWINAUTO_MCP_SAFETY.md`. Optional **face** features are off until you opt in  see **SAFETY 5** and `PYWINAUTO_MCP_ENABLE_FACE`. Optional **global keylogger** is off until you opt in  see **SAFETY 6** and `PYWINAUTO_MCP_ENABLE_KEYLOGGER`.

**Native Windows vs websites (HTML DOM):** **pywinauto-mcp** drives **desktop UI** (Win32 / UI Automation  windows, dialogs, many native controls). It does **not** expose the **HTML DOM** inside a browser tab. For **website** automation and analysis (selectors, accessibility tree, network, console), use a **browser MCP**; those servers are usually built on **Playwright** (or Chromium-only stacks). The two are **orthogonal**  combine them in your IDE when a workflow needs **both** a real browser page and a **native** app on the same machine.

### Complementary: [autohotkey-mcp](https://github.com/sandraschi/autohotkey-mcp) (sibling repo)

Fleet sibling **[`autohotkey-mcp`](https://github.com/sandraschi/autohotkey-mcp)** targets **AutoHotkey v2 scriptlets**: list/run/stop scripts from a depot, optional **ScriptletCOMBridge**, optional **LLM-assisted** generation of `.ahk` into a sandbox folder. This repo targets **PyWinAuto + portmanteau tools** (window/element tree, mouse/keyboard, visual, system). **Neither replaces the other.**

| | **pywinauto-mcp (here)** | **autohotkey-mcp** |
|--|--|--|
| **Core idea** | **Structured native UI automation** — UIA/window discovery, element ops, OCR/screenshots, one MCP tool surface. | **AHK script lifecycle** — run and manage scriptlets, peek source/metadata, optional generate AHK. |
| **Overlap** | Both assume a **high-trust Windows session** (read each repo’s **SAFETY**). | Same. |
| **Not duplicated** | No first-class **scriptlet depot** or **AHK generation** workflow. | No **UI Automation tree** or **portmanteau** window/element API like here. |
| **Typical use** | “Drive this app’s UI from the model” (clicks, fields, windows). | “Run or author **hotkey/macro** AHK I already organize in a folder.” |
| **Together** | Install **both** MCP servers when you want **agent-driven UI control** and **AHK utilities** in the same client; keep boundaries clear (native UI here, AHK scripts there). | — |

### Discovery (GitHub, Glama, MCP catalogs)

- **Safety:** [`docs/SAFETY.md`](docs/SAFETY.md)  kill switch, rate limits, HITL (human-in-the-loop), dry-run.
- **Dual-use / research:** [Dual-use tooling](docs/SAFETY.md#dual-use-tooling-research-forensics-and-guardrails) — capability vs. intent, guardrails, vendor refusal context.
- **Isolation:** **Windows Sandbox** / VM via [`virtualization-mcp`](https://github.com/sandraschi/virtualization-mcp). Repo stars are **not** a safety guarantee.

### Product & docs

- **PRD / index:** [`docs/PRD.md`](docs/PRD.md)  [`docs/README.md`](docs/README.md)
- **Web dashboard:** [`web_sota/`](web_sota/)  `start.ps1` (ports **10788** / **10789**)

### Prompts, skills, MCPB

- **MCP prompts:** `desktop_automation_operator_protocol`, `desktop_automation_runbook`  [`src/pywinauto_mcp/prompts.py`](src/pywinauto_mcp/prompts.py).
- **Cursor skill:** [`skills/desktop-automation-protocol/SKILL.md`](skills/desktop-automation-protocol/SKILL.md).
- **Foreground:** [`docs/OPERATOR_PROTOCOL.md`](docs/OPERATOR_PROTOCOL.md)  keep the target app focused during automation.
- **MCPB:** [`mcpb/manifest.json`](mcpb/manifest.json) packages the server; prompts come from the running process unless you extend the pack.

### Planned / todo

- **Optional voice (STT / keyword / speaker-adjacent):** Not implemented. Would mirror face: **env + optional extra**, local-first, same HITL (human-in-the-loop) / safety docs  not authentication.

## Examples

- **[examples/README.md](examples/README.md)** — **demos:** mouse dance, 9-Notepad grid, typewriter Notepad, plus older samples. Run all three in order: **`just demo`** (requires [just](https://github.com/casey/just)).
- **just paint-demo** — Industrialized MS Paint drawing (justfile/PowerShell orchestrated).
- [examples/notepad_basic.py](examples/notepad_basic.py) — simple window flow.
- [examples/calculator_advanced.py](examples/calculator_advanced.py) — element tree.
- [examples/system_monitoring.py](examples/system_monitoring.py) — processes / tray.

Latency depends on the host, target app, and backends (OCR, etc.); treat any old benchmark tables as obsolete.

## Tools (portmanteau)

Seven core interfaces plus **`get_desktop_state`**, **optional** `automation_face` when enabled, and **optional** `global_keylogger` when enabled (see **SAFETY**):

| Tool | Operations | Description |
|------|------------|-------------|
| `automation_windows` | 11 | Window management (list, find, maximize, etc.) |
| `automation_elements` | 14 | UI element interaction (click, hover, text, etc.) |
| `automation_mouse` | 9 | Mouse — HITL (human-in-the-loop) may apply |
| `automation_keyboard` | 4 | Keyboard — HITL (human-in-the-loop) may apply |
| `global_keylogger` | 5 | Session keyboard capture (opt-in: `PYWINAUTO_MCP_ENABLE_KEYLOGGER`; see SAFETY §6) |
| `automation_visual` | 4 | Screenshot, OCR, find image |
| `automation_face` | 5 | Face (opt-in: env + `face` extra) |
| `automation_system` |  | status, **help**, wait, info, clipboard, processes, start_app |
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

**Prerequisites:** [uv](https://docs.astral.sh/uv/) recommended  Python 3.12+  Windows 10/11  Tesseract optional (visual/OCR).

**Run with uvx (published package):**

```bash
uvx pywinauto-mcp
```

**Claude Desktop (example):** replace `<PATH-TO-CLONE>` with the directory where you cloned this repository (not a path from another machine).

```json
"mcpServers": {
  "pywinauto-mcp": {
    "command": "uv",
    "args": ["--directory", "<PATH-TO-CLONE>", "run", "pywinauto-mcp"]
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

**Canonical:** [`docs/SAFETY.md`](docs/SAFETY.md)  two-server model with **`virtualization-mcp`**, HITL (human-in-the-loop), env vars, fleet docs.

**Dual-use / research framing:** [Dual-use tooling (research, forensics, guardrails)](docs/SAFETY.md#dual-use-tooling-research-forensics-and-guardrails) — why full desktop automation and hooks overlap offensive tooling in **capability**, how **intent and authorization** differ, and what this repo does to limit abuse.

Desktop automation is **not** browser-sandboxed. **Sampling** and long agent loops can multiply tool calls.

### Human-in-the-loop (HITL)

**HITL** (human-in-the-loop) means an operator must **approve** before mutating **mouse** / **keyboard** when the server is configured that way.

- **`approve_automation(duration_minutes=...)`** before mutating **mouse** / **keyboard**, or tools return `clarification_needed`.
- **`automation_mouse("position")`** and **`automation_mouse("telemetry")`** are read-only and skip approval.

---

## Operations Overview

### 🖱️ Mouse Control (`automation_mouse`)
Consolidates all mouse interactions: position tracking, clicking, dragging, and hovering.

**Pointer injection** uses the in-repo **`win32_mouse`** backend (**`SetCursorPos`** / **`mouse_event`**, DPI-aware) for **`automation_mouse`** and for coordinate-based clicks in **`automation_elements`** — not PyAutoGUI alone, so moves and clicks stay reliable on scaled displays. Responses may include **`input_backend: "win32_mouse"`**. **Failsafe** matches PyAutoGUI: moving the cursor to the **upper-left screen corner** aborts injected pointer ops unless **`PYWINAUTO_MCP_BYPASS_HITL=1`** (also disables that corner check for **`win32_mouse`**).

**Operations**: `position`, `click`, `double_click`, `right_click`, `move`, `move_relative`, `scroll`, `drag`, `hover`, `telemetry`

**Key Tool: Visual Telemetry HUD**
Launches a high-visibility, "Always-on-Top" overlay for real-time calibration:
- **Coordinate Tracking**: Live X/Y position updates.
- **Scrolling Input Buffer**: Displays the last 20 keyboard characters and click events (visual verification only, no persistence).
- **Industrial Safety**: High visibility ensures monitoring is transparent and operator-auditable.

```powershell
# Example: Launch telemetry HUD for 30 seconds
mcp-invoke automation_mouse --operation "telemetry" --telemetry_duration 30
```

### Environment variables

| Env | Purpose |
|-----|---------|
| `PYWINAUTO_MCP_BYPASS_HITL=1` | Bypasses approval prompts and disables pointer failsafe (`pyautogui.FAILSAFE` and **`win32_mouse`** corner escape) for trust-controlled demos/CI. |
| `PYWINAUTO_MCP_KILL_SWITCH=1` | Blocks mutating mouse/keyboard (after HITL (human-in-the-loop) path). |
| `PYWINAUTO_MCP_MAX_ACTIONS_PER_MINUTE` | Default `120`  rolling 60s cap for mutating actions. |
| `PYWINAUTO_MCP_DRY_RUN=1` | Count actions without sending input (`dry_run` in results). |
| `PYWINAUTO_MCP_ENABLE_FACE=1` | Allows registering **`automation_face`** (needs `face` extra). |
| `PYWINAUTO_MCP_ENABLE_KEYLOGGER=1` | Allows registering **`global_keylogger`** (session keyboard capture; see SAFETY §6). |
| `PYWINAUTO_LLM_BASE_URL` | Default OpenAI-compatible root for the **web_sota** local-LLM proxy (e.g. Ollama `http://127.0.0.1:11434/v1`, LM Studio `http://127.0.0.1:1234/v1`). The UI can override per session. |
| `PYWINAUTO_MCP_CAMERA_MAX_INDEX` | Max OpenCV index to probe for **`GET /api/v1/cameras/`** (default `10`, capped at 32). |

**`automation_safety(operation="status"|"reset_counters")`**  counters and flags. **`automation_system("help")`** returns a structured overview (version, tools, safety keys, doc paths).

**Fleet:** `mcp-central-docs`  `patterns/PYWINAUTO_MCP_SAFETY.md`.

---

## Testing (CI vs local)

See **[docs/TESTING.md](docs/TESTING.md)**  environment-aware markers (`requires_hardware`, `destructive`, ) aligned with **mcp-central-docs** `standards/testing-environment-aware.md`. In CI, hardware-marked tests are skipped; run locally on Windows to exercise OpenCV / real window flows.

## Maintenance

- Documentation should match **implemented** tools and env vars.
- **`glama.json`:** update when releasing or when marketplace metadata changes.
- **Portable clones:** avoid committing machine-specific paths (e.g. a fixed drive + `Dev\repos\...`). Run **`just check-machine-paths`** (or `pwsh -File scripts/check-no-machine-paths.ps1`) on `src/` and key root files; use **`-FullRepo`** to scan the whole tree (legacy docs may still match until cleaned).

## License

MIT  Copyright (c) 2026 Sandra Schipal.

---

## Web dashboard (`web_sota`)

Optional Vite UI + local backend. Default ports from **`web_sota/start.ps1`** (or repo-root **`start.ps1`**): frontend **10788**, backend **10789**. The start scripts **wait for the Python API to be reachable** before starting Vite so the Vite proxy does not log connection refused errors during a cold **`uv run`**.

```powershell
# From repo root (recommended)
.\start.ps1

# Or from web_sota
Set-Location web_sota
.\start.ps1
```

Open `http://localhost:10788`  **Help** route documents safety, env vars, and tool overview (same themes as `automation_system("help")`).

**Local LLM chat** (`/chat`): proxies to **Ollama** or **LM Studio** (OpenAI-compatible `/v1` on localhost only). Pick a model, optional **personas**, **prompt refiner**, and **repo knowledge** pre-prompt (`src/pywinauto_mcp/llm_repo_context.py`) for questions like can I click and drag?. Start Ollama or LM Studio first; then **Refresh models**.
