"""PyWinAuto MCP Tools Package - Portmanteau Edition.

This package contains 8 comprehensive portmanteau tools for Windows UI automation,
following FastMCP 2.13+ best practices for tool consolidation.

PORTMANTEAU TOOL ARCHITECTURE:
Instead of 60+ individual tools, this package consolidates related operations
into 8 comprehensive portmanteau tools:

1. automation_windows   - Window management (11 operations)
2. automation_elements  - UI element interaction (14 operations)
3. automation_mouse     - Mouse control (9 operations)
4. automation_keyboard  - Keyboard input (4 operations)
5. automation_visual    - Screenshots/OCR/image recognition (4 operations)
6. automation_face      - Face recognition (5 operations)
7. automation_system    - System utilities (7 operations)
8. get_desktop_state    - Comprehensive desktop UI discovery (standalone)

This design:
- Prevents tool explosion while maintaining full functionality
- Improves discoverability by grouping related operations
- Reduces cognitive load when working with automation tasks
- Follows FastMCP 2.13+ best practices
"""

import logging

# Set up logging
logger = logging.getLogger(__name__)

# Import the app instance from the app module
try:
    from pywinauto_mcp.app import app

    logger.info("Successfully imported FastMCP app instance")
except ImportError as e:
    logger.error(f"Failed to import FastMCP app: {e}")
    app = None

# List of portmanteau tool modules to import
PORTMANTEAU_MODULES = [
    "portmanteau_windows",  # Window management
    "portmanteau_elements",  # UI element interaction
    "portmanteau_mouse",  # Mouse control
    "portmanteau_keyboard",  # Keyboard input
    "portmanteau_visual",  # Visual/screenshot/OCR
    "portmanteau_face",  # Face recognition
    "portmanteau_system",  # System utilities
    "desktop_state",  # Desktop state capture (standalone)
]

# Import all portmanteau tool modules - this will trigger their registration with FastMCP
if app is not None:
    for module_name in PORTMANTEAU_MODULES:
        try:
            __import__(f"{__name__}.{module_name}", fromlist=["*"])
            logger.info(f"Successfully imported {module_name}")
        except ImportError as e:
            logger.error(f"Failed to import {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error initializing {module_name}: {e}")

# Export the main components
__all__ = [
    "app",
    # Portmanteau tools
    "portmanteau_windows",
    "portmanteau_elements",
    "portmanteau_mouse",
    "portmanteau_keyboard",
    "portmanteau_visual",
    "portmanteau_face",
    "portmanteau_system",
    "desktop_state",
]
