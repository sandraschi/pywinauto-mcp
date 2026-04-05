# PRD — PyWinAuto MCP (portmanteau edition)

## 1. Overview

**PyWinAuto MCP** is a [Model Context Protocol](https://modelcontextprotocol.io/) server for **Windows UI automation**. It exposes **portmanteau tools** (PyWinAuto, PyAutoGUI, OCR, optional face) so agentic clients can drive **real desktop sessions** with HITL and safety limits.

**Non-goals:** This server does **not** replace **Windows Sandbox** or disposable VMs — pair with **`virtualization-mcp`** when isolation is required. See [`SAFETY.md`](SAFETY.md).

## 2. Goals

| Goal | Detail |
|------|--------|
| **Tool efficiency** | Consolidate many operations into **8 portmanteau tools** + `get_desktop_state` to limit tool explosion and token load. |
| **Framework** | **FastMCP 3.1+** — stdio/SSE and HTTP MCP surface; async tools; docstring-first descriptions. |
| **Safety** | HITL (`approve_automation`), kill switch, rate limits, dry-run, optional face **opt-in** only. |
| **Operator UX** | Optional **`web_sota`** dashboard: REST bridge, tools hub, help, local LLM chat, live host metrics, biometrics (browser preview + safety snapshot). |
| **Testability** | **Environment-aware pytest** (CI vs local hardware) per **mcp-central-docs** `standards/testing-environment-aware.md` — see [`TESTING.md`](TESTING.md). |
| **Maintainability** | Ruff, type hints, docs match **implemented** behavior. |

## 3. Key product surfaces

### 3.1 MCP tools (core)

- `automation_windows`, `automation_elements`, `automation_mouse`, `automation_keyboard`, `automation_visual`, `automation_system`, `get_desktop_state`
- **`automation_face`** — registered only when **`PYWINAUTO_MCP_ENABLE_FACE=1`** and **`face`** extra installed ([`SAFETY.md`](SAFETY.md) §5).
- **`approve_automation`**, **`automation_safety`** — HITL and counters.

### 3.2 HTTP / ASGI

- **FastAPI** routes under **`/api/v1/*`** (health, tools list/call, windows, **LLM proxy**, **cameras**, **system/info**, **safety/status**).
- FastMCP **`http_app()`** mounted so **`/mcp`** remains the streamable MCP endpoint.
- **CORS** for local `web_sota` dev ports.

### 3.3 Web dashboard (`web_sota`)

- **Vite** dev server; **`start.ps1`** — backend **10789**, frontend **10788** (fleet **10700+** range; see **mcp-central-docs** `standards/WEBAPP_STANDARDS.md`).
- **Proxy:** `/api` → backend (same-origin API calls).
- **Routes:** Overview, Windows, Elements, Tools Hub, **Local LLM** (`/chat`), Help, Biometrics, Settings. (No in-repo robotics teleop or 3D “digital twin” — use fleet **robotics-mcp**.)
- **Local LLM:** OpenAI-compatible proxy to **Ollama** / **LM Studio** (`PYWINAUTO_LLM_BASE_URL`); personas, prompt refiner, repo context (`llm_repo_context.py`).
- **Cameras:** `GET /api/v1/cameras/`; UI selection when multiple devices; syncs `camera_index` with Tools / face capture.
- **Biometrics:** browser preview + **`GET /api/v1/safety/status`** + optional **`automation_face`** via **`POST /api/v1/tools/call`** when face tool is registered.
- **Transparency:** Dashboard host metrics and biometrics safety line are **live**; browser webcam preview is **local MediaDevices** (not OpenCV — indices may differ).

## 4. Technical standards

- **Python 3.12+**, **Windows 10/11** host for production automation.
- **Ruff** for lint/format; prefer **`dict`**, **`X \| None`**, async MCP tools.
- **Testing:** Markers `requires_hardware`, `destructive`, etc.; CI skips hardware probes; see [`TESTING.md`](TESTING.md).

## 5. Success metrics (directional)

- Tool calls return structured **`success` / `error`** with recoverable guidance where feasible.
- **First connection** documented for common MCP clients (`README`, `glama.json`).
- **Docs** (`SAFETY`, `OPERATOR_PROTOCOL`, PRD, changelog) stay aligned with code.

## 6. References

| Doc | Purpose |
|-----|---------|
| [`SAFETY.md`](SAFETY.md) | Isolation, face opt-in, two-server model |
| [`OPERATOR_PROTOCOL.md`](OPERATOR_PROTOCOL.md) | Focus and foreground during automation |
| [`TESTING.md`](TESTING.md) | CI vs local, pytest markers |
| [`LLM_REPO_CONTEXT.md`](LLM_REPO_CONTEXT.md) | Canonical pointer for web chat repo context source |
| **mcp-central-docs** | `patterns/PYWINAUTO_MCP_SAFETY.md`, `standards/testing-environment-aware.md` |

---

*Version note: PRD updated with web_sota, REST API, LLM proxy, cameras, and testing strategy — 2026.*
