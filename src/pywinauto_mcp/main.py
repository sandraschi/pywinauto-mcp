"""
PyWinAuto MCP - FastMCP 2.10 compliant Windows UI automation server.

This module provides a FastMCP server that exposes Windows UI automation capabilities
through a RESTful API, with full support for FastMCP 2.10 tool definitions,
structured output, and elicitation patterns.
"""

import logging
import time
import win32gui
import win32process
import psutil
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union, Annotated, Tuple

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP, mcp
from pydantic import BaseModel, Field, HttpUrl, conint, constr
from pywinauto import Application, Desktop, findwindows, timings
from pywinauto.controls.uia_controls import EditWrapper
from pywinauto.findwindows import ElementNotFoundError, WindowAmbiguousError
from pywinauto.timings import TimeoutError as PywinautoTimeoutError

from .config import settings
from . import security_endpoints  # Import security endpoints to register tools
from .api import face_recognition  # Import face recognition endpoints

# Type aliases
WindowHandle = int
ProcessId = int
ControlId = str


class MouseButton(str, Enum):
    """Mouse button types."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    PRIMARY = "primary"  # Alias for left
    SECONDARY = "secondary"  # Alias for right


class ModifierKey(str, Enum):
    """Keyboard modifier keys."""
    SHIFT = "shift"
    CTRL = "ctrl"
    ALT = "alt"
    WIN = "win"


class Rectangle(BaseModel):
    """Rectangle coordinates and dimensions."""
    left: int = Field(..., description="Left coordinate")
    top: int = Field(..., description="Top coordinate")
    right: int = Field(..., description="Right coordinate")
    bottom: int = Field(..., description="Bottom coordinate")
    width: int = Field(..., description="Width in pixels")
    height: int = Field(..., description="Height in pixels")


class WindowInfo(BaseModel):
    """Information about a window."""
    window_handle: WindowHandle = Field(..., description="Unique window handle")
    title: str = Field(..., description="Window title")
    class_name: str = Field(..., description="Window class name")
    process_id: ProcessId = Field(..., description="Process ID of the window")
    is_visible: bool = Field(..., description="Whether the window is visible")
    is_enabled: bool = Field(..., description="Whether the window is enabled")
    rectangle: Rectangle = Field(..., description="Window position and size")
    url: Optional[HttpUrl] = Field(None, description="URL if this is a browser window")
    process_name: Optional[str] = Field(None, description="Name of the process")
    executable_path: Optional[str] = Field(None, description="Path to the executable")


class ElementInfo(BaseModel):
    """Information about a UI element."""
    handle: int = Field(..., description="Element handle")
    name: str = Field(..., description="Element name")
    class_name: str = Field(..., description="Element class name")
    control_type: str = Field(..., description="Type of the control")
    is_visible: bool = Field(..., description="Whether the element is visible")
    is_enabled: bool = Field(..., description="Whether the element is enabled")
    has_keyboard_focus: bool = Field(..., description="Whether the element has keyboard focus")
    rectangle: Rectangle = Field(..., description="Element position and size")
    automation_id: Optional[str] = Field(None, description="Automation ID of the element")
    control_id: Optional[int] = Field(None, description="Control ID")
    process_id: Optional[ProcessId] = Field(None, description="Process ID of the element")
    runtime_id: Optional[str] = Field(None, description="Runtime ID of the element")
    text: Optional[str] = Field(None, description="Text content (for text controls)")
    is_readonly: Optional[bool] = Field(None, description="Whether the element is read-only")
    line_count: Optional[int] = Field(None, description="Number of lines (for text controls)")
    value: Optional[Union[str, int, float, bool]] = Field(
        None, 
        description="Current value of the element"
    )
    pattern_support: Dict[str, bool] = Field(
        default_factory=dict,
        description="Supported UI automation patterns"
    )
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional element properties"
    )

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize security modules
app_monitor.init()
intruder_detector.init()
# Face recognition module is initialized when imported

# Initialize FastMCP app
app = FastMCP(
    name=settings.MCP_NAME,
    version=settings.MCP_VERSION,
    description=settings.MCP_DESCRIPTION,
    log_level=settings.LOG_LEVEL,
    # Enable structured output for LARKS
    structured_output=True,
    # Enable elicitation for better user interaction
    enable_elicitation=True,
    # Define tool categories for better organization
    tool_categories=[
        {"name": "windows", "description": "Window management operations"},
        {"name": "elements", "description": "UI element interactions"},
        {"name": "input", "description": "Keyboard and mouse input"},
        {"name": "info", "description": "Information retrieval"},
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global application cache
app.state.windows = {}


def get_application(process_id: Optional[int] = None, **kwargs) -> Application:
    """Get or create a PyWinAuto Application instance."""
    if process_id and process_id in app.state.windows:
        return app.state.windows[process_id]
    
    app_instance = Application(backend="uia").connect(process=process_id, **kwargs)
    if process_id:
        app.state.windows[process_id] = app_instance
    return app_instance


@app.on_event("startup")
async def startup_event():
    """Initialize application state."""
    logger.info("Starting PyWinAuto MCP server...")
    logger.info(f"Server running on http://{settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down PyWinAuto MCP server...")


@mcp.tool(
    name="health_check",
    description="Check if the PyWinAuto MCP server is running",
    category="info",
    output_schema={
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Service status"},
            "service": {"type": "string", "description": "Service name"},
            "version": {"type": "string", "description": "Service version"},
            "timestamp": {"type": "string", "format": "date-time", "description": "Current server time"}
        },
        "required": ["status", "service", "version", "timestamp"]
    },
    examples=[
        {"name": "Basic health check", "input": {}}
    ]
)
@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Service health status and version information.
        
    Example:
        ```json
        {
            "status": "ok",
            "service": "pywinauto-mcp",
            "version": "0.1.0",
            "timestamp": "2025-07-27T22:45:00Z"
        }
        ```
    """
    return {
        "status": "ok",
        "service": settings.MCP_NAME,
        "version": settings.MCP_VERSION,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


@mcp.tool(
    name="find_window",
    description="Find a window by its attributes such as title, class name, or process ID",
    category="windows",
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Window title (supports regex)",
                "x-elicitation": {
                    "type": "text",
                    "placeholder": "Enter window title or part of it"
                }
            },
            "class_name": {
                "type": "string",
                "description": "Window class name"
            },
            "process_id": {
                "type": "integer",
                "description": "Process ID of the window"
            },
            "timeout": {
                "type": "number",
                "description": "Timeout in seconds",
                "default": 10.0
            }
        },
        "anyOf": [
            {"required": ["title"]},
            {"required": ["class_name"]},
            {"required": ["process_id"]}
        ]
    },
    output_schema=WindowInfo.schema(),
    examples=[
        {
            "name": "Find by title",
            "input": {"title": "Notepad"}
        },
        {
            "name": "Find by class name",
            "input": {"class_name": "Notepad", "timeout": 5.0}
        }
    ]
)
@app.post("/api/windows/find")
async def find_window(
    title: Optional[str] = Query(
        None,
        description="Window title (supports regex)",
        example="Untitled - Notepad"
    ),
    class_name: Optional[str] = Query(
        None,
        description="Window class name",
        example="Notepad"
    ),
    process_id: Optional[int] = Query(
        None,
        description="Process ID of the window",
        ge=0,
        example=1234
    ),
    timeout: float = Query(
        settings.TIMEOUT,
        description="Timeout in seconds",
        ge=0.1,
        le=60.0,
        example=10.0
    ),
) -> WindowInfo:
    """
    Find a window by its attributes.
    
    This tool locates a window using the specified criteria and returns detailed
    information about it. At least one search criterion must be provided.
    
    Args:
        title: Window title (supports regex)
        class_name: Window class name
        process_id: Process ID of the window
        timeout: Maximum time to wait for the window to be found (seconds)
        
    Returns:
        WindowInfo: Detailed information about the found window
        
    Raises:
        HTTPException: If no matching window is found or an error occurs
        
    Example:
        ```python
        # Find Notepad window by title
        window = find_window(title="Untitled - Notepad")
        
        # Find window by class name with a shorter timeout
        window = find_window(class_name="Notepad", timeout=5.0)
        ```
    """
    try:
        criteria = {}
        if title:
            criteria["title_re"] = title
        if class_name:
            criteria["class_name"] = class_name
        if process_id:
            criteria["process"] = process_id
            
        if not criteria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one search criteria must be provided"
            )
            
        handle = findwindows.find_window(**criteria, timeout=timeout)
        window = Desktop(backend="uia").window(handle=handle)
        
        return {
            "window_handle": handle,
            "title": window.window_text(),
            "class_name": window.class_name(),
            "process_id": window.process_id(),
            "is_visible": window.is_visible(),
            "is_enabled": window.is_enabled(),
            "rectangle": {
                "left": window.rectangle().left,
                "top": window.rectangle().top,
                "right": window.rectangle().right,
                "bottom": window.rectangle().bottom,
                "width": window.rectangle().width(),
                "height": window.rectangle().height(),
            },
        }
        
    except (ElementNotFoundError, WindowAmbiguousError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PywinautoTimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"Window not found within {timeout} seconds"
        )
    except Exception as e:
        logger.exception("Error finding window")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


class ClickAction(BaseModel):
    """Result of a click action."""
    success: bool = Field(..., description="Whether the click was successful")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="When the action was performed")
    element_info: Optional[ElementInfo] = Field(None, description="Information about the clicked element")


@mcp.tool(
    name="click_element",
    description="Click on a UI element in the specified window",
    category="elements",
    input_schema={
        "type": "object",
        "properties": {
            "window_handle": {
                "type": "integer",
                "description": "Handle of the parent window",
                "x-elicitation": {
                    "type": "function",
                    "function": "find_window",
                    "output_property": "window_handle"
                }
            },
            "control_id": {
                "type": "string",
                "description": "Automation ID of the control to click",
                "x-elicitation": {
                    "type": "function",
                    "function": "find_element",
                    "output_property": "automation_id"
                }
            },
            "control_type": {
                "type": "string",
                "description": "Type of the control (e.g., 'Button', 'Edit')",
                "enum": ["Button", "Edit", "MenuItem", "TreeItem", "CheckBox", "RadioButton", "ComboBox", "List", "DataGrid", "Document"],
                "default": "Button"
            },
            "title": {
                "type": "string",
                "description": "Title or name of the control"
            },
            "double": {
                "type": "boolean",
                "description": "Whether to perform a double-click",
                "default": False
            },
            "button": {
                "type": "string",
                "description": "Mouse button to use",
                "enum": [b.value for b in MouseButton],
                "default": "left"
            },
            "pressed": {
                "type": "string",
                "description": "Modifier keys to press during the click (comma-separated)",
                "default": ""
            },
            "coords": {
                "type": "array",
                "items": {"type": "integer"},
                "minItems": 2,
                "maxItems": 2,
                "description": "[x, y] coordinates relative to the element"
            }
        },
        "required": ["window_handle"],
        "anyOf": [
            {"required": ["control_id"]},
            {"required": ["title"]}
        ]
    },
    output_schema=ClickAction.schema(),
    examples=[
        {
            "name": "Click a button by ID",
            "input": {"window_handle": 123456, "control_id": "btnSubmit"}
        },
        {
            "name": "Right-click with modifier keys",
            "input": {"window_handle": 123456, "title": "File", "button": "right", "pressed": "ctrl+shift"}
        }
    ]
)
@app.post("/api/element/click")
async def click_element(
    window_handle: int = Query(..., description="Handle of the parent window"),
    control_id: Optional[str] = Query(None, description="Automation ID of the control"),
    control_type: Optional[str] = Query(None, description="Type of the control"),
    title: Optional[str] = Query(None, description="Title or name of the control"),
    double: bool = Query(False, description="Whether to perform a double-click"),
    button: MouseButton = Query("left", description="Mouse button to use"),
    pressed: str = Query("", description="Modifier keys to press during the click"),
    coords: Optional[tuple[int, int]] = Query(None, description="[x, y] coordinates relative to the element"),
) -> ClickAction:
    """
    Click on a UI element in the specified window.
    
    This tool allows clicking on any UI element within a window using various
    identification methods. It supports different mouse buttons and modifier keys.
    
    Args:
        window_handle: Handle of the parent window (from find_window)
        control_id: Automation ID of the control to click
        control_type: Type of the control (e.g., 'Button', 'Edit')
        title: Title or name of the control
        double: Whether to perform a double-click
        button: Mouse button to use ('left', 'right', 'middle')
        pressed: Modifier keys to press during the click (e.g., 'ctrl+shift')
        coords: [x, y] coordinates relative to the element
        
    Returns:
        ClickAction: Result of the click operation with element information
        
    Raises:
        HTTPException: If the element is not found or the click fails
        
    Example:
        ```python
        # Click a button by its automation ID
        result = click_element(
            window_handle=123456,
            control_id="btnSubmit"
        )
        
        # Right-click with modifier keys
        result = click_element(
            window_handle=123456,
            title="File",
            button="right",
            pressed="ctrl+shift"
        )
        ```
    """
    try:
        window = Desktop(backend="uia").window(handle=window_handle)
        
        # Find the target element
        if control_id:
            element = window.child_window(auto_id=control_id, control_type=control_type)
        elif title:
            element = window.child_window(title=title, control_type=control_type)
        else:
            element = window
            
        if not element.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Element not found: control_id={control_id}, title={title}"
            )
            
        # Perform the click
        if coords:
            element.click_input(button=button, coords=coords, double=double, pressed=pressed)
        else:
            element.click(button=button, double=double, pressed=pressed)
            
        return {"status": "success", "message": "Click performed successfully"}
        
    except Exception as e:
        logger.exception("Error clicking element")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


class WindowState(str, Enum):
    """Window state options."""
    NORMAL = "normal"
    MAXIMIZED = "maximized"
    MINIMIZED = "minimized"
    HIDDEN = "hidden"


class WindowInfoList(BaseModel):
    """List of window information."""
    windows: List[WindowInfo] = Field(..., description="List of window information objects")
    count: int = Field(..., description="Total number of windows found")
    timestamp: str = Field(..., description="When the list was generated")


class WindowActionResult(BaseModel):
    """Result of a window action."""
    success: bool = Field(..., description="Whether the action was successful")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="When the action was performed")
    window_info: Optional[WindowInfo] = Field(None, description="Updated window information")


class TypeAction(BaseModel):
    """Result of a type action."""
    success: bool = Field(..., description="Whether typing was successful")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="When the action was performed")
    element_info: Optional[ElementInfo] = Field(None, description="Information about the target element")
    text_typed: str = Field(..., description="The text that was actually typed")
    text_length: int = Field(..., description="Number of characters typed")


@mcp.tool(
    name="type_text",
    description="Type text into a window or control",
    category="elements",
    input_schema={
        "type": "object",
        "properties": {
            "window_handle": {
                "type": "integer",
                "description": "Handle of the parent window",
                "x-elicitation": {
                    "type": "function",
                    "function": "find_window",
                    "output_property": "window_handle"
                }
            },
            "text": {
                "type": "string",
                "description": "Text to type into the control",
                "x-elicitation": {
                    "type": "text",
                    "placeholder": "Enter text to type"
                }
            },
            "control_id": {
                "type": "string",
                "description": "Automation ID of the target control"
            },
            "control_type": {
                "type": "string",
                "description": "Type of the control (e.g., 'Edit')",
                "enum": ["Edit", "Document", "ComboBox", "PasswordBox"],
                "default": "Edit"
            },
            "title": {
                "type": "string",
                "description": "Title or name of the control"
            },
            "with_spaces": {
                "type": "boolean",
                "description": "Whether to include spaces in the typed text",
                "default": True
            },
            "with_newlines": {
                "type": "boolean",
                "description": "Whether to include newlines in the typed text",
                "default": True
            },
            "with_tabs": {
                "type": "boolean",
                "description": "Whether to include tabs in the typed text",
                "default": True
            },
            "clear_first": {
                "type": "boolean",
                "description": "Whether to clear the field before typing",
                "default": True
            },
            "set_value": {
                "type": "boolean",
                "description": "Use set_value() instead of type_keys() for better performance",
                "default": False
            }
        },
        "required": ["window_handle", "text"]
    },
    output_schema=TypeAction.schema(),
    examples=[
        {
            "name": "Type into an edit field",
            "input": {
                "window_handle": 123456,
                "control_id": "txtUsername",
                "text": "testuser@example.com"
            }
        },
        {
            "name": "Type with special keys",
            "input": {
                "window_handle": 123456,
                "text": "Line 1{ENTER}Line 2{TAB}After tab",
                "with_newlines": False
            }
        }
    ]
)
@app.post("/api/element/type")
async def type_text(
    window_handle: int = Query(..., description="Handle of the parent window"),
    text: str = Query(..., description="Text to type into the control"),
    control_id: Optional[str] = Query(None, description="Automation ID of the target control"),
    control_type: Optional[str] = Query("Edit", description="Type of the control"),
    title: Optional[str] = Query(None, description="Title or name of the control"),
    with_spaces: bool = Query(True, description="Whether to include spaces in the typed text"),
    with_newlines: bool = Query(True, description="Whether to include newlines in the typed text"),
    with_tabs: bool = Query(True, description="Whether to include tabs in the typed text"),
    clear_first: bool = Query(True, description="Whether to clear the field before typing"),
    set_value: bool = Query(False, description="Use set_value() for better performance"),
) -> TypeAction:
    """
    Type text into a window or control.
    
    This tool simulates keyboard input to type text into the specified control.
    It supports special key sequences like {ENTER}, {TAB}, {BACKSPACE}, etc.
    
    Args:
        window_handle: Handle of the parent window (from find_window)
        text: Text to type into the control
        control_id: Automation ID of the target control
        control_type: Type of the control (e.g., 'Edit', 'Document')
        title: Title or name of the control
        with_spaces: Whether to include spaces in the typed text
        with_newlines: Whether to include newlines in the typed text
        with_tabs: Whether to include tabs in the typed text
        clear_first: Whether to clear the field before typing
        set_value: Use set_value() instead of type_keys() for better performance
        
    Returns:
        TypeAction: Result of the type operation with details
        
    Raises:
        HTTPException: If the target element is not found or not editable
        
    Example:
        ```python
        # Type into a text field
        result = type_text(
            window_handle=123456,
            control_id="usernameField",
            text="testuser@example.com"
        )
        
        # Type with special keys (press ENTER after text)
        result = type_text(
            window_handle=123456,
            text="Search query{ENTER}",
            with_newlines=False
        )
        ```
    """
    try:
        window = Desktop(backend="uia").window(handle=window_handle)
        
        # Find the target element if specified
        if control_id or title:
            element = window.child_window(
                auto_id=control_id,
                control_type=control_type,
                title=title
            )
        else:
            element = window
            
        if not element.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Element not found: control_id={control_id}, title={title}"
            )
            
        # Type the text
        element.type_keys(
            text,
            with_spaces=with_spaces,
            with_newlines=with_newlines,
            with_tabs=with_tabs,
        )
        
        return {"status": "success", "message": "Text typed successfully"}
        
    except Exception as e:
        logger.exception("Error typing text")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@mcp.tool()
@app.post("/api/element/info")
async def get_element_info(
    window_handle: int,
    control_id: Optional[str] = None,
    control_type: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get information about a UI element.
    
    Args:
        window_handle: Handle of the parent window
        control_id: Automation ID of the control
        control_type: Type of the control
        title: Title or name of the control
        
    Returns:
        Element information
    """
    try:
        window = Desktop(backend="uia").window(handle=window_handle)
        
        # Find the target element if specified
        if control_id or title:
            element = window.child_window(
                auto_id=control_id,
                control_type=control_type,
                title=title
            )
        else:
            element = window
            
        if not element.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Element not found: control_id={control_id}, title={title}"
            )
            
        # Get element properties
        element_info = {
            "handle": element.handle,
            "name": element.window_text(),
            "class_name": element.class_name(),
            "control_type": element.friendly_class_name(),
            "is_visible": element.is_visible(),
            "is_enabled": element.is_enabled(),
            "has_keyboard_focus": element.has_keyboard_focus(),
            "rectangle": {
                "left": element.rectangle().left,
                "top": element.rectangle().top,
                "right": element.rectangle().right,
                "bottom": element.rectangle().bottom,
                "width": element.rectangle().width(),
                "height": element.rectangle().height(),
            },
            "automation_id": element.automation_id(),
            "control_id": element.control_id(),
            "process_id": element.process_id(),
            "runtime_id": element.runtime_id(),
        }
        
        # Add additional properties for specific control types
        if isinstance(element, EditWrapper):
            element_info["text"] = element.get_value()
            element_info["is_readonly"] = element.is_read_only()
            element_info["line_count"] = element.line_count()
            
        return element_info
        
    except Exception as e:
        logger.exception("Error getting element info")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@mcp.tool(
    name="list_windows",
    description="List all open windows matching the specified criteria",
    category="window_management",
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Filter by window title (supports regex)",
                "default": ".*"
            },
            "class_name": {
                "type": "string",
                "description": "Filter by window class name",
                "default": ".*"
            },
            "process_name": {
                "type": "string",
                "description": "Filter by process name (e.g., 'notepad.exe')"
            },
            "visible_only": {
                "type": "boolean",
                "description": "Whether to include only visible windows",
                "default": True
            },
            "enabled_only": {
                "type": "boolean",
                "description": "Whether to include only enabled windows",
                "default": True
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "minimum": 1,
                "maximum": 1000,
                "default": 100
            }
        }
    },
    output_schema=WindowInfoList.schema(),
    examples=[
        {
            "name": "List all visible Notepad windows",
            "input": {"title": ".*Notepad.*", "visible_only": True}
        },
        {
            "name": "List all visible windows from a specific process",
            "input": {"process_name": "chrome.exe", "visible_only": True}
        }
    ]
)
@app.get("/api/windows")
async def list_windows(
    title: str = Query(".*", description="Filter by window title (supports regex)"),
    class_name: str = Query(".*", description="Filter by window class name"),
    process_name: Optional[str] = Query(None, description="Filter by process name"),
    visible_only: bool = Query(True, description="Include only visible windows"),
    enabled_only: bool = Query(True, description="Include only enabled windows"),
    max_results: int = Query(100, description="Maximum number of results to return", ge=1, le=1000),
) -> WindowInfoList:
    """
    List all open windows matching the specified criteria.
    
    This tool provides a filtered list of all open windows based on the specified
    criteria such as title, class name, process name, and window state.
    
    Args:
        title: Regular expression pattern to match window titles
        class_name: Regular expression pattern to match window class names
        process_name: Name of the process that owns the window (e.g., 'notepad.exe')
        visible_only: Whether to include only visible windows
        enabled_only: Whether to include only enabled windows
        max_results: Maximum number of windows to return (1-1000)
        
    Returns:
        WindowInfoList: List of matching windows with their details
        
    Example:
        ```python
        # List all visible Notepad windows
        result = list_windows(title=".*Notepad.*", visible_only=True)
        
        # List all Chrome browser windows
        result = list_windows(process_name="chrome.exe", visible_only=True)
        
        # List all windows with a specific class
        result = list_windows(class_name="Chrome_WidgetWin_1")
        ```
    """
    try:
        desktop = Desktop(backend="uia")
        windows = []
        
        # Get all top-level windows
        try:
            top_windows = desktop.windows(
                visible_only=visible_only,
                enabled_only=enabled_only,
                title=title,
                class_name=class_name,
            )
            
            # Filter by process name if specified
            if process_name:
                top_windows = [
                    w for w in top_windows 
                    if w.process_id() and 
                    process_name.lower() in w.process_name().lower()
                ]
            
            # Convert to WindowInfo objects
            for window in top_windows[:max_results]:
                try:
                    rect = window.rectangle()
                    window_info = WindowInfo(
                        window_handle=window.handle,
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
                        ),
                        process_name=window.process_name(),
                        executable_path=window.executable_path()
                    )
                    windows.append(window_info)
                except Exception as e:
                    logger.warning(f"Error getting window info: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list windows: {str(e)}"
            )
            
        return WindowInfoList(
            windows=windows,
            count=len(windows),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in list_windows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@mcp.tool(
    name="set_window_state",
    description="Change the state of a window (minimize, maximize, restore, hide)",
    category="window_management",
    input_schema={
        "type": "object",
        "properties": {
            "window_handle": {
                "type": "integer",
                "description": "Handle of the window to modify",
                "x-elicitation": {
                    "type": "function",
                    "function": "list_windows",
                    "output_property": "windows[].window_handle"
                }
            },
            "state": {
                "type": "string",
                "enum": [s.value for s in WindowState],
                "description": "New window state"
            },
            "timeout": {
                "type": "number",
                "minimum": 0.1,
                "maximum": 30.0,
                "default": 5.0,
                "description": "Timeout in seconds"
            }
        },
        "required": ["window_handle", "state"]
    },
    output_schema=WindowActionResult.schema(),
    examples=[
        {
            "name": "Maximize a window",
            "input": {"window_handle": 123456, "state": "maximized"}
        },
        {
            "name": "Minimize a window",
            "input": {"window_handle": 123456, "state": "minimized"}
        },
        {
            "name": "Restore a window",
            "input": {"window_handle": 123456, "state": "normal"}
        }
    ]
)
@app.post("/api/window/{window_handle}/state")
async def set_window_state(
    window_handle: int = Path(..., description="Handle of the window to modify"),
    state: WindowState = Query(..., description="New window state"),
    timeout: float = Query(5.0, description="Timeout in seconds", ge=0.1, le=30.0),
) -> WindowActionResult:
    """
    Change the state of a window (minimize, maximize, restore, hide).
    
    This tool allows you to change the state of a window, such as minimizing,
    maximizing, restoring, or hiding it. The window is identified by its handle.
    
    Args:
        window_handle: Handle of the window to modify
        state: New window state (minimized, maximized, normal, hidden)
        timeout: Maximum time to wait for the operation to complete (seconds)
        
    Returns:
        WindowActionResult: Result of the operation with updated window info
        
    Raises:
        HTTPException: If the window is not found or the operation fails
        
    Example:
        ```python
        # Maximize a window
        result = set_window_state(window_handle=123456, state="maximized")
        
        # Minimize a window
        result = set_window_state(window_handle=123456, state="minimized")
        
        # Restore a window to normal state
        result = set_window_state(window_handle=123456, state="normal")
        ```
    """
    try:
        desktop = Desktop(backend="uia")
        
        try:
            window = desktop.window(handle=window_handle)
            
            # Save current state for rollback
            original_state = {
                "is_visible": window.is_visible(),
                "is_minimized": window.is_minimized(),
                "is_maximized": window.is_maximized()
            }
            
            # Apply the new state
            try:
                if state == WindowState.MINIMIZED:
                    window.minimize()
                elif state == WindowState.MAXIMIZED:
                    window.maximize()
                elif state == WindowState.NORMAL:
                    if window.is_minimized() or window.is_maximized():
                        window.restore()
                elif state == WindowState.HIDDEN:
                    window.hide()
                    
                # Wait for the state to be applied
                start_time = time.time()
                while time.time() - start_time < timeout:
                    current_state = {
                        "is_visible": window.is_visible(),
                        "is_minimized": window.is_minimized(),
                        "is_maximized": window.is_maximized()
                    }
                    
                    # Check if the desired state is achieved
                    if state == WindowState.MINIMIZED and current_state["is_minimized"]:
                        break
                    elif state == WindowState.MAXIMIZED and current_state["is_maximized"]:
                        break
                    elif state == WindowState.NORMAL and not current_state["is_minimized"] and not current_state["is_maximized"]:
                        break
                    elif state == WindowState.HIDDEN and not current_state["is_visible"]:
                        break
                        
                    time.sleep(0.1)
                
                # Get updated window info
                rect = window.rectangle()
                window_info = WindowInfo(
                    window_handle=window.handle,
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
                    ),
                    process_name=window.process_name(),
                    executable_path=window.executable_path()
                )
                
                return WindowActionResult(
                    success=True,
                    message=f"Window state changed to {state}",
                    timestamp=datetime.utcnow().isoformat(),
                    window_info=window_info
                )
                
            except Exception as e:
                # Try to restore original state
                try:
                    if original_state["is_minimized"]:
                        window.minimize()
                    elif original_state["is_maximized"]:
                        window.maximize()
                    else:
                        window.restore()
                except:
                    pass
                    
                raise e
                
        except Exception as e:
            logger.error(f"Error changing window state: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to change window state: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in set_window_state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


# Export the FastAPI app for ASGI servers
app = app.app
