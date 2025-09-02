"""
Visual tools for PyWinAuto MCP.

This module provides visual tools for screen capture, image recognition, and
other visual automation tasks.
"""
import os
import time
import cv2
import numpy as np
import pyautogui
from typing import Optional, Dict, Any, Tuple, Union
from PIL import Image, ImageGrab
from pywinauto import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from ..core.decorators import tool, stateful

@tool
def take_screenshot(region: Optional[Dict[str, int]] = None, 
                  save_path: Optional[str] = None) -> dict:
    """
    Take a screenshot of the screen or a specific region.
    
    Args:
        region: Optional dict with 'left', 'top', 'width', 'height' to capture a specific region
        save_path: Optional path to save the screenshot
        
    Returns:
        dict: Status and screenshot information
    """
    try:
        if region:
            screenshot = pyautogui.screenshot(region=(
                region.get('left', 0),
                region.get('top', 0),
                region.get('width', 0),
                region.get('height', 0)
            ))
            region_info = region
        else:
            screenshot = pyautogui.screenshot()
            region_info = {
                'left': 0,
                'top': 0,
                'width': screenshot.width,
                'height': screenshot.height
            }
        
        # Convert to numpy array for OpenCV if needed
        screenshot_np = np.array(screenshot)
        screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            cv2.imwrite(save_path, screenshot_np)
        
        return {
            "status": "success",
            "screenshot": {
                "size": (screenshot.width, screenshot.height),
                "mode": screenshot.mode,
                "region": region_info,
                "saved_path": save_path if save_path else None
            },
            "numpy_shape": screenshot_np.shape
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def find_image_on_screen(image_path: str, 
                       confidence: float = 0.8, 
                       grayscale: bool = False,
                       region: Optional[Dict[str, int]] = None) -> dict:
    """
    Find an image on the screen using template matching.
    
    Args:
        image_path: Path to the template image to find
        confidence: Confidence threshold (0-1) for matching (default: 0.8)
        grayscale: Whether to convert images to grayscale for matching (faster)
        region: Optional dict with 'left', 'top', 'width', 'height' to search within
        
    Returns:
        dict: Status and match information
    """
    try:
        # Check if image exists
        if not os.path.exists(image_path):
            return {
                "status": "error",
                "message": f"Image file not found: {image_path}"
            }
        
        # Take screenshot of the region or full screen
        if region:
            screenshot = pyautogui.screenshot(region=(
                region.get('left', 0),
                region.get('top', 0),
                region.get('width', 0),
                region.get('height', 0)
            ))
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot_np = np.array(screenshot)
        screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Load template image
        template = cv2.imread(image_path)
        if template is None:
            return {
                "status": "error",
                "message": f"Failed to load template image: {image_path}"
            }
        
        # Convert to grayscale if requested
        if grayscale:
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Perform template matching
            result = cv2.matchTemplate(
                screenshot_gray, 
                template_gray, 
                cv2.TM_CCOEFF_NORMED
            )
        else:
            # For color images, we'll match each channel and average the results
            channels = cv2.split(template)
            result = None
            
            for channel in channels:
                if result is None:
                    result = cv2.matchTemplate(
                        screenshot_np, 
                        channel, 
                        cv2.TM_CCOEFF_NORMED
                    )
                else:
                    result += cv2.matchTemplate(
                        screenshot_np, 
                        channel, 
                        cv2.TM_CCOEFF_NORMED
                    )
            
            result /= len(channels)
        
        # Find all matches above confidence threshold
        locations = np.where(result >= confidence)
        matches = []
        
        for pt in zip(*locations[::-1]):
            matches.append({
                'x': int(pt[0]) + (region['left'] if region else 0),
                'y': int(pt[1]) + (region['top'] if region else 0),
                'width': template.shape[1],
                'height': template.shape[0],
                'confidence': float(result[pt[1], pt[0]])
            })
        
        # Remove duplicate matches (non-maximum suppression)
        matches = _nms_matches(matches, 0.5)
        
        return {
            "status": "success",
            "matches_found": len(matches),
            "matches": matches,
            "confidence_threshold": confidence,
            "search_region": region
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _nms_matches(matches: list, overlap_threshold: float) -> list:
    """Apply non-maximum suppression to remove overlapping matches."""
    if not matches:
        return []
    
    # Convert to numpy array for easier manipulation
    boxes = np.array([[
        m['x'], m['y'], 
        m['x'] + m['width'], 
        m['y'] + m['height']
    ] for m in matches])
    confidences = np.array([m['confidence'] for m in matches])
    
    # If no boxes, return empty list
    if len(boxes) == 0:
        return []
    
    # Initialize the list of picked indexes
    pick = []
    
    # Grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    
    # Compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(confidences)
    
    # Keep looping while some indexes still remain in the indexes list
    while len(idxs) > 0:
        # Grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        
        # Find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        
        # Compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        
        # Compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]
        
        # Delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlap_threshold)[0])))
    
    # Return only the matches that were picked
    return [matches[i] for i in pick]

@tool
def get_text_under_cursor(region: Optional[Dict[str, int]] = None) -> dict:
    """
    Get text at the current cursor position using OCR.
    
    Args:
        region: Optional dict with 'width' and 'height' to define a region around the cursor
        
    Returns:
        dict: Status and extracted text
    """
    try:
        import pytesseract
        from PIL import ImageGrab
        
        # Get cursor position
        x, y = pyautogui.position()
        
        # Define region around cursor
        width = region.get('width', 200) if region else 200
        height = region.get('height', 50) if region else 50
        
        left = max(0, x - width // 2)
        top = max(0, y - height // 2)
        
        # Capture screen region
        screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))
        
        # Use Tesseract to extract text
        text = pytesseract.image_to_string(screenshot)
        text = text.strip()
        
        return {
            "status": "success",
            "text": text,
            "position": {
                "x": x,
                "y": y,
                "region": {
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height,
                    "right": left + width,
                    "bottom": top + height
                }
            }
        }
    except ImportError:
        return {
            "status": "error",
            "message": "pytesseract is required for OCR. Install with: pip install pytesseract"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_ui_tree(max_depth: int = 3, 
               app: Optional[Application] = None) -> dict:
    """
    Get a hierarchical representation of the UI tree.
    
    Args:
        max_depth: Maximum depth to traverse the UI tree (default: 3)
        app: Optional Application instance to get UI tree from
        
    Returns:
        dict: Hierarchical UI tree structure
    """
    try:
        if app is None:
            app = Application(backend="uia").connect(active_only=True)
        
        def get_element_tree(element, depth=0):
            if depth > max_depth:
                return None
                
            try:
                element_info = {
                    "class_name": element.class_name(),
                    "text": element.window_text()[:100],  # Limit text length
                    "control_type": getattr(element.element_info, 'control_type', None),
                    "automation_id": getattr(element, 'automation_id', lambda: '')(),
                    "is_visible": element.is_visible(),
                    "is_enabled": element.is_enabled(),
                    "rect": {
                        "left": element.rectangle().left,
                        "top": element.rectangle().top,
                        "right": element.rectangle().right,
                        "bottom": element.rectangle().bottom,
                        "width": element.rectangle().width(),
                        "height": element.rectangle().height()
                    },
                    "children": []
                }
                
                # Limit children to prevent excessive output
                max_children = 20
                children = []
                try:
                    children = element.children()
                    for i, child in enumerate(children):
                        if i >= max_children:
                            element_info["children"].append({
                                "info": f"... and {len(children) - max_children} more children"
                            })
                            break
                        child_tree = get_element_tree(child, depth + 1)
                        if child_tree:
                            element_info["children"].append(child_tree)
                except Exception as e:
                    element_info["children_error"] = str(e)
                
                return element_info
            except Exception as e:
                return {
                    "error": f"Failed to process element: {str(e)}",
                    "element_type": str(type(element))
                }
        
        # Start with the main window
        main_window = app.top_window()
        ui_tree = get_element_tree(main_window)
        
        return {
            "status": "success",
            "ui_tree": ui_tree,
            "max_depth": max_depth
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Add all tools to __all__
__all__ = [
    'take_screenshot',
    'find_image_on_screen',
    'get_text_under_cursor',
    'get_ui_tree'
]
