"""
Inspect the ToolResult class to understand its structure.
"""
import asyncio
import inspect
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import the MCP app from main
from pywinauto_mcp.main import mcp_app

async def inspect_toolresult():
    """Inspect the ToolResult class and its instances."""
    try:
        # Get the health check tool
        tools = await mcp_app.get_tools()
        if not tools:
            logger.warning("No tools found in MCP app")
            return
        
        # Get the first tool to inspect its run method return type
        tool_name, tool = next(iter(tools.items()))
        print(f"\nInspecting tool: {tool_name}")
        print("=" * 50)
        
        # Get the run method
        run_method = getattr(tool, 'run', None)
        if not run_method:
            print("Tool does not have a run method")
            return
        
        # Get the return type annotation of the run method
        run_sig = inspect.signature(run_method)
        return_type = run_sig.return_annotation
        print(f"Return type of run method: {return_type}")
        
        # If the return type is a string, try to evaluate it
        if isinstance(return_type, str):
            try:
                # Try to evaluate the return type in the global namespace
                import sys
                import builtins
                from importlib import import_module
                
                # Get the module where the tool is defined
                module_name = tool.__module__
                module = sys.modules.get(module_name)
                if not module:
                    module = import_module(module_name)
                
                # Evaluate the return type in the module's namespace
                namespace = {**vars(builtins), **vars(module)}
                return_type = eval(return_type, namespace)
                print(f"Evaluated return type: {return_type}")
            except Exception as e:
                print(f"Could not evaluate return type: {e}")
        
        # Get the actual return value from calling the tool
        print("\nCalling tool to inspect return value...")
        try:
            # Call the tool with empty arguments
            result = await tool.run({})
            print(f"\nTool result type: {type(result).__name__}")
            print(f"Tool result dir: {dir(result)}")
            
            # Print all attributes of the result
            print("\nResult attributes:")
            for attr in dir(result):
                if not attr.startswith('__'):
                    try:
                        attr_value = getattr(result, attr)
                        print(f"  - {attr}: {attr_value}")
                    except Exception as e:
                        print(f"  - {attr}: <error accessing: {e}>")
            
            # Try to convert to dict if possible
            if hasattr(result, 'dict'):
                print("\nResult as dict:")
                print(result.dict())
            
            # Try to get the JSON schema
            if hasattr(result, 'schema_json'):
                print("\nResult JSON schema:")
                print(result.schema_json(indent=2))
                
        except Exception as e:
            print(f"Error calling tool: {e}")
    
    except Exception as e:
        logger.error(f"Error inspecting ToolResult: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(inspect_toolresult())
