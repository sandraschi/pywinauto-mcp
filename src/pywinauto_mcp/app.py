"""
FastMCP application instance for PyWinAuto MCP.

This module creates the FastMCP app instance to avoid circular imports
between main.py and the tools modules.
"""

import logging
import sys

logger = logging.getLogger(__name__)

# Import FastMCP and create the app instance
try:
    from fastmcp import FastMCP
    logger.info("Successfully imported FastMCP")
    
    # Create the FastMCP app instance
    app = FastMCP(
        name="pywinauto-mcp",
        version="0.1.0"
    )
    
    logger.info("FastMCP app instance created successfully")
    
except ImportError as e:
    logger.critical(f"Failed to import FastMCP: {e}")
    logger.critical("Please install FastMCP 2.12+ using: pip install fastmcp>=2.12.0")
    app = None
except Exception as e:
    logger.critical(f"Error creating FastMCP app: {e}", exc_info=True)
    app = None

# Check OCR dependencies
try:
    import pytesseract
    from PIL import Image, ImageGrab
    OCR_AVAILABLE = True
    logger.info("OCR dependencies available")
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR dependencies not available")
