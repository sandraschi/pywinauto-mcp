"""PyWinAuto MCP Tools Package - Portmanteau Edition.

This package registers **seven** core portmanteau tools plus **get_desktop_state**.
**automation_face** is optional (off by default); see `docs/SAFETY.md` §5 and `PYWINAUTO_MCP_ENABLE_FACE`.

PORTMANTEAU TOOL ARCHITECTURE:
Instead of 60+ individual tools, this package consolidates related operations
into comprehensive portmanteau tools:

1. automation_windows   - Window management (11 operations)
2. automation_elements  - UI element interaction (14 operations)
3. automation_mouse     - Mouse control (9 operations)
4. automation_keyboard  - Keyboard input (4 operations)
5. automation_visual    - Screenshots/OCR/image recognition (4 operations)
6. automation_face      - Face recognition (5 operations) — **opt-in** (`PYWINAUTO_MCP_ENABLE_FACE=1` + face extra)
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

try:
    from pywinauto_mcp.safety import ENV_ENABLE_FACE, is_face_tool_enabled
except ImportError:
    ENV_ENABLE_FACE = "PYWINAUTO_MCP_ENABLE_FACE"

    def is_face_tool_enabled() -> bool:
        return False


# List of portmanteau tool modules to import (face is opt-in: see docs/SAFETY.md §5)
PORTMANTEAU_MODULES = [
    "portmanteau_windows",  # Window management
    "portmanteau_elements",  # UI element interaction
    "portmanteau_mouse",  # Mouse control
    "portmanteau_keyboard",  # Keyboard input
    "portmanteau_visual",  # Visual/screenshot/OCR
    "portmanteau_system",  # System utilities
    "desktop_state",  # Desktop state capture (standalone)
]
if is_face_tool_enabled():
    # Insert before system so ordering matches historical "face before system" lists
    idx = PORTMANTEAU_MODULES.index("portmanteau_system")
    PORTMANTEAU_MODULES.insert(idx, "portmanteau_face")
    logger.info("Face tool enabled (%s=1): will load portmanteau_face", ENV_ENABLE_FACE)
else:
    logger.info(
        "automation_face not registered (opt-in). Set %s=1 and install the face extra to enable.",
        ENV_ENABLE_FACE,
    )

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
