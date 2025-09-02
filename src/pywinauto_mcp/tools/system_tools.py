"""
System interaction tools for PyWinAuto MCP.

This module provides system-level functionality like keyboard input, window management,
and process handling.
"""
import time
import psutil
import pyautogui
import pygetwindow as gw
from typing import Optional, Dict, Any, List
from pywinauto import Application, findwindows
from pywinauto.controls.hwndwrapper import HwndWrapper
from ..core.decorators import tool, stateful

@tool
def press_key(key_combination: str) -> dict:
    """
    Simulate key press(es).
    
    Args:
        key_combination: Key or key combination (e.g., 'ctrl+c', 'alt+tab')
        
    Returns:
        dict: Status of the key press
    """
    try:
        pyautogui.hotkey(*key_combination.split('+'))
        return {"status": "success", "key_pressed": key_combination}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def type_text(text: str, interval: float = 0.1) -> dict:
    """
    Type text at the current cursor position.
    
    Args:
        text: Text to type
        interval: Delay between keystrokes in seconds (default: 0.1)
        
    Returns:
        dict: Status of the typing operation
    """
    try:
        pyautogui.write(text, interval=interval)
        return {"status": "success", "characters_typed": len(text)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_active_window() -> dict:
    """
    Get information about the currently active window.
    
    Returns:
        dict: Window information including title, process ID, and dimensions
    """
    try:
        window = gw.getActiveWindow()
        if not window:
            return {"status": "error", "message": "No active window found"}
            
        return {
            "status": "success",
            "window": {
                "title": window.title,
                "process_id": window._hWnd,
                "is_active": window.isActive,
                "is_maximized": window.isMaximized,
                "is_minimized": window.isMinimized,
                "position": {
                    "left": window.left,
                    "top": window.top,
                    "right": window.right,
                    "bottom": window.bottom,
                    "width": window.width,
                    "height": window.height
                }
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def wait_for_window(title: str, timeout: float = 10.0, exact_match: bool = True) -> dict:
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
            
            if window and window.visible:
                window.activate()
                return {
                    "status": "success",
                    "window": {
                        "title": window.title,
                        "process_id": window._hWnd,
                        "is_active": True
                    }
                }
        except (IndexError, gw.PyGetWindowException):
            pass
            
        time.sleep(0.5)
    
    return {"status": "timeout", "message": f"Window with title '{title}' not found within {timeout} seconds"}

@tool
def bring_window_to_foreground(window_title: str, exact_match: bool = True) -> dict:
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
                return {"status": "error", "message": f"No window with title containing '{window_title}' found"}
            window = windows[0]
            
        if window:
            window.activate()
            return {
                "status": "success",
                "window": {
                    "title": window.title,
                    "process_id": window._hWnd
                }
            }
        else:
            return {"status": "error", "message": "Window not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_process_list() -> dict:
    """
    Get a list of running processes.
    
    Returns:
        dict: List of processes with details
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'create_time']):
            try:
                process_info = proc.as_dict(attrs=['pid', 'name', 'username', 'status', 'create_time'])
                processes.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        return {
            "status": "success",
            "process_count": len(processes),
            "processes": processes
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def wait(seconds: float) -> dict:
    """
    Wait for the specified number of seconds.
    
    Args:
        seconds: Number of seconds to wait
        
    Returns:
        dict: Status of the wait operation
    """
    try:
        time.sleep(seconds)
        return {"status": "success", "waited_seconds": seconds}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_system_clipboard() -> dict:
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
            "content_type": "text"
        }
    except ImportError:
        return {
            "status": "error",
            "message": "pyperclip module not installed. Install with: pip install pyperclip"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def set_system_clipboard(text: str) -> dict:
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
            "characters_copied": len(text)
        }
    except ImportError:
        return {
            "status": "error",
            "message": "pyperclip module not installed. Install with: pip install pyperclip"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Add all tools to __all__
__all__ = [
    'press_key',
    'type_text',
    'get_active_window',
    'wait_for_window',
    'bring_window_to_foreground',
    'get_process_list',
    'wait',
    'get_system_clipboard',
    'set_system_clipboard'
]
