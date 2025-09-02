"""
Basic input and system interaction tools for PyWinAuto MCP.

This module contains fundamental tools for mouse and keyboard interaction.
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any, List

import pyautogui
from pywinauto import Desktop

# Import the FastMCP app instance from the app module
try:
    from pywinauto_mcp.app import app
    logger = logging.getLogger(__name__)
    logger.info("Successfully imported FastMCP app instance in basic_tools")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import FastMCP app in basic_tools: {e}")
    app = None

# Only proceed with tool registration if app is available
if app is not None:
    logger.info("Registering basic tools with FastMCP")

    @app.tool(
        name="health_check",
        description="Check if the PyWinAuto MCP server is running and operational."
    )
    def health_check() -> Dict[str, str]:
        """Check if the PyWinAuto MCP server is running and operational."""
        return {
            "status": "healthy",
            "server": "PyWinAuto MCP",
            "version": "0.1.0",
            "timestamp": datetime.utcnow().isoformat(),
        }

    @app.tool(
        name="get_cursor_position",
        description="Get current mouse cursor position."
    )
    def get_cursor_position() -> Dict[str, Any]:
        """Get current mouse cursor position."""
        try:
            x, y = pyautogui.position()
            return {
                "status": "success",
                "x": x,
                "y": y,
                "position": (x, y),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="click_at_position",
        description="Click at specific screen coordinates."
    )
    def click_at_position(x: int, y: int, button: str = "left") -> Dict[str, Any]:
        """
        Click at specific screen coordinates.
        
        Args:
            x: X coordinate to click
            y: Y coordinate to click  
            button: Mouse button to click ("left", "right", "middle")
        """
        try:
            pyautogui.click(x, y, button=button)
            return {
                "status": "success",
                "action": "click",
                "position": (x, y),
                "button": button,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="move_mouse",
        description="Move mouse to specific coordinates."
    )
    def move_mouse(x: int, y: int) -> Dict[str, Any]:
        """
        Move mouse to specific coordinates.
        
        Args:
            x: X coordinate to move to
            y: Y coordinate to move to
        """
        try:
            pyautogui.moveTo(x, y)
            return {
                "status": "success",
                "action": "move",
                "position": (x, y),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="scroll_mouse",
        description="Scroll mouse wheel at current or specified position."
    )
    def scroll_mouse(amount: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """
        Scroll mouse wheel at current or specified position.
        
        Args:
            amount: Scroll amount (positive = up, negative = down)
            x: Optional X coordinate to scroll at
            y: Optional Y coordinate to scroll at
        """
        try:
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
            
            pyautogui.scroll(amount)
            
            return {
                "status": "success",
                "action": "scroll",
                "amount": amount,
                "position": (x, y) if x is not None and y is not None else None,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="list_windows",
        description="List all visible windows on the desktop."
    )
    def list_windows() -> Dict[str, Any]:
        """List all visible windows on the desktop."""
        try:
            desktop = Desktop(backend="uia")
            windows = []
            
            for window in desktop.windows():
                try:
                    window_info = {
                        "title": window.window_text(),
                        "class_name": window.class_name(),
                        "handle": window.handle,
                        "is_visible": window.is_visible(),
                        "is_enabled": window.is_enabled(),
                    }
                    
                    try:
                        rect = window.rectangle()
                        window_info["rect"] = {
                            "left": rect.left,
                            "top": rect.top,
                            "right": rect.right,
                            "bottom": rect.bottom,
                            "width": rect.width(),
                            "height": rect.height()
                        }
                    except Exception:
                        pass
                        
                    windows.append(window_info)
                except Exception as e:
                    logger.warning(f"Error getting window info: {e}")
            
            return {
                "status": "success",
                "windows_found": len(windows),
                "windows": windows
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="find_window_by_title",
        description="Find window by title text."
    )
    def find_window_by_title(title: str, partial: bool = True) -> Dict[str, Any]:
        """
        Find window by title text.
        
        Args:
            title: Window title to search for
            partial: Whether to do partial match (default: True)
        """
        try:
            desktop = Desktop(backend="uia")
            matching_windows = []
            
            for window in desktop.windows():
                try:
                    window_title = window.window_text()
                    
                    if (partial and title.lower() in window_title.lower()) or \
                       (not partial and title.lower() == window_title.lower()):
                        
                        window_info = {
                            "title": window_title,
                            "class_name": window.class_name(),
                            "handle": window.handle,
                            "is_visible": window.is_visible(),
                            "is_enabled": window.is_enabled(),
                        }
                        
                        try:
                            rect = window.rectangle()
                            window_info["rect"] = {
                                "left": rect.left,
                                "top": rect.top,
                                "right": rect.right,
                                "bottom": rect.bottom,
                                "width": rect.width(),
                                "height": rect.height()
                            }
                        except Exception:
                            pass
                            
                        matching_windows.append(window_info)
                except Exception as e:
                    logger.warning(f"Error checking window: {e}")
            
            return {
                "status": "success",
                "windows_found": len(matching_windows),
                "windows": matching_windows,
                "search_term": title,
                "partial_match": partial
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="type_text",
        description="Type text at current cursor position."
    )
    def type_text(text: str) -> Dict[str, Any]:
        """
        Type text at current cursor position.
        
        Args:
            text: Text to type
        """
        try:
            pyautogui.write(text)
            return {
                "status": "success",
                "action": "type_text",
                "text": text,
                "length": len(text),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="send_keys",
        description="Send special key combinations."
    )
    def send_keys(keys: str) -> Dict[str, Any]:
        """
        Send special key combinations.
        
        Args:
            keys: Key combination (e.g., "ctrl+c", "alt+tab", "enter")
        """
        try:
            pyautogui.hotkey(*keys.split("+"))
            return {
                "status": "success",
                "action": "send_keys",
                "keys_sent": keys,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

else:
    logger.error("FastMCP app not available - tools will not be registered")

# Add all tools to __all__
__all__ = [
    'health_check',
    'get_cursor_position',
    'click_at_position',
    'move_mouse',
    'scroll_mouse',
    'list_windows',
    'find_window_by_title',
    'type_text',
    'send_keys'
]
