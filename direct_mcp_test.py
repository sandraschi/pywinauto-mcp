"""
Direct test of the PyWinAuto MCP tools.

This script tests the MCP tools directly without using the stdio server.
"""
import asyncio
import json
import logging
import inspect
from typing import Dict, Any, Callable, Awaitable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the MCP app and tools from main
from pywinauto_mcp.main import mcp_app, health_check, find_window

async def test_health_check() -> Dict[str, Any]:
    """Test the health check tool directly."""
    try:
        # Call the health check function directly
        if not asyncio.iscoroutinefunction(health_check):
            # If it's not a coroutine, call it directly
            result = health_check()
            if hasattr(result, "dict"):
                result = result.dict()
        else:
            # If it's a coroutine, await it
            result = await health_check()
            if hasattr(result, "dict"):
                result = result.dict()
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

async def test_find_window() -> Dict[str, Any]:
    """Test the find_window tool directly."""
    try:
        # Call the find_window function directly with test parameters
        kwargs = {
            "title": "Program Manager",
            "class_name": "Progman",
            "timeout": 5.0
        }
        
        # Filter kwargs to only include parameters that the function accepts
        sig = inspect.signature(find_window)
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        
        if not asyncio.iscoroutinefunction(find_window):
            # If it's not a coroutine, call it directly
            result = find_window(**filtered_kwargs)
        else:
            # If it's a coroutine, await it
            result = await find_window(**filtered_kwargs)
        
        # Convert the result to a dictionary for printing
        result_dict = result.dict() if hasattr(result, "dict") else result
        print("Find window result:", json.dumps(result_dict, indent=2, default=str))
        
        # Verify the result
        if isinstance(result, dict) and "window_handle" in result:
            logger.info("Find window test passed!")
            return {"status": "PASSED", "result": result_dict}
        else:
            logger.error(f"Find window test failed: {result}")
            return {"status": "FAILED", "result": result_dict}
            
    except Exception as e:
        logger.error(f"Find window test failed with error: {e}")
        return {"status": "ERROR", "error": str(e)}

async def run_tests():
    """Run all tests and print results."""
    test_results = {}
    
    # Run health check test
    print("\n" + "="*50)
    print("Running health check test...")
    print("="*50)
    health_check_result = await test_health_check()
    test_results["health_check"] = health_check_result["status"]
    
    # Run find_window test if health check passed
    if health_check_result["status"] == "PASSED":
        print("\n" + "="*50)
        print("Running find_window test...")
        print("="*50)
        find_window_result = await test_find_window()
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
