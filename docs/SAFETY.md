# pywinauto-mcp — Safety & isolation

**Read this before enabling this server in an IDE.** Desktop automation is **host-powerful**; “sandbox safety” for **untrusted UI** requires a **second fleet server**, not pywinauto alone.

**Foreground / focus:** If you automate “start app X and test it,” read **[OPERATOR_PROTOCOL.md](OPERATOR_PROTOCOL.md)** — the user should **step back from the terminal/IDE** so automation does not fight for focus.

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

---

## 5. Face recognition (`automation_face`) — opt-in, purpose, and data

The **`automation_face`** tool is **off by default**. Two steps are required to expose it:

1. **Operator opt-in (runtime):** set **`PYWINAUTO_MCP_ENABLE_FACE=1`** (or `true` / `yes` / `on`) in the server environment (see **`automation_safety(status)`** — `face_tool_opt_in` / `PYWINAUTO_MCP_ENABLE_FACE`).
2. **Dependencies:** install the **`face`** extra (see `pyproject.toml`) so the face-recognition stack is available.

Without both, the server does **not** register **`automation_face`**; other portmanteau tools are unchanged.

### Why it exists

It supports **explicit, local** workflows for **operator presence** at the machine: e.g. a coarse “is the intended person still at this PC?” signal to **reduce casual misuse** if someone else sits down at an unlocked session while **desktop automation** is in play. That is **not** strong authentication, not a compliance control, and not a substitute for locking the screen — but it can **raise the bar** together with **HITL**, **env limits**, and normal session hygiene.

### Communication

Describe it as **optional**, **consent-based**, **local**, and **for operator presence** — not for covert or remote monitoring. Demos and README should state that clearly.

### Treat face data as sensitive

- Stored encodings and images under **`data/known_faces/`** (or paths your deployment uses) are **biometric-adjacent** — protect them like **secrets** (disk encryption, backups policy, who can read the repo).
- **Do not** imply that face match **prevents** misuse; it only **narrows** risk when integrated thoughtfully.

### If you do not need it

Leave **`PYWINAUTO_MCP_ENABLE_FACE`** unset (default). Do not install the **`face`** extra. Window/element automation does not require face features.

### Camera hardware (`capture`)

**Supported:** Any camera that Windows exposes to **OpenCV** via `cv2.VideoCapture(index)` — typically:

- **Integrated / built-in** laptop camera (often listed as *Integrated Camera* in Device Manager).
- **Standard USB webcams** (UVC / “USB Video Device” class).

Use the **`camera_index`** argument (`0`, `1`, …) to pick the device. Order is **OS enumeration order**, not a fixed name: the built-in cam is often **`0`** when it is the default; an external USB cam may be **`0`** or **`1`** depending on what Windows assigns. There is **no** special product name “usbcam” in the API — that is just informal shorthand some people use for **USB UVC** webcams.

**Out of scope (for now):** **TP-Link Tapo**, other **IP / RTSP / cloud** cameras, and stacks that need vendor apps or RTSP URLs. Those are unnecessarily complicated for local **`capture`**; use a **built-in or USB UVC** camera instead.
