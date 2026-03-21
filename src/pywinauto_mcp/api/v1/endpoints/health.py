"""Health check endpoints for PyWinAutoMCP.

This module provides health check and status endpoints for the PyWinAutoMCP API.
"""

from typing import Any

from fastapi import APIRouter
from fastmcp import mcp

# Create router
router = APIRouter()


@mcp.tool("Check if the service is running")
@router.get("/health", response_model=dict[str, Any])
async def health_check() -> dict[str, Any]:
    """Health check endpoint.

    Returns the current status of the PyWinAutoMCP service.
    """
    return {"status": "ok", "service": "pywinauto-mcp", "version": "1.0.0", "api_version": "v1"}


@mcp.tool("Get service status and version information")
@router.get("/status", response_model=dict[str, Any])
async def status() -> dict[str, Any]:
    """Get detailed status information about the service.

    Returns version information and service status.
    """
    return {
        "status": "ok",
        "service": "pywinauto-mcp",
        "version": "1.0.0",
        "api_version": "v1",
        "description": "Windows UI Automation MCP Server",
        "endpoints": [
            {"path": "/api/v1/health", "method": "GET", "description": "Health check"},
            {"path": "/api/v1/status", "method": "GET", "description": "Service status"},
            {"path": "/api/v1/windows", "method": "GET", "description": "List windows"},
            {
                "path": "/api/v1/windows/find",
                "method": "GET",
                "description": "Find windows by criteria",
            },
            {
                "path": "/api/v1/windows/{window_handle}",
                "method": "GET",
                "description": "Get window details",
            },
            {"path": "/api/v1/windows/click", "method": "POST", "description": "Click an element"},
            {"path": "/api/v1/windows/type", "method": "POST", "description": "Type text"},
            {
                "path": "/api/v1/windows/{window_handle}/elements",
                "method": "GET",
                "description": "Get window elements",
            },
            {
                "path": "/api/v1/windows/{window_handle}/close",
                "method": "POST",
                "description": "Close a window",
            },
        ],
    }
