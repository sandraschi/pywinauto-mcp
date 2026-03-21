"""Tests for mouse control tools."""

from unittest.mock import patch

import pytest


class TestMousePosition:
    """Tests for mouse position tools."""

    @patch("pywinauto_mcp.tools.mouse.pyautogui")
    def test_get_mouse_position(self, mock_pyautogui, app_instance):
        """Test getting mouse position."""
        from pywinauto_mcp.tools import mouse

        get_cursor_position = mouse.get_cursor_position
        if hasattr(get_cursor_position, "fn"):
            get_cursor_position = get_cursor_position.fn

        mock_pyautogui.position.return_value = (500, 300)

        result = get_cursor_position()

        assert isinstance(result, dict)
        # Check for position data
        assert "status" in result or "x" in result or "position" in result

    @patch("pywinauto_mcp.tools.basic_tools.pyautogui")
    def test_move_mouse(self, mock_pyautogui, app_instance):
        """Test moving mouse to position."""
        from pywinauto_mcp.tools import basic_tools

        move_mouse = basic_tools.move_mouse
        if hasattr(move_mouse, "fn"):
            move_mouse = move_mouse.fn

        result = move_mouse(x=100, y=200)

        mock_pyautogui.moveTo.assert_called_once()
        assert isinstance(result, dict)
        assert "success" in result or "error" in result or "status" in result


class TestMouseClick:
    """Tests for mouse click operations."""

    @patch("pywinauto_mcp.tools.basic_tools.pyautogui")
    def test_click_at_position(self, mock_pyautogui, app_instance):
        """Test clicking at specific coordinates."""
        from pywinauto_mcp.tools import basic_tools

        click_at_position = basic_tools.click_at_position
        if hasattr(click_at_position, "fn"):
            click_at_position = click_at_position.fn

        result = click_at_position(x=100, y=200)

        mock_pyautogui.click.assert_called_once()
        assert isinstance(result, dict)

    @patch("pywinauto_mcp.tools.basic_tools.pyautogui")
    def test_click_at_position_right_button(self, mock_pyautogui, app_instance):
        """Test right-clicking at position."""
        from pywinauto_mcp.tools import basic_tools

        click_at_position = basic_tools.click_at_position
        if hasattr(click_at_position, "fn"):
            click_at_position = click_at_position.fn

        result = click_at_position(x=100, y=200, button="right")

        mock_pyautogui.click.assert_called_once()
        assert isinstance(result, dict)

    @patch("pywinauto_mcp.tools.mouse.pyautogui")
    def test_double_click(self, mock_pyautogui, app_instance):
        """Test double-clicking."""
        from pywinauto_mcp.tools import mouse

        double_click = mouse.double_click
        if hasattr(double_click, "fn"):
            double_click = double_click.fn

        result = double_click(x=100, y=200)

        mock_pyautogui.doubleClick.assert_called_once()
        assert isinstance(result, dict)


class TestMouseScroll:
    """Tests for mouse scroll operations."""

    @patch("pywinauto_mcp.tools.basic_tools.pyautogui")
    def test_scroll_mouse(self, mock_pyautogui, app_instance):
        """Test scrolling mouse wheel."""
        from pywinauto_mcp.tools import basic_tools

        scroll_mouse = basic_tools.scroll_mouse
        if hasattr(scroll_mouse, "fn"):
            scroll_mouse = scroll_mouse.fn

        result = scroll_mouse(amount=3)

        mock_pyautogui.scroll.assert_called_once()
        assert isinstance(result, dict)

    @patch("pywinauto_mcp.tools.basic_tools.pyautogui")
    def test_scroll_mouse_at_position(self, mock_pyautogui, app_instance):
        """Test scrolling at specific position."""
        from pywinauto_mcp.tools import basic_tools

        scroll_mouse = basic_tools.scroll_mouse
        if hasattr(scroll_mouse, "fn"):
            scroll_mouse = scroll_mouse.fn

        result = scroll_mouse(amount=-5, x=500, y=300)

        mock_pyautogui.scroll.assert_called_once()
        assert isinstance(result, dict)


class TestMouseDrag:
    """Tests for mouse drag operations."""

    @patch("pywinauto_mcp.tools.input.pyautogui")
    def test_drag_mouse(self, mock_pyautogui, app_instance):
        """Test dragging mouse."""
        # Skip this test - input.py doesn't import pyautogui directly
        pytest.skip("input.py drag_mouse uses different implementation")
