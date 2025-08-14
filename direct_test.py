"""
Direct test of the PyWinAuto MCP server functionality.

This script directly imports and calls the health check function to verify it works.
"""
import asyncio
from pywinauto_mcp.main import health_check

async def test_health_check():
    """Test the health check function directly."""
    try:
        print("Calling health_check()...")
        result = await health_check()
        print(f"Health check result: {result}")
        return result
    except Exception as e:
        print(f"Error calling health_check: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_health_check())
