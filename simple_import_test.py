import sys
import importlib

def main():
    print(f"Python version: {sys.version}\n")
    
    # Try to import FastMCP
    try:
        fastmcp = importlib.import_module('fastmcp')
        print(f"FastMCP module found at: {fastmcp.__file__}")
        
        # List all attributes
        print("\nFastMCP attributes:")
        for attr in dir(fastmcp):
            if not attr.startswith('_'):
                print(f"- {attr}")
        
    except ImportError as e:
        print(f"Error importing FastMCP: {e}")
    
    # Check for specific classes
    for cls in ['FastMCP', 'MCP', 'MCPLifecycle']:
        try:
            mod = importlib.import_module('fastmcp')
            if hasattr(mod, cls):
                print(f"\nFound class: {cls}")
                print(f"Type: {type(getattr(mod, cls))}")
            else:
                print(f"\nClass not found: {cls}")
        except Exception as e:
            print(f"Error checking for {cls}: {e}")

if __name__ == "__main__":
    main()
