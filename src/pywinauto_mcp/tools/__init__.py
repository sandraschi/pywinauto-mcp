"""
PyWinAuto MCP Tools Package

This package contains various tools for window automation, element interaction,
and system operations. Each submodule contains related functionality grouped by category.
"""

from .window import *
from .element import *
from .input import *
from .visual import *
from .mouse import *
from .system_tools import *
from .element_tools import *
from .visual_tools import *

# Import modules that don't have __all__ exports separately
from . import utils
from . import auto_discovery

__all__ = [
    # Re-export all tools from submodules that have __all__
    *window.__all__,
    *element.__all__,
    *input.__all__,
    *visual.__all__,
    *mouse.__all__,
    *system_tools.__all__,
    *element_tools.__all__,
    *visual_tools.__all__,
]
