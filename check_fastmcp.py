import sys
import os
import importlib.util

def get_package_version(package_name):
    """Get the version of an installed package."""
    try:
        module = importlib.import_module(package_name)
        return getattr(module, '__version__', 'version not found')
    except ImportError:
        return 'not installed'

def main():
    print("Python version:", sys.version)
    print("\nChecking FastMCP installation:")
    
    # Check FastMCP version
    fastmcp_version = get_package_version('fastmcp')
    print(f"\nFastMCP version: {fastmcp_version}")
    
    # Try to import FastMCP and list its attributes
    try:
        import fastmcp
        print("\nFastMCP module found at:", os.path.abspath(fastmcp.__file__))
        
        print("\nFastMCP attributes:")
        attrs = [a for a in dir(fastmcp) if not a.startswith('_')]
        for attr in attrs:
            print(f"- {attr}")
            
        # Check for common classes
        for cls in ['FastMCP', 'MCP', 'MCPLifecycle', 'App']:
            if hasattr(fastmcp, cls):
                print(f"\nFound class: {cls}")
                cls_obj = getattr(fastmcp, cls)
                methods = [m for m in dir(cls_obj) if not m.startswith('_') and callable(getattr(cls_obj, m))]
                for method in methods:
                    print(f"  - {method}()")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
