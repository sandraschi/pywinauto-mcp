"""
Visual tools for PyWinAuto MCP.

This module provides functions for taking screenshots, image processing,
and optical character recognition (OCR).
"""
import base64
import io
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, BinaryIO

import cv2
import numpy as np
from PIL import Image, ImageGrab, ImageOps

from .utils import (
    register_tool,
    validate_window_handle,
    get_desktop,
    SuccessResponse,
    ErrorResponse,
    timer
)

logger = logging.getLogger(__name__)

# Try to import OCR dependencies
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    logger.warning("pytesseract not available. OCR functionality will be limited.")
    OCR_AVAILABLE = False

__all__ = [
    'take_screenshot',
    'save_screenshot',
    'extract_text',
    'extract_region',
    'find_image',
    'highlight_element'
]

@register_tool(
    name="take_screenshot",
    description="Takes a screenshot of the entire screen or a specific window.",
    category="visual"
)
def take_screenshot(
    window_handle: Optional[int] = None,
    region: Optional[Tuple[int, int, int, int]] = None,
    format: str = "png",
    return_base64: bool = False
) -> Dict[str, Any]:
    """
    Take a screenshot of the entire screen or a specific window.

    Args:
        window_handle: Optional handle of the window to capture (None for entire screen)
        region: Optional tuple (left, top, right, bottom) defining the region to capture
        format: Image format ("png" or "jpg")
        return_base64: If True, return the image as a base64-encoded string

    Returns:
        Dict containing the screenshot data or an error message
    """
    if format.lower() not in ["png", "jpg", "jpeg"]:
        return ErrorResponse(
            error="Invalid format. Must be 'png' or 'jpg'.",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer("Taking screenshot"):
            if window_handle is not None:
                if not validate_window_handle(window_handle):
                    return ErrorResponse(
                        error=f"Invalid window handle: {window_handle}",
                        error_type="InvalidWindowHandle"
                    ).dict()
                
                window = get_desktop().window(handle=window_handle)
                if not window.exists():
                    return ErrorResponse(
                        error=f"Window with handle {window_handle} not found",
                        error_type="WindowNotFound"
                    ).dict()
                
                rect = window.rectangle()
                bbox = (rect.left, rect.top, rect.right, rect.bottom)
                
                if region:
                    left, top, right, bottom = region
                    left += rect.left
                    top += rect.top
                    right = min(rect.right, left + right)
                    bottom = min(rect.bottom, top + bottom)
                    bbox = (left, top, right, bottom)
                
                screenshot = ImageGrab.grab(bbox=bbox)
            else:
                screenshot = ImageGrab.grab(bbox=region)
            
            # Convert to the requested format
            if format.lower() in ["jpg", "jpeg"]:
                format = "JPEG"
                img_io = io.BytesIO()
                screenshot.convert('RGB').save(img_io, format=format, quality=95)
            else:
                format = "PNG"
                img_io = io.BytesIO()
                screenshot.save(img_io, format=format, optimize=True)
            
            img_io.seek(0)
            
            if return_base64:
                img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
                return SuccessResponse(
                    data={
                        "image": img_data,
                        "format": format.lower(),
                        "size": len(img_io.getvalue())
                    }
                ).dict()
            else:
                return SuccessResponse(
                    data={
                        "image": img_io.getvalue(),
                        "format": format.lower(),
                        "size": len(img_io.getvalue())
                    }
                ).dict()
    
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}", exc_info=True)
        return ErrorResponse(
            error=f"Failed to take screenshot: {str(e)}",
            error_type="ScreenshotError"
        ).dict()

@register_tool(
    name="extract_text",
    description="Extracts text from an image or screen region using OCR.",
    category="visual"
)
def extract_text(
    image_path: Optional[str] = None,
    window_handle: Optional[int] = None,
    region: Optional[Tuple[int, int, int, int]] = None,
    language: str = "eng",
    config: str = "--psm 6"
) -> Dict[str, Any]:
    """
    Extract text from an image or screen region using OCR.

    Args:
        image_path: Path to the image file (if not using window/region)
        window_handle: Handle of the window to capture (if not using image_path)
        region: Region to capture (left, top, right, bottom)
        language: Language code for OCR (e.g., 'eng', 'fra', 'spa')
        config: Tesseract configuration parameters

    Returns:
        Dict containing the extracted text and confidence scores
    """
    if not OCR_AVAILABLE:
        return ErrorResponse(
            error="OCR functionality requires pytesseract to be installed. Please install it with: pip install pytesseract",
            error_type="DependencyError"
        ).dict()
    
    if image_path and (window_handle is not None or region is not None):
        return ErrorResponse(
            error="Cannot specify both image_path and window_handle/region",
            error_type="InvalidArgument"
        ).dict()
    
    if not image_path and window_handle is None and region is None:
        return ErrorResponse(
            error="Must specify either image_path or window_handle/region",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer("Extracting text with OCR"):
            if image_path:
                if not os.path.isfile(image_path):
                    return ErrorResponse(
                        error=f"Image file not found: {image_path}",
                        error_type="FileNotFound"
                    ).dict()
                
                image = cv2.imread(image_path)
                if image is None:
                    return ErrorResponse(
                        error=f"Failed to load image: {image_path}",
                        error_type="ImageError"
                    ).dict()
                
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                screenshot_result = take_screenshot(
                    window_handle=window_handle,
                    region=region,
                    format="png"
                )
                
                if not screenshot_result.get("success", False):
                    return screenshot_result
                
                screenshot_data = screenshot_result["data"]["image"]
                nparr = np.frombuffer(screenshot_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply thresholding for better text recognition
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Perform OCR
            data = pytesseract.image_to_data(
                gray, 
                output_type=pytesseract.Output.DICT,
                lang=language,
                config=config
            )
            
            # Process the results
            n_boxes = len(data['level'])
            results = []
            
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # Only include results with confidence > 0
                    results.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'bounding_box': {
                            'left': int(data['left'][i]),
                            'top': int(data['top'][i]),
                            'width': int(data['width'][i]),
                            'height': int(data['height'][i])
                        }
                    })
            
            # Extract just the text
            text = ' '.join([r['text'] for r in results if r['text'].strip()])
            
            return SuccessResponse(
                data={
                    'text': text.strip(),
                    'results': results,
                    'language': language
                }
            ).dict()
    
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}", exc_info=True)
        return ErrorResponse(
            error=f"Failed to extract text: {str(e)}",
            error_type="OCRError"
        ).dict()

@register_tool(
    name="find_image",
    description="Finds a template image within a screenshot or window.",
    category="visual"
)
def find_image(
    template_path: str,
    window_handle: Optional[int] = None,
    region: Optional[Tuple[int, int, int, int]] = None,
    threshold: float = 0.8
) -> Dict[str, Any]:
    """
    Find a template image within a screenshot or window.

    Args:
        template_path: Path to the template image to find
        window_handle: Optional handle of the window to search in (None for entire screen)
        region: Optional region (left, top, right, bottom) to search within
        threshold: Confidence threshold (0-1) for template matching

    Returns:
        Dict containing the match results
    """
    if not os.path.isfile(template_path):
        return ErrorResponse(
            error=f"Template file not found: {template_path}",
            error_type="FileNotFound"
        ).dict()
    
    if not (0 <= threshold <= 1):
        return ErrorResponse(
            error="Threshold must be between 0 and 1",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Finding template image: {template_path}"):
            # Load the template image
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return ErrorResponse(
                    error=f"Failed to load template image: {template_path}",
                    error_type="ImageError"
                ).dict()
            
            # Take a screenshot of the target area
            screenshot_result = take_screenshot(
                window_handle=window_handle,
                region=region,
                format="png"
            )
            
            if not screenshot_result.get("success", False):
                return screenshot_result
            
            # Convert screenshot to OpenCV format
            screenshot_data = screenshot_result["data"]["image"]
            nparr = np.frombuffer(screenshot_data, np.uint8)
            screenshot = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert both images to grayscale
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Get dimensions of the template
            h, w = template_gray.shape
            
            # Perform template matching
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Check if the best match meets the threshold
            if max_val >= threshold:
                # Calculate the center of the matched region
                top_left = max_loc
                center_x = top_left[0] + w // 2
                center_y = top_left[1] + h // 2
                
                # If window_handle was provided, adjust coordinates to be relative to the window
                if window_handle is not None:
                    window = get_desktop().window(handle=window_handle)
                    rect = window.rectangle()
                    center_x += rect.left
                    center_y += rect.top
                # If region was provided, adjust coordinates
                elif region is not None:
                    center_x += region[0]
                    center_y += region[1]
                
                return SuccessResponse(
                    data={
                        "found": True,
                        "confidence": float(max_val),
                        "location": {
                            "x": int(center_x),
                            "y": int(center_y),
                            "width": int(w),
                            "height": int(h)
                        },
                        "bounding_box": {
                            "left": int(top_left[0]),
                            "top": int(top_left[1]),
                            "right": int(top_left[0] + w),
                            "bottom": int(top_left[1] + h)
                        }
                    }
                ).dict()
            else:
                return SuccessResponse(
                    data={
                        "found": False,
                        "confidence": float(max_val),
                        "message": "No match found above threshold"
                    }
                ).dict()
    
    except Exception as e:
        logger.error(f"Error finding image: {str(e)}", exc_info=True)
        return ErrorResponse(
            error=f"Failed to find image: {str(e)}",
            error_type="ImageError"
        ).dict()

@register_tool(
    name="highlight_element",
    description="Highlights a UI element with a colored rectangle.",
    category="visual"
)
def highlight_element(
    window_handle: int,
    control_id: str,
    color: str = "red",
    thickness: int = 2,
    duration: float = 3.0,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Highlight a UI element with a colored rectangle.

    Args:
        window_handle: Handle of the window containing the element
        control_id: Control ID of the element to highlight
        color: Highlight color (name or hex code, e.g., "red" or "#FF0000")
        thickness: Thickness of the highlight border in pixels
        duration: Duration to show the highlight in seconds (0 for just save/return)
        output_path: Optional path to save the highlighted image

    Returns:
        Dict containing the result of the operation
    """
    if not validate_window_handle(window_handle):
        return ErrorResponse(
            error=f"Invalid window handle: {window_handle}",
            error_type="InvalidWindowHandle"
        ).dict()
    
    if thickness < 1:
        return ErrorResponse(
            error="Thickness must be at least 1",
            error_type="InvalidArgument"
        ).dict()
    
    try:
        with timer(f"Highlighting element with control_id '{control_id}'"):
            # Get the window and element
            window = get_desktop().window(handle=window_handle)
            element = window.child_window(control_id=control_id)
            
            if not element.exists():
                return ErrorResponse(
                    error=f"Element with control_id '{control_id}' not found",
                    error_type="ElementNotFound"
                ).dict()
            
            # Get the element's rectangle
            rect = element.rectangle()
            
            # Take a screenshot of the window
            screenshot_result = take_screenshot(
                window_handle=window_handle,
                format="png"
            )
            
            if not screenshot_result.get("success", False):
                return screenshot_result
            
            # Convert screenshot to OpenCV format
            screenshot_data = screenshot_result["data"]["image"]
            nparr = np.frombuffer(screenshot_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert color name to BGR
            color_lower = color.lower()
            if color_lower == "red":
                bgr_color = (0, 0, 255)  # Red in BGR
            elif color_lower == "green":
                bgr_color = (0, 255, 0)  # Green in BGR
            elif color_lower == "blue":
                bgr_color = (255, 0, 0)  # Blue in BGR
            elif color_lower.startswith("#") and len(color) == 7:  # Hex color
                hex_color = color.lstrip('#')
                bgr_color = (
                    int(hex_color[4:6], 16),  # B
                    int(hex_color[2:4], 16),  # G
                    int(hex_color[0:2], 16)   # R
                )
            else:
                bgr_color = (0, 0, 255)  # Default to red
            
            # Draw the highlight rectangle
            cv2.rectangle(
                img,
                (rect.left, rect.top),
                (rect.right, rect.bottom),
                bgr_color,
                thickness
            )
            
            # Save the image if output_path is provided
            saved_path = None
            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                cv2.imwrite(output_path, img)
                saved_path = os.path.abspath(output_path)
            
            # Convert back to PIL Image for display if needed
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            
            # Show the image if duration > 0
            if duration > 0:
                # Save to a temporary file and open it
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                    temp_path = temp_file.name
                    pil_img.save(temp_path)
                
                try:
                    # Open the image with the default viewer
                    os.startfile(temp_path)
                    
                    # Wait for the specified duration
                    time.sleep(duration)
                    
                    # Try to close the image viewer (may not work for all viewers)
                    try:
                        os.system(f'taskkill /F /IM "{os.path.basename(temp_path)}"')
                    except:
                        pass
                    
                finally:
                    # Clean up the temporary file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            # Prepare the response
            response_data = {
                "element": {
                    "control_id": control_id,
                    "bounding_box": {
                        "left": rect.left,
                        "top": rect.top,
                        "right": rect.right,
                        "bottom": rect.bottom,
                        "width": rect.width(),
                        "height": rect.height()
                    }
                },
                "highlight": {
                    "color": color,
                    "thickness": thickness,
                    "duration": duration
                },
                "saved": saved_path is not None,
                "output_path": saved_path
            }
            
            return SuccessResponse(data=response_data).dict()
    
    except Exception as e:
        logger.error(f"Error highlighting element: {str(e)}", exc_info=True)
        return ErrorResponse(
            error=f"Failed to highlight element: {str(e)}",
            error_type="VisualError"
        ).dict()
