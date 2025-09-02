"""
PyWinAuto MCP Tools Package

This package contains all the tools for the PyWinAuto MCP server.
"""

import logging

# Set up logging
logger = logging.getLogger(__name__)

# Import the app instance from the main package
try:
    from pywinauto_mcp.main import app
    logger.info("Successfully imported FastMCP app instance")
except ImportError as e:
    logger.error(f"Failed to import FastMCP app: {e}")
    app = None

# Import tool modules - this will trigger their registration
# Only import if app is available
if app is not None:
    try:
        from . import basic_tools  # Basic input and system tools
        logger.info("Successfully imported basic_tools")
    except ImportError as e:
        logger.error(f"Failed to import basic_tools: {e}")

    # Import all tool modules to register them with FastMCP
    try:
        from . import window       # Window management tools
        logger.info("Successfully imported window tools")
    except ImportError as e:
        logger.error(f"Failed to import window tools: {e}")

    try:
        from . import element      # Element interaction tools
        logger.info("Successfully imported element tools")
    except ImportError as e:
        logger.error(f"Failed to import element tools: {e}")

    try:
        from . import input  # Input simulation tools
        logger.info("Successfully imported input tools")
    except ImportError as e:
        logger.error(f"Failed to import input tools: {e}")

    try:
        from . import visual  # Visual tools
        logger.info("Successfully imported visual tools")
    except ImportError as e:
        logger.error(f"Failed to import visual tools: {e}")

    try:
        from . import visual_tools  # Additional visual tools
        logger.info("Successfully imported visual_tools")
    except ImportError as e:
        logger.error(f"Failed to import visual_tools: {e}")

    try:
        from . import mouse  # Mouse control tools
        logger.info("Successfully imported mouse tools")
    except ImportError as e:
        logger.error(f"Failed to import mouse tools: {e}")

    try:
        from . import system_tools  # System utilities
        logger.info("Successfully imported system tools")
    except ImportError as e:
        logger.error(f"Failed to import system tools: {e}")
        
    try:
        from . import element_tools  # Element tools
        logger.info("Successfully imported element_tools")
    except ImportError as e:
        logger.error(f"Failed to import element_tools: {e}")
        
    try:
        from . import utils  # Utility functions
        logger.info("Successfully imported utils")
    except ImportError as e:
        logger.error(f"Failed to import utils: {e}")

# Export the main components and all tool modules
__all__ = [
    'app',
    'basic_tools',
    'window',
    'element',
    'element_tools',
    'input',
    'visual',
    'visual_tools',
    'mouse',
    'system_tools',
    'utils'
]
