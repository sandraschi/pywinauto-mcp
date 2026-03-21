"""Integration tests for the FastMCP app instance."""

import pytest


class TestAppInitialization:
    """Tests for app initialization."""

    def test_app_instance_exists(self):
        """Test that app instance is created."""
        from pywinauto_mcp.app import app

        assert app is not None
        assert hasattr(app, "name")
        assert app.name == "pywinauto-mcp"

    def test_app_version(self):
        """Test that app has correct version."""
        from pywinauto_mcp.app import app

        assert app.version == "0.2.0"

    def test_ocr_availability_flag(self):
        """Test OCR availability flag."""
        from pywinauto_mcp.app import OCR_AVAILABLE

        assert isinstance(OCR_AVAILABLE, bool)


class TestToolRegistration:
    """Tests for tool registration."""

    def test_tools_are_registered(self, app_instance):
        """Test that tools are registered with the app."""
        # Try to get tools list if available
        if hasattr(app_instance, "list_tools"):
            tools = app_instance.list_tools()
            assert tools is not None

    def test_health_check_tool_exists(self, app_instance):
        """Test that health_check tool is registered."""
        from pywinauto_mcp.tools import basic_tools

        health_check = basic_tools.health_check

        # FastMCP wraps in FunctionTool, check it exists
        assert health_check is not None
        assert hasattr(health_check, "name")
        assert health_check.name == "health_check"

        # Access underlying function via .fn
        if hasattr(health_check, "fn"):
            health_check_fn = health_check.fn
            # Should return valid result
            result = health_check_fn()
            assert isinstance(result, dict)
            assert "status" in result


class TestModuleImports:
    """Tests for module imports."""

    def test_all_tool_modules_importable(self):
        """Test that all tool modules can be imported."""
        modules = [
            "pywinauto_mcp.tools.basic_tools",
            "pywinauto_mcp.tools.window",
            "pywinauto_mcp.tools.element",
            "pywinauto_mcp.tools.mouse",
            "pywinauto_mcp.tools.input",
            "pywinauto_mcp.tools.system_tools",
            "pywinauto_mcp.tools.visual",
            "pywinauto_mcp.tools.face_recognition",
        ]

        for module_name in modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
