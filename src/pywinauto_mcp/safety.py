"""Rate limits, kill switch, and dry-run for desktop UI automation (FastMCP + sampling amplification).

Vendor "My Computer"–style products add guardrails; this module adds **server-side** belts for
self-hosted pywinauto-mcp. See mcp-central-docs: patterns/PYWINAUTO_MCP_SAFETY.md
"""

from __future__ import annotations

import os
import time
from collections import deque
from typing import Any

# --- Environment (document in README + central docs) ---
ENV_KILL_SWITCH = "PYWINAUTO_MCP_KILL_SWITCH"
ENV_MAX_PER_MINUTE = "PYWINAUTO_MCP_MAX_ACTIONS_PER_MINUTE"
ENV_DRY_RUN = "PYWINAUTO_MCP_DRY_RUN"


def _truthy(val: str | None) -> bool:
    if val is None:
        return False
    return val.lower() in ("1", "true", "yes", "on")


class MutationGate:
    """Sliding window: mutating UI actions per rolling 60s + lifetime counter."""

    def __init__(self) -> None:
        self._times: deque[float] = deque()
        self._total: int = 0

    def reset_window(self) -> None:
        self._times.clear()

    def snapshot(self) -> dict[str, Any]:
        now = time.time()
        while self._times and now - self._times[0] > 60.0:
            self._times.popleft()
        cap = int(os.getenv(ENV_MAX_PER_MINUTE, "120"))
        return {
            "actions_last_60s": len(self._times),
            "max_actions_per_minute": cap,
            "total_mutations_session": self._total,
            "kill_switch": _truthy(os.getenv(ENV_KILL_SWITCH)),
            "dry_run": _truthy(os.getenv(ENV_DRY_RUN)),
        }

    def before_mutation(self, *, read_only: bool) -> dict[str, Any]:
        """Return whether to execute a mutating pyautogui/pywinauto action."""
        if read_only:
            return {"allow": True, "dry_run": False, "code": "ok"}

        if _truthy(os.getenv(ENV_KILL_SWITCH)):
            return {
                "allow": False,
                "dry_run": False,
                "code": "kill_switch",
                "message": f"{ENV_KILL_SWITCH}=1 blocks all mutating automation.",
            }

        if _truthy(os.getenv(ENV_DRY_RUN)):
            self._record()
            return {
                "allow": True,
                "dry_run": True,
                "code": "dry_run",
                "message": f"{ENV_DRY_RUN}=1: mutation not executed; counted for metrics.",
            }

        cap = int(os.getenv(ENV_MAX_PER_MINUTE, "120"))
        now = time.time()
        while self._times and now - self._times[0] > 60.0:
            self._times.popleft()
        if len(self._times) >= cap:
            return {
                "allow": False,
                "dry_run": False,
                "code": "rate_limit",
                "message": f"Exceeded {cap} mutating actions per rolling 60s. Slow down or raise {ENV_MAX_PER_MINUTE}.",
            }
        self._record()
        return {"allow": True, "dry_run": False, "code": "ok"}

    def _record(self) -> None:
        self._times.append(time.time())
        self._total += 1


_gate = MutationGate()


def get_gate() -> MutationGate:
    return _gate


def before_mutation(*, read_only: bool) -> dict[str, Any]:
    return _gate.before_mutation(read_only=read_only)
