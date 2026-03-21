---
name: desktop-automation-protocol
description: Foreground and focus rules when driving Windows UI via pywinauto-mcp (step back from terminal/IDE; avoid focus fights).
---

# Desktop automation protocol (pywinauto-mcp)

## When this applies

The user wants to **start an app** and **test or automate it** using **pywinauto** / **pywinauto-mcp** tools.

## Tell the user

- After automation starts, **do not keep the terminal or IDE in the foreground** for typing or “helping.”
- **Do not Alt+Tab** to other apps (browser, mail, chat) while a click/type sequence is in progress — the **target app should keep focus**.
- If **HITL approval** appears, complete **only** that, then let the **target window** stay in front again.
- Prefer reading logs on a **second monitor** or between **paused** steps.

## Canonical docs in repo

- `docs/OPERATOR_PROTOCOL.md`
- `docs/SAFETY.md`

## MCP prompts (when server exposes prompts)

- `desktop_automation_operator_protocol`
- `desktop_automation_runbook`
