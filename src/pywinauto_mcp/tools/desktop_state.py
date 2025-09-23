"""
Desktop State Capture Tools for PyWinAuto MCP.

Provides comprehensive desktop state capture with UI element discovery,
visual annotations, and OCR capabilities.
"""

import logging
from typing import Optional

# Import the FastMCP app instance
try:
    from pywinauto_mcp.main import app
    logger = logging.getLogger(__name__)
    logger.info("Successfully imported FastMCP app instance in desktop state tools")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import FastMCP app in desktop state tools: {e}")
    app = None

# Import desktop state capture functionality
try:
    from pywinauto_mcp.desktop_state import DesktopStateCapture
    logger.info("Successfully imported desktop state capture functionality")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import desktop state capture: {e}")
    DesktopStateCapture = None

# Only proceed with tool registration if app and functionality are available
if app is not None and DesktopStateCapture is not None:
    logger.info("Registering desktop state tools with FastMCP")

    @app.tool()
    def get_desktop_state(
        use_vision: bool = False,
        use_ocr: bool = False,
        max_depth: int = 10,
        element_timeout: float = 0.5
    ) -> dict:
        """
        Capture comprehensive desktop state with UI element discovery

        This tool provides a complete snapshot of the current desktop state,
        including all visible UI elements, their properties, and optional visual
        annotations and OCR text extraction.

        Args:
            use_vision: Include annotated screenshot with element boundaries highlighted
            use_ocr: Use OCR to extract text from visual elements that don't have readable text
            max_depth: Maximum UI tree traversal depth (higher = more elements, slower)
            element_timeout: Timeout in seconds for processing each UI element (helps with slow IDEs)

        Returns:
            Desktop state with:
            - text: Human-readable report of all elements
            - interactive_elements: List of clickable/actionable elements
            - informative_elements: List of text/display elements
            - element_count: Total number of discovered elements
            - screenshot_base64: Base64-encoded annotated screenshot (if use_vision=True)

        Example:
            Basic capture: get_desktop_state()
            With vision: get_desktop_state(use_vision=True)
            With OCR: get_desktop_state(use_ocr=True)
            Fast IDE analysis: get_desktop_state(max_depth=15, element_timeout=0.2)
            Full analysis: get_desktop_state(use_vision=True, use_ocr=True, max_depth=15, element_timeout=0.5)
        """
        try:
            logger.info(f"Starting desktop state capture (vision={use_vision}, ocr={use_ocr}, depth={max_depth}, timeout={element_timeout})")

            capturer = DesktopStateCapture(max_depth=max_depth, element_timeout=element_timeout)
            result = capturer.capture(use_vision=use_vision, use_ocr=use_ocr)

            logger.info(f"Desktop state capture completed: {result['element_count']} elements found")
            return result

        except Exception as e:
            logger.error(f"Desktop state capture failed: {e}")
            # Return a basic error response
            return {
                "error": str(e),
                "text": f"Failed to capture desktop state: {e}",
                "interactive_elements": [],
                "informative_elements": [],
                "element_count": 0
            }

else:
    logger = logging.getLogger(__name__)
    logger.warning("Desktop state tools not available - missing dependencies or app instance")

    @app.tool()
    def get_desktop_state(
        use_vision: bool = False,
        use_ocr: bool = False,
        max_depth: int = 10,
        element_timeout: float = 0.5
    ) -> dict:
        """
        Desktop state capture is not available

        This tool requires additional dependencies (PIL, pytesseract) that are not installed.
        """
        return {
            "error": "Desktop state capture not available - missing dependencies",
            "text": "Install PIL and pytesseract to enable desktop state capture functionality",
            "interactive_elements": [],
            "informative_elements": [],
            "element_count": 0
        }
