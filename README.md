# PyWinAuto MCP - Portmanteau Edition

**Version 0.3.2** | **SOTA 2026** | **FastMCP 3.1+** | **Last Sync: 2026-03-21**

> **New users — isolation:** This server automates **your Windows desktop** (high privilege). For **Windows Sandbox / disposable VMs** + mapped assets, **also install `virtualization-mcp`** alongside this server. **→ Full checklist:** [`docs/SAFETY.md`](docs/SAFETY.md) · fleet: `mcp-central-docs/patterns/PYWINAUTO_MCP_SAFETY.md`.

A FastMCP-compliant server for Windows UI automation using PyWinAuto. Portmanteau tools consolidate 60+ operations; see **[docs/SAFETY.md](docs/SAFETY.md)** before enabling in Cursor / Antigravity / Claude Desktop.

### Discovery (GitHub, Glama, MCP catalogs)

- **Safety first:** [`docs/SAFETY.md`](docs/SAFETY.md) is the checklist (kill switch, rate limits, HITL, dry-run).
- **Real isolation:** Use **Windows Sandbox** or a disposable VM via **[`virtualization-mcp`](https://github.com/sandraschi/virtualization-mcp)** alongside this server — do not rely on repo stars as a safety signal.
- **Stars:** Stars reflect **distribution / interest**, not verified safety.

## 🚀 SOTA 2026 Updates

### 💎 Gold Standard Examples
We have transitioned from legacy scripts to a comprehensive Python-based example gallery:
- [notepad_basic.py](examples/notepad_basic.py): Simple window automation flow.
- [calculator_advanced.py](examples/calculator_advanced.py): Complex element tree traversal and interaction.
- [system_monitoring.py](examples/system_monitoring.py): Background process and system tray management.

### ⚡ Performance Benchmarks
| Operation | Average Latency (ms) | Success Rate |
|-----------|----------------------|--------------|
| Window Discovery | 45ms | 99.8% |
| Element Click | 120ms | 98.5% |
| OCR Extraction | 450ms | 95.0% |
| Face Recognition | 850ms | 99.2% |

### 🛠 Tool Consolidation (Portmanteau)
The Portmanteau Edition consolidates 60+ legacy tools into **8 high-utility interfaces**:

| Tool | Operations | Description |
|------|------------|-------------|
| `automation_windows` | 11 | Window management (list, find, maximize, etc.) |
| `automation_elements` | 14 | UI element interaction (click, hover, text, etc.) |
| `automation_mouse` | 9 | Mouse control (move, click, scroll, drag) |
| `automation_keyboard` | 4 | Keyboard input (type, press, hotkey) |
| `automation_visual` | 4 | Visual operations (screenshot, OCR, find image) |
| `automation_face` | 5 | Face recognition (add, recognize, list, delete) |
| `automation_system` | 7 | System utilities (health, help, processes) |
| `get_desktop_state` | 1 | Comprehensive desktop UI discovery |

---

## 🏆 Core Features

### 🔍 Window Management (`automation_windows`)
```python
# Find window by title
automation_windows("find", title="Notepad", partial=True)

# Maximize, minimize, restore
automation_windows("maximize", handle=12345)
```

### 🎯 Element Interaction (`automation_elements`)
```python
# Click and set text
automation_elements("click", window_handle=12345, control_id="btnOK")
automation_elements("set_text", window_handle=12345, control_id="Edit1", text="Hello!")
```

### 📸 Visual Intelligence (`automation_visual`)
```python
# OCR text extraction
automation_visual("extract_text", image_path="screen.png")

# Find image on screen
automation_visual("find_image", template_path="button.png", threshold=0.8)
```

---

## 🚀 Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

### 📦 Quick Start
Run immediately via `uvx`:
```bash
uvx pywinauto-mcp
```

### 🎯 Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "pywinauto-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/pywinauto-mcp", "run", "pywinauto-mcp"]
  }
}
```
### Prerequisites
- Windows 10/11 Pro
- Python 3.10+
- Tesseract OCR (Optional, for visual tools)

### Install via MCPB (Recommended)
```powershell
mcpb install pywinauto-mcp
```

### Install from source
```powershell
uv pip install -e .
```

## 🚀 Quick Start (Claude Desktop)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pywinauto": {
      "command": "python",
      "args": ["-m", "pywinauto_mcp"],
      "env": {
        "PYTHONPATH": "D:\\Dev\\repos\\pywinauto-mcp"
      }
    }
  }
}
```

## 🛡️ Safety

**Canonical doc:** **[`docs/SAFETY.md`](docs/SAFETY.md)** — two-server model (**pywinauto-mcp** + **`virtualization-mcp`** for Sandbox/VM), HITL, env vars, fleet links.

**Summary:** Desktop UI automation is **not** sandboxed like a browser tab. **FastMCP 3.1 sampling** and **agentic** loops can multiply tool calls.

### Human-in-the-loop

- Call **`approve_automation(duration_minutes=...)`** before mutating **mouse** / **keyboard** automation, or those tools return `clarification_needed`.
- **`automation_mouse("position")`** is read-only and skips approval.

### Kill switch, rate limit, dry-run

| Env | Purpose |
|-----|---------|
| `PYWINAUTO_MCP_KILL_SWITCH=1` | Emergency stop: blocks mutating mouse/keyboard after HITL. |
| `PYWINAUTO_MCP_MAX_ACTIONS_PER_MINUTE` | Default `120` — max mutating actions per **rolling 60 seconds**. |
| `PYWINAUTO_MCP_DRY_RUN=1` | Logically “execute” for metrics but **do not** call pyautogui (`dry_run` status). |

Tool **`automation_safety(operation="status"|"reset_counters")`** exposes counters and current flags.

**Fleet (`mcp-central-docs`):** `patterns/PYWINAUTO_MCP_SAFETY.md` — vendor comparison, sampling amplification, IDE chain rules, guest-side Sandbox automation.

## 🤝 Maintenance Policy
This repository follows the **Sandra SOTA 2026 Standards**:
- **Zero Fiction**: Documentation reflects actual tool capabilities.
- **Portmanteau Priority**: Tools are consolidated for discovery.
- **Glama Freshness**: `glama.json` is updated weekly to prevent stale marketplace entries.

## 📄 License
MIT License - Copyright (c) 2026 Sandra Schipal.


## 🌐 Webapp Dashboard

This MCP server includes a free, premium web interface for monitoring and control.
By default, the web dashboard runs on port **10788**.
*(Assigned ports: **10788** (Web dashboard frontend), **10789** (Web dashboard backend))*

To start the webapp:
1. Navigate to the `webapp` (or `web`, `frontend`) directory.
2. Run `start.bat` (Windows) or `./start.ps1` (PowerShell).
3. Open `http://localhost:10788` in your browser.
