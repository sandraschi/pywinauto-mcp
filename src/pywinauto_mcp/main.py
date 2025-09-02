"""
PyWinAuto MCP - FastMCP 2.12+ compliant Windows UI automation server.
This is a managed MCP server that is started and managed by the MCP client.
"""

import logging
import logging.config
import sys
import os
from typing import Optional, Dict, Any

# Configure logging before other imports to ensure proper logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('pywinauto-mcp.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Import the FastMCP app instance
try:
    from pywinauto_mcp.app import app, OCR_AVAILABLE
    logger.info("Successfully imported FastMCP app instance")
    
    if app is None:
        logger.critical("FastMCP app instance is None - cannot continue")
        sys.exit(1)
    
    # Import tools after app is available to ensure proper registration
    try:
        from pywinauto_mcp.tools import basic_tools  # noqa: F401
        logger.info("Successfully imported tools")
    except Exception as e:
        logger.error(f"Error importing tools: {e}")
    
    # MCP lifecycle hooks (if supported by this version of FastMCP)
    if hasattr(app, 'on_startup'):
        @app.on_startup
        def on_startup() -> None:
            """Called when the MCP server starts."""
            logger.info("PyWinAuto MCP server starting...")
            logger.info(f"OCR available: {OCR_AVAILABLE}")
    
    if hasattr(app, 'on_shutdown'):
        @app.on_shutdown
        def on_shutdown() -> None:
            """Called when the MCP server shuts down."""
            logger.info("PyWinAuto MCP server shutting down...")
    
    logger.info("MCP server initialized successfully")
    
except ImportError as e:
    logger.critical(f"Failed to import FastMCP app: {e}")
    sys.exit(1)
except Exception as e:
    logger.critical(f"Error initializing MCP server: {e}", exc_info=True)
    sys.exit(1)

async def get_registered_tools():
    """Helper function to get registered tools as a list."""
    try:
        # Get tools from the app instance
        if hasattr(app, 'list_tools'):
            tools_result = app.list_tools()
            if hasattr(tools_result, 'tools') and tools_result.tools:
                return [tool.name for tool in tools_result.tools]
        elif hasattr(app, '_tools'):
            return list(app._tools.keys())
        else:
            logger.warning("Could not determine how to list tools from FastMCP app")
            return []
    except Exception as e:
        logger.error(f"Error getting registered tools: {e}")
        return []

def main() -> None:
    """Run the PyWinAuto MCP server."""
    try:
        logger.info("Starting PyWinAuto MCP server...")
        logger.info(f"FastMCP version: 2.12.0")
        logger.info(f"OCR available: {OCR_AVAILABLE}")
        
        # List registered tools
        import asyncio
        registered_tools = asyncio.run(get_registered_tools())
        logger.info(f"Registered tools: {', '.join(registered_tools) if registered_tools else 'No tools registered'}")
        
        # Run the MCP server
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.critical(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("PyWinAuto MCP server stopped")


if __name__ == "__main__":
    main()
