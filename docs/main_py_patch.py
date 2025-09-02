"""
Patch for main.py to enable auto-discovery of all @register_tool decorated functions.

Apply this patch to expose all 40+ implemented tools instead of just the 9 manually registered ones.
"""

# Add this import at the top of main.py after other imports:
IMPORT_ADDITION = '''
# Auto-discovery imports
from pywinauto_mcp.tools.auto_discovery import (
    discover_and_register_tools, 
    create_missing_tool_files,
    validate_tool_registration
)
'''

# Add this function after the existing tool definitions in main.py:
FUNCTION_ADDITION = '''
def setup_auto_discovery() -> None:
    """Initialize auto-discovery system and register all tools."""
    logger.info("Setting up tool auto-discovery system...")
    
    try:
        # Create missing stub files first
        create_missing_tool_files()
        
        # Validate we have the expected tools
        if not validate_tool_registration():
            logger.warning("Tool validation failed - some expected tools missing")
        
        # Auto-discover and register all tools
        registered_count = discover_and_register_tools(mcp)
        
        if registered_count > 0:
            logger.info(f"🎉 Auto-discovery SUCCESS: {registered_count} tools now available!")
        else:
            logger.error("❌ Auto-discovery FAILED: No tools were registered")
            
    except Exception as e:
        logger.error(f"Auto-discovery setup failed: {e}", exc_info=True)
        # Don't crash the server, continue with manually registered tools
'''

# Add this call in main() function before starting the server:
MAIN_FUNCTION_ADDITION = '''
        # Set up auto-discovery BEFORE starting server
        setup_auto_discovery()
'''

# Complete patched main() function location:
PATCH_LOCATION = '''
def main() -> None:
    """
    Run the PyWinAuto MCP server.
    
    This function initializes the server, loads configuration,
    and starts the FastMCP application.
    """
    try:
        # Load environment and configuration
        load_environment()
        log_system_info()
        
        # Set up auto-discovery BEFORE starting server  <-- ADD THIS LINE
        setup_auto_discovery()                          <-- ADD THIS LINE
        
        # Register shutdown handler
        import signal
        signal.signal(signal.SIGINT, lambda s, f: handle_shutdown())
        signal.signal(signal.SIGTERM, lambda s, f: handle_shutdown())
        
        # Start the server - FastMCP 2.10.1+ runs via stdio for MCP protocol
        logger.info("Starting PyWinAuto MCP server...")
        
        # Run the MCP server using stdio transport (default for MCP)
        mcp.run()
'''

print("=== PATCH INSTRUCTIONS FOR MAIN.PY ===")
print()
print("1. Add imports at the top:")
print(IMPORT_ADDITION)
print()
print("2. Add setup function after existing tool definitions:")
print(FUNCTION_ADDITION)
print()
print("3. Modify main() function to call setup_auto_discovery():")
print("   Add these lines before 'Register shutdown handler':")
print("   # Set up auto-discovery BEFORE starting server")
print("   setup_auto_discovery()")
print()
print("4. Test the fix:")
print("   python list_mcp_tools.py")
print("   # Should show 40+ tools instead of 9")
print()
print("=== END PATCH ===")
