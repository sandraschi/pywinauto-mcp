"""
Element interaction tools for PyWinAuto MCP.

This module provides functions for interacting with UI elements within windows,
including clicking, double-clicking, right-clicking, and hovering.
"""
import logging
from typing import Dict, Optional, Tuple, Any, List

from pywinauto import ElementNotFoundError, ElementNotVisible, InvalidWindowHandle
from pywinauto.controls.uia_controls import ButtonWrapper, EditWrapper, ComboBoxWrapper

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
    'click_element',
    'double_click_element',
    'right_click_element',
    'hover_element',
    'get_element_info',
    'get_element_text',
    'set_element_text',
    'get_element_rect',
    'is_element_visible',
    'is_element_enabled',
    'get_all_elements'
]

def _get_element(window, control_id: Optional[str] = None, x: Optional[int] = None, y: Optional[int] = None):
    """
    Get an element by control ID or coordinates.
    
    Args:
        window: The parent window
        control_id: The control ID
        x: X coordinate (if using coordinates)
        y: Y coordinate (if using coordinates)
        
    Returns:
        The UI element
        
    Raises:
        ElementNotFound: If the element is not found
        ElementNotVisible: If the element is not visible
    """
    if control_id is not None:
        # Get element by control ID
        element = window.child_window(control_id=control_id)
        if not element.exists():
            raise ElementNotFound(f"Element with control_id '{control_id}' not found")
    elif x is not None and y is not None:
        # Get element by coordinates
        element = window.from_point(x, y)
        if not element.exists():
            raise ElementNotFound(f"No element found at coordinates ({x}, {y})")
    else:
        raise ValueError("Either control_id or both x and y coordinates must be provided")
    
    if not element.is_visible():
        raise ElementNotVisible("Element exists but is not visible")
    
    return element

@register_tool(
    name="click_element",
    description="Clicks on a UI element.",
    category="element"
)
def click_element(
    window_handle: int,
    control_id: Optional[str] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = "left",
    double: bool = False,
    absolute: bool = False
) -> Dict[str, Any]:
    """
    Click on a UI element.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to click (optional if x and y are provided)
        x: X coordinate relative to the window (optional if control_id is provided)
        y: Y coordinate relative to the window (optional if control_id is provided)
        button: The mouse button to use ("left", "right", "middle")
        double: Whether to perform a double-click
        absolute: Whether the coordinates are screen-absolute (default: window-relative)

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if control_id is None and (x is None or y is None):
        return ErrorResponse(
            error="Either control_id or both x and y coordinates must be provided",
            error_type="InvalidArguments"
        ).dict()
    
    if button.lower() not in ["left", "right", "middle"]:
        return ErrorResponse(
            error=f"Invalid button: {button}. Must be one of: left, right, middle",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Clicking element with control_id={control_id} at ({x}, {y})"):
            window = get_desktop().window(handle=window_handle)
            
            if control_id:
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
                
                # Click the element
                if double:
                    element.double_click(button=button)
                else:
                    element.click(button=button)
                
                return SuccessResponse(
                    data={"message": f"Successfully clicked element with control_id '{control_id}'"}
                ).dict()
            else:
                # Click at coordinates
                if absolute:
                    import pyautogui
                    pyautogui.click(x, y, button=button, clicks=2 if double else 1)
                else:
                    window.click_input(button=button, coords=(x, y), double=double)
                
                return SuccessResponse(
                    data={"message": f"Successfully clicked at coordinates ({x}, {y})"}
                ).dict()
                
    except ElementNotFound as e:
        return ErrorResponse(
            error=str(e),
            error_type="ElementNotFound"
        ).dict()
    except ElementNotVisible as e:
        return ErrorResponse(
            error=str(e),
            error_type="ElementNotVisible"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error clicking element: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="double_click_element",
    description="Double-clicks on a UI element.",
    category="element"
)
def double_click_element(
    window_handle: int,
    control_id: Optional[str] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = "left"
) -> Dict[str, Any]:
    """
    Double-click on a UI element.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to click (optional if x and y are provided)
        x: X coordinate relative to the window (optional if control_id is provided)
        y: Y coordinate relative to the window (optional if control_id is provided)
        button: The mouse button to use ("left", "right", "middle")

    Returns:
        Dict containing the result of the operation
    """
    return click_element(
        window_handle=window_handle,
        control_id=control_id,
        x=x,
        y=y,
        button=button,
        double=True
    )

@register_tool(
    name="right_click_element",
    description="Right-clicks on a UI element.",
    category="element"
)
def right_click_element(
    window_handle: int,
    control_id: Optional[str] = None,
    x: Optional[int] = None,
    y: Optional[int] = None
) -> Dict[str, Any]:
    """
    Right-click on a UI element.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to click (optional if x and y are provided)
        x: X coordinate relative to the window (optional if control_id is provided)
        y: Y coordinate relative to the window (optional if control_id is provided)

    Returns:
        Dict containing the result of the operation
    """
    return click_element(
        window_handle=window_handle,
        control_id=control_id,
        x=x,
        y=y,
        button="right"
    )

@register_tool(
    name="hover_element",
    description="Hovers the mouse over a UI element.",
    category="element"
)
def hover_element(
    window_handle: int,
    control_id: Optional[str] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    duration: float = 0.5
) -> Dict[str, Any]:
    """
    Hover the mouse over a UI element.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element to hover over (optional if x and y are provided)
        x: X coordinate relative to the window (optional if control_id is provided)
        y: Y coordinate relative to the window (optional if control_id is provided)
        duration: Duration of the hover in seconds

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if control_id is None and (x is None or y is None):
        return ErrorResponse(
            error="Either control_id or both x and y coordinates must be provided",
            error_type="InvalidArguments"
        ).dict()
    
    if duration < 0:
        return ErrorResponse(
            error="Duration must be a non-negative number",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Hovering over element with control_id={control_id} at ({x}, {y}) for {duration}s"):
            window = get_desktop().window(handle=window_handle)
            
            if control_id:
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
                
                # Hover over the element
                element.hover()
                
                # If duration is specified, wait before moving the mouse away
                if duration > 0:
                    import time
                    time.sleep(duration)
                
                return SuccessResponse(
                    data={"message": f"Successfully hovered over element with control_id '{control_id}'"}
                ).dict()
            else:
                # Hover at coordinates
                window.move_mouse(coords=(x, y))
                
                # If duration is specified, wait before moving the mouse away
                if duration > 0:
                    import time
                    time.sleep(duration)
                
                return SuccessResponse(
                    data={"message": f"Successfully hovered at coordinates ({x}, {y})"}
                ).dict()
                
    except ElementNotFound as e:
        return ErrorResponse(
            error=str(e),
            error_type="ElementNotFound"
        ).dict()
    except ElementNotVisible as e:
        return ErrorResponse(
            error=str(e),
            error_type="ElementNotVisible"
        ).dict()
    except Exception as e:
        return ErrorResponse(
            error=f"Error hovering over element: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="get_element_info",
    description="Gets detailed information about a UI element.",
    category="element"
)
def get_element_info(window_handle: int, control_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a UI element.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element

    Returns:
        Dict containing element information
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
    
    try:
        with timer(f"Getting info for element with control_id '{control_id}'"):
            window = get_desktop().window(handle=window_handle)
            element = window.child_window(control_id=control_id)
            
            if not element.exists():
                return ErrorResponse(
                    error=f"Element with control_id '{control_id}' not found",
                    error_type="ElementNotFound"
                ).dict()
            
            # Get basic properties
            rect = element.rectangle()
            element_info = {
                "control_id": control_id,
                "class_name": element.class_name(),
                "text": element.window_text(),
                "is_visible": element.is_visible(),
                "is_enabled": element.is_enabled(),
                "position": {
                    "left": rect.left,
                    "top": rect.top,
                    "width": rect.width(),
                    "height": rect.height()
                },
                "control_type": element.element_info.control_type,
                "automation_id": element.element_info.automation_id,
                "name": element.element_info.name,
                "runtime_id": element.element_info.runtime_id,
                "process_id": element.element_info.process_id,
                "handle": element.handle
            }
            
            # Get additional properties based on control type
            if isinstance(element, ButtonWrapper):
                element_info["control_type"] = "Button"
                element_info["is_checked"] = element.get_toggle_state() if hasattr(element, 'get_toggle_state') else None
            elif isinstance(element, EditWrapper):
                element_info["control_type"] = "Edit"
                element_info["text_length"] = len(element.get_value())
                element_info["is_readonly"] = element.is_read_only()
            elif isinstance(element, ComboBoxWrapper):
                element_info["control_type"] = "ComboBox"
                element_info["items"] = element.item_count()
                element_info["selected_index"] = element.selected_index()
            
            return SuccessResponse(
                data={"element": element_info}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting element info: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="get_element_text",
    description="Gets the text of a UI element.",
    category="element"
)
def get_element_text(window_handle: int, control_id: str) -> Dict[str, Any]:
    """
    Get the text of a UI element.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element

    Returns:
        Dict containing the element text
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
    
    try:
        with timer(f"Getting text for element with control_id '{control_id}'"):
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
            
            text = element.window_text()
            
            return SuccessResponse(
                data={"text": text}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting element text: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="set_element_text",
    description="Sets the text of a UI element.",
    category="element"
)
def set_element_text(window_handle: int, control_id: str, text: str) -> Dict[str, Any]:
    """
    Set the text of a UI element.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element
        text: The text to set

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
    
    try:
        with timer(f"Setting text for element with control_id '{control_id}'"):
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
            
            # Set the text
            element.set_text(text)
            
            # Verify the text was set
            current_text = element.window_text()
            if current_text == text:
                return SuccessResponse(
                    data={"message": f"Successfully set text for element with control_id '{control_id}'"}
                ).dict()
            else:
                return ErrorResponse(
                    error=f"Failed to set text for element with control_id '{control_id}'. Expected: '{text}', Actual: '{current_text}'",
                    error_type="ElementOperationFailed"
                ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error setting element text: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="get_element_rect",
    description="Gets the rectangle of a UI element.",
    category="element"
)
def get_element_rect(window_handle: int, control_id: str) -> Dict[str, Any]:
    """
    Get the rectangle of a UI element.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element

    Returns:
        Dict containing the element rectangle
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
    
    try:
        with timer(f"Getting rectangle for element with control_id '{control_id}'"):
            window = get_desktop().window(handle=window_handle)
            element = window.child_window(control_id=control_id)
            
            if not element.exists():
                return ErrorResponse(
                    error=f"Element with control_id '{control_id}' not found",
                    error_type="ElementNotFound"
                ).dict()
            
            rect = element.rectangle()
            
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
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting element rectangle: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="is_element_visible",
    description="Checks if a UI element is visible.",
    category="element"
)
def is_element_visible(window_handle: int, control_id: str) -> Dict[str, Any]:
    """
    Check if a UI element is visible.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element

    Returns:
        Dict containing the visibility status
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
    
    try:
        with timer(f"Checking visibility for element with control_id '{control_id}'"):
            window = get_desktop().window(handle=window_handle)
            element = window.child_window(control_id=control_id)
            
            if not element.exists():
                return ErrorResponse(
                    error=f"Element with control_id '{control_id}' not found",
                    error_type="ElementNotFound"
                ).dict()
            
            is_visible = element.is_visible()
            
            return SuccessResponse(
                data={"is_visible": is_visible}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error checking element visibility: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="is_element_enabled",
    description="Checks if a UI element is enabled.",
    category="element"
)
def is_element_enabled(window_handle: int, control_id: str) -> Dict[str, Any]:
    """
    Check if a UI element is enabled.

    Args:
        window_handle: The handle of the parent window
        control_id: The control ID of the element

    Returns:
        Dict containing the enabled status
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
    
    try:
        with timer(f"Checking enabled status for element with control_id '{control_id}'"):
            window = get_desktop().window(handle=window_handle)
            element = window.child_window(control_id=control_id)
            
            if not element.exists():
                return ErrorResponse(
                    error=f"Element with control_id '{control_id}' not found",
                    error_type="ElementNotFound"
                ).dict()
            
            is_enabled = element.is_enabled()
            
            return SuccessResponse(
                data={"is_enabled": is_enabled}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error checking element enabled status: {str(e)}",
            error_type="ElementOperationError"
        ).dict()

@register_tool(
    name="get_all_elements",
    description="Gets all UI elements in a window.",
    category="element"
)
def get_all_elements(window_handle: int, max_depth: int = 3) -> Dict[str, Any]:
    """
    Get all UI elements in a window.

    Args:
        window_handle: The handle of the parent window
        max_depth: Maximum depth to traverse the element tree

    Returns:
        Dict containing information about all elements
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if max_depth < 1 or max_depth > 10:
        return ErrorResponse(
            error="max_depth must be between 1 and 10",
            error_type="InvalidArgument"
        ).dict()
    
    def get_element_info(element, depth: int = 0) -> Dict[str, Any]:
        if depth > max_depth:
            return None
            
        try:
            if not element.exists():
                return None
                
            rect = element.rectangle()
            
            element_info = {
                "class_name": element.class_name(),
                "control_type": element.element_info.control_type if hasattr(element, 'element_info') else None,
                "automation_id": element.element_info.automation_id if hasattr(element, 'element_info') else None,
                "name": element.element_info.name if hasattr(element, 'element_info') else None,
                "text": element.window_text(),
                "is_visible": element.is_visible(),
                "is_enabled": element.is_enabled(),
                "position": {
                    "left": rect.left,
                    "top": rect.top,
                    "width": rect.width(),
                    "height": rect.height()
                },
                "children": []
            }
            
            # Get children
            try:
                for child in element.children():
                    child_info = get_element_info(child, depth + 1)
                    if child_info:
                        element_info["children"].append(child_info)
            except Exception as e:
                logger.debug(f"Error getting children: {str(e)}")
                
            return element_info
            
        except Exception as e:
            logger.debug(f"Error getting element info: {str(e)}")
            return None
    
    try:
        with timer(f"Getting all elements in window {window_handle} with max_depth={max_depth}"):
            window = get_desktop().window(handle=window_handle)
            
            if not window.exists():
                return ErrorResponse(
                    error=f"Window with handle {window_handle} not found",
                    error_type="WindowNotFound"
                ).dict()
            
            # Get the root element
            root_element = get_element_info(window)
            
            if not root_element:
                return ErrorResponse(
                    error="Failed to get root element",
                    error_type="ElementOperationError"
                ).dict()
            
            return SuccessResponse(
                data={"elements": root_element}
            ).dict()
            
    except Exception as e:
        return ErrorResponse(
            error=f"Error getting all elements: {str(e)}",
            error_type="ElementOperationError"
        ).dict()
