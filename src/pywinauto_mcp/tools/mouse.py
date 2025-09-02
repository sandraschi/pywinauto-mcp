"""
Mouse interaction tools for PyWinAuto MCP.

This module provides mouse-related functionality including movement, clicking, dragging, and scrolling.
"""
from typing import Optional, Tuple, Union
import time
import pyautogui
from pywinauto import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.timings import Timings
from ..core.decorators import tool, stateful

# Set default delay between mouse actions
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

@tool
def mouse_move_relative(x: int, y: int) -> dict:
    """
    Move mouse relative to current position.
    
    Args:
        x: Pixels to move horizontally (positive = right, negative = left)
        y: Pixels to move vertically (positive = down, negative = up)
        
    Returns:
        dict: Status and new position
    """
    current_x, current_y = pyautogui.position()
    new_x = current_x + x
    new_y = current_y + y
    pyautogui.moveTo(new_x, new_y)
    return {"status": "success", "position": (new_x, new_y)}

@tool
def mouse_move_to_element(element: Union[HwndWrapper, dict], x: int = None, y: int = None) -> dict:
    """
    Move mouse to a UI element.
    
    Args:
        element: Pywinauto element or element info dict
        x: Optional x offset from element's center
        y: Optional y offset from element's center
        
    Returns:
        dict: Status and position
    """
    if hasattr(element, 'rectangle'):
        rect = element.rectangle()
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2
    elif isinstance(element, dict) and 'rect' in element:
        rect = element['rect']
        center_x = (rect['left'] + rect['right']) // 2
        center_y = (rect['top'] + rect['bottom']) // 2
    else:
        raise ValueError("Invalid element type. Must be Pywinauto element or element info dict.")
    
    target_x = center_x + (x or 0)
    target_y = center_y + (y or 0)
    
    pyautogui.moveTo(target_x, target_y)
    return {"status": "success", "position": (target_x, target_y)}

@tool
def mouse_hover(element: Union[HwndWrapper, dict], duration: float = 0.5) -> dict:
    """
    Hover over an element.
    
    Args:
        element: Pywinauto element or element info dict
        duration: Time in seconds to hover (default: 0.5)
        
    Returns:
        dict: Status and hover position
    """
    result = mouse_move_to_element(element)
    time.sleep(duration)
    return result

@tool
def drag_and_drop(source: Union[HwndWrapper, dict], 
                 target: Union[HwndWrapper, dict], 
                 duration: float = 0.5) -> dict:
    """
    Drag from source to target element.
    
    Args:
        source: Source element to drag from
        target: Target element to drop to
        duration: Duration of the drag in seconds (default: 0.5)
        
    Returns:
        dict: Status and positions
    """
    # Get source and target positions
    src_pos = mouse_move_to_element(source)
    time.sleep(0.1)  # Small delay before drag
    
    # Get target position
    target_pos = mouse_move_to_element(target)
    
    # Perform drag and drop
    pyautogui.mouseDown()
    time.sleep(0.1)  # Small delay after mouse down
    
    # Move to target
    pyautogui.moveTo(target_pos['position'][0], target_pos['position'][1], duration=duration)
    time.sleep(0.1)  # Small delay before release
    
    pyautogui.mouseUp()
    
    return {
        "status": "success",
        "source_position": src_pos['position'],
        "target_position": target_pos['position']
    }

@tool
def right_click(element: Optional[Union[HwndWrapper, dict]] = None, 
               x: int = None, y: int = None) -> dict:
    """
    Right-click on an element or at specific coordinates.
    
    Args:
        element: Optional element to click on
        x: X coordinate (if element not provided)
        y: Y coordinate (if element not provided)
        
    Returns:
        dict: Status and click position
    """
    if element is not None:
        pos = mouse_move_to_element(element, x, y)['position']
    elif x is not None and y is not None:
        pos = (x, y)
        pyautogui.moveTo(x, y)
    else:
        pos = pyautogui.position()
    
    pyautogui.rightClick()
    return {"status": "success", "position": pos}

@tool
def double_click(element: Optional[Union[HwndWrapper, dict]] = None, 
               x: int = None, y: int = None) -> dict:
    """
    Double-click on an element or at specific coordinates.
    
    Args:
        element: Optional element to click on
        x: X coordinate (if element not provided)
        y: Y coordinate (if element not provided)
        
    Returns:
        dict: Status and click position
    """
    if element is not None:
        pos = mouse_move_to_element(element, x, y)['position']
    elif x is not None and y is not None:
        pos = (x, y)
        pyautogui.moveTo(x, y)
    else:
        pos = pyautogui.position()
    
    pyautogui.doubleClick()
    return {"status": "success", "position": pos}

@tool
def mouse_scroll(amount: int, x: int = None, y: int = None) -> dict:
    """
    Scroll the mouse wheel.
    
    Args:
        amount: Number of 'clicks' to scroll (positive = up, negative = down)
        x: Optional X coordinate to move to before scrolling
        y: Optional Y coordinate to move to before scrolling
        
    Returns:
        dict: Status and scroll position
    """
    if x is not None and y is not None:
        pyautogui.moveTo(x, y)
    
    pyautogui.scroll(amount)
    
    return {
        "status": "success", 
        "position": pyautogui.position(),
        "scroll_amount": amount
    }

@tool
def get_cursor_position() -> dict:
    """
    Get current cursor position.
    
    Returns:
        dict: Current cursor position (x, y)
    """
    x, y = pyautogui.position()
    return {"status": "success", "position": (x, y)}

@tool
def highlight_element(element: Union[HwndWrapper, dict], duration: float = 2.0) -> dict:
    """
    Visually highlight an element by drawing a rectangle around it.
    
    Args:
        element: Element to highlight
        duration: Duration in seconds to show the highlight (default: 2.0)
        
    Returns:
        dict: Status and element bounds
    """
    try:
        import cv2
        import numpy as np
        from PIL import ImageGrab
        
        # Get element rectangle
        if hasattr(element, 'rectangle'):
            rect = element.rectangle()
            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
        elif isinstance(element, dict) and 'rect' in element:
            rect = element['rect']
            left, top, right, bottom = rect['left'], rect['top'], rect['right'], rect['bottom']
        else:
            raise ValueError("Invalid element type. Must be Pywinauto element or element info dict.")
        
        # Take screenshot of the screen
        screenshot = ImageGrab.grab()
        img = np.array(screenshot)
        
        # Convert RGB to BGR (OpenCV uses BGR by default)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Draw rectangle
        color = (0, 255, 0)  # Green
        thickness = 3
        cv2.rectangle(img, (left, top), (right, bottom), color, thickness)
        
        # Show the image
        cv2.imshow('Element Highlight', img)
        cv2.waitKey(int(duration * 1000))  # Convert seconds to milliseconds
        cv2.destroyAllWindows()
        
        return {
            "status": "success",
            "bounds": {"left": left, "top": top, "right": right, "bottom": bottom}
        }
    except ImportError:
        return {
            "status": "warning",
            "message": "Highlighting requires OpenCV and Pillow. Install with: pip install opencv-python pillow"
        }

# Add all tools to __all__
__all__ = [
    'mouse_move_relative',
    'mouse_move_to_element',
    'mouse_hover',
    'drag_and_drop',
    'right_click',
    'double_click',
    'mouse_scroll',
    'get_cursor_position',
    'highlight_element'
]
