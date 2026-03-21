"""PyWinAuto MCP package.

This package provides Windows UI automation capabilities through a FastMCP 2.12+ compliant server.
NOW WITH COMPLETE FUNCTIONALITY - all advertised functions implemented.
"""

from .main import app as mcp
from .main import main

__version__ = "0.2.0"
__all__ = ["mcp", "main"]
