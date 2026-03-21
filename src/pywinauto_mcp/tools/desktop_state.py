"""Desktop State Capture Tools for PyWinAuto MCP tracking SOTA 2026 standards.

Provides comprehensive desktop state capture with UI element discovery,
visual annotations, and OCR capabilities.
"""

import logging

# Import the FastMCP app instance
try:
    from pywinauto_mcp.app import app

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
        element_timeout: float = 0.5,
    ) -> dict:
        """Capture comprehensive desktop state with UI element discovery.

        SOTA 2026 CAPTURE PROTOCOL:
        This tool provides a pixel-perfect, element-aware snapshot of the current
        UI state. It utilizes recursive tree traversal with depth control and
        optional multimodal (Vision + OCR) enhancement features.

        Args:
            use_vision (bool): Include annotated screenshot with element boundaries.
            use_ocr (bool): Use OCR to extract text from visual components.
            max_depth (int): Maximum UI tree traversal depth (SOTA default: 10).
            element_timeout (float): Per-element processing threshold.

        Returns:
            dict: Comprehensive desktop state dictionary.

        Example:
            get_desktop_state(use_vision=True, use_ocr=True)
            get_desktop_state(max_depth=15, element_timeout=0.2)

        """
        try:
            logger.info(f"Starting SOTA desktop state capture (vision={use_vision}, ocr={use_ocr})")
            import time

            timestamp = time.time()
            visual_metadata = {
                "timestamp": timestamp,
                "engine": "pywinauto-mcp-sota-2026",
                "identity": "desktop-state-capture",
            }

            capturer = DesktopStateCapture(max_depth=max_depth, element_timeout=element_timeout)
            result = capturer.capture(use_vision=use_vision, use_ocr=use_ocr)

            # Inject SOTA metadata
            result["visual_metadata"] = visual_metadata
            result["status"] = "success"

            logger.info(
                f"Desktop state capture completed: {result['element_count']} elements found"
            )
            return result

        except Exception as e:
            logger.error(f"Desktop state capture failed: {e}")
            # Return a basic error response
            return {
                "error": str(e),
                "text": f"Failed to capture desktop state: {e}",
                "interactive_elements": [],
                "informative_elements": [],
                "element_count": 0,
            }

else:
    logger = logging.getLogger(__name__)
    logger.warning("Desktop state tools not available - missing dependencies or app instance")
