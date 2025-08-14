"""
Direct test of PyWinAuto MCP tools using FastMCP's internal mechanisms.

This script tests the MCP tools by directly accessing them through the FastMCP app.
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the MCP app from main
from pywinauto_mcp.main import mcp_app

class MCPTestClient:
    """A test client for MCP tools that uses FastMCP's internal mechanisms."""
    
    def __init__(self, app):
        """Initialize the test client with a FastMCP app instance."""
        self.app = app
        self.tools = {}
    
    async def _load_tools(self):
        """Load all available tools from the MCP app."""
        try:
            # Get all tools from the app (await the coroutine)
            tools = await self.app.get_tools()
            if not tools:
                logger.warning("No tools found in MCP app")
                return
                
            for name, tool in tools.items():
                self.tools[name] = tool
                logger.debug(f"Loaded tool: {name} -> {tool}")
        except Exception as e:
            logger.error(f"Error loading tools: {e}")
            raise
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call an MCP tool by name with the given arguments."""
        # Get the tool
        tool = self.tools.get(tool_name)
        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found in MCP app")
        
        logger.debug(f"Calling tool: {tool_name} with args: {kwargs}")
        
        # Call the tool using its run method
        try:
            # Call the tool's run method with the arguments and await it
            tool_result = await tool.run(kwargs)
            
            # Get the structured content from the ToolResult
            result = tool_result.structured_content
            
            # If the result is a dictionary with a 'status' field, use that to determine success
            if isinstance(result, dict):
                if result.get("status") == "ok":
                    return {"status": "success", "result": result}
                else:
                    error = result.get("error", "Unknown error")
                    return {"status": "error", "error": error, "result": result}
            else:
                # If we can't determine success from the result, assume it was successful
                return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}': {e}")
            return {"status": "error", "error": str(e)}

async def test_health_check(client: MCPTestClient) -> Dict[str, Any]:
    """Test the health check tool."""
    try:
        result = await client.call_tool("health_check")
        print("\nHealth check result:", json.dumps(result, indent=2))
        
        # Verify the result
        if result.get("status") == "success" and result.get("result", {}).get("status") == "ok":
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
        
        print("\nFind window result:", json.dumps(result, indent=2, default=str))
        
        # Verify the result - check if we got a window handle in the result
        if result.get("status") == "success" and result.get("result", {}).get("window_handle"):
            logger.info("Find window test passed!")
            return {"status": "PASSED", "result": result}
        else:
            # If we got here, the call was successful but didn't return the expected data
            logger.error(f"Find window test failed: {result}")
            return {"status": "FAILED", "result": result}
            
    except Exception as e:
        logger.error(f"Find window test failed with error: {e}")
        return {"status": "ERROR", "error": str(e)}

async def run_tests():
    """Run all tests and print results."""
    # Create a test client
    client = MCPTestClient(mcp_app)
    
    # Load tools asynchronously
    try:
        await client._load_tools()
    except Exception as e:
        logger.error(f"Failed to load tools: {e}")
        return False
    
    # Print available tools for debugging
    print("\n" + "="*50)
    print("Available MCP Tools:")
    print("="*50)
    for tool_name in client.tools.keys():
        print(f"- {tool_name}")
    
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
