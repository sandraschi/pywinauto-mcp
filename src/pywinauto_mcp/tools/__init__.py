"""
PyWinAuto MCP Tools Package

This package contains all the tools for the PyWinAuto MCP server.
"""

import logging
from typing import List, Any

# Set up logging
logger = logging.getLogger(__name__)

# Import the app instance from the main package
try:
    from pywinauto_mcp.main import app
    logger.info("Successfully imported FastMCP app instance")
except ImportError as e:
    logger.error(f"Failed to import FastMCP app: {e}")
    app = None

# List of all tool modules to import
TOOL_MODULES = [
    'basic_tools',    # Basic input and system tools
    'window',         # Window management tools
    'element',        # Element interaction tools
    'input',          # Input simulation tools
    'mouse',          # Mouse interaction tools
    'system_tools',   # System-level tools
    'visual',         # Visual tools (screenshots, OCR, etc.)
    'face_recognition', # Face recognition tools
    'desktop_state'   # Desktop state capture tools
]

# Import all tool modules - this will trigger their registration with FastMCP
if app is not None:
    for module_name in TOOL_MODULES:
        try:
            __import__(f'{__name__}.{module_name}', fromlist=['*'])
            logger.info(f"Successfully imported {module_name} tools")
        except ImportError as e:
            logger.error(f"Failed to import {module_name} tools: {e}")
        except Exception as e:
            logger.error(f"Error initializing {module_name} tools: {e}")

# Export the main components and all tool modules
__all__ = [
    'app',
    'basic_tools',
    'window',
    'element',
    'input',
    'visual_tools',
    'mouse',
    'system_tools'
]
