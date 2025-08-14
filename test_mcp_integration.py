"""
Integration test for PyWinAuto MCP tools using FastMCP's internal mechanisms.

This script tests the MCP tools by creating a test client that properly interacts
with the FastMCP app instance.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the MCP app and tools from main
from pywinauto_mcp.main import mcp_app

class MCPTestClient:
    """A test client for MCP tools that uses FastMCP's internal mechanisms."""
    
    def __init__(self, app):
        """Initialize the test client with a FastMCP app instance."""
        self.app = app
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call an MCP tool by name with the given arguments."""
        # Get the tool function
        tool_func = getattr(self.app, tool_name, None)
        if tool_func is None:
            raise ValueError(f"Tool '{tool_name}' not found in MCP app")
        
        # Call the tool function
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**kwargs)
        else:
            result = tool_func(**kwargs)
        
        # Convert the result to a dictionary if it's a Pydantic model
        if hasattr(result, "dict"):
            result = result.dict()
        
        return result

async def test_health_check(client: MCPTestClient) -> Dict[str, Any]:
    """Test the health check tool."""
    try:
        result = await client.call_tool("health_check")
        print("Health check result:", json.dumps(result, indent=2))
        
        # Verify the result
        if result.get("status") == "ok":
            logger.info("Health check test passed!")
            return {"status": "PASSED", "result": result}
        else:
            logger.error(f"Health check test failed: {result}")
            return {"status": "FAILED", "result": result}
            
    except Exception as e:
        logger.error(f"Health check test failed with error: {e}")
        return {"status": "ERROR", "error": str(e)}

async def test_find_window(client: MCPTestClient) -> Dict[str, Any]:
    """Test the find_window tool."""
    try:
        result = await client.call_tool(
            "find_window",
            title="Program Manager",
            class_name="Progman",
            timeout=5.0
        )
        
        print("Find window result:", json.dumps(result, indent=2, default=str))
        
        # Verify the result
        if isinstance(result, dict) and "window_handle" in result:
            logger.info("Find window test passed!")
            return {"status": "PASSED", "result": result}
        else:
            logger.error(f"Find window test failed: {result}")
            return {"status": "FAILED", "result": result}
            
    except Exception as e:
        logger.error(f"Find window test failed with error: {e}")
        return {"status": "ERROR", "error": str(e)}

async def run_tests():
    """Run all tests and print results."""
    # Create a test client
    client = MCPTestClient(mcp_app)
    test_results = {}
    
    # Run health check test
    print("\n" + "="*50)
    print("Running health check test...")
    print("="*50)
    health_check_result = await test_health_check(client)
    test_results["health_check"] = health_check_result["status"]
    
    # Run find_window test if health check passed
    if health_check_result["status"] == "PASSED":
        print("\n" + "="*50)
        print("Running find_window test...")
        print("="*50)
        find_window_result = await test_find_window(client)
        test_results["find_window"] = find_window_result["status"]
    else:
        test_results["find_window"] = "SKIPPED (health check failed)"
    
    # Print summary
    print("\n" + "="*50)
    print("Test Results:")
    print("="*50)
    for test_name, result in test_results.items():
        print(f"{test_name}: {result}")
    
    # Return overall success
    return all(result == "PASSED" for result in test_results.values())

if __name__ == "__main__":
    asyncio.run(run_tests())
