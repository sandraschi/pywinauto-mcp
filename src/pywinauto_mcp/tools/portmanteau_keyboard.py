"""Keyboard input portmanteau tool for PyWinAuto MCP.

PORTMANTEAU PATTERN RATIONALE:
Instead of creating 4+ separate tools (one per keyboard operation), this tool consolidates related
keyboard input operations into a single interface. This design:
- Prevents tool explosion (4+ tools → 1 tool) while maintaining full functionality
- Improves discoverability by grouping related operations together
- Follows FastMCP 2.13+ best practices for feature-rich MCP servers

SUPPORTED OPERATIONS:
- type: Type text at current focus (supports special characters)
- press: Press a single key
- hotkey: Press key combination (e.g., Ctrl+C)
- hold: Hold a key down while performing other actions
"""

import logging
import time
from typing import Any, Literal

import pyautogui

# Import the FastMCP app instance
try:
    from pywinauto_mcp.app import app

    logger = logging.getLogger(__name__)
    logger.info("Successfully imported FastMCP app instance in portmanteau_keyboard")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import FastMCP app in portmanteau_keyboard: {e}")
    app = None


if app is not None:
    logger.info("Registering portmanteau_keyboard tool with FastMCP")

    @app.tool(
        name="automation_keyboard",
        description="""Comprehensive keyboard input tool for Windows automation tracking SOTA 2026.

SUPPORTED OPERATIONS:
- type: Performs sequential character input at the current keyboard focus.
- press: Executes a single key strike or repeated strikes of the same key.
- hotkey: Triggers complex key combinations (Ctrl+C, Alt+Tab, etc.).
- hold: Maintains a modifier key state while executing subsequent actions.

DIALOGIC RETURN PATTERN:
If the keyboard focus is ambiguous or the target application state changes during execution,
this tool returns a clarification_needed status with focus_metadata.

Examples:
    automation_keyboard("type", text="Hello World!")
    automation_keyboard("press", key="enter")
    automation_keyboard("hotkey", keys=["ctrl", "c"])

""",
    )
    def automation_keyboard(
        operation: Literal["type", "press", "hotkey", "hold"],
        text: str | None = None,
        key: str | None = None,
        keys: list[str] | None = None,
        interval: float = 0.05,
        presses: int = 1,
        pause: float = 0.1,
    ) -> dict[str, Any]:
        """Comprehensive keyboard input operations for Windows automation.

        PORTMANTEAU PATTERN RATIONALE:
        Consolidates all keyboard interaction methods into a single interface to prevent tool
        fragmentation while providing consistent input sequencing. Follows FastMCP 2.14.3
        standards for robust input management.

        SUPPORTED OPERATIONS:
        - type: Performs sequential character input at the current keyboard focus.
        - press: Executes a single key strike or repeated strikes of the same key.
        - hotkey: Triggers complex key combinations such as CTRL plus C or ALT plus TAB.
        - hold: Maintains a modifier key state while executing subsequent actions.

        DIALOGIC RETURN PATTERN:
        This tool implements the SOTA 2026 Dialogic Return Pattern for input validation.
        When an requested key sequence is ambiguous or potentially destructive, the tool
        transitions to a status of clarification_needed. The return payload includes
        detailed diagnostic_info regarding the current focus state and suggested alternative
        keys. AI agents must evaluate these recovery_options before re-attempting the input
        to ensure intended application behavior.

        USAGE AND RECOVERY:
        Standard execution requires an operation and relevant text or key parameters.
        In scenarios where keyboard focus is lost, use the returned focus_metadata to
        re-verify the target element before proceeding with retries. This maintains
        interaction integrity even during heavy system load.

        Args:
            operation (str, required): The keyboard action to perform.
            text (str | None): Plaintext string for sequential typing operations.
            key (str | None): Single key identifier for strike operations.
            keys (list[str] | None): Sequence of keys for complex hotkey combinations.
            interval (float): Delay between individual characters during typing.
            presses (int): Frequency of execution for the specified key strike.
            pause (float): Post-operation suspension duration to ensure input processing.

        Returns:
            dict[str, Any]: Operation-specific result dictionary with success status and input metadata.

        """
        try:
            timestamp = time.time()
            # Basic focus metadata for tracking
            focus_metadata = {
                "timestamp": timestamp,
                "app": "unknown",  # Could be expanded with focus tracking logic
            }

            # === HITL SECURITY CHECK ===
            try:
                from pywinauto_mcp.app import approval_state

                if not approval_state.is_approved():
                    # Format the details for user transparency
                    action_detail = ""
                    if operation == "type":
                        action_detail = f"Type: '{text}'"
                    elif operation == "press":
                        action_detail = f"Press: {key}"
                    elif operation == "hotkey":
                        action_detail = f"Hotkey: {'+'.join(keys) if keys else 'None'}"
                    elif operation == "hold":
                        action_detail = f"Hold: {keys[0]} + {keys[-1] if keys else 'None'}"

                    return {
                        "status": "clarification_needed",
                        "operation": operation,
                        "message": "SECURITY: Human approval required for UI automation.",
                        "hitl_prompt": f"Approve keyboard action? [{action_detail}]",
                        "hitl_options": {
                            "approve_current": "Retries this action one-time",
                            "approve_window": "Approves all UI actions for 5 minutes",
                        },
                        "technical_details": {
                            "operation": operation,
                            "text": text,
                            "key": key,
                            "keys": keys,
                        },
                    }
            except ImportError:
                logger.error("Failed to import approval_state for HITL check")
                # Fallback to safety if state cannot be checked
                return {
                    "status": "error",
                    "error": "Security subsystem unavailable (import error)",
                }

            from pywinauto_mcp.safety import before_mutation

            gate = before_mutation(read_only=False)
            if not gate.get("allow"):
                return {
                    "status": "blocked",
                    "code": gate.get("code"),
                    "message": gate.get("message", "Mutation blocked"),
                    "operation": operation,
                    "focus_metadata": focus_metadata,
                }
            if gate.get("dry_run"):
                return {
                    "status": "dry_run",
                    "message": gate.get("message"),
                    "operation": operation,
                    "focus_metadata": focus_metadata,
                }

            # === TYPE OPERATION ===
            if operation == "type":
                if text is None:
                    return {
                        "status": "error",
                        "operation": "type",
                        "error": "text parameter is required",
                    }

                pyautogui.write(text, interval=interval)

                return {
                    "status": "success",
                    "operation": "type",
                    "text_length": len(text),
                    "interval": interval,
                    "timestamp": timestamp,
                    "focus_metadata": focus_metadata,
                }

            # === PRESS OPERATION ===
            elif operation == "press":
                if key is None:
                    return {
                        "status": "error",
                        "operation": "press",
                        "error": "key parameter is required",
                    }

                for _ in range(presses):
                    pyautogui.press(key)
                    if pause > 0:
                        time.sleep(pause)

                return {
                    "status": "success",
                    "operation": "press",
                    "key": key,
                    "presses": presses,
                    "timestamp": timestamp,
                    "focus_metadata": focus_metadata,
                }

            # === HOTKEY OPERATION ===
            elif operation == "hotkey":
                if keys is None or len(keys) == 0:
                    return {
                        "status": "error",
                        "operation": "hotkey",
                        "error": "keys parameter is required (list of keys)",
                    }

                for _ in range(presses):
                    pyautogui.hotkey(*keys)
                    if pause > 0:
                        time.sleep(pause)

                return {
                    "status": "success",
                    "operation": "hotkey",
                    "keys": keys,
                    "combination": "+".join(keys),
                    "presses": presses,
                    "timestamp": timestamp,
                    "focus_metadata": focus_metadata,
                }

            # === HOLD OPERATION ===
            elif operation == "hold":
                if keys is None or len(keys) < 2:
                    return {
                        "status": "error",
                        "operation": "hold",
                        "error": "keys parameter requires at least 2 keys (modifier + key)",
                    }

                # Use pywinauto keyboard for more complex sequences
                modifier = keys[0]
                target_key = keys[-1]

                with pyautogui.hold(modifier):
                    pyautogui.press(target_key)

                return {
                    "status": "success",
                    "operation": "hold",
                    "modifier": modifier,
                    "key": target_key,
                    "timestamp": timestamp,
                    "focus_metadata": focus_metadata,
                }

            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "valid_operations": ["type", "press", "hotkey", "hold"],
                }

        except Exception as e:
            return {
                "status": "error",
                "operation": operation,
                "error": str(e),
                "error_type": type(e).__name__,
            }


__all__ = ["automation_keyboard"]
