"""
API v1 Router for PyWinAutoMCP.

This module contains all API routes for version 1 of the PyWinAutoMCP API.
"""
from fastapi import APIRouter

# Import all endpoint modules
from pywinauto_mcp.api.v1.endpoints import windows, health

# Create the API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(windows.router, prefix="/windows", tags=["windows"])