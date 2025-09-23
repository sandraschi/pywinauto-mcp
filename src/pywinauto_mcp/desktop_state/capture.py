"""
Desktop State Capture - Main orchestrator for desktop state capture
"""

from typing import Dict, Optional
from PIL import ImageGrab
from .walker import UIElementWalker
from .annotator import ScreenshotAnnotator
from .ocr import OCRExtractor
from .formatter import DesktopStateFormatter


class DesktopStateCapture:
    """Main desktop state capture orchestrator"""

    def __init__(self,
                 max_depth: int = 10,
                 tesseract_cmd: Optional[str] = None):
        self.walker = UIElementWalker(max_depth)
        self.annotator = ScreenshotAnnotator()
        self.ocr = OCRExtractor(tesseract_cmd)
        self.formatter = DesktopStateFormatter()

    def capture(self, use_vision: bool = False, use_ocr: bool = False) -> Dict:
        """
        Capture desktop state

        Args:
            use_vision: Include annotated screenshot
            use_ocr: Use OCR to extract text from elements

        Returns:
            Dictionary with text report, element data, and optional screenshot
        """
        # Walk UI tree
        elements = self.walker.walk()

        screenshot = None

        if use_vision or use_ocr:
            # Capture screenshot
            screenshot = ImageGrab.grab()

            # Enhance with OCR if requested
            if use_ocr:
                elements = self.ocr.enhance_elements(elements, screenshot)

            # Annotate screenshot if vision enabled
            if use_vision:
                screenshot = self.annotator.capture_and_annotate(elements)

        # Format output
        return self.formatter.format(elements, screenshot)
