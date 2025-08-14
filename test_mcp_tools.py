"""
Test script for PyWinAuto MCP tools.

This script tests the MCP tools directly using FastMCP's testing utilities.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from mcp.testing import MCPTestClient
from pywinauto_mcp.main import mcp_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_health_check():
    """Test the health check tool."""
    try:
        # Create a test client
        async with MCPTestClient(mcp_app) as client:
            # Call the health check tool
            response = await client.call("health_check")
            
            # Check the response
            assert response.get("status") == "ok", "Health check did not return status 'ok'"
            assert "service" in response, "Health check response missing 'service' field"
            assert "version" in response, "Health check response missing 'version' field"
            assert "timestamp" in response, "Health check response missing 'timestamp' field"
            
            logger.info("Health check test passed!")
            print(f"Health check response: {json.dumps(response, indent=2)}")
            return True
            
    except Exception as e:
        logger.error(f"Health check test failed: {e}")
        return False

async def test_find_window():
    """Test the find_window tool."""
    try:
        # Create a test client
        async with MCPTestClient(mcp_app) as client:
            # Call the find_window tool to find the desktop window
            response = await client.call(
                "find_window",
                title="Program Manager",
                class_name="Progman",
                timeout=5.0
            )
            
            # Check the response
            assert "window_handle" in response, "find_window response missing 'window_handle' field"
            assert "title" in response, "find_window response missing 'title' field"
            assert "class_name" in response, "find_window response missing 'class_name' field"
            
            logger.info("find_window test passed!")
            print(f"find_window response: {json.dumps(response, indent=2, default=str)}")
            return True
            
    except Exception as e:
        logger.error(f"find_window test failed: {e}")
        return False

async def run_tests():
    """Run all tests."""
    tests = [
        ("Health Check", test_health_check),
        ("Find Window", test_find_window),
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running test: {name}")
        print(f"{'='*50}")
        success = await test_func()
        results[name] = "PASSED" if success else "FAILED"
    
    # Print summary
    print("\nTest Results:")
    print("-" * 50)
    for name, result in results.items():
        print(f"{name}: {result}")
    
    # Return overall success
    return all(result == "PASSED" for result in results.values())

if __name__ == "__main__":
    asyncio.run(run_tests())
