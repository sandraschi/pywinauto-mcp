"""
Basic input and system interaction tools for PyWinAuto MCP.

This module contains fundamental tools for mouse and keyboard interaction.
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any, List

import pyautogui
from pywinauto import Desktop

# Import the FastMCP app instance from the main package
try:
    from pywinauto_mcp.main import app
    logger = logging.getLogger(__name__)
    logger.info("Successfully imported FastMCP app instance in basic_tools")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import FastMCP app in basic_tools: {e}")
    app = None

# Only proceed with tool registration if app is available
if app is None:
    logger.warning("Skipping tool registration - FastMCP app not available")
else:
    # All tool registrations go inside this block
    logger.info("Registering basic tools with FastMCP")

    @app.tool(
        name="health_check",
        description="Check if the PyWinAuto MCP server is running and operational.",
        category="system"
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
        description="Get current mouse cursor position.",
        category="input"
    )
    def get_cursor_position() -> Dict[str, Any]:
        """Get current mouse cursor position."""
        try:
            x, y = pyautogui.position()
            return {
                "status": "success", 
                "position": {"x": x, "y": y},
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="click_at_position",
        description="Click at specific screen coordinates.",
        category="input"
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
            if button == "left":
                pyautogui.click(x, y)
            elif button == "right":
                pyautogui.rightClick(x, y)
            elif button == "middle":
                pyautogui.middleClick(x, y)
            else:
                return {"status": "error", "error": f"Invalid button: {button}"}
                
            return {
                "status": "success",
                "action": f"{button}_click",
                "position": {"x": x, "y": y},
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="move_mouse",
        description="Move mouse to specific coordinates.",
        category="input"
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
                "action": "move_mouse",
                "position": {"x": x, "y": y},
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="scroll_mouse",
        description="Scroll mouse wheel at current or specified position.",
        category="input"
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
            
            pos = pyautogui.position()
            return {
                "status": "success",
                "action": "scroll",
                "scroll_amount": amount,
                "position": {"x": pos[0], "y": pos[1]},
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="list_windows",
        description="List all visible windows on the desktop.",
        category="system"
    )
    def list_windows() -> Dict[str, Any]:
        """List all visible windows on the desktop."""
        try:
            windows = []
            for window in Desktop(backend="uia").windows():
                try:
                    if window.is_visible():
                        rect = window.rectangle()
                        windows.append({
                            "title": window.window_text(),
                            "class_name": window.class_name(),
                            "handle": window.handle,
                            "process_id": window.process_id(),
                            "rectangle": {
                                "left": rect.left,
                                "top": rect.top,
                                "right": rect.right,
                                "bottom": rect.bottom,
                                "width": rect.width(),
                                "height": rect.height()
                            }
                        })
                except Exception as e:
                    logger.debug(f"Error processing window: {e}")
                    continue
                
            return {
                "status": "success",
                "windows_found": len(windows),
                "windows": windows,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="find_window_by_title",
        description="Find window by title text.",
        category="system"
    )
    def find_window_by_title(title: str, partial: bool = True) -> Dict[str, Any]:
        """
        Find window by title text.
        
        Args:
            title: Window title to search for
            partial: Whether to do partial match (default: True)
        """
        try:
            windows = []
            desktop = Desktop(backend="uia")
            
            for window in desktop.windows():
                try:
                    if not window.is_visible():
                        continue
                        
                    window_title = window.window_text()
                    match = False
                    
                    if partial:
                        match = title.lower() in window_title.lower()
                    else:
                        match = title == window_title
                        
                    if match:
                        rect = window.rectangle()
                        windows.append({
                            "title": window_title,
                            "class_name": window.class_name(),
                            "handle": window.handle,
                            "process_id": window.process_id(),
                            "rectangle": {
                                "left": rect.left,
                                "top": rect.top,
                                "right": rect.right,
                                "bottom": rect.bottom,
                                "width": rect.width(),
                                "height": rect.height()
                            }
                        })
                except Exception as e:
                    logger.debug(f"Error processing window: {e}")
                    continue
                
            return {
                "status": "success",
                "windows_found": len(windows),
                "windows": windows,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="type_text",
        description="Type text at current cursor position.",
        category="input"
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
                "text_typed": text,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.tool(
        name="send_keys",
        description="Send special key combinations.",
        category="input"
    )
    def send_keys(keys: str) -> Dict[str, Any]:
        """
        Send special key combinations.
        
        Args:
            keys: Key combination (e.g., "ctrl+c", "alt+tab", "enter")
        """
        try:
            pyautogui.hotkey(*keys.split('+'))
            return {
                "status": "success",
                "action": "send_keys",
                "keys_sent": keys,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
