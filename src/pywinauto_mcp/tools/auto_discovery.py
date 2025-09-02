"""
Auto-discovery tool registration system for PyWinAuto MCP.

This module provides the mechanism to automatically discover and register
all tools decorated with @register_tool across the tools package.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


def discover_and_register_tools(mcp_app: Any) -> int:
    """
    Auto-discover and register all tools from the tools package.
    
    Args:
        mcp_app: The FastMCP application instance
        
    Returns:
        int: Number of tools successfully registered
    """
    # List of all tool modules to scan
    tool_modules = [
        "pywinauto_mcp.tools.window",
        "pywinauto_mcp.tools.element", 
        "pywinauto_mcp.tools.input",
        "pywinauto_mcp.tools.visual",
        "pywinauto_mcp.tools.system",
        "pywinauto_mcp.tools.file",
        "pywinauto_mcp.tools.web",
        "pywinauto_mcp.tools.debug",
        "pywinauto_mcp.tools.notification",
        "pywinauto_mcp.tools.data",
        "pywinauto_mcp.tools.accessibility",
        "pywinauto_mcp.tools.performance",
        "pywinauto_mcp.tools.security",
        "pywinauto_mcp.tools.mouse",
        "pywinauto_mcp.tools.system_tools",
        "pywinauto_mcp.tools.element_tools",
        "pywinauto_mcp.tools.visual_tools"
    ]
    
    registered_count = 0
    tool_registry: Dict[str, Callable] = {}
    
    logger.info("Starting auto-discovery of tools...")
    
    for module_name in tool_modules:
        try:
            # Import the module to trigger @register_tool decorators
            module = importlib.import_module(module_name)
            logger.debug(f"Successfully imported {module_name}")
            
            # Find all functions with _is_tool attribute
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if hasattr(func, '_is_tool') and func._is_tool:
                    
                    # Extract tool metadata
                    tool_name = getattr(func, '_tool_name', name)
                    tool_description = getattr(func, '_tool_description', func.__doc__ or "")
                    tool_category = getattr(func, '_tool_category', 'general')
                    
                    # Avoid duplicate registrations
                    if tool_name in tool_registry:
                        logger.warning(f"Tool '{tool_name}' already registered, skipping duplicate from {module_name}")
                        continue
                    
                    # Create a wrapper function for FastMCP
                    def create_wrapper(original_func: Callable, orig_name: str) -> Callable:
                        """Create a wrapper that preserves the original function signature."""
                        
                        # Use functools.wraps to preserve metadata
                        import functools
                        
                        @functools.wraps(original_func)
                        def wrapper(*args, **kwargs):
                            try:
                                return original_func(*args, **kwargs)
                            except Exception as e:
                                logger.error(f"Error in tool '{orig_name}': {e}", exc_info=True)
                                return {
                                    "success": False,
                                    "error": str(e),
                                    "error_type": e.__class__.__name__
                                }
                        
                        return wrapper
                    
                    # Create the wrapper
                    wrapped_func = create_wrapper(func, tool_name)
                    
                    # Register with FastMCP
                    try:
                        # Use FastMCP's @tool decorator
                        decorated_func = mcp_app.tool(
                            name=tool_name, 
                            description=tool_description
                        )(wrapped_func)
                        
                        # Store in registry
                        tool_registry[tool_name] = decorated_func
                        
                        registered_count += 1
                        logger.info(f"✅ Registered tool: '{tool_name}' ({tool_category}) from {module_name}")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to register tool '{tool_name}': {e}")
                        continue
                        
        except ImportError as e:
            logger.warning(f"⚠️  Could not import {module_name}: {e}")
            continue
        except Exception as e:
            logger.error(f"❌ Error processing {module_name}: {e}", exc_info=True)
            continue
    
    logger.info(f"🎯 Auto-discovery complete: {registered_count} tools registered")
    
    # Log summary by category
    categories = {}
    for module_name in tool_modules:
        try:
            module = importlib.import_module(module_name)
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if hasattr(func, '_is_tool') and func._is_tool:
                    category = getattr(func, '_tool_category', 'general')
                    categories[category] = categories.get(category, 0) + 1
        except:
            pass
    
    for category, count in categories.items():
        logger.info(f"  📁 {category}: {count} tools")
    
    return registered_count


def create_missing_tool_files() -> None:
    """Create stub files for missing tool modules."""
    
    base_dir = Path(__file__).parent
    missing_files = [
        "system.py", "file.py", "web.py", "debug.py",
        "notification.py", "data.py", "accessibility.py", 
        "performance.py", "security.py"
    ]
    
    stub_content = '''"""
{module_name} tools for PyWinAuto MCP.

This module will contain {module_desc} functionality.
Currently a stub - implementation needed.
"""

from .utils import register_tool

__all__ = []

# TODO: Implement {module_name} tools
# Example:
# @register_tool(
#     name="example_tool",
#     description="Example tool description",
#     category="{category}"
# )
# def example_tool() -> Dict[str, Any]:
#     return {{"success": True, "message": "Not implemented yet"}}
'''
    
    for filename in missing_files:
        file_path = base_dir / filename
        if not file_path.exists():
            module_name = filename.replace('.py', '')
            module_desc = module_name.replace('_', ' ')
            category = module_name
            
            content = stub_content.format(
                module_name=module_name,
                module_desc=module_desc,
                category=category
            )
            
            try:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"Created stub file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to create {file_path}: {e}")


def list_registered_tools(mcp_app: Any) -> List[Dict[str, Any]]:
    """
    List all currently registered tools.
    
    Args:
        mcp_app: The FastMCP application instance
        
    Returns:
        List of tool information dictionaries
    """
    tools = []
    
    # Access FastMCP's internal tool registry
    if hasattr(mcp_app, '_tools'):
        for tool_name, tool_info in mcp_app._tools.items():
            tools.append({
                "name": tool_name,
                "description": getattr(tool_info, 'description', ''),
                "category": getattr(tool_info, '_tool_category', 'unknown')
            })
    
    return sorted(tools, key=lambda x: (x['category'], x['name']))


def validate_tool_registration() -> bool:
    """
    Validate that all expected tools are properly registered.
    
    Returns:
        bool: True if validation passes
    """
    expected_min_tools = 35  # We expect at least 35 tools
    
    # Count tools with @register_tool decorator
    tool_modules = [
        "pywinauto_mcp.tools.window",
        "pywinauto_mcp.tools.element", 
        "pywinauto_mcp.tools.input",
        "pywinauto_mcp.tools.visual"
    ]
    
    total_decorated = 0
    for module_name in tool_modules:
        try:
            module = importlib.import_module(module_name)
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if hasattr(func, '_is_tool') and func._is_tool:
                    total_decorated += 1
        except ImportError:
            continue
    
    logger.info(f"Found {total_decorated} tools with @register_tool decorator")
    
    if total_decorated < expected_min_tools:
        logger.warning(f"Expected at least {expected_min_tools} tools, found {total_decorated}")
        return False
    
    return True
