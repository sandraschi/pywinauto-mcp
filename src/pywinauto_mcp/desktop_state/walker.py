"""
UI Element Walker - Traverse Windows UI Automation tree and extract elements
"""

from typing import List, Dict, Optional
from pywinauto import Desktop


class UIElementWalker:
    """Walk Windows UI Automation tree and extract elements"""

    INTERACTIVE_TYPES = {
        'Button', 'Edit', 'ComboBox', 'ListItem', 'MenuItem',
        'TabItem', 'Hyperlink', 'CheckBox', 'RadioButton',
        'Slider', 'ScrollBar', 'DataItem', 'Link'
    }

    INFORMATIVE_TYPES = {
        'Text', 'StatusBar', 'TitleBar', 'ToolBar', 'Header'
    }

    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self.elements = []

    def walk(self, root_element=None) -> List[Dict]:
        """Walk UI tree and extract element information"""
        if root_element is None:
            root_element = Desktop(backend='uia')

        self.elements = []
        self._recurse(root_element, depth=0)
        return self.elements

    def _recurse(self, element, depth: int):
        """Recursively walk UI tree"""
        if depth > self.max_depth:
            return

        try:
            # Extract element properties
            info = self._extract_element_info(element)

            if info and self._should_include(info):
                info['id'] = len(self.elements)
                self.elements.append(info)

            # Recurse children
            for child in element.children():
                self._recurse(child, depth + 1)

        except Exception as e:
            # Skip problematic elements
            pass

    def _extract_element_info(self, element) -> Optional[Dict]:
        """Extract all relevant properties from element"""
        try:
            # Get bounding rectangle
            rect = element.rectangle()

            # Get parent window
            parent_window = self._get_parent_window(element)

            info = {
                'type': element.control_type,
                'name': element.window_text(),
                'app': parent_window.window_text() if parent_window else 'Desktop',
                'bounds': {
                    'x': rect.left,
                    'y': rect.top,
                    'width': rect.width(),
                    'height': rect.height()
                },
                'is_visible': element.is_visible(),
                'is_enabled': element.is_enabled(),
                'shortcut': getattr(element, 'access_key', ''),
                'class_name': element.class_name()
            }

            return info

        except Exception:
            return None

    def _get_parent_window(self, element):
        """Find parent top-level window"""
        current = element
        while current:
            try:
                if current.control_type == 'Window':
                    return current
                current = current.parent()
            except:
                break
        return None

    def _should_include(self, info: Dict) -> bool:
        """Determine if element should be included"""
        # Must be visible
        if not info.get('is_visible'):
            return False

        # Must have valid bounds
        if info['bounds']['width'] <= 0 or info['bounds']['height'] <= 0:
            return False

        # Must be interactive or informative
        elem_type = info.get('type', '')
        if elem_type not in self.INTERACTIVE_TYPES and elem_type not in self.INFORMATIVE_TYPES:
            return False

        return True
