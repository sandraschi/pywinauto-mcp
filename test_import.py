print("Testing FastMCP import...")
try:
    import fastmcp
    print("FastMCP imported successfully!")
    print(f"FastMCP location: {fastmcp.__file__}")
    print("\nAvailable attributes:")
    for attr in dir(fastmcp):
        if not attr.startswith('_'):
            print(f"- {attr}")
except Exception as e:
    print(f"Error importing FastMCP: {e}")
