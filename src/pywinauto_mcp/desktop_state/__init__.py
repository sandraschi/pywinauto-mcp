"""
Desktop State Capture Module

Provides comprehensive UI element discovery, visual annotations, and OCR capabilities
for Windows desktop automation.
"""

from .walker import UIElementWalker
from .annotator import ScreenshotAnnotator
from .ocr import OCRExtractor
from .formatter import DesktopStateFormatter
from .capture import DesktopStateCapture

__all__ = [
    'UIElementWalker',
    'ScreenshotAnnotator',
    'OCRExtractor',
    'DesktopStateFormatter',
    'DesktopStateCapture'
]
