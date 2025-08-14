"""
PyWinAutoMCP - Windows UI Automation MCP Server.

This module provides the main application setup for the PyWinAutoMCP server.
"""
import logging
from typing import Dict, Any
from fastmcp import FastMCP
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pywinauto_mcp.core.config import get_config
from pywinauto_mcp.api import api_router


def create_app(config: Dict[str, Any] = None) -> FastMCP:
    """Create and configure the FastMCP application.
    
    Args:
        config: Optional configuration dictionary. If not provided,
                configuration will be loaded using get_config().
                
    Returns:
        FastMCP: Configured FastMCP application instance
    """
    # Load configuration if not provided
    if config is None:
        config = get_config()
    
    # Set up logging
    log_level = config.get("log_level", "INFO").upper()
    logging.basicConfig(level=log_level)
    logger = logging.getLogger("pywinauto-mcp")
    
    # Initialize FastMCP with required parameters
    app = FastMCP(
        name="pywinauto-mcp",
        version="1.0.0"
    )
    
    # Set additional configuration
    app.structured_output = True
    app.enable_elicitation = True
    
    # Add tool categories
    app.tool_categories = [
        {"name": "windows", "description": "Window management operations"},
        {"name": "elements", "description": "UI element interactions"},
        {"name": "input", "description": "Keyboard and mouse input"},
        {"name": "info", "description": "Information retrieval"},
    ]
    
    # Add logger to the app instance
    app.logger = logger
    
    # Include API router
    app.include_router(api_router)
    
    return app


# Create the application instance
app = create_app()
