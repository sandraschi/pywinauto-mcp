"""
Test script to verify FastMCP imports and available attributes.
"""
import sys
import pkg_resources

def check_package_version(package_name):
    """Check the installed version of a package."""
    try:
        version = pkg_resources.get_distribution(package_name).version
        print(f"{package_name} version: {version}")
        return version
    except pkg_resources.DistributionNotFound:
        print(f"{package_name} is not installed")
        return None

def check_fastmcp_imports():
    """Check FastMCP imports and available attributes."""
    print("\n=== Checking FastMCP imports ===")
    
    # Check FastMCP version
    fastmcp_version = check_package_version('fastmcp')
    
    # Try to import FastMCP
    try:
        import fastmcp
        print("\nFastMCP module found at:", fastmcp.__file__)
        
        # List all non-private attributes
        print("\nFastMCP attributes:")
        attrs = [a for a in dir(fastmcp) if not a.startswith('_')]
        for attr in attrs:
            print(f"- {attr}")
            
            # For classes, list their methods
            attr_value = getattr(fastmcp, attr)
            if isinstance(attr_value, type):
                methods = [m for m in dir(attr_value) if not m.startswith('_')]
                for method in methods:
                    print(f"  - {method}()")
        
        # Check for common FastMCP classes
        common_classes = ['FastMCP', 'MCP', 'MCPLifecycle']
        print("\nChecking for common FastMCP classes:")
        for cls in common_classes:
            has_cls = hasattr(fastmcp, cls)
            print(f"- {cls}: {'Found' if has_cls else 'Not found'}")
            if has_cls:
                print(f"  - Type: {type(getattr(fastmcp, cls))}")
        
        return True
    except ImportError as e:
        print(f"Error importing FastMCP: {e}")
        return False

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    check_fastmcp_imports()
