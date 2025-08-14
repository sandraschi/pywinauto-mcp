"""PyWinAuto MCP package.

This package provides Windows UI automation capabilities through a FastMCP 2.10 compliant server.
"""

from .main import (
    health_check,
    find_window,
    click_element,
    type_text,
    list_windows,
    get_element_info,
    extract_text,
    extract_region,
    find_text,
    mcp,
    main
)

__version__ = "0.2.0"
__all__ = [
    'health_check',
    'find_window',
    'click_element',
    'type_text',
    'list_windows',
    'get_element_info',
    'extract_text',
    'extract_region',
    'find_text',
    'mcp',
    'main'
]
