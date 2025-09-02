"""
Test script to verify Python environment and basic imports.
"""
import sys
import os
import platform

def main():
    print("="*50)
    print("Python Environment Information")
    print("="*50)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Current working directory: {os.getcwd()}")
    
    print("\n" + "="*50)
    print("Environment Variables")
    print("="*50)
    for key, value in os.environ.items():
        if 'python' in key.lower() or 'path' in key.lower():
            print(f"{key}: {value}")
    
    print("\n" + "="*50)
    print("Attempting to import FastMCP")
    print("="*50)
    try:
        import fastmcp
        print(f"Successfully imported FastMCP from: {os.path.abspath(fastmcp.__file__)}")
        print(f"FastMCP version: {getattr(fastmcp, '__version__', 'Not available')}")
        print("\nFastMCP attributes:")
        for attr in dir(fastmcp):
            if not attr.startswith('_'):
                print(f"- {attr}")
    except ImportError as e:
        print(f"Error importing FastMCP: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure FastMCP is installed in your Python environment")
        print("2. Check your PYTHONPATH environment variable")
        print("3. Try running: pip install fastmcp")

if __name__ == "__main__":
    main()
