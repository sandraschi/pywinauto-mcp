"""
UI Element tools for PyWinAuto MCP.

This module provides tools for interacting with and validating UI elements.
"""
from typing import Optional, Dict, Any, List, Union, Tuple
import time
from pywinauto import Application, findwindows
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.timings import Timings
from ..core.decorators import tool, stateful

@tool
def element_exists(selector: Union[str, Dict[str, Any]], 
                 timeout: float = 5.0, 
                 app: Optional[Application] = None) -> dict:
    """
    Check if a UI element exists.
    
    Args:
        selector: Element selector (title, class_name, or dict of properties)
        timeout: Maximum time to wait for element (default: 5 seconds)
        app: Optional Application instance to use for finding the element
        
    Returns:
        dict: Status and existence information
    """
    start_time = time.time()
    last_error = None
    
    while time.time() - start_time < timeout:
        try:
            if app is None:
                app = Application(backend="uia").connect(active_only=True)
            
            if isinstance(selector, dict):
                element = app.window(**selector)
            elif isinstance(selector, str):
                # Try to find by title first, then by class name
                try:
                    element = app.window(title=selector)
                    if not element.exists():
                        element = app.window(class_name=selector)
                except Exception:
                    element = app.window(class_name=selector)
            else:
                return {
                    "status": "error",
                    "message": "Invalid selector type. Must be string or dict."
                }
            
            if element.exists():
                return {
                    "status": "success",
                    "exists": True,
                    "element_info": _get_element_info(element)
                }
                
        except Exception as e:
            last_error = str(e)
            time.sleep(0.1)
    
    return {
        "status": "timeout" if last_error is None else "error",
        "exists": False,
        "message": last_error or f"Element not found within {timeout} seconds"
    }

@tool
def wait_for_element(selector: Union[str, Dict[str, Any]], 
                   timeout: float = 10.0,
                   app: Optional[Application] = None) -> dict:
    """
    Wait for a UI element to appear.
    
    Args:
        selector: Element selector (title, class_name, or dict of properties)
        timeout: Maximum time to wait in seconds (default: 10)
        app: Optional Application instance to use for finding the element
        
    Returns:
        dict: Status and element information if found
    """
    result = element_exists(selector, timeout, app)
    if result.get("exists", False):
        return {
            "status": "success",
            "element": result["element_info"]
        }
    else:
        return {
            "status": "error",
            "message": f"Element not found within {timeout} seconds"
        }

@tool
def verify_text(selector: Union[str, Dict[str, Any]], 
               expected_text: str,
               exact_match: bool = True,
               timeout: float = 5.0,
               app: Optional[Application] = None) -> dict:
    """
    Verify that an element contains the expected text.
    
    Args:
        selector: Element selector (title, class_name, or dict of properties)
        expected_text: Text to verify
        exact_match: If True, text must match exactly (default: True)
        timeout: Maximum time to wait for element (default: 5 seconds)
        app: Optional Application instance to use for finding the element
        
    Returns:
        dict: Status and verification result
    """
    result = wait_for_element(selector, timeout, app)
    if result["status"] != "success":
        return result
    
    element_info = result["element"]
    actual_text = element_info.get("text", "")
    
    if exact_match:
        text_matches = (actual_text == expected_text)
    else:
        text_matches = (expected_text.lower() in actual_text.lower())
    
    return {
        "status": "success" if text_matches else "failure",
        "expected_text": expected_text,
        "actual_text": actual_text,
        "exact_match": exact_match,
        "match_found": text_matches
    }

@tool
def get_element_rect(selector: Union[str, Dict[str, Any]],
                   timeout: float = 5.0,
                   app: Optional[Application] = None) -> dict:
    """
    Get the position and size of a UI element.
    
    Args:
        selector: Element selector (title, class_name, or dict of properties)
        timeout: Maximum time to wait for element (default: 5 seconds)
        app: Optional Application instance to use for finding the element
        
    Returns:
        dict: Status and rectangle information
    """
    result = wait_for_element(selector, timeout, app)
    if result["status"] != "success":
        return result
    
    element_info = result["element"]
    if "rect" not in element_info:
        return {
            "status": "error",
            "message": "Element does not have rectangle information"
        }
    
    rect = element_info["rect"]
    return {
        "status": "success",
        "rect": rect,
        "width": rect["right"] - rect["left"],
        "height": rect["bottom"] - rect["top"],
        "position": {
            "x": rect["left"],
            "y": rect["top"]
        }
    }

def _get_element_info(element) -> Dict[str, Any]:
    """Extract relevant information from a UI element."""
    try:
        element_info = {
            "class_name": element.class_name(),
            "text": element.window_text(),
            "control_id": element.control_id(),
            "process_id": element.process_id(),
            "is_visible": element.is_visible(),
            "is_enabled": element.is_enabled(),
            "handle": element.handle,
            "runtime_id": element.runtime_id() if hasattr(element, 'runtime_id') else None,
            "automation_id": element.automation_id() if hasattr(element, 'automation_id') else None,
            "name": element.element_info.name if hasattr(element, 'element_info') else None,
            "control_type": element.element_info.control_type if hasattr(element, 'element_info') else None,
            "rect": {
                "left": element.rectangle().left,
                "top": element.rectangle().top,
                "right": element.rectangle().right,
                "bottom": element.rectangle().bottom,
                "width": element.rectangle().width(),
                "height": element.rectangle().height()
            }
        }
        
        # Add any custom properties if they exist
        if hasattr(element, 'get_properties'):
            element_info["properties"] = element.get_properties()
            
        return element_info
    except Exception as e:
        return {
            "error": f"Failed to get element info: {str(e)}",
            "element_type": str(type(element))
        }

# Add all tools to __all__
__all__ = [
    'element_exists',
    'wait_for_element',
    'verify_text',
    'get_element_rect'
]
