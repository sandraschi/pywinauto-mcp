"""
PyWinAuto MCP Tools Package

This package contains various tools for window automation, element interaction,
and system operations. Each submodule contains related functionality grouped by category.
"""

from .window import *
from .element import *
from .input import *
from .visual import *
from .system import *
from .file import *
from .web import *
from .debug import *
from .notification import *
from .data import *
from .accessibility import *
from .performance import *
from .security import *

__all__ = [
    # Re-export all tools from submodules
    *window.__all__,
    *element.__all__,
    *input.__all__,
    *visual.__all__,
    *system.__all__,
    *file.__all__,
    *web.__all__,
    *debug.__all__,
    *notification.__all__,
    *data.__all__,
    *accessibility.__all__,
    *performance.__all__,
    *security.__all__,
]
