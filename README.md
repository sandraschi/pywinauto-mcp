# pywinauto-mcp · Windows Computer Use Agent

<p align="center">
  <a href="https://github.com/sandraschi/pywinauto-mcp"><img src="https://img.shields.io/github/stars/sandraschi/pywinauto-mcp?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/sandraschi/pywinauto-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
</p>

**A Windows computer use agent** — FastMCP server that gives AI assistants **hands on the real desktop**: windows, UI elements, mouse, keyboard, screenshots, OCR, shortcuts, dialogs, and outcome verification. Not a browser sandbox; runs in **your** session with HITL, kill switch, and rate limits.

Pair with **[virtualization-mcp](https://github.com/sandraschi/virtualization-mcp)** for Windows Sandbox / VM isolation. Read **[docs/SAFETY.md](docs/SAFETY.md)** before production use.

> 📖 **[INSTALL.md](INSTALL.md)** — desktop installer, `uv` setup, MCP client config

This repo is named after **[Pywinauto](https://github.com/pywinauto/pywinauto)** — the Python library that drives **Windows UI Automation (UIA)** and Win32 controls. The MCP server wraps that (and related libraries) as structured tools for AI clients. It is an **operator-visible automation assistant**, not covert surveillance software.

---

## Contents

- [Quick Start](#quick-start)
- [Python stack (py- modules)](#python-stack-py--modules)
- [Optional invasive features](#optional-invasive-features-off-by-default)
- [Documentation](#documentation)
- [Ports](#ports)
- [Tech Stack](#tech-stack)
- [Fleet & siblings](#fleet--siblings)
- [License](#license)

---

## Quick Start

```powershell
git clone https://github.com/sandraschi/pywinauto-mcp
cd pywinauto-mcp
just bootstrap
just serve
```

**MCP (stdio)** — add to Cursor / Claude Desktop:

```json
{
  "mcpServers": {
    "pywinauto-mcp": {
      "command": "uv",
      "args": ["--directory", "<PATH-TO-CLONE>", "run", "pywinauto-mcp"]
    }
  }
}
```

**Optional web operator UI:** `.\start.ps1` → http://127.0.0.1:10788 (proxies API on **10789**).

**Demos:** `just demo` — mouse dance, Notepad grid, typewriter (see [examples/README.md](examples/README.md)).

---

## Python stack (py- modules)

| Package | Role in this project |
|---------|----------------------|
| **[pywinauto](https://github.com/pywinauto/pywinauto)** | **Core** — attach to HWNDs, walk UIA/Win32 control trees, click/type/read elements (`automation_windows`, `automation_elements`). |
| **pywin32** | Low-level Win32 COM/API (session, processes, DPI helpers) used alongside pywinauto. |
| **pygetwindow** | Window titles/rectangles for discovery and layout. |
| **pyautogui** | Fallback screen-level pointer/screenshot helpers where UIA is not enough. |
| **pynput** | Injects and **optionally** listens to keyboard/mouse at the session level; powers normal `automation_keyboard` simulation and the **opt-in** `global_keylogger` hook. |
| **pyperclip** | Clipboard read/write for `automation_system`. |
| **opencv-python-headless** | Screenshots, camera index probe, template match paths in `automation_visual` / biometrics preview. |
| **pytesseract** | OCR in `automation_visual` (needs Tesseract installed on the host). |
| **face_recognition** + **dlib** | **Optional extra only** (`uv sync --extra face`) for `automation_face` — not installed in the default desktop bundle. |

Other important non-`py` deps: **FastMCP** (MCP server), **FastAPI** + **uvicorn** (REST + `/mcp` HTTP), **Pillow**, **numpy**, **httpx**.

---

## Optional invasive features (off by default)

**Default install:** window/element/mouse/keyboard/visual automation only. No ambient monitoring.

| Feature | Shipped in code? | Default? | Enable |
|---------|------------------|----------|--------|
| **`automation_face`** | Yes — local webcam capture/match | **Off** — tool not registered | `PYWINAUTO_MCP_ENABLE_FACE=1` + `uv sync --extra face` ([SAFETY.md §5](docs/SAFETY.md)) |
| **`global_keylogger`** | Yes — session keyboard hook | **Off** — tool not registered | `PYWINAUTO_MCP_ENABLE_KEYLOGGER=1` ([SAFETY.md §6](docs/SAFETY.md)) |

**Keylogger is not stealth spyware.** It is an explicit MCP tool: disabled unless you set the env flag, requires **HITL approval** to `start`, stores events in a **bounded in-memory buffer** (not hidden files), and the server **stops the hook on shutdown**. Use only on machines you own for debugging shortcut/focus issues — not for credential harvesting.

**Face recognition is not a background plan-only sketch** — the tool is implemented but **opt-in** like the keylogger. The operator UI **Biometrics** page is a control panel when you enable it; it does not run face matching unless you opt in and call the tool.

---

## Documentation

### For operators

| Doc | Content |
|-----|---------|
| [INSTALL.md](INSTALL.md) | Desktop app, `uv` / `uvx`, MCP client wiring |
| [docs/SAFETY.md](docs/SAFETY.md) | HITL, kill switch, opt-in face & keylogger (non-stealth) |
| [docs/OPERATOR_PROTOCOL.md](docs/OPERATOR_PROTOCOL.md) | Foreground focus during automation |
| [docs/DESKTOP_APP.md](docs/DESKTOP_APP.md) | Tauri operator app + PyInstaller sidecar |
| [docs/MEMOPS_CUA.md](docs/MEMOPS_CUA.md) | Computer use agent doctrine (fleet CUA role) |
| [docs/CUA_ROADMAP.md](docs/CUA_ROADMAP.md) | Closed-loop assistant roadmap |
| [examples/README.md](examples/README.md) | Runnable demos and paint orchestration |

### For developers

| Doc | Content |
|-----|---------|
| [docs/README.md](docs/README.md) | Documentation hub |
| [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) | Full map + stale-doc warning |
| [docs/PRD.md](docs/PRD.md) | Product requirements |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System diagram, components, fleet role |
| [docs/TOOLS.md](docs/TOOLS.md) | Portmanteau MCP tools reference |
| [docs/TESTING.md](docs/TESTING.md) | CI vs local pytest, hardware markers |
| [docs/mcp-technical/README.md](docs/mcp-technical/README.md) | MCP transport, production checklist |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Contributor quick start (archived notes in `docs/development/archive/`) |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

### Packaging & distribution

| Doc | Content |
|-----|---------|
| [mcpb/README.md](mcpb/README.md) | MCPB bundle (Claude Desktop `.mcpb`) |
| [docs/mcpb-packaging/README.md](docs/mcpb-packaging/README.md) | Build guide and fleet packaging standards |

### Prompts & skills

| Asset | Purpose |
|-------|---------|
| [skills/desktop-automation-protocol/SKILL.md](skills/desktop-automation-protocol/SKILL.md) | Cursor agent skill |
| `desktop_automation_operator_protocol` | MCP prompt (`src/pywinauto_mcp/prompts.py`) |

---

## Ports

| Port | Service |
|------|---------|
| **10788** | Frontend — Vite operator UI (`web_sota`) |
| **10789** | Backend — FastAPI `/api/v1/*` + FastMCP HTTP `/mcp` |

Stdio MCP has no port (host-launched process).

---

## Tech Stack

- **MCP:** Python 3.12+, FastMCP 3.2+, portmanteau tools (windows, elements, mouse, keyboard, visual, assert, dialog, shortcut, task, system)
- **Input:** `win32_mouse` (DPI-aware), optional Win32 keyboard (`CUA_MCP_KEYBOARD=win32`)
- **Web:** Vite + React operator dashboard, local LLM proxy (Ollama / LM Studio)
- **Desktop:** Tauri 2 operator app (optional installer)
- **Quality:** Ruff, Biome, pytest (environment-aware), `just` recipes

---

## Fleet & siblings

| Tool | What it does | When to use |
|------|-------------|-------------|
| **pywinauto-mcp (here)** | **Computer use agent** — structured native UI automation via UIA element tree, screenshots, OCR | You need to **inspect controls, click buttons, read text** from apps with accessibility trees. Best for modern Windows apps. Shows "CUA at work" HUD during `analyze_winapp` crawls and `global_keylogger` sessions. |
| [autohotkey-mcp](https://github.com/sandraschi/autohotkey-mcp) | AHK scriptlet depot — list, run, stop, generate `.ahk` scripts. Best for **low-level input recording/replay** and apps that don't expose UIA. | You have a **depot of AHK scripts** or need **raw keyboard/mouse recording** via AHK's built-in recorder. Shows "CUA at work" HUD while scriptlets run. |
| [openmanus-mcp](https://github.com/sandraschi/openmanus-mcp) | OpenManus agent bridge + computer/bash tools | You need a general-purpose agent with bash/computer access inside a sandbox. |
| [virtualization-mcp](https://github.com/sandraschi/virtualization-mcp) | Sandbox / VM isolation | You need to isolate automation in a disposable VM. |

**Overlap:** both pywinauto-mcp and autohotkey-mcp control Windows input. **Use AHK** for raw low-level recording/replay (AHK's built-in recorder + `run_scriptlet`). **Use pywinauto** when you need UIA element tree access, OCR, or structured window state capture.

Fleet standards: [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) — `patterns/PYWINAUTO_MCP_SAFETY.md`, `standards/MCPB_PACKAGING_STANDARDS.md`.

**Browser vs desktop:** This server drives **Win32 / UI Automation**. For HTML/DOM and websites, use a **Playwright browser MCP** alongside this one.

---

## License

MIT — Copyright (c) 2026 Sandra Schipal.
