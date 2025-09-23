"""
Screenshot Annotator - Annotate screenshots with UI element bounding boxes
"""

from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont, ImageGrab
import base64
from io import BytesIO


class ScreenshotAnnotator:
    """Annotate screenshots with UI element bounding boxes"""

    COLOR_MAP = {
        'Button': '#00FF00',      # Green
        'Edit': '#FFFF00',        # Yellow
        'Link': '#00FFFF',        # Cyan
        'ListItem': '#FF00FF',    # Magenta
        'MenuItem': '#FFA500',    # Orange
        'CheckBox': '#87CEEB',    # Sky Blue
        'RadioButton': '#DDA0DD', # Plum
        'default': '#FFFFFF'      # White
    }

    def __init__(self, font_size: int = 12):
        self.font_size = font_size
        try:
            self.font = ImageFont.truetype("arial.ttf", font_size)
        except:
            self.font = ImageFont.load_default()

    def capture_and_annotate(self, elements: List[Dict]) -> Image:
        """Capture screenshot and draw element annotations"""
        # Capture full screen
        screenshot = ImageGrab.grab()
        draw = ImageDraw.Draw(screenshot)

        # Draw each element
        for elem in elements:
            self._draw_element(draw, elem)

        return screenshot

    def _draw_element(self, draw: ImageDraw, elem: Dict):
        """Draw single element annotation"""
        bounds = elem['bounds']
        x = bounds['x']
        y = bounds['y']
        x2 = x + bounds['width']
        y2 = y + bounds['height']

        # Get color for element type
        color = self.COLOR_MAP.get(elem['type'], self.COLOR_MAP['default'])

        # Draw bounding box
        draw.rectangle([x, y, x2, y2], outline=color, width=2)

        # Draw label with ID
        label = str(elem['id'])
        label_bg = [x, y - 18, x + 30, y - 2]

        draw.rectangle(label_bg, fill=color)
        draw.text((x + 2, y - 16), label, fill='#000000', font=self.font)

    def to_base64(self, image: Image) -> str:
        """Convert image to base64 string"""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
