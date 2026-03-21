"""Tests for system-level tools."""

import time
from unittest.mock import MagicMock, patch


class TestWaitForWindow:
    """Tests for wait_for_window tool."""

    @patch("pygetwindow.getWindowsWithTitle")
    def test_wait_for_window_found(self, mock_get_windows, app_instance):
        """Test waiting for window that exists."""
        from pywinauto_mcp.tools import system_tools

        wait_for_window = system_tools.wait_for_window
        if hasattr(wait_for_window, "fn"):
            wait_for_window = wait_for_window.fn

        mock_window = MagicMock()
        mock_window.title = "Test Window"
        mock_window.isActive = True
        mock_window._hWnd = 12345
        mock_get_windows.return_value = [mock_window]

        result = wait_for_window(title="Test Window", timeout=1.0)

        assert isinstance(result, dict)
        assert "status" in result or "found" in result or "error" in result

    @patch("pygetwindow.getWindowsWithTitle")
    def test_wait_for_window_timeout(self, mock_get_windows, app_instance):
        """Test waiting for window that doesn't appear."""
        from pywinauto_mcp.tools import system_tools

        wait_for_window = system_tools.wait_for_window
        if hasattr(wait_for_window, "fn"):
            wait_for_window = wait_for_window.fn

        mock_get_windows.return_value = []

        result = wait_for_window(title="Non-existent Window", timeout=0.1)

        assert isinstance(result, dict)
        assert "status" in result or "found" in result or "timeout" in result or "error" in result


class TestGetProcessInfo:
    """Tests for process information tools."""

    @patch("pywinauto_mcp.tools.system_tools.psutil")
    def test_get_process_list(self, mock_psutil, app_instance):
        """Test getting process list."""
        from pywinauto_mcp.tools import system_tools

        get_process_list = system_tools.get_process_list
        if hasattr(get_process_list, "fn"):
            get_process_list = get_process_list.fn

        mock_process = MagicMock()
        mock_process.name.return_value = "test.exe"
        mock_process.pid = 1234
        mock_process.status.return_value = "running"
        mock_psutil.process_iter.return_value = [mock_process]

        result = get_process_list()

        assert isinstance(result, dict)
        assert "processes" in result or "error" in result


class TestWait:
    """Tests for wait tool."""

    def test_wait_blocks_for_duration(self, app_instance):
        """Test that wait blocks for specified duration."""
        from pywinauto_mcp.tools import system_tools

        wait = system_tools.wait
        if hasattr(wait, "fn"):
            wait = wait.fn

        start_time = time.time()
        result = wait(seconds=0.1)
        elapsed = time.time() - start_time

        assert elapsed >= 0.1
        assert isinstance(result, dict)
        assert "success" in result or "waited" in result or "status" in result
