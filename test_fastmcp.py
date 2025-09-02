"""
Test script to verify FastMCP installation and available attributes.
"""
import sys
import os
import importlib

def print_divider(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def main():
    print(f"Python version: {sys.version}\n")
    
    # Check if FastMCP is installed
    print_divider("Checking FastMCP Installation")
    try:
        import fastmcp
        print(f"FastMCP is installed at: {os.path.abspath(fastmcp.__file__)}")
    except ImportError as e:
        print(f"Error importing FastMCP: {e}")
        print("Please install FastMCP using: pip install fastmcp")
        return
    
    # List all attributes in FastMCP
    print_divider("FastMCP Attributes")
    fastmcp = importlib.import_module('fastmcp')
    for attr in dir(fastmcp):
        if not attr.startswith('_'):
            print(f"- {attr}")
    
    # Check for specific classes
    print_divider("Checking for Specific Classes")
    classes_to_check = ['FastMCP', 'MCP', 'MCPLifecycle', 'App']
    for cls_name in classes_to_check:
        try:
            cls = getattr(fastmcp, cls_name)
            print(f"Found class: {cls_name} ({type(cls)})")
            # List methods of the class
            if isinstance(cls, type):
                print(f"  Methods in {cls_name}:")
                for method in dir(cls):
                    if not method.startswith('_') and callable(getattr(cls, method)):
                        print(f"  - {method}()")
        except AttributeError:
            print(f"Class not found: {cls_name}")
    
    # Check for lifecycle decorators
    print_divider("Checking for Lifecycle Decorators")
    for attr in dir(fastmcp):
        if attr.startswith('on_') and callable(getattr(fastmcp, attr)):
            print(f"Found lifecycle decorator: {attr}")

if __name__ == "__main__":
    main()
