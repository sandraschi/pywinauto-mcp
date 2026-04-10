"""Pydantic models for PyWinAuto MCP tool parameters and results.

Ensures strict schema visibility and validation for portmanteau tools.
"""

from typing import Any, Optional, Literal, List
from pydantic import BaseModel, Field


class WindowOperationRequest(BaseModel):
    """Request model for window management operations."""

    operation: Literal[
        "list",
        "find",
        "manage",
        "focus",
        "get_active",
        "maximize",
        "minimize",
        "restore",
        "close",
        "activate",
        "position",
        "rect",
        "title",
        "state",
    ] = Field(..., description="The window operation to perform.")

    handle: Optional[int] = Field(
        None, description="Window handle (HWND). Required for all operations except 'list', 'find', and 'get_active'."
    )
    
    title: Optional[str] = Field(
        None, description="Window title or partial title. Used primarily with the 'find' operation."
    )
    
    process_id: Optional[int] = Field(
        None, description="Process ID to match against during 'find'."
    )
    
    class_name: Optional[str] = Field(
        None, description="Window class name to match against during 'find'."
    )
    
    partial: bool = Field(
        True, description="Whether to perform a partial title match during 'find'."
    )
    
    action: Optional[Literal["maximize", "minimize", "restore", "close", "activate", "focus"]] = Field(
        None, description="Specific window action to perform when operation set to 'manage'."
    )
    
    x: Optional[int] = Field(None, description="Target X coordinate for 'position' operation.")
    y: Optional[int] = Field(None, description="Target Y coordinate for 'position' operation.")
    width: Optional[int] = Field(None, description="Target width for 'position' operation.")
    height: Optional[int] = Field(None, description="Target height for 'position' operation.")


class ElementOperationRequest(BaseModel):
    """Request model for element-level automation operations."""

    window_handle: int = Field(..., description="Handle of the parent window containing the element.")
    
    operation: Literal[
        "list",
        "info",
        "click",
        "double_click",
        "right_click",
        "hover",
        "set_text",
        "get_text",
        "wait",
        "exists",
        "rect",
        "visible",
        "enabled",
        "verify_text"
    ] = Field(..., description="The element operation to perform.")
    
    # Selection criteria (Legacy individual fields supported for backward compat and explicit schema)
    control_id: Optional[str] = Field(None, description="Element Control ID.")
    auto_id: Optional[str] = Field(None, description="Element Automation ID.")
    title: Optional[str] = Field(None, description="Element Title/Name.")
    control_type: Optional[str] = Field(None, description="Element Control Type (e.g., 'Button').")
    class_name: Optional[str] = Field(None, description="Element Class Name.")
    
    # Coordinate fallback
    x: Optional[int] = Field(None, description="Relative or absolute X coordinate.")
    y: Optional[int] = Field(None, description="Relative or absolute Y coordinate.")
    absolute: bool = Field(False, description="Whether coordinates are screen-absolute.")
    
    # Action parameters
    text: Optional[str] = Field(None, description="Text to enter for 'set_text'.")
    expected_text: Optional[str] = Field(None, description="Text to verify for 'verify_text'.")
    exact_match: bool = Field(False, description="Use exact match for 'verify_text'.")
    button: Literal["left", "right", "middle"] = Field("left", description="Mouse button for clicks.")
    duration: float = Field(0.0, description="Duration for 'hover' or movement delay.")
    
    # Discovery parameters
    max_depth: int = Field(2, description="Max depth for 'list' recursion.")
    timeout: float = Field(10.0, description="Max wait time in seconds.")


class MouseOperationRequest(BaseModel):
    """Request model for mouse input operations."""

    operation: Literal[
        "move", "move_relative", "click", "double_click", "right_click", 
        "scroll", "drag", "hover", "position", "telemetry"
    ] = Field(..., description="The mouse operation to perform.")
    
    x: Optional[int] = Field(None, description="X coordinate or relative X offset.")
    y: Optional[int] = Field(None, description="Y coordinate or relative Y offset.")
    
    target_x: Optional[int] = Field(None, description="Target X for 'drag'.")
    target_y: Optional[int] = Field(None, description="Target Y for 'drag'.")
    
    # Legacy aliases support
    x2: Optional[int] = Field(None, description="Alias for target_x.")
    y2: Optional[int] = Field(None, description="Alias for target_y.")
    
    button: Literal["left", "right", "middle"] = Field("left", description="Mouse button to use.")
    amount: int = Field(1, description="Amount to scroll or number of clicks.")
    clicks: int = Field(1, description="Alias for amount.")
    
    horizontal: bool = Field(False, description="Whether to scroll horizontally.")
    duration: float = Field(0.0, description="Movement duration in seconds.")
    hover_duration: float = Field(0.5, description="Duration to pause for 'hover'.")
    
    telemetry_duration: int = Field(10, description="Duration in seconds to show the HUD.")
    capture_keys: bool = Field(False, description="Whether to capture key presses in HUD.")


class KeyloggerOperationRequest(BaseModel):
    """Request model for global keyboard capture (pynput low-level hook)."""

    operation: Literal["start", "stop", "status", "read", "clear"] = Field(
        ..., description="Keylogger operation: start/stop the listener, status, read buffered events, or clear buffer."
    )
    max_buffer: int = Field(
        5000,
        description="Ring buffer capacity for 'start' (oldest dropped when full).",
        ge=1,
        le=100_000,
    )
    include_release: bool = Field(
        False,
        description="For 'start': also record key release events (roughly doubles volume).",
    )
    limit: int = Field(100, description="Max events to return for 'read' (most recent batch).", ge=1, le=10_000)
    flush: bool = Field(
        False,
        description="For 'read': remove returned events from the buffer (keeps older events if any).",
    )


class KeyboardOperationRequest(BaseModel):
    """Request model for keyboard input operations."""

    operation: Literal["type", "hotkey", "press", "release", "hold"] = Field(
        ..., description="The keyboard operation to perform."
    )
    
    text: Optional[str] = Field(None, description="Text to type for 'type'.")
    key: Optional[str] = Field(None, description="Single key for 'press'.")
    keys: Optional[List[str]] = Field(None, description="Key list for 'hotkey' or 'hold'.")
    
    presses: int = Field(1, description="Number of times to press the key.")
    interval: float = Field(0.0, description="Pause between characters for 'type'.")
    pause: float = Field(0.0, description="Pause between repeated presses.")


class VisualOperationRequest(BaseModel):
    """Request model for visual/OCR operations."""

    operation: Literal["screenshot", "extract_text", "find_image", "highlight"] = Field(
        ..., description="The visual operation to perform."
    )
    
    window_handle: Optional[int] = Field(None, description="HWND of target window.")
    
    region_left: Optional[int] = Field(None, description="X1 coordinate of region.")
    region_top: Optional[int] = Field(None, description="Y1 coordinate of region.")
    region_right: Optional[int] = Field(None, description="X2 coordinate of region.")
    region_bottom: Optional[int] = Field(None, description="Y2 coordinate of region.")
    
    image_path: Optional[str] = Field(None, description="Source image path for OCR.")
    template_path: Optional[str] = Field(None, description="Template image path for matching.")
    output_path: Optional[str] = Field(None, description="Path to save output image.")
    
    format: str = Field("png", description="Image format (png, jpg, etc.).")
    return_base64: bool = Field(False, description="Return base64 string instead of path.")
    
    language: str = Field("eng", description="Tesseract language code.")
    ocr_config: str = Field("--psm 6", description="Tesseract config flags.")
    threshold: float = Field(0.8, description="Matching confidence threshold (0-1).", ge=0, le=1)
    
    control_id: Optional[str] = Field(None, description="Element ID for highlighting.")
    color: str = Field("red", description="Highlight color name.")
    thickness: int = Field(2, description="Highlight border thickness.", ge=1)
    highlight_duration: float = Field(3.0, description="Duration to show highlight in seconds.", ge=0)


class FaceOperationRequest(BaseModel):
    """Request model for face recognition operations."""

    operation: Literal["add", "recognize", "list", "delete", "capture"] = Field(
        ..., description="The face recognition operation."
    )
    
    name: Optional[str] = Field(None, description="Person's name for registration/deletion.")
    image_path: Optional[str] = Field(None, description="Image path for recognition/registration.")
    camera_index: int = Field(0, description="Webcam index (0 is primary).", ge=0)
    save_capture_path: Optional[str] = Field(None, description="Path to save captured frame.")
    tolerance: float = Field(0.6, description="Matching tolerance (lower is stricter).", ge=0, le=1)


class SystemOperationRequest(BaseModel):
    """Request model for system-level operations."""

    operation: Literal[
        "status", "help", "wait", "info", "wait_for_window", 
        "clipboard_get", "clipboard_set", "processes", "start_app"
    ] = Field(..., description="The system operation to perform.")
    
    seconds: Optional[float] = Field(None, description="Seconds to wait.", ge=0)
    title: Optional[str] = Field(None, description="Window title for wait_for_window.")
    timeout: float = Field(10.0, description="Operation timeout in seconds.", ge=0)
    exact_match: bool = Field(False, description="Exact title match if True.")
    text: Optional[str] = Field(None, description="Clipboard text content.")
    app_path: Optional[str] = Field(None, description="App executable path.")
    work_dir: Optional[str] = Field(None, description="App working directory.")
    filter: Optional[str] = Field(None, description="Process name filter.")


class DesktopStateRequest(BaseModel):
    """Request model for get_desktop_state discovery."""

    use_vision: bool = Field(False, description="Include annotated screenshots.")
    use_ocr: bool = Field(False, description="Use OCR for text extraction.")
    max_depth: int = Field(10, description="Max UI tree depth.", ge=1)
    element_timeout: float = Field(0.5, description="Timeout per element capture.", ge=0)


class MissionOperationRequest(BaseModel):
    """Request model for high-level agentic missions."""

    operation: Literal["plan", "status", "cancel", "record", "replay"] = Field(
        "plan", description="The mission operation to perform."
    )
    goal: str = Field(..., description="The high-level objective to achieve.")
    strategy: Literal["element", "visual"] = Field(
        "element", description="Whether to prefer UIA elements or visual cues."
    )
    mission_id: Optional[str] = Field(None, description="Unique ID for session persistence.")
    steps: Optional[List[dict]] = Field(None, description="Pre-defined steps for 'replay'.")


class ToolResult(BaseModel):
    """Standardized response model for all MCP tools."""

    status: Literal["success", "error", "clarification_needed", "blocked"] = Field(
        ..., description="The outcome of the operation."
    )
    
    message: str = Field(..., description="A human-readable summary of the result.")
    
    data: Optional[Any] = Field(None, description="Operation-specific payload (e.g., window metadata).")
    
    recovery_tip: Optional[str] = Field(
        None, description="Actionable guidance for agents if the operation failed or was ambiguous."
    )
