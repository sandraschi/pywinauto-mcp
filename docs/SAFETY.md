# pywinauto-mcp — Safety & isolation

**Read this before enabling this server in an IDE.** Desktop automation is **host-powerful**; “sandbox safety” for **untrusted UI** requires a **second fleet server**, not pywinauto alone.

---

## 1. Two-server model (recommended for new users)

| Goal | Install |
|------|---------|
| **Drive the real Windows desktop** (your session) | **pywinauto-mcp** (this repo) + **`approve_automation`**, env limits below |
| **Disposable desktop** (Windows Sandbox / VM) for installs + UI tests | **Also install `virtualization-mcp`** (fleet repo) — launches Sandbox, maps `assets`, optional dev stack / AIRGAP |

**pywinauto-mcp does not spin up Windows Sandbox.** For **full** isolation, add **virtualization-mcp** to your MCP client and use it to **provision** the box; run **automation inside the guest** (script with pywinauto) or a test runner — see fleet doc below.

---

## 2. Built into this server (host session)

- **HITL:** `approve_automation` — required for mutating **mouse** / **keyboard** (except `automation_mouse("position")`).
- **Env:** `PYWINAUTO_MCP_KILL_SWITCH`, `PYWINAUTO_MCP_MAX_ACTIONS_PER_MINUTE`, `PYWINAUTO_MCP_DRY_RUN`.
- **Tool:** `automation_safety(status | reset_counters)`.

---

## 3. Fleet documentation (canonical)

Clone **mcp-central-docs** (sibling repo) and read:

- **`patterns/PYWINAUTO_MCP_SAFETY.md`** — sampling amplification, IDE chain rules, **sandboxed execution** (guest-side pywinauto + virtualization-mcp).
- **`patterns/FLEET_COMPUTER_USE_MCP.md`** — computer-use architecture, mitigations.

---

## 4. Do not

- Put **pywinauto-mcp** in the **default IDE chain** for **web-only** work — use **browser MCP** for Vite/webapps.
- Rely on **host** pywinauto to “click inside” the Windows Sandbox window — automate **inside** the guest session instead.
- Treat **OpenManus** + **openmanus-mcp** + **pywinauto** + **OpenClaw / Manus-class** autonomy as **low-friction** — that combination **multiplies** tool loops and sampling against **OS-wide** input. See **mcp-central-docs** `patterns/PYWINAUTO_MCP_SAFETY.md` § *OpenManus, openmanus-mcp, OpenClaw, Manus-class* and **integrations/openmanus.md** (Caution block).
