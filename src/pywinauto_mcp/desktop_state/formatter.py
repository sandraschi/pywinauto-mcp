"""
Desktop State Formatter - Format desktop state into structured output
"""

from typing import List, Dict, Optional
from PIL import Image
from .walker import UIElementWalker


class DesktopStateFormatter:
    """Format desktop state into structured output"""

    def format(self, elements: List[Dict], screenshot: Optional[Image] = None) -> Dict:
        """Format complete state output"""
        # Separate element types
        interactive = [e for e in elements if self._is_interactive(e)]
        informative = [e for e in elements if self._is_informative(e)]

        # Build text report
        text_report = self._build_text_report(interactive, informative)

        # Prepare output
        output = {
            'text': text_report,
            'interactive_elements': interactive,
            'informative_elements': informative,
            'element_count': len(elements)
        }

        # Add screenshot if provided
        if screenshot:
            from .annotator import ScreenshotAnnotator
            annotator = ScreenshotAnnotator()
            output['screenshot_base64'] = annotator.to_base64(screenshot)

        return output

    def _build_text_report(self, interactive: List[Dict], informative: List[Dict]) -> str:
        """Build human-readable text report"""
        lines = []

        # Interactive elements section
        lines.append("Interactive Elements:")
        lines.append("-" * 60)
        for elem in interactive:
            bounds = elem['bounds']
            name = elem.get('name', elem.get('ocr_text', ''))
            lines.append(
                f"[{elem['id']}] {elem['type']} \"{name}\" "
                f"at ({bounds['x']},{bounds['y']}) - App: {elem['app']}"
            )

        lines.append("\n")

        # Informative elements section
        lines.append("Informative Elements:")
        lines.append("-" * 60)
        for elem in informative:
            name = elem.get('name', elem.get('ocr_text', ''))
            if name:
                lines.append(f"- {name} (App: {elem['app']})")

        return "\n".join(lines)

    def _is_interactive(self, elem: Dict) -> bool:
        """Check if element is interactive"""
        return elem['type'] in UIElementWalker.INTERACTIVE_TYPES

    def _is_informative(self, elem: Dict) -> bool:
        """Check if element is informative"""
        return elem['type'] in UIElementWalker.INFORMATIVE_TYPES
