"""
PyWinAutoMCP Plugins Package.

This package contains all the plugins for PyWinAutoMCP.
"""
import sys
from pathlib import Path
from typing import Dict, Type, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pywinauto_mcp.core.plugin import PyWinAutoPlugin

# This will be populated by plugin modules
PLUGINS: Dict[str, Type[PyWinAutoPlugin]] = {}

def register_plugin(plugin_class: Type[PyWinAutoPlugin]) -> Type[PyWinAutoPlugin]:
    """Register a plugin class.
    
    This decorator is used by plugin modules to register themselves.
    
    Args:
        plugin_class: The plugin class to register
        
    Returns:
        The same plugin class, for chaining
    """
    PLUGINS[plugin_class.get_name()] = plugin_class
    return plugin_class

__all__ = ['PLUGINS', 'register_plugin']
