"""
Window management tools for PyWinAuto MCP.

This module provides functions for managing windows, including maximizing,
minimizing, restoring, and setting window positions.
"""
import logging
from typing import Any, Dict, Optional, Tuple

from pywinauto import WindowNotFoundError

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
    'maximize_window',
    'minimize_window',
    'restore_window',
    'set_window_position',
    'get_active_window',
    'close_window',
    'get_window_rect',
    'get_window_title',
    'get_window_state',
    'set_window_foreground',
    'get_all_windows'
]

@register_tool(
    name="maximize_window",
    description="Maximizes the specified window.",
    category="window"
)
def maximize_window(handle: int) -> Dict[str, Any]:
    """
    Maximize a window.

    Args:
        handle: The window handle to maximize

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Maximizing window {handle}"):
            window = get_desktop().window(handle=handle)
            window.maximize()
            
            # Verify the window is actually maximized
            if window.is_maximized():
                return SuccessResponse(
                    data={"message": f"Window {handle} maximized successfully"}
                ).dict()
            else:
                return ErrorResponse(
                    error=f"Failed to maximize window {handle}",
                    error_type="WindowMaximizeFailed"
                ).dict()
                
    except WindowNotFoundError as e:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error maximizing window: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="minimize_window",
    description="Minimizes the specified window.",
    category="window"
)
def minimize_window(handle: int) -> Dict[str, Any]:
    """
    Minimize a window.

    Args:
        handle: The window handle to minimize

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Minimizing window {handle}"):
            window = get_desktop().window(handle=handle)
            window.minimize()
            
            # Verify the window is actually minimized
            if window.is_minimized():
                return SuccessResponse(
                    data={"message": f"Window {handle} minimized successfully"}
                ).dict()
            else:
                return ErrorResponse(
                    error=f"Failed to minimize window {handle}",
                    error_type="WindowMinimizeFailed"
                ).dict()
                
    except WindowNotFoundError:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error minimizing window: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="restore_window",
    description="Restores a minimized or maximized window to its normal state.",
    category="window"
)
def restore_window(handle: int) -> Dict[str, Any]:
    """
    Restore a window to its normal state.

    Args:
        handle: The window handle to restore

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Restoring window {handle}"):
            window = get_desktop().window(handle=handle)
            window.restore()
            
            # Verify the window is actually restored
            if not window.is_minimized() and not window.is_maximized():
                return SuccessResponse(
                    data={"message": f"Window {handle} restored successfully"}
                ).dict()
            else:
                return ErrorResponse(
                    error=f"Failed to restore window {handle}",
                    error_type="WindowRestoreFailed"
                ).dict()
                
    except WindowNotFoundError:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error restoring window: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="set_window_position",
    description="Sets the position and size of a window.",
    category="window"
)
def set_window_position(
    handle: int,
    x: int,
    y: int,
    width: int,
    height: int
) -> Dict[str, Any]:
    """
    Set the position and size of a window.

    Args:
        handle: The window handle
        x: The x-coordinate of the top-left corner
        y: The y-coordinate of the top-left corner
        width: The width of the window
        height: The height of the window

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if width <= 0 or height <= 0:
        return ErrorResponse(
            error=f"Invalid dimensions: width={width}, height={height}",
            error_type="InvalidDimensions"
        ).dict()
    
    try:
        with timer(f"Setting position for window {handle} to ({x}, {y}) {width}x{height}"):
            window = get_desktop().window(handle=handle)
            window.move_window(x, y, width, height)
            
            # Verify the window was moved/resized correctly
            rect = window.rectangle()
            if (rect.left == x and rect.top == y and 
                rect.width() == width and rect.height() == height):
                return SuccessResponse(
                    data={
                        "message": f"Window {handle} positioned successfully",
                        "position": {"x": x, "y": y, "width": width, "height": height}
                    }
                ).dict()
            else:
                return ErrorResponse(
                    error=f"Failed to position window {handle}",
                    error_type="WindowPositionFailed"
                ).dict()
                
    except WindowNotFoundError:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error positioning window: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="get_active_window",
    description="Gets the currently active window.",
    category="window"
)
def get_active_window() -> Dict[str, Any]:
    """
    Get the currently active window.

    Returns:
        Dict containing information about the active window
    """
    try:
        with timer("Getting active window"):
            window = get_desktop().window(active_only=True)
            
            if not window.exists():
                return ErrorResponse(
                    error="No active window found",
                    error_type="NoActiveWindow"
                ).dict()
            
            rect = window.rectangle()
            
            return SuccessResponse(
                data={
                    "handle": window.handle,
                    "title": window.window_text(),
                    "class_name": window.class_name(),
                    "is_visible": window.is_visible(),
                    "is_enabled": window.is_enabled(),
                    "is_minimized": window.is_minimized(),
                    "is_maximized": window.is_maximized(),
                    "position": {
                        "x": rect.left,
                        "y": rect.top,
                        "width": rect.width(),
                        "height": rect.height()
                    }
                }
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting active window: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="close_window",
    description="Closes the specified window.",
    category="window"
)
def close_window(handle: int) -> Dict[str, Any]:
    """
    Close a window.

    Args:
        handle: The window handle to close

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Closing window {handle}"):
            window = get_desktop().window(handle=handle)
            window.close()
            
            # Verify the window was closed
            if not window.exists():
                return SuccessResponse(
                    data={"message": f"Window {handle} closed successfully"}
                ).dict()
            else:
                return ErrorResponse(
                    error=f"Failed to close window {handle}",
                    error_type="WindowCloseFailed"
                ).dict()
                
    except WindowNotFoundError:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error closing window: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="get_window_rect",
    description="Gets the rectangle of a window.",
    category="window"
)
def get_window_rect(handle: int) -> Dict[str, Any]:
    """
    Get the rectangle of a window.

    Args:
        handle: The window handle

    Returns:
        Dict containing the window rectangle
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Getting rectangle for window {handle}"):
            window = get_desktop().window(handle=handle)
            rect = window.rectangle()
            
            return SuccessResponse(
                data={
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                    "width": rect.width(),
                    "height": rect.height()
                }
            ).dict()
            
    except WindowNotFoundError:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting window rectangle: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="get_window_title",
    description="Gets the title of a window.",
    category="window"
)
def get_window_title(handle: int) -> Dict[str, Any]:
    """
    Get the title of a window.

    Args:
        handle: The window handle

    Returns:
        Dict containing the window title
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Getting title for window {handle}"):
            window = get_desktop().window(handle=handle)
            title = window.window_text()
            
            return SuccessResponse(
                data={"title": title}
            ).dict()
            
    except WindowNotFoundError:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting window title: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="get_window_state",
    description="Gets the state of a window.",
    category="window"
)
def get_window_state(handle: int) -> Dict[str, Any]:
    """
    Get the state of a window.

    Args:
        handle: The window handle

    Returns:
        Dict containing the window state
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Getting state for window {handle}"):
            window = get_desktop().window(handle=handle)
            
            return SuccessResponse(
                data={
                    "is_minimized": window.is_minimized(),
                    "is_maximized": window.is_maximized(),
                    "is_visible": window.is_visible(),
                    "is_enabled": window.is_enabled(),
                    "is_active": window.is_active()
                }
            ).dict()
            
    except WindowNotFoundError:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting window state: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="set_window_foreground",
    description="Brings a window to the foreground and activates it.",
    category="window"
)
def set_window_foreground(handle: int) -> Dict[str, Any]:
    """
    Bring a window to the foreground and activate it.

    Args:
        handle: The window handle

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(handle):
        return ErrorResponse(
            error=f"Invalid window handle: {handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    try:
        with timer(f"Bringing window {handle} to foreground"):
            window = get_desktop().window(handle=handle)
            window.set_focus()
            
            # Verify the window is in the foreground
            active_window = get_desktop().window(active_only=True)
            if active_window.handle == handle:
                return SuccessResponse(
                    data={"message": f"Window {handle} brought to foreground successfully"}
                ).dict()
            else:
                return ErrorResponse(
                    error=f"Failed to bring window {handle} to foreground",
                    error_type="WindowForegroundFailed"
                ).dict()
                
    except WindowNotFoundError:
        return ErrorResponse(
            error=f"Window not found: {handle}",
            error_type="WindowNotFound"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error bringing window to foreground: {str(e)}",
            error_type="WindowOperationError"
        ).dict()

@register_tool(
    name="get_all_windows",
    description="Gets information about all visible windows.",
    category="window"
)
def get_all_windows() -> Dict[str, Any]:
    """
    Get information about all visible windows.

    Returns:
        Dict containing information about all visible windows
    """
    try:
        with timer("Getting all windows"):
            desktop = get_desktop()
            windows = []
            
            for window in desktop.windows():
                try:
                    rect = window.rectangle()
                    windows.append({
                        "handle": window.handle,
                        "title": window.window_text(),
                        "class_name": window.class_name(),
                        "is_visible": window.is_visible(),
                        "is_enabled": window.is_enabled(),
                        "is_minimized": window.is_minimized(),
                        "is_maximized": window.is_maximized(),
                        "position": {
                            "left": rect.left,
                            "top": rect.top,
                            "width": rect.width(),
                            "height": rect.height()
                        }
                    })
                except Exception as e:
                    logger.warning(f"Error getting window info: {str(e)}")
                    continue
            
            return SuccessResponse(
                data={"windows": windows, "count": len(windows)}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting windows: {str(e)}",
            error_type="WindowOperationError"
        ).dict()
