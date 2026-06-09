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

---

## Contents

- [Quick Start](#quick-start)
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

## Documentation

### For operators

| Doc | Content |
|-----|---------|
| [INSTALL.md](INSTALL.md) | Desktop app, `uv` / `uvx`, MCP client wiring |
| [docs/SAFETY.md](docs/SAFETY.md) | HITL, kill switch, dual-use framing, face/keylogger opt-in |
| [docs/OPERATOR_PROTOCOL.md](docs/OPERATOR_PROTOCOL.md) | Foreground focus during automation |
| [docs/DESKTOP_APP.md](docs/DESKTOP_APP.md) | Tauri operator app + PyInstaller sidecar |
| [docs/MEMOPS_CUA.md](docs/MEMOPS_CUA.md) | Computer use agent doctrine (fleet CUA role) |
| [docs/CUA_ROADMAP.md](docs/CUA_ROADMAP.md) | Closed-loop assistant roadmap |
| [examples/README.md](examples/README.md) | Runnable demos and paint orchestration |

### For developers

| Doc | Content |
|-----|---------|
| [docs/README.md](docs/README.md) | Full documentation index |
| [docs/PRD.md](docs/PRD.md) | Product requirements |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System diagram, components, fleet role |
| [docs/TOOLS.md](docs/TOOLS.md) | Portmanteau MCP tools reference |
| [docs/TESTING.md](docs/TESTING.md) | CI vs local pytest, hardware markers |
| [docs/mcp-technical/README.md](docs/mcp-technical/README.md) | MCP transport, production checklist |
| [docs/development/README.md](docs/development/README.md) | Dev guides and fleet patterns |
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

| Repo | Role |
|------|------|
| **pywinauto-mcp (here)** | **Computer use agent** — structured native UI automation |
| [autohotkey-mcp](https://github.com/sandraschi/autohotkey-mcp) | AHK scriptlet depot / hotkey macros |
| [openmanus-mcp](https://github.com/sandraschi/openmanus-mcp) | OpenManus agent bridge + computer/bash tools |
| [virtualization-mcp](https://github.com/sandraschi/virtualization-mcp) | Sandbox / VM isolation |

Fleet standards: [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) — `patterns/PYWINAUTO_MCP_SAFETY.md`, `standards/MCPB_PACKAGING_STANDARDS.md`.

**Browser vs desktop:** This server drives **Win32 / UI Automation**. For HTML/DOM and websites, use a **Playwright browser MCP** alongside this one.

---

## License

MIT — Copyright (c) 2026 Sandra Schipal.
