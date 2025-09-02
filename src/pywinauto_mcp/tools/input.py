"""
Input tools for PyWinAuto MCP.

This module provides functions for simulating keyboard input, mouse movements,
and other input-related operations.
"""
import logging
import time
from typing import Dict, List, Optional, Union, Any

import pywinauto.keyboard as keyboard
import pywinauto.mouse as mouse
from pywinauto.findwindows import ElementNotFoundError, ElementAmbiguousError
from pywinauto.base_wrapper import ElementNotVisible

from .utils import (
    register_tool,
    validate_window_handle,
    get_desktop,
    SuccessResponse,
    ErrorResponse,
    timer
)

logger = logging.getLogger(__name__)

__all__ = [
    'type_text',
    'press_key',
    'press_hotkey',
    'move_mouse',
    'drag_mouse',
    'scroll_mouse',
    'get_mouse_position',
    'wait_for_element',
    'wait_for_element_visible',
    'wait_for_element_enabled',
    'wait_for_element_not_visible',
    'wait_for_element_not_enabled'
]

@register_tool(
    name="type_text",
    description="Types text at the current keyboard focus or a specified element.",
    category="input"
)
def type_text(
    text: str,
    window_handle: Optional[int] = None,
    control_id: Optional[str] = None,
    interval: float = 0.0,
    with_spaces: bool = True,
    with_tabs: bool = True,
    with_newlines: bool = True,
    pause: float = 0.01
) -> Dict[str, Any]:
    """
    Type text at the current keyboard focus or a specified element.

    Args:
        text: The text to type
        window_handle: Optional handle of the parent window (required if control_id is provided)
        control_id: Optional control ID of the element to type into
        interval: Optional delay between keystrokes in seconds
        with_spaces: Whether to include spaces in the typed text
        with_tabs: Whether to include tabs in the typed text
        with_newlines: Whether to include newlines in the typed text
        pause: Pause after typing in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not text:
        return ErrorResponse(
            error="No text provided to type",
            error_type="InvalidArgument"
        ).dict()
    
    if control_id and not window_handle:
        return ErrorResponse(
            error="window_handle is required when control_id is provided",
            error_type="InvalidArgument"
        ).dict()
    
    if window_handle and not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Typing text (length: {len(text)}) into {'control ' + control_id if control_id else 'keyboard focus'}"):
            # If control_id is provided, set focus to the element first
            if control_id:
                window = get_desktop().window(handle=window_handle)
                element = window.child_window(control_id=control_id)
                
                if not element.exists():
                    return ErrorResponse(
                        error=f"Element with control_id '{control_id}' not found",
                        error_type="ElementNotFound"
                    ).dict()
                
                if not element.is_visible():
                    return ErrorResponse(
                        error=f"Element with control_id '{control_id}' is not visible",
                        error_type="ElementNotVisible"
                    ).dict()
                
                if not element.is_enabled():
                    return ErrorResponse(
                        error=f"Element with control_id '{control_id}' is not enabled",
                        error_type="ElementNotEnabled"
                    ).dict()
                
                # Set focus to the element
                element.set_focus()
                # Wait a bit for the focus to take effect
                time.sleep(0.1)
            
            # Type the text
            keyboard.send_keys(
                text,
                pause=interval,
                with_spaces=with_spaces,
                with_tabs=with_tabs,
                with_newlines=with_newlines,
                pause_between_events=pause
            )
            
            return SuccessResponse(
                data={"message": f"Successfully typed {len(text)} characters"}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error typing text: {str(e)}",
            error_type="InputError"
        ).dict()

@register_tool(
    name="press_key",
    description="Presses a key or combination of keys.",
    category="input"
)
def press_key(
    keys: Union[str, List[str]],
    presses: int = 1,
    interval: float = 0.1,
    pause: float = 0.1
) -> Dict[str, Any]:
    """
    Press a key or combination of keys.

    Args:
        keys: The key or list of keys to press (e.g., 'a', 'ctrl+c', ['ctrl', 'c'])
        presses: Number of times to press the key(s)
        interval: Delay between repeated presses in seconds
        pause: Pause after pressing in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not keys:
        return ErrorResponse(
            error="No keys provided to press",
            error_type="InvalidArgument"
        ).dict()
    
    if presses < 1:
        return ErrorResponse(
            error="Number of presses must be at least 1",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Pressing keys: {keys} (presses: {presses})"):
            # Convert single key to list if needed
            if isinstance(keys, str):
                keys = [keys]
            
            # Press the keys the specified number of times
            for _ in range(presses):
                keyboard.send_keys(
                    keys,
                    pause=interval
                )
                
                if pause > 0 and _ < presses - 1:  # Don't pause after the last press
                    time.sleep(pause)
            
            return SuccessResponse(
                data={"message": f"Successfully pressed keys: {keys}"}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error pressing keys: {str(e)}",
            error_type="InputError"
        ).dict()

@register_tool(
    name="press_hotkey",
    description="Presses a combination of keys (hotkey/shortcut).",
    category="input"
)
def press_hotkey(
    *keys: str,
    presses: int = 1,
    interval: float = 0.1,
    pause: float = 0.1
) -> Dict[str, Any]:
    """
    Press a combination of keys (hotkey/shortcut).

    Args:
        *keys: The keys to press simultaneously (e.g., 'ctrl', 'c')
        presses: Number of times to press the hotkey
        interval: Delay between repeated presses in seconds
        pause: Pause after pressing in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not keys:
        return ErrorResponse(
            error="No keys provided for hotkey",
            error_type="InvalidArgument"
        ).dict()
    
    if presses < 1:
        return ErrorResponse(
            error="Number of presses must be at least 1",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Pressing hotkey: {'+'.join(keys)} (presses: {presses})"):
            # Press the hotkey the specified number of times
            for _ in range(presses):
                keyboard.send_combinations(keys)
                
                if pause > 0 and _ < presses - 1:  # Don't pause after the last press
                    time.sleep(pause)
            
            return SuccessResponse(
                data={"message": f"Successfully pressed hotkey: {'+'.join(keys)}"}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error pressing hotkey: {str(e)}",
            error_type="InputError"
        ).dict()

@register_tool(
    name="move_mouse",
    description="Moves the mouse cursor to the specified coordinates.",
    category="input"
)
def move_mouse(
    x: int,
    y: int,
    relative: bool = False,
    duration: float = 0.0,
    tween: Optional[str] = None
) -> Dict[str, Any]:
    """
    Move the mouse cursor to the specified coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
        relative: If True, coordinates are relative to the current position
        duration: Time in seconds to take for the movement (0 for instant)
        tween: Tweening function for the movement (e.g., 'linear', 'easeInOutQuad')

    Returns:
        Dict containing the result of the operation
    """
    try:
        with timer(f"Moving mouse to ({x}, {y}) {'relative' if relative else 'absolute'}"):
            if relative:
                mouse.move((x, y), duration=duration, tween=tween)
            else:
                mouse.move(coords=(x, y), duration=duration, tween=tween)
            
            return SuccessResponse(
                data={"message": f"Mouse moved to ({x}, {y})"}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error moving mouse: {str(e)}",
            error_type="InputError"
        ).dict()

@register_tool(
    name="drag_mouse",
    description="Drags the mouse from one point to another.",
    category="input"
)
def drag_mouse(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    button: str = "left",
    duration: float = 0.5,
    tween: Optional[str] = None
) -> Dict[str, Any]:
    """
    Drag the mouse from one point to another.

    Args:
        x1: Starting X coordinate
        y1: Starting Y coordinate
        x2: Ending X coordinate
        y2: Ending Y coordinate
        button: Mouse button to use ("left", "right", "middle")
        duration: Time in seconds to take for the drag
        tween: Tweening function for the movement

    Returns:
        Dict containing the result of the operation
    """
    if button.lower() not in ["left", "right", "middle"]:
        return ErrorResponse(
            error=f"Invalid button: {button}. Must be one of: left, right, middle",
            error_type="InvalidArgument"
        ).dict()
    
    if duration < 0:
        return ErrorResponse(
            error="Duration must be a non-negative number",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Dragging mouse from ({x1}, {y1}) to ({x2}, {y2}) with {button} button"):
            # Move to starting position
            mouse.move(coords=(x1, y1))
            
            # Press the mouse button
            mouse.press(button=button, coords=(x1, y1))
            
            try:
                # Move to ending position
                if duration > 0:
                    # For smooth dragging, we need to implement our own tweening
                    # since pywinauto's mouse.drag() doesn't support duration
                    import math
                    
                    steps = max(2, int(duration * 100))  # At least 2 steps
                    for i in range(steps + 1):
                        t = i / steps
                        
                        # Apply tweening if specified
                        if tween == "easeInOutQuad":
                            # Ease in/out quadratic
                            if t < 0.5:
                                t = 2 * t * t
                            else:
                                t = -1 + (4 - 2 * t) * t
                        elif tween == "linear" or not tween:
                            # Linear (default)
                            pass
                        # Add more tweening functions as needed
                        
                        # Calculate intermediate position
                        x = int(x1 + t * (x2 - x1))
                        y = int(y1 + t * (y2 - y1))
                        
                        # Move to intermediate position
                        mouse.move(coords=(x, y))
                        
                        # Small delay between steps for smooth movement
                        if i < steps:
                            time.sleep(duration / steps)
                else:
                    # Instant movement
                    mouse.move(coords=(x2, y2))
                
            finally:
                # Always release the mouse button, even if an error occurs
                mouse.release(button=button, coords=(x2, y2))
            
            return SuccessResponse(
                data={"message": f"Successfully dragged from ({x1}, {y1}) to ({x2}, {y2})"}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error dragging mouse: {str(e)}",
            error_type="InputError"
        ).dict()

@register_tool(
    name="scroll_mouse",
    description="Scrolls the mouse wheel.",
    category="input"
)
def scroll_mouse(
    clicks: int,
    x: Optional[int] = None,
    y: Optional[int] = None,
    horizontal: bool = False
) -> Dict[str, Any]:
    """
    Scroll the mouse wheel.

    Args:
        clicks: Number of clicks to scroll (positive for up/right, negative for down/left)
        x: X coordinate to scroll at (None for current position)
        y: Y coordinate to scroll at (None for current position)
        horizontal: If True, scroll horizontally; otherwise scroll vertically

    Returns:
        Dict containing the result of the operation
    """
    if clicks == 0:
        return ErrorResponse(
            error="Number of clicks must be non-zero",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Scrolling {'horizontally' if horizontal else 'vertically'} by {clicks} clicks at ({x or 'current'}, {y or 'current'})"):
            # Move to the specified coordinates if provided
            if x is not None and y is not None:
                mouse.move(coords=(x, y))
            
            # Scroll the mouse wheel
            if horizontal:
                mouse.horizontal_scroll(clicks, (x, y) if x is not None and y is not None else None)
            else:
                mouse.vertical_scroll(clicks, (x, y) if x is not None and y is not None else None)
            
            return SuccessResponse(
                data={"message": f"Successfully scrolled {'horizontally' if horizontal else 'vertically'} by {clicks} clicks"}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error scrolling mouse: {str(e)}",
            error_type="InputError"
        ).dict()

@register_tool(
    name="get_mouse_position",
    description="Gets the current mouse cursor position.",
    category="input"
)
def get_mouse_position() -> Dict[str, Any]:
    """
    Get the current mouse cursor position.

    Returns:
        Dict containing the mouse coordinates
    """
    try:
        with timer("Getting mouse position"):
            x, y = mouse.get_cursor_pos()
            
            return SuccessResponse(
                data={"x": x, "y": y}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting mouse position: {str(e)}",
            error_type="InputError"
        ).dict()

@register_tool(
    name="wait_for_element",
    description="Waits for an element to exist.",
    category="input"
)
def wait_for_element(
    window_handle: int,
    control_id: str,
    timeout: float = 10.0,
    retry_interval: float = 0.5
) -> Dict[str, Any]:
    """
    Wait for an element to exist.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to wait for
        timeout: Maximum time to wait in seconds
        retry_interval: Time to wait between retries in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if not control_id:
        return ErrorResponse(
            error="control_id is required",
            error_type="InvalidArgument"
        ).dict()
    
    if timeout <= 0:
        return ErrorResponse(
            error="Timeout must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    if retry_interval <= 0:
        return ErrorResponse(
            error="Retry interval must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Waiting for element with control_id '{control_id}' (timeout: {timeout}s)"):
            window = get_desktop().window(handle=window_handle)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                element = window.child_window(control_id=control_id)
                if element.exists():
                    return SuccessResponse(
                        data={"message": f"Element with control_id '{control_id}' found"}
                    ).dict()
                
                time.sleep(retry_interval)
            
            return ErrorResponse(
                error=f"Timed out waiting for element with control_id '{control_id}'",
                error_type="TimeoutError"
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error waiting for element: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="wait_for_element_visible",
    description="Waits for an element to be visible.",
    category="input"
)
def wait_for_element_visible(
    window_handle: int,
    control_id: str,
    timeout: float = 10.0,
    retry_interval: float = 0.5
) -> Dict[str, Any]:
    """
    Wait for an element to be visible.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to wait for
        timeout: Maximum time to wait in seconds
        retry_interval: Time to wait between retries in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if not control_id:
        return ErrorResponse(
            error="control_id is required",
            error_type="InvalidArgument"
        ).dict()
    
    if timeout <= 0:
        return ErrorResponse(
            error="Timeout must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    if retry_interval <= 0:
        return ErrorResponse(
            error="Retry interval must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Waiting for element with control_id '{control_id}' to be visible (timeout: {timeout}s)"):
            window = get_desktop().window(handle=window_handle)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                element = window.child_window(control_id=control_id)
                if element.exists() and element.is_visible():
                    return SuccessResponse(
                        data={"message": f"Element with control_id '{control_id}' is now visible"}
                    ).dict()
                
                time.sleep(retry_interval)
            
            return ErrorResponse(
                error=f"Timed out waiting for element with control_id '{control_id}' to be visible",
                error_type="TimeoutError"
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error waiting for element to be visible: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="wait_for_element_enabled",
    description="Waits for an element to be enabled.",
    category="input"
)
def wait_for_element_enabled(
    window_handle: int,
    control_id: str,
    timeout: float = 10.0,
    retry_interval: float = 0.5
) -> Dict[str, Any]:
    """
    Wait for an element to be enabled.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to wait for
        timeout: Maximum time to wait in seconds
        retry_interval: Time to wait between retries in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if not control_id:
        return ErrorResponse(
            error="control_id is required",
            error_type="InvalidArgument"
        ).dict()
    
    if timeout <= 0:
        return ErrorResponse(
            error="Timeout must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    if retry_interval <= 0:
        return ErrorResponse(
            error="Retry interval must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Waiting for element with control_id '{control_id}' to be enabled (timeout: {timeout}s)"):
            window = get_desktop().window(handle=window_handle)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                element = window.child_window(control_id=control_id)
                if element.exists() and element.is_enabled():
                    return SuccessResponse(
                        data={"message": f"Element with control_id '{control_id}' is now enabled"}
                    ).dict()
                
                time.sleep(retry_interval)
            
            return ErrorResponse(
                error=f"Timed out waiting for element with control_id '{control_id}' to be enabled",
                error_type="TimeoutError"
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error waiting for element to be enabled: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="wait_for_element_not_visible",
    description="Waits for an element to not be visible.",
    category="input"
)
def wait_for_element_not_visible(
    window_handle: int,
    control_id: str,
    timeout: float = 10.0,
    retry_interval: float = 0.5
) -> Dict[str, Any]:
    """
    Wait for an element to not be visible.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to wait for
        timeout: Maximum time to wait in seconds
        retry_interval: Time to wait between retries in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if not control_id:
        return ErrorResponse(
            error="control_id is required",
            error_type="InvalidArgument"
        ).dict()
    
    if timeout <= 0:
        return ErrorResponse(
            error="Timeout must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    if retry_interval <= 0:
        return ErrorResponse(
            error="Retry interval must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Waiting for element with control_id '{control_id}' to not be visible (timeout: {timeout}s)"):
            window = get_desktop().window(handle=window_handle)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                element = window.child_window(control_id=control_id)
                if not element.exists() or not element.is_visible():
                    return SuccessResponse(
                        data={"message": f"Element with control_id '{control_id}' is no longer visible"}
                    ).dict()
                
                time.sleep(retry_interval)
            
            return ErrorResponse(
                error=f"Timed out waiting for element with control_id '{control_id}' to not be visible",
                error_type="TimeoutError"
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error waiting for element to not be visible: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="wait_for_element_not_enabled",
    description="Waits for an element to not be enabled.",
    category="input"
)
def wait_for_element_not_enabled(
    window_handle: int,
    control_id: str,
    timeout: float = 10.0,
    retry_interval: float = 0.5
) -> Dict[str, Any]:
    """
    Wait for an element to not be enabled.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to wait for
        timeout: Maximum time to wait in seconds
        retry_interval: Time to wait between retries in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if not control_id:
        return ErrorResponse(
            error="control_id is required",
            error_type="InvalidArgument"
        ).dict()
    
    if timeout <= 0:
        return ErrorResponse(
            error="Timeout must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    if retry_interval <= 0:
        return ErrorResponse(
            error="Retry interval must be a positive number",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Waiting for element with control_id '{control_id}' to not be enabled (timeout: {timeout}s)"):
            window = get_desktop().window(handle=window_handle)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                element = window.child_window(control_id=control_id)
                if not element.exists() or not element.is_enabled():
                    return SuccessResponse(
                        data={"message": f"Element with control_id '{control_id}' is no longer enabled"}
                    ).dict()
                
                time.sleep(retry_interval)
            
            return ErrorResponse(
                error=f"Timed out waiting for element with control_id '{control_id}' to not be enabled",
                error_type="TimeoutError"
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error waiting for element to not be enabled: {str(e)}",
            error_type="ElementOperationError"
        ).dict()
