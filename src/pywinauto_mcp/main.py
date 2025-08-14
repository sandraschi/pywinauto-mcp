"""
PyWinAuto MCP - FastMCP 2.10 compliant Windows UI automation server.
Fixed version with proper FastMCP integration.
"""

import logging
import logging.config
import time
import asyncio
import sys
import io
import base64
import json
import os
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Callable, cast

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Try to import OCR dependencies
try:
    import pytesseract
    from PIL import Image, ImageGrab
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from fastmcp import FastMCP
from pydantic import BaseModel, Field, validator, HttpUrl, conint, constr
from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader
from functools import wraps
import time
from typing import Callable, TypeVar, Any, cast

# Type variable for generic function typing
F = TypeVar('F', bound=Callable[..., Any])

# Rate limiting
RATE_LIMITS = {}
RATE_LIMIT_WINDOW = 60  # 1 minute window
RATE_LIMIT_MAX = 100  # Max requests per window

def rate_limit(func: F) -> F:
    """Decorator to implement rate limiting."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        client_ip = "default"  # In a real app, get from request
        now = time.time()
        
        # Clean up old entries
        for ip in list(RATE_LIMITS.keys()):
            if now - RATE_LIMITS[ip]['timestamp'] > RATE_LIMIT_WINDOW:
                del RATE_LIMITS[ip]
        
        # Check rate limit
        if client_ip in RATE_LIMITS:
            if RATE_LIMITS[client_ip]['count'] >= RATE_LIMIT_MAX:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            RATE_LIMITS[client_ip]['count'] += 1
        else:
            RATE_LIMITS[client_ip] = {'count': 1, 'timestamp': now}
        
        return await func(*args, **kwargs)
    
    return cast(F, wrapper)
from pywinauto import Desktop, findwindows
from pywinauto.findwindows import ElementNotFoundError, WindowAmbiguousError
from pywinauto.timings import TimeoutError as PywinautoTimeoutError

# Configure logging
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'pywinauto-mcp.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'pywinauto': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False
        }
    }
})

logger = logging.getLogger(__name__)

# Security configuration
API_KEYS = set()  # In production, load from secure storage

class SecurityMiddleware:
    """Middleware for API key authentication and security headers."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Add security headers
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers.update({
                    b"x-content-type-options": b"nosniff",
                    b"x-frame-options": b"DENY",
                    b"x-xss-protection": b"1; mode=block",
                    b"content-security-policy": b"default-src 'self'"
                })
                message["headers"] = list(headers.items())
            await send(message)
        
        # Skip auth for health check
        if scope["path"] == "/health":
            await self.app(scope, receive, send_with_headers)
            return
            
        # Check API key
        api_key = None
        for header_name, header_value in scope.get("headers", []):
            if header_name.lower() == b"x-api-key":
                api_key = header_value.decode()
                break
        
        if not api_key or api_key not in API_KEYS:
            response = {
                "status": "error",
                "error": "Invalid or missing API key"
            }
            await send_with_headers({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                ]
            })
            await send_with_headers({
                "type": "http.response.body",
                "body": json.dumps(response).encode(),
                "more_body": False
            })
            return
        
        # Proceed with the request
        await self.app(scope, receive, send_with_headers)

# Initialize FastMCP app with security middleware
mcp = FastMCP("pywinauto-mcp")
mcp.app.add_middleware(SecurityMiddleware)

# Add CORS middleware (configure as needed)
from fastapi.middleware.cors import CORSMiddleware
mcp.app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Rectangle(BaseModel):
    """Rectangle coordinates and dimensions."""
    left: int = Field(..., description="Left coordinate", ge=0)
    top: int = Field(..., description="Top coordinate", ge=0)
    right: int = Field(..., description="Right coordinate", ge=0)
    bottom: int = Field(..., description="Bottom coordinate", ge=0)
    width: int = Field(..., description="Width in pixels", gt=0)
    height: int = Field(..., description="Height in pixels", gt=0)
    
    @validator('right')
    def validate_right_gte_left(cls, v, values):
        if 'left' in values and v < values['left']:
            raise ValueError('right must be >= left')
        return v
    
    @validator('bottom')
    def validate_bottom_gte_top(cls, v, values):
        if 'top' in values and v < values['top']:
            raise ValueError('bottom must be >= top')
        return v
    
    @validator('width')
    def validate_width_matches_coords(cls, v, values):
        if 'left' in values and 'right' in values and v != (values['right'] - values['left']):
            raise ValueError('width must match right - left')
        return v
    
    @validator('height')
    def validate_height_matches_coords(cls, v, values):
        if 'top' in values and 'bottom' in values and v != (values['bottom'] - values['top']):
            raise ValueError('height must match bottom - top')
        return v


class WindowInfo(BaseModel):
    """Information about a window."""
    window_handle: int = Field(..., description="Unique window handle", gt=0)
    title: str = Field(..., description="Window title", max_length=1024)
    class_name: str = Field(..., description="Window class name", max_length=256)
    process_id: int = Field(..., description="Process ID of the window", gt=0)
    is_visible: bool = Field(..., description="Whether the window is visible")
    is_enabled: bool = Field(..., description="Whether the window is enabled")
    rectangle: Rectangle = Field(..., description="Window position and size")
    
    class Config:
        schema_extra = {
            "example": {
                "window_handle": 123456,
                "title": "Untitled - Notepad",
                "class_name": "Notepad",
                "process_id": 1234,
                "is_visible": True,
                "is_enabled": True,
                "rectangle": {
                    "left": 100,
                    "top": 100,
                    "right": 800,
                    "bottom": 600,
                    "width": 700,
                    "height": 500
                }
            }
        }


class HealthStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"

class SystemInfo(BaseModel):
    """System information model."""
    platform: str = Field(..., description="Operating system platform")
    python_version: str = Field(..., description="Python version")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    uptime: float = Field(..., description="System uptime in seconds")

@mcp.tool()
@rate_limit
async def health_check() -> Dict[str, Any]:
    """
    Check the health status of the PyWinAuto MCP server.
    
    Returns:
        Dict containing service status, version, and system information
    """
    try:
        # Get system information
        import platform
        import psutil
        
        system_info = {
            "status": HealthStatus.OK,
            "service": "pywinauto-mcp",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "uptime": time.time() - psutil.boot_time()
            },
            "dependencies": {
                "fastmcp": "2.10.0",  # Should be dynamically checked
                "pywinauto": "0.6.8",
                "pydantic": "2.0.0",
                "opencv-python": "4.8.0",
                "pytesseract": "0.3.10"
            },
            "services": {
                "ocr_available": OCR_AVAILABLE,
                "windows_automation": True
            }
        }
        
        # Check for warnings
        warnings = []
        if system_info["system"]["cpu_usage"] > 90:
            warnings.append("High CPU usage")
            system_info["status"] = HealthStatus.WARNING
            
        if system_info["system"]["memory_usage"] > 90:
            warnings.append("High memory usage")
            system_info["status"] = HealthStatus.WARNING
            
        if warnings:
            system_info["warnings"] = warnings
        
        return system_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": HealthStatus.ERROR,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@mcp.tool()
def find_window(
    title: Optional[str] = None,
    class_name: Optional[str] = None,
    process_id: Optional[int] = None,
    timeout: float = 10.0
) -> Dict[str, Any]:
    """Find a window by its attributes."""
    start_time = time.time()
    last_error = None
    
    while time.time() - start_time < timeout:
        try:
            criteria = {}
            if title:
                criteria["title_re"] = title
            if class_name:
                criteria["class_name"] = class_name
            if process_id:
                criteria["process"] = process_id
                
            if not criteria:
                raise ValueError("At least one search criteria must be provided")
                
            # Try to find the window
            try:
                handle = findwindows.find_window(**criteria)
                window = Desktop(backend="uia").window(handle=handle)
                
                rect = window.rectangle()
                window_info = WindowInfo(
                    window_handle=handle,
                    title=window.window_text(),
                    class_name=window.class_name(),
                    process_id=window.process_id(),
                    is_visible=window.is_visible(),
                    is_enabled=window.is_enabled(),
                    rectangle=Rectangle(
                        left=rect.left,
                        top=rect.top,
                        right=rect.right,
                        bottom=rect.bottom,
                        width=rect.width(),
                        height=rect.height()
                    )
                )
                
                return {
                    "status": "success",
                    "result": window_info.dict()
                }
                
            except findwindows.WindowNotFoundError as e:
                last_error = e
                time.sleep(0.5)
                continue
                
        except Exception as e:
            logger.error(f"Error finding window: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    error_msg = f"Timed out after {timeout} seconds while trying to find window"
    if last_error:
        error_msg += f". Last error: {str(last_error)}"
        
    return {
        "status": "error",
        "error": error_msg
    }


@mcp.tool()
def click_element(
    window_handle: int,
    control_id: Optional[str] = None,
    title: Optional[str] = None,
    button: str = "left"
) -> Dict[str, Any]:
    """Click on a UI element in the specified window."""
    try:
        window = Desktop(backend="uia").window(handle=window_handle)
        
        if control_id:
            element = window.child_window(auto_id=control_id)
        elif title:
            element = window.child_window(title=title)
        else:
            element = window
            
        if not element.exists():
            raise ValueError(f"Element not found: control_id={control_id}, title={title}")
            
        element.click(button=button)
        
        return {
            "success": True, 
            "message": "Click performed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception("Error clicking element")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def type_text(
    window_handle: int,
    text: str,
    control_id: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """Type text into a window or control."""
    try:
        window = Desktop(backend="uia").window(handle=window_handle)
        
        if control_id or title:
            element = window.child_window(auto_id=control_id, title=title)
        else:
            element = window
            
        if not element.exists():
            raise ValueError(f"Element not found: control_id={control_id}, title={title}")
            
        element.type_keys(text)
        
        return {
            "success": True, 
            "message": "Text typed successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "text_length": len(text)
        }
        
    except Exception as e:
        logger.exception("Error typing text")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_element_info(
    window_handle: int,
    control_id: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """Get detailed information about a UI element.
    
    Args:
        window_handle: Handle of the parent window
        control_id: ID of the control element (optional)
        title: Title of the control element (optional)
        
    Returns:
        Dictionary containing element information or error details
    """
    try:
        window = Desktop(backend="uia").window(handle=window_handle)
        
        if control_id or title:
            element = window.child_window(auto_id=control_id, title=title)
        else:
            element = window
            
        if not element.exists():
            raise ValueError(f"Element not found: control_id={control_id}, title={title}")
        
        # Get element properties
        rect = element.rectangle()
        element_info = {
            "handle": element.handle,
            "title": element.window_text(),
            "class_name": element.class_name(),
            "control_type": element.element_info.control_type,
            "automation_id": element.element_info.automation_id,
            "is_visible": element.is_visible(),
            "is_enabled": element.is_enabled(),
            "has_keyboard_focus": element.has_keyboard_focus(),
            "is_keyboard_focusable": element.is_keyboard_focusable(),
            "process_id": element.process_id(),
            "rectangle": {
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
                "width": rect.width(),
                "height": rect.height()
            },
            "children_count": len(element.children()),
            "patterns": [p.UserDefinedId for p in element.get_pattern_list()]
        }
        
        return {
            "status": "success",
            "element": element_info
        }
        
    except Exception as e:
        logger.exception("Error getting element info")
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def extract_text(
    image_path: Optional[str] = None,
    window_handle: Optional[int] = None,
    language: str = 'eng'
) -> Dict[str, Any]:
    """Extract text from an image or window using OCR.
    
    Args:
        image_path: Path to the image file (optional if window_handle is provided)
        window_handle: Handle of the window to capture (optional if image_path is provided)
        language: Language for OCR (default: 'eng' for English)
        
    Returns:
        Dictionary containing extracted text and metadata
    """
    if not OCR_AVAILABLE:
        return {
            "status": "error",
            "error": "OCR dependencies not installed. Install with: pip install pytesseract pillow"
        }
    
    try:
        if image_path:
            # Read image from file
            img = Image.open(image_path)
        elif window_handle:
            # Capture window screenshot
            window = Desktop(backend="uia").window(handle=window_handle)
            if not window.exists():
                raise ValueError(f"Window with handle {window_handle} not found")
                
            # Get window rectangle and capture
            rect = window.rectangle()
            img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
        else:
            raise ValueError("Either image_path or window_handle must be provided")
        
        # Convert to grayscale for better OCR
        img = img.convert('L')
        
        # Perform OCR
        text = pytesseract.image_to_string(img, lang=language)
        
        return {
            "status": "success",
            "text": text.strip(),
            "language": language,
            "source": "file" if image_path else f"window:{window_handle}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception("Error extracting text with OCR")
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def extract_region(
    image_path: str,
    x: int,
    y: int,
    width: int,
    height: int,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """Extract a region from an image.
    
    Args:
        image_path: Path to the source image
        x: X coordinate of the top-left corner
        y: Y coordinate of the top-left corner
        width: Width of the region
        height: Height of the region
        output_path: Path to save the extracted region (optional)
        
    Returns:
        Dictionary with operation status and region information
    """
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Extract region
        region = img[y:y+height, x:x+width]
        
        # Save if output path is provided
        if output_path:
            cv2.imwrite(output_path, region)
        
        # Convert to base64 for the response
        _, buffer = cv2.imencode('.png', region)
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "status": "success",
            "region": {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "image": f"data:image/png;base64,{img_str}"
            },
            "saved_to": output_path,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception("Error extracting image region")
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def find_text(
    text: str,
    image_path: Optional[str] = None,
    window_handle: Optional[int] = None,
    language: str = 'eng',
    regex: bool = False
) -> Dict[str, Any]:
    """Find the position of specific text in an image or window.
    
    Args:
        text: Text to find
        image_path: Path to the image file (optional if window_handle is provided)
        window_handle: Handle of the window to capture (optional if image_path is provided)
        language: Language for OCR (default: 'eng' for English)
        regex: Whether to treat the text as a regular expression
        
    Returns:
        Dictionary containing text position and context
    """
    if not OCR_AVAILABLE:
        return {
            "status": "error",
            "error": "OCR dependencies not installed. Install with: pip install pytesseract pillow"
        }
    
    try:
        if image_path:
            # Read image from file
            img = Image.open(image_path)
        elif window_handle:
            # Capture window screenshot
            window = Desktop(backend="uia").window(handle=window_handle)
            if not window.exists():
                raise ValueError(f"Window with handle {window_handle} not found")
                
            # Get window rectangle and capture
            rect = window.rectangle()
            img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
        else:
            raise ValueError("Either image_path or window_handle must be provided")
        
        # Convert to grayscale for better OCR
        img_gray = img.convert('L')
        
        # Get data including bounding boxes
        data = pytesseract.image_to_data(
            img_gray,
            lang=language,
            output_type=pytesseract.Output.DICT
        )
        
        # Search for the text
        matches = []
        for i, word in enumerate(data['text']):
            if not word.strip():
                continue
                
            # Check for match
            matched = False
            if regex:
                import re
                if re.search(text, word, re.IGNORECASE):
                    matched = True
            elif text.lower() in word.lower():
                matched = True
                
            if matched:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                matches.append({
                    'text': word,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'confidence': float(data['conf'][i]) / 100.0
                })
        
        return {
            "status": "success",
            "matches": matches,
            "count": len(matches),
            "language": language,
            "source": "file" if image_path else f"window:{window_handle}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception("Error finding text in image")
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
def list_windows() -> Dict[str, Any]:
    """List all visible windows on the desktop."""
    try:
        desktop = Desktop(backend="uia")
        windows = []
        
        for window in desktop.windows():
            try:
                if window.is_visible():
                    rect = window.rectangle()
                    window_info = {
                        "handle": window.handle,
                        "title": window.window_text(),
                        "class_name": window.class_name(),
                        "process_id": window.process_id(),
                        "rectangle": {
                            "left": rect.left,
                            "top": rect.top,
                            "right": rect.right,
                            "bottom": rect.bottom,
                            "width": rect.width(),
                            "height": rect.height()
                        }
                    }
                    windows.append(window_info)
            except Exception as e:
                # Skip windows that can't be accessed
                continue
        
        return {
            "status": "success",
            "windows": windows,
            "count": len(windows)
        }
        
    except Exception as e:
        logger.exception("Error listing windows")
        return {
            "status": "error",
            "error": str(e)
        }


def load_environment() -> None:
    """Load environment variables and configuration."""
    from dotenv import load_dotenv
    import os
    
    # Load .env file if it exists
    load_dotenv()
    
    # Load API keys from environment
    api_keys = os.getenv("API_KEYS", "").split(",")
    API_KEYS.update(filter(None, (key.strip() for key in api_keys)))
    
    # Configure logging level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.getLogger().setLevel(log_level)

def log_system_info() -> None:
    """Log system information at startup."""
    import platform
    import psutil
    
    logger.info("=" * 60)
    logger.info(f"Starting PyWinAuto MCP Server")
    logger.info(f"Version: 1.0.0")
    logger.info(f"Python: {platform.python_version()} on {platform.platform()}")
    logger.info(f"CPU: {psutil.cpu_count()} cores, {psutil.cpu_percent()}% usage")
    logger.info(f"Memory: {psutil.virtual_memory().percent}% used")
    logger.info("=" * 60)

def handle_shutdown() -> None:
    """Handle server shutdown gracefully."""
    logger.info("Shutting down PyWinAuto MCP server...")
    # Add any cleanup code here
    logger.info("Server stopped")

def main() -> None:
    """
    Run the PyWinAuto MCP server.
    
    This function initializes the server, loads configuration,
    and starts the FastMCP application.
    """
    try:
        # Load environment and configuration
        load_environment()
        log_system_info()
        
        # Register shutdown handler
        import signal
        signal.signal(signal.SIGINT, lambda s, f: handle_shutdown())
        signal.signal(signal.SIGTERM, lambda s, f: handle_shutdown())
        
        # Start the server
        logger.info("Starting PyWinAuto MCP server...")
        mcp.run(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            reload=os.getenv("ENV", "development") == "development"
        )
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.critical(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        handle_shutdown()


if __name__ == "__main__":
    main()
