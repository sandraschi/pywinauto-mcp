"""API package for PyWinAutoMCP.

This package contains all API routes and endpoints for the PyWinAutoMCP server.
"""

from fastapi import APIRouter

# Import API routers
from pywinauto_mcp.api.v1 import api_router as v1_router

# Create the main API router
api_router = APIRouter()

# Include all API version routers
api_router.include_router(v1_router, prefix="/api/v1")
