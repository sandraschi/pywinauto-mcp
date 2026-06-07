# Cua Driver parity roadmap (pywinauto-mcp)

**Reference:** [mcp-central-docs: CUA_DRIVER_AND_PYWINAUTO.md](file:///D:/Dev/repos/mcp-central-docs/patterns/CUA_DRIVER_AND_PYWINAUTO.md)

**Goal:** Approximate the [Cua Driver](https://cua.ai/docs/cua-driver/guide/getting-started/introduction) agent loop on Windows **without** abandoning fleet safety (HITL, kill switch, dry-run).

---

## Target agent loop

```text
automation_windows("find", title="LibreOffice Calc") → HWND
get_window_state(window_handle, capture_mode="som") → snapshot_id + elements[].element_index
automation_elements("click", window_handle, snapshot_id, element_index=14, dispatch="background")
get_window_state(...) → verify
```

---

## Phase checklist

### Phase 1 — Cua-shaped API

- [x] `capture_mode`: `ax` | `som` | `vision`
- [x] `get_window_state` — per-window snapshot + `snapshot_id`
- [x] `automation_elements` — `snapshot_id` + `element_index`
- [x] `PYWINAUTO_MCP_DISPATCH` default `foreground`; `background` UIA-first
- [x] `docs/CUA_PARITY.md`
- [x] Unit tests (`tests/test_cua_parity.py`)

### Phase 2 — Background honesty

- [x] `status=blocked`, `data.code=background_unavailable`
- [x] No `SetForegroundWindow` on read paths when dispatch env is `background`
- [x] Window-rect screenshot for `vision` / scoped `som`
- [x] [`OFFICE_BACKGROUND_MATRIX.md`](OFFICE_BACKGROUND_MATRIX.md)

### Phase 3 — Fleet & operator

- [x] `PYWINAUTO_MCP_TRAJECTORY_LOG=1` → JSONL in `%LOCALAPPDATA%\pywinauto-mcp\trajectories`
- [x] `pywinauto-mcp mcp-config` (stdio JSON snippet)
- [x] fleet-agent-mcp: [`docs/pywinauto-cua-loop.md`](file:///D:/Dev/repos/fleet-agent-mcp/docs/pywinauto-cua-loop.md)
- [x] [`OPERATOR_PROTOCOL.md`](OPERATOR_PROTOCOL.md) — foreground vs background profiles

### Phase 4 — Advanced parity

- [x] Virtual agent cursor overlay (`PYWINAUTO_MCP_AGENT_OVERLAY=1`)
- [x] Win32 `PostMessage` click path (`win32_window.postmessage_click_at`)
- [x] `cua_computer_use_screenshot` MCP tool (window-scoped, compat alias)

### E2E (LibreOffice + libreoffice-mcp fleet)

- [x] `tests/e2e/test_libreoffice_cua_loop.py` — live Calc: `get_window_state`, capture modes, snapshot click signal
- [x] Run: `uv run pytest -m e2e` (excluded from default `pytest` via `-m "not e2e"`)

---

## Environment variables

| Variable | Values | Default |
|----------|--------|---------|
| `PYWINAUTO_MCP_DISPATCH` | `foreground` \| `background` | `foreground` |
| `PYWINAUTO_MCP_TRAJECTORY_LOG` | `1` enables JSONL | off |
| `PYWINAUTO_MCP_AGENT_OVERLAY` | `1` shows agent marker | off |
| `PYWINAUTO_MCP_KILL_SWITCH` | `1` blocks mutations | off |
| `PYWINAUTO_E2E_SOFFICE` | Path to `soffice.exe` | auto-detect |

---

## Key modules

| File | Role |
|------|------|
| `snapshot_store.py` | Snapshot registry |
| `dispatch.py` | Foreground/background click chain |
| `win32_window.py` | Bbox grab, PostMessage |
| `trajectory.py` | JSONL logging |
| `agent_overlay.py` | Virtual cursor marker |
| `tools/window_state.py` | `get_window_state` |
| `tools/computer_use_compat.py` | `cua_computer_use_screenshot` |
| `cli.py` | `mcp-config` output |
