"""FastMCP application instance for PyWinAuto MCP - Portmanteau Edition.

This module creates the FastMCP app instance to avoid circular imports
between main.py and the tools modules.

FastMCP 2.13.1 compliant.
"""

import logging
import os
import time

logger = logging.getLogger(__name__)

# Import FastMCP and create the app instance
try:
    from fastmcp import FastMCP

    logger.info("Successfully imported FastMCP")

    # Create the FastMCP app instance with FastMCP 2.13+ features
    app = FastMCP(
        name="pywinauto-mcp",
        version="0.3.2",
        # FastMCP 2.13+ supports additional configuration
    )

    logger.info("FastMCP 2.13.1 app instance created successfully")

except ImportError as e:
    logger.critical(f"Failed to import FastMCP: {e}")
    logger.critical("Please install FastMCP 2.13.1+ using: pip install fastmcp>=2.13.1")
    app = None
except Exception as e:
    logger.critical(f"Error creating FastMCP app: {e}", exc_info=True)
    app = None

# Check OCR dependencies
try:
    import pytesseract  # noqa: F401
    from PIL import Image, ImageGrab  # noqa: F401

    OCR_AVAILABLE = True
    logger.info("OCR dependencies available")
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR dependencies not available")


# --- HITL SECURITY LAYER ---


class ApprovalState:
    """Manages the Human-in-the-Loop (HITL) approval window for UI automation."""

    def __init__(self):
        self.safe_window_until: float = 0.0

    def is_approved(self) -> bool:
        """Checks if the current action is within a safe approval window."""
        return time.time() < self.safe_window_until

    def set_safe_window(self, duration_minutes: float):
        """Sets a safe window for the next N minutes."""
        self.safe_window_until = time.time() + (duration_minutes * 60)

    def clear(self):
        """Clears the approval window immediately."""
        self.safe_window_until = 0.0


# Global approval state instance
approval_state = ApprovalState()


@app.tool()
def approve_automation(duration_minutes: float = 5.0) -> dict:
    """Approve UI automation actions for a specified duration to prevent repetitive prompts.

    Args:
        duration_minutes: Number of minutes to allow automated actions (default 5.0).

    """
    approval_state.set_safe_window(duration_minutes)
    until_str = time.strftime("%H:%M:%S", time.localtime(approval_state.safe_window_until))
    return {
        "status": "success",
        "message": f"UI automation approved until {until_str} ({duration_minutes} minutes)",
        "safe_window_until": approval_state.safe_window_until,
    }


@app.tool()
def automation_safety(
    operation: str = "status",
) -> dict:
    """Inspect or reset server-side safety limits (rate, kill switch, dry-run). Not a substitute for HITL.

    Operations:
    - status: Counters + env flags (PYWINAUTO_MCP_KILL_SWITCH, DRY_RUN, MAX_ACTIONS_PER_MINUTE).
    - reset_counters: Clear rolling window counters (does not disable kill switch).

    See README "Safety" and mcp-central-docs patterns/PYWINAUTO_MCP_SAFETY.md.
    """
    from pywinauto_mcp.safety import ENV_DRY_RUN, ENV_KILL_SWITCH, ENV_MAX_PER_MINUTE, get_gate

    gate = get_gate()
    op = (operation or "status").lower().strip()
    if op == "reset_counters":
        gate.reset_window()
        return {
            "status": "success",
            "message": "Rolling action window cleared.",
            "snapshot": gate.snapshot(),
        }
    if op == "status":
        snap = gate.snapshot()
        return {
            "status": "success",
            "snapshot": snap,
            "env": {
                ENV_KILL_SWITCH: os.getenv(ENV_KILL_SWITCH),
                ENV_DRY_RUN: os.getenv(ENV_DRY_RUN),
                ENV_MAX_PER_MINUTE: os.getenv(ENV_MAX_PER_MINUTE),
            },
            "hitl": {"safe_window_until": approval_state.safe_window_until},
        }
    return {
        "status": "error",
        "error": f"Unknown operation: {operation}. Use status or reset_counters.",
    }
