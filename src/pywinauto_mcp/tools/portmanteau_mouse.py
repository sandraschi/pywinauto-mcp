"""Mouse interaction portmanteau tool for PyWinAuto MCP.

PORTMANTEAU PATTERN RATIONALE:
Instead of creating 10+ separate tools (one per mouse operation), this tool consolidates related
mouse interaction operations into a single interface. This design:
- Prevents tool explosion (10+ tools → 1 tool) while maintaining full functionality
- Improves discoverability by grouping related operations together
- Reduces cognitive load when working with mouse automation tasks
- Follows FastMCP 2.13+ best practices for feature-rich MCP servers

SUPPORTED OPERATIONS:
- position: Get current cursor position
- move: Move mouse to absolute coordinates
- move_relative: Move mouse relative to current position
- click: Click at position or current location
- double_click: Double-click at position
- right_click: Right-click at position
- scroll: Scroll mouse wheel (vertical or horizontal)
- drag: Drag from one point to another
- hover: Move to position and hover for duration
"""

import logging
import time
from typing import Any, Literal

import pyautogui

# Import the FastMCP app instance
try:
    from pywinauto_mcp.app import app

    logger = logging.getLogger(__name__)
    logger.info("Successfully imported FastMCP app instance in portmanteau_mouse")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import FastMCP app in portmanteau_mouse: {e}")
    app = None

# Configure pyautogui
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True


if app is not None:
    logger.info("Registering portmanteau_mouse tool with FastMCP")

    @app.tool(
        name="automation_mouse",
        description="""Comprehensive mouse control tool for Windows automation tracking SOTA 2026.

SUPPORTED OPERATIONS:
- position: Returns current cursor coordinates.
- click: Executes relative or absolute button clicks.
- double_click: Performs two rapid clicks at the target location.
- right_click: Triggers contextual clicks.
- move: Relocates the cursor using absolute or relative coordinates.
- scroll: Manipulates the mouse wheel vertically or horizontally.
- drag: Smoothly moves objects between coordinates.
- hover: Pauses at location to trigger UI tooltips.

DIALOGIC RETURN PATTERN:
If coordinates are off-screen or target high-risk system areas, returns clarification_needed.

Examples:
    automation_mouse("position")
    automation_mouse("move", x=500, y=300)
    automation_mouse("click", button="right")

""",
    )
    def automation_mouse(
        operation: Literal[
            "position",  # Added "position" to Literal type hint
            "click",
            "double_click",
            "right_click",
            "move",
            "move_relative",
            "scroll",
            "drag",
            "hover",
        ],
        x: int | None = None,
        y: int | None = None,
        target_x: int | None = None,
        target_y: int | None = None,
        button: str = "left",
        amount: int = 0,
        horizontal: bool = False,
        duration: float = 0.0,
        hover_duration: float = 0.5,
    ) -> dict[str, Any]:
        """Comprehensive mouse control operations for Windows automation.

        PORTMANTEAU PATTERN RATIONALE:
        Consolidates cursor movement and clicking operations into a single tool to reduce
        API surface area while maintaining precise physical input control. Follows FastMCP
        2.14.3 patterns for stateful input tracking.

        SUPPORTED OPERATIONS:
        - click: Executes a single mouse button click at specified or current coordinates.
        - double_click: Performs two rapid clicks at the target location.
        - right_click: Triggers a contextual click at the target location.
        - move: Relocates the cursor to absolute screen coordinates.
        - move_relative: Shifts the cursor by a specified pixel offset from current position.
        - scroll: Manipulates the mouse wheel vertically or horizontally.
        - drag: Moves the cursor from start to end coordinates while holding a button.
        - hover: Places the cursor at a location for a specific duration to trigger tooltips.
        - position: Retrieves the current coordinates of the mouse cursor.

        DIALOGIC RETURN PATTERN:
        This tool implements the SOTA 2026 Dialogic Return Pattern for safety-critical UI
        interactions. If a mouse operation targets coordinates that are outside of specific
        security boundaries or are identified as ambiguous screen regions, the tool
        returns a clarification_needed status. In this state, the payload includes
        visual_context metadata and coordinate_options to allow the agent to verify
        the intended target before final execution.

        USAGE AND RECOVERY:
        Specify the operation and coordinates or relative offsets. In cases where the
        cursor fails to move or the target element is blocked, the tool returns
        diagnostic_info indicating the current cursor position and any potential OS
        interrupts. Agents should use the provided recovery_options to re-synchronize
        the input stream.

        Args:
            operation (str, required): The mouse action to perform.
            x (int | None): Absolute horizontal coordinate.
            y (int | None): Absolute vertical coordinate.
            target_x (int | None): Destination horizontal coordinate for drag operations.
            target_y (int | None): Destination vertical coordinate for drag operations.
            button (str): The specific mouse button to utilize (left, right, middle).
            amount (int): Scrolling distance or click frequency depending on context.
            horizontal (bool): Directional toggle for scrolling operations.
            duration (float): Time in seconds to complete a movement or drag.
            hover_duration (float): Time to stay at coordinates for hover operations.

        Returns:
            dict[str, Any]: Operation-specific result dictionary with sensor metadata and status.

        """
        try:
            timestamp = time.time()
            screen_width, screen_height = pyautogui.size()
            sensor_metadata = {
                "screen_resolution": (screen_width, screen_height),
                "timestamp": timestamp,
            }

            # === HITL SECURITY CHECK ===
            if operation != "position":
                try:
                    from pywinauto_mcp.app import approval_state

                    if not approval_state.is_approved():
                        # Format the details for user transparency
                        action_detail = f"Mouse: {operation}"
                        if x is not None and y is not None:
                            action_detail += f" at ({x}, {y})"
                        elif operation == "scroll":
                            action_detail += f" amount {amount}"

                        return {
                            "status": "clarification_needed",
                            "operation": operation,
                            "message": "SECURITY: Human approval required for UI automation.",
                            "hitl_prompt": f"Approve mouse action? [{action_detail}]",
                            "hitl_options": {
                                "approve_current": "Retries this action one-time",
                                "approve_window": "Approves all UI actions for 5 minutes",
                            },
                            "technical_details": {
                                "operation": operation,
                                "x": x,
                                "y": y,
                                "button": button,
                                "amount": amount,
                                "target_x": target_x,
                                "target_y": target_y,
                            },
                            "sensor_metadata": sensor_metadata,
                        }
                except ImportError:
                    logger.error("Failed to import approval_state for HITL check")
                    # Fallback to safety if state cannot be checked
                    return {
                        "status": "error",
                        "error": "Security subsystem unavailable (import error)",
                    }

            # === RATE / KILL SWITCH / DRY-RUN (see pywinauto_mcp.safety) ===
            from pywinauto_mcp.safety import before_mutation

            read_only = operation == "position"
            gate = before_mutation(read_only=read_only)
            if not gate.get("allow"):
                return {
                    "status": "blocked",
                    "code": gate.get("code"),
                    "message": gate.get("message", "Mutation blocked"),
                    "operation": operation,
                    "sensor_metadata": sensor_metadata,
                }
            if gate.get("dry_run"):
                return {
                    "status": "dry_run",
                    "message": gate.get("message"),
                    "operation": operation,
                    "x": x,
                    "y": y,
                    "sensor_metadata": sensor_metadata,
                }

            # === POSITION OPERATION ===
            if operation == "position":
                pos_x, pos_y = pyautogui.position()
                return {
                    "status": "success",
                    "operation": "position",
                    "x": pos_x,
                    "y": pos_y,
                    "position": (pos_x, pos_y),
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            # === MOVE OPERATION ===
            elif operation == "move":
                if x is None or y is None:
                    return {
                        "status": "error",
                        "operation": "move",
                        "error": "x and y parameters are required",
                        "timestamp": timestamp,  # Added timestamp
                    }
                pyautogui.moveTo(x, y, duration=duration)
                return {
                    "status": "success",
                    "operation": "move",
                    "x": x,
                    "y": y,
                    "duration": duration,
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            # === MOVE_RELATIVE OPERATION ===
            elif operation == "move_relative":
                if x is None or y is None:
                    return {
                        "status": "error",
                        "operation": "move_relative",
                        "error": "x and y parameters are required (as offsets)",
                    }
                current_x, current_y = pyautogui.position()
                new_x = current_x + x
                new_y = current_y + y
                pyautogui.moveTo(new_x, new_y, duration=duration)
                return {
                    "status": "success",
                    "operation": "move_relative",
                    "offset": (x, y),
                    "from_position": (current_x, current_y),
                    "to_position": (new_x, new_y),
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            # === CLICK OPERATION ===
            elif operation == "click":
                if x is not None and y is not None:
                    pyautogui.click(x, y, button=button)
                    position = (x, y)
                else:
                    pyautogui.click(button=button)
                    position = pyautogui.position()

                return {
                    "status": "success",
                    "operation": "click",
                    "position": position,
                    "button": button,
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            # === DOUBLE_CLICK OPERATION ===
            elif operation == "double_click":
                if x is not None and y is not None:
                    pyautogui.doubleClick(x, y, button=button)
                    position = (x, y)
                else:
                    pyautogui.doubleClick(button=button)
                    position = pyautogui.position()

                return {
                    "status": "success",
                    "operation": "double_click",
                    "position": position,
                    "button": button,
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            # === RIGHT_CLICK OPERATION ===
            elif operation == "right_click":
                if x is not None and y is not None:
                    pyautogui.rightClick(x, y)
                    position = (x, y)
                else:
                    pyautogui.rightClick()
                    position = pyautogui.position()

                return {
                    "status": "success",
                    "operation": "right_click",
                    "position": position,
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            # === SCROLL OPERATION ===
            elif operation == "scroll":
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y)

                if horizontal:
                    pyautogui.hscroll(amount)
                else:
                    pyautogui.scroll(amount)

                return {
                    "status": "success",
                    "operation": "scroll",
                    "amount": amount,
                    "direction": "horizontal" if horizontal else "vertical",
                    "position": (x, y) if x and y else pyautogui.position(),
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            # === DRAG OPERATION ===
            elif operation == "drag":
                if x is None or y is None:
                    return {
                        "status": "error",
                        "operation": "drag",
                        "error": "x and y (start coordinates) are required",
                    }
                if target_x is None or target_y is None:
                    return {
                        "status": "error",
                        "operation": "drag",
                        "error": "target_x and target_y are required",
                    }

                pyautogui.moveTo(x, y)
                pyautogui.drag(target_x - x, target_y - y, duration=duration, button=button)

                return {
                    "status": "success",
                    "operation": "drag",
                    "from_position": (x, y),
                    "to_position": (target_x, target_y),
                    "button": button,
                    "duration": duration,
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            # === HOVER OPERATION ===
            elif operation == "hover":
                if x is None or y is None:
                    return {
                        "status": "error",
                        "operation": "hover",
                        "error": "x and y parameters are required",
                    }

                pyautogui.moveTo(x, y, duration=duration)
                time.sleep(hover_duration)

                return {
                    "status": "success",
                    "operation": "hover",
                    "position": (x, y),
                    "hover_duration": hover_duration,
                    "timestamp": timestamp,
                    "sensor_metadata": sensor_metadata,
                }

            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "valid_operations": [
                        "position",
                        "move",
                        "move_relative",
                        "click",
                        "double_click",
                        "right_click",
                        "scroll",
                        "drag",
                        "hover",
                    ],
                }

        except Exception as e:
            return {
                "status": "error",
                "operation": operation,
                "error": str(e),
                "error_type": type(e).__name__,
            }


__all__ = ["automation_mouse"]
