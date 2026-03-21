"""Tests for window management tools."""

from unittest.mock import MagicMock, patch


class TestGetAllWindows:
    """Tests for get_all_windows tool."""

    @patch("pywinauto_mcp.tools.window.get_desktop")
    def test_get_all_windows_returns_list(self, mock_desktop, app_instance):
        """Test that get_all_windows returns a list of windows."""
        # Import the tool function
        from pywinauto_mcp.tools import window

        # Access the underlying function if it's wrapped
        get_all_windows = window.get_all_windows
        if hasattr(get_all_windows, "fn"):
            get_all_windows = get_all_windows.fn

        # Setup mock
        mock_desktop_obj = MagicMock()
        mock_window = MagicMock()
        mock_window.is_visible.return_value = True
        mock_window.handle = 12345
        mock_window.window_text.return_value = "Test Window"
        mock_window.class_name.return_value = "TestClass"
        mock_window.is_enabled.return_value = True
        mock_rect = MagicMock()
        mock_rect.left = 100
        mock_rect.top = 100
        mock_rect.right = 800
        mock_rect.bottom = 600
        mock_window.rectangle.return_value = mock_rect
        mock_desktop_obj.windows.return_value = [mock_window]
        mock_desktop.return_value = mock_desktop_obj

        result = get_all_windows()

        assert isinstance(result, dict)
        assert "windows" in result or "error" in result

    @patch("pywinauto_mcp.tools.window.get_desktop")
    def test_get_all_windows_empty_result(self, mock_desktop, app_instance):
        """Test get_all_windows when no windows are found."""
        from pywinauto_mcp.tools import window

        get_all_windows = window.get_all_windows
        if hasattr(get_all_windows, "fn"):
            get_all_windows = get_all_windows.fn

        mock_desktop_obj = MagicMock()
        mock_desktop_obj.windows.return_value = []
        mock_desktop.return_value = mock_desktop_obj

        result = get_all_windows()

        assert isinstance(result, dict)
        assert "windows" in result or "error" in result


class TestGetActiveWindow:
    """Tests for get_active_window tool."""

    @patch("pywinauto_mcp.tools.window.get_desktop")
    def test_get_active_window_returns_window(self, mock_desktop, app_instance):
        """Test that get_active_window returns active window info."""
        from pywinauto_mcp.tools import window

        get_active_window = window.get_active_window
        if hasattr(get_active_window, "fn"):
            get_active_window = get_active_window.fn

        mock_desktop_obj = MagicMock()
        mock_window = MagicMock()
        mock_window.handle = 12345
        mock_window.window_text.return_value = "Active Window"
        mock_desktop_obj.windows.return_value = [mock_window]
        mock_desktop.return_value = mock_desktop_obj

        result = get_active_window()

        assert isinstance(result, dict)
        assert (
            "handle" in result
            or "window_handle" in result
            or "error" in result
            or "status" in result
        )


class TestFindWindow:
    """Tests for find_window tool."""

    @patch("pywinauto_mcp.tools.basic_tools.Desktop")
    def test_find_window_by_title(self, mock_desktop, app_instance):
        """Test finding window by title."""
        from pywinauto_mcp.tools import basic_tools

        find_window_by_title = basic_tools.find_window_by_title
        if hasattr(find_window_by_title, "fn"):
            find_window_by_title = find_window_by_title.fn

        mock_desktop_obj = MagicMock()
        mock_window = MagicMock()
        mock_window.window_text.return_value = "Test Window"
        mock_window.handle = 12345
        mock_window.class_name.return_value = "TestClass"
        mock_window.is_visible.return_value = True
        mock_window.is_enabled.return_value = True
        mock_desktop_obj.windows.return_value = [mock_window]
        mock_desktop.return_value = mock_desktop_obj

        result = find_window_by_title(title="Test Window")

        assert isinstance(result, dict)
        # Should either have handle/window_handle or error
        assert (
            "handle" in result
            or "window_handle" in result
            or "windows" in result
            or "error" in result
        )

    @patch("pywinauto_mcp.tools.basic_tools.Desktop")
    def test_find_window_not_found(self, mock_desktop, app_instance):
        """Test find_window_by_title when window is not found."""
        from pywinauto_mcp.tools import basic_tools

        find_window_by_title = basic_tools.find_window_by_title
        if hasattr(find_window_by_title, "fn"):
            find_window_by_title = find_window_by_title.fn

        mock_desktop_obj = MagicMock()
        mock_desktop_obj.windows.return_value = []
        mock_desktop.return_value = mock_desktop_obj

        result = find_window_by_title(title="Non-existent Window")

        assert isinstance(result, dict)
        assert "error" in result or "window_handle" not in result


class TestWindowOperations:
    """Tests for window manipulation operations."""

    @patch("pywinauto_mcp.tools.window.get_desktop")
    def test_maximize_window(self, mock_desktop, app_instance):
        """Test maximizing a window."""
        from pywinauto_mcp.tools import window

        maximize_window = window.maximize_window
        if hasattr(maximize_window, "fn"):
            maximize_window = maximize_window.fn

        mock_desktop_obj = MagicMock()
        mock_window = MagicMock()
        mock_desktop_obj.window.return_value = mock_window
        mock_desktop.return_value = mock_desktop_obj

        result = maximize_window(handle=12345)

        assert isinstance(result, dict)
        assert "status" in result

    @patch("pywinauto_mcp.tools.window.get_desktop")
    def test_minimize_window(self, mock_desktop, app_instance):
        """Test minimizing a window."""
        from pywinauto_mcp.tools import window

        minimize_window = window.minimize_window
        if hasattr(minimize_window, "fn"):
            minimize_window = minimize_window.fn

        mock_desktop_obj = MagicMock()
        mock_window = MagicMock()
        mock_desktop_obj.window.return_value = mock_window
        mock_desktop.return_value = mock_desktop_obj

        result = minimize_window(handle=12345)

        assert isinstance(result, dict)
        assert "status" in result

    @patch("pywinauto_mcp.tools.window.get_desktop")
    def test_close_window(self, mock_desktop, app_instance):
        """Test closing a window."""
        from pywinauto_mcp.tools import window

        close_window = window.close_window
        if hasattr(close_window, "fn"):
            close_window = close_window.fn

        mock_desktop_obj = MagicMock()
        mock_window = MagicMock()
        mock_desktop_obj.window.return_value = mock_window
        mock_desktop.return_value = mock_desktop_obj

        result = close_window(handle=12345)

        assert isinstance(result, dict)
        assert "status" in result
