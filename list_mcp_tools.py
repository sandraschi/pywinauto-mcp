"""
List all available MCP tools in the PyWinAuto MCP app.
"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the MCP app from main
from pywinauto_mcp.main import mcp_app

def list_mcp_tools():
    """List all available MCP tools in the app."""
    print("\n" + "="*50)
    print("Available MCP Tools:")
    print("="*50)
    
    # Check if the app has a tools attribute
    if hasattr(mcp_app, 'tools'):
        tools = mcp_app.tools
        if hasattr(tools, 'items'):
            for name, tool in tools.items():
                print(f"- {name}: {tool}")
        else:
            print("No tools found in app.tools")
    else:
        print("The app does not have a 'tools' attribute")
    
    # Check for other potential tool attributes
    print("\n" + "="*50)
    print("App attributes:")
    print("="*50)
    for attr in dir(mcp_app):
        if not attr.startswith('_'):  # Skip private attributes
            print(f"- {attr}: {getattr(mcp_app, attr, 'N/A')}")

if __name__ == "__main__":
    list_mcp_tools()
