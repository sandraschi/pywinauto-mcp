"""Tests for basic tools (health_check, get_help, etc.)."""

from datetime import datetime


class TestHealthCheck:
    """Tests for health_check tool."""

    def test_health_check_returns_healthy_status(self, app_instance):
        """Test that health_check returns healthy status."""
        from pywinauto_mcp.tools import basic_tools

        health_check = basic_tools.health_check
        # FastMCP wraps functions in FunctionTool, access via .fn attribute
        if hasattr(health_check, "fn"):
            health_check = health_check.fn

        result = health_check()

        assert result["status"] == "healthy"
        assert result["server"] == "PyWinAuto MCP"
        assert result["version"] == "0.2.0"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)

    def test_health_check_timestamp_format(self, app_instance):
        """Test that health_check timestamp is valid ISO format."""
        from pywinauto_mcp.tools import basic_tools

        health_check = basic_tools.health_check
        if hasattr(health_check, "fn"):
            health_check = health_check.fn

        result = health_check()
        timestamp = result["timestamp"]

        # Should be parseable as ISO format
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)


class TestGetHelp:
    """Tests for get_help tool."""

    def test_get_help_overview(self, app_instance):
        """Test get_help without parameters returns overview."""
        from pywinauto_mcp.tools import basic_tools

        get_help = basic_tools.get_help
        if hasattr(get_help, "fn"):
            get_help = get_help.fn

        result = get_help()

        assert result["server"] == "PyWinAuto MCP v0.2.0"
        assert "total_tools" in result
        assert "categories" in result
        assert result["status"] == "success"

    def test_get_help_with_category(self, app_instance):
        """Test get_help with category filter."""
        from pywinauto_mcp.tools import basic_tools

        get_help = basic_tools.get_help
        if hasattr(get_help, "fn"):
            get_help = get_help.fn

        result = get_help(category="system")

        assert result["category"] == "system"
        assert "tools" in result
        assert result["status"] == "success"

    def test_get_help_with_invalid_category(self, app_instance):
        """Test get_help with invalid category."""
        from pywinauto_mcp.tools import basic_tools

        get_help = basic_tools.get_help
        if hasattr(get_help, "fn"):
            get_help = get_help.fn

        result = get_help(category="invalid_category")

        assert result["status"] == "error"
        assert "error" in result
        assert "available_categories" in result

    def test_get_help_with_tool_name(self, app_instance):
        """Test get_help with specific tool name."""
        from pywinauto_mcp.tools import basic_tools

        get_help = basic_tools.get_help
        if hasattr(get_help, "fn"):
            get_help = get_help.fn

        result = get_help(tool_name="health_check")

        assert result["status"] == "success"
        assert "tool_details" in result

    def test_get_help_with_invalid_tool_name(self, app_instance):
        """Test get_help with invalid tool name."""
        from pywinauto_mcp.tools import basic_tools

        get_help = basic_tools.get_help
        if hasattr(get_help, "fn"):
            get_help = get_help.fn

        result = get_help(tool_name="invalid_tool")

        assert result["status"] == "error"
        assert "error" in result
        assert "available_tools" in result
