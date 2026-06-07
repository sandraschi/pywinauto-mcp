"""CLI helpers (mcp-config snippet for Cursor / Claude Desktop)."""

from __future__ import annotations

import json
import shutil
import sys


def mcp_config_stdio() -> dict:
    """Build recommended stdio MCP server config."""
    exe = shutil.which("pywinauto-mcp")
    if exe:
        command = exe
        args: list[str] = []
    else:
        command = sys.executable
        args = ["-m", "pywinauto_mcp.main", "--stdio"]
    return {
        "mcpServers": {
            "pywinauto": {
                "command": command,
                "args": args,
                "env": {
                    "PYWINAUTO_MCP_DISPATCH": "foreground",
                },
            }
        }
    }


def print_mcp_config() -> None:
    """Print JSON for pasting into Cursor MCP settings."""
    print(json.dumps(mcp_config_stdio(), indent=2))
    print(
        "\n# Background computer-use profile (dedicated session only):\n"
        '# Set env PYWINAUTO_MCP_DISPATCH=background and PYWINAUTO_MCP_TRAJECTORY_LOG=1\n',
        file=sys.stderr,
    )


def main_cli() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "mcp-config":
        print_mcp_config()
    else:
        print("Usage: pywinauto-mcp mcp-config", file=sys.stderr)
        sys.exit(1)
