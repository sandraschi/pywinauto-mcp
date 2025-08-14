"""
Inspect MCP tools to understand their structure and how to call them.
"""
import asyncio
import inspect
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import the MCP app from main
from pywinauto_mcp.main import mcp_app

async def inspect_mcp_tools():
    """Inspect the MCP tools to understand their structure."""
    try:
        # Get all tools from the app
        tools = await mcp_app.get_tools()
        if not tools:
            logger.warning("No tools found in MCP app")
            return
        
        print("\n" + "="*50)
        print(f"Found {len(tools)} MCP tools:")
        print("="*50)
        
        for tool_name, tool in tools.items():
            print(f"\nTool: {tool_name}")
            print("-" * (len(tool_name) + 6))
            
            # Print tool type
            print(f"Type: {type(tool).__name__}")
            
            # Print tool attributes
            print("\nAttributes:")
            for attr in dir(tool):
                if not attr.startswith('_'):  # Skip private attributes
                    try:
                        attr_value = getattr(tool, attr)
                        # Skip methods and long values for readability
                        if not callable(attr_value) and not isinstance(attr_value, (list, dict)) or isinstance(attr_value, type):
                            print(f"  - {attr}: {attr_value}")
                    except Exception as e:
                        print(f"  - {attr}: <error accessing: {e}>")
            
            # Print tool methods
            print("\nMethods:")
            for name, method in inspect.getmembers(tool, predicate=inspect.ismethod):
                if not name.startswith('_'):  # Skip private methods
                    print(f"  - {name}{inspect.signature(method)}")
            
            # Print tool documentation
            doc = inspect.getdoc(tool)
            if doc:
                print("\nDocumentation:")
                print(f"  {doc}")
            
            print("\n" + "="*50)
    
    except Exception as e:
        logger.error(f"Error inspecting tools: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(inspect_mcp_tools())
