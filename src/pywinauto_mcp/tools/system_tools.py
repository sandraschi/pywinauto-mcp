"""
System interaction tools for PyWinAuto MCP.

This module provides system-level functionality like keyboard input, window management,
and process handling.
"""
import time
import psutil
import pyautogui
import logging
import pygetwindow as gw
from typing import Optional, Dict, Any, List, TypedDict, Union
from pywinauto import Application, findwindows

# Define a type for element info dict
class ElementInfo(TypedDict, total=False):
    rect: Any  # Can be a rectangle object with left, top, width, height
    x: int
    y: int
    width: int
    height: int
    class_name: str
    text: str
    control_id: int
    process_id: int
    is_visible: bool
    is_enabled: bool
    handle: int
    runtime_id: Any
    automation_id: str
    name: str
    control_type: str

# Import the FastMCP app instance from the main package
try:
    from pywinauto_mcp.main import app
    logger = logging.getLogger(__name__)
    logger.info("Successfully imported FastMCP app instance in system tools")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import FastMCP app in system tools: {e}")
    app = None

# Only proceed with tool registration if app is available
if app is not None:
    logger.info("Registering system tools with FastMCP")

    # press_key and type_text are defined in input.py

    @app.tool(
        name="wait_for_window",
        description="Wait for a window with the specified title to become active."
    )
    def wait_for_window(
        title: str, 
        timeout: float = 10.0, 
        exact_match: bool = True
    ) -> Dict[str, Any]:
        """
        Wait for a window with the specified title to become active.
        
        Args:
            title: Window title or partial title to wait for
            timeout: Maximum time to wait in seconds (default: 10)
            exact_match: Whether to match the window title exactly (default: True)
            
        Returns:
            dict: Status and window information if found
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if exact_match:
                    window = gw.getWindowsWithTitle(title)[0]
                else:
                    windows = gw.getWindowsWithTitle(title)
                    if windows:
                        window = windows[0]
                    else:
                        window = None
                
                if window:
                    return {
                        "status": "success",
                        "window_title": window.title,
                        "window_handle": window._hWnd,
                        "position": (window.left, window.top),
                        "size": (window.width, window.height),
                        "wait_time": time.time() - start_time
                    }
            except (IndexError, Exception):
                pass
                
            time.sleep(0.5)
        
        return {
            "status": "timeout",
            "error": f"Window with title '{title}' not found within {timeout} seconds"
        }

    @app.tool(
        name="bring_window_to_foreground",
        description="Bring a window to the foreground by its title."
    )
    def bring_window_to_foreground(
        window_title: str, 
        exact_match: bool = True
    ) -> Dict[str, Any]:
        """
        Bring a window to the foreground by its title.
        
        Args:
            window_title: Title or partial title of the window
            exact_match: Whether to match the window title exactly (default: True)
            
        Returns:
            dict: Status of the operation
        """
        try:
            if exact_match:
                window = gw.getWindowsWithTitle(window_title)[0]
            else:
                windows = gw.getWindowsWithTitle(window_title)
                if not windows:
                    return {
                        "status": "error",
                        "error": f"No window found with title containing '{window_title}'"
                    }
                window = windows[0]
            
            window.activate()
            
            return {
                "status": "success",
                "window_title": window.title,
                "window_handle": window._hWnd
            }
        except IndexError:
            return {
                "status": "error",
                "error": f"No window found with title '{window_title}'"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }

    @app.tool(
        name="get_process_list",
        description="Get a list of running processes."
    )
    def get_process_list() -> Dict[str, Any]:
        """
        Get a list of running processes.
        
        Returns:
            dict: List of processes with details
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
                try:
                    process_info = proc.info
                    processes.append({
                        'pid': process_info['pid'],
                        'name': process_info['name'],
                        'username': process_info['username'],
                        'status': process_info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return {
                "status": "success",
                "process_count": len(processes),
                "processes": processes,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }

    @app.tool(
        name="wait",
        description="Wait for the specified number of seconds."
    )
    def wait(seconds: float) -> Dict[str, Any]:
        """
        Wait for the specified number of seconds.
        
        Args:
            seconds: Number of seconds to wait
            
        Returns:
            dict: Status of the wait operation
        """
        try:
            time.sleep(seconds)
            return {
                "status": "success",
                "waited_seconds": seconds,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }

    @app.tool(
        name="get_system_clipboard",
        description="Get the current content of the system clipboard."
    )
    def get_system_clipboard() -> Dict[str, Any]:
        """
        Get the current content of the system clipboard.
        
        Returns:
            dict: Clipboard content and status
        """
        try:
            import pyperclip
            content = pyperclip.paste()
            return {
                "status": "success",
                "content": content,
                "content_length": len(content),
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }

    @app.tool(
        name="set_system_clipboard",
        description="Set the content of the system clipboard."
    )
    def set_system_clipboard(text: str) -> Dict[str, Any]:
        """
        Set the content of the system clipboard.
        
        Args:
            text: Text to set in the clipboard
            
        Returns:
            dict: Status of the operation
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            return {
                "status": "success",
                "characters_copied": len(text),
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }

# Add all tools to __all__
__all__ = [
    'wait_for_window',
    'bring_window_to_foreground',
    'get_process_list',
    'wait',
    'get_system_clipboard',
    'set_system_clipboard'
]
