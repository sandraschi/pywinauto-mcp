# Operator protocol — desktop automation (pywinauto-mcp)

When you ask to **start an application** and **test or drive it via pywinauto**, the automation only works if **one foreground story** is stable. This doc is for **humans** and for **agents** explaining the same rules to the user.

## Why this exists

- PyWinAuto drives **whatever window is focused** and the **real mouse/keyboard queue**.
- If you keep **the IDE, terminal, or chat** in front, automation may click/type the **wrong surface**, or fight you for focus.
- “Helping” by **switching apps mid-run** (Alt+Tab, clicking the terminal, opening another window) is the most common way to **flakify** a run.

## Rules (share with the user before the first click)

1. **Step back from the terminal / IDE** once the run has started — do not type in the terminal or bring the agent UI to the foreground unless you are answering **HITL approval** or **stopping** the run.
2. **Do not surface another app on purpose** (browser, mail, second IDE) while the workflow is driving the target app — let the **target app hold focus** unless the plan explicitly needs a different window.
3. **If you must read output**, prefer **side-by-side** or a **second monitor**, or wait for a **natural pause** between tool calls — avoid stealing focus from the app under test.
4. **HITL (approve_automation)** may appear for mouse/keyboard — when it does, **complete only that approval**, then **return focus** to the target app (or leave the desktop clear) as the workflow expects.
5. **Kill switch / dry-run** — see [`SAFETY.md`](SAFETY.md); automation is not a substitute for Sandbox/VM isolation when you need a disposable desktop.

## For agents (wording you can surface verbatim)

> “I’m going to start or test **{app}** using desktop automation. **Please don’t keep the terminal or IDE in the foreground** while clicks run — switch to **{app}** or leave it focused, and **avoid Alt+Tabbing** to other apps until I say the step is done. If you need to approve a prompt, do that only, then let the automated window stay on top.”

## Related

- [`SAFETY.md`](SAFETY.md) — HITL, env limits, two-server model with `virtualization-mcp`.
