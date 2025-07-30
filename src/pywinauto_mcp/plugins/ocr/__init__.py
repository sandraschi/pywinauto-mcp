"""
OCR Plugin for PyWinAutoMCP.

This module provides OCR (Optical Character Recognition) capabilities
for extracting text from images and windows.
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pywinauto_mcp.core.plugin import PyWinAutoPlugin
from pywinauto_mcp.plugins.ocr.service import OCRService


def setup_plugin(app, config: Dict[str, Any] = None):
    """Plugin factory function.
    
    Args:
        app: The FastMCP application instance
        config: Optional configuration dictionary
        
    Returns:
        OCRPlugin: An instance of the OCR plugin
    """
    return OCRPlugin(app, config)


__all__ = ['OCRPlugin', 'setup_plugin']
