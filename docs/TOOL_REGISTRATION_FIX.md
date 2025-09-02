# PyWinAuto MCP Tool Registration Fix

**Problem**: Only 9 tools are exposed via MCP instead of the 44+ implemented tools

**Root Cause**: The `@register_tool` decorator only sets metadata but doesn't actually register tools with FastMCP. All comprehensive tools in the `tools/` directory are implemented but never exposed.

## Current State

### Working (Manual Registration)
- `main.py` contains 9 tools manually registered with `@mcp.tool()`:
  - health_check, find_window, click_element, type_text, get_element_info
  - extract_text, extract_region, find_text, list_windows

### Missing (Auto Registration)
- `tools/window.py`: 11+ window management tools
- `tools/element.py`: 12+ element interaction tools  
- `tools/input.py`: 12+ input/keyboard tools
- `tools/visual.py`: 4+ visual/OCR tools
- Plus: system.py, file.py, web.py, debug.py, notification.py, data.py, accessibility.py, performance.py, security.py

**Total Missing**: 35+ sophisticated tools already implemented!

## Fix Implementation

### Option A: Auto-Discovery Registration (Recommended)

Create a tool auto-discovery system that finds all `@register_tool` decorated functions and registers them with FastMCP.

#### Step 1: Update `main.py`

Add after the FastMCP initialization:

```python
# Add after: mcp = FastMCP("pywinauto-mcp")

def register_all_tools():
    """Auto-discover and register all tools from the tools package."""
    import importlib
    import inspect
    from pathlib import Path
    
    tools_dir = Path(__file__).parent / "tools"
    
    # Import all tool modules to trigger @register_tool decorators
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
        "pywinauto_mcp.tools.security"
    ]
    
    registered_count = 0
    
    for module_name in tool_modules:
        try:
            module = importlib.import_module(module_name)
            
            # Find all functions with _is_tool attribute
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if hasattr(func, '_is_tool') and func._is_tool:
                    
                    # Create FastMCP tool wrapper
                    @mcp.tool(name=func._tool_name, description=func._tool_description)
                    def wrapped_tool(*args, **kwargs):
                        return func(*args, **kwargs)
                    
                    # Preserve original function metadata
                    wrapped_tool.__name__ = func._tool_name
                    wrapped_tool.__doc__ = func._tool_description
                    wrapped_tool._category = func._tool_category
                    
                    registered_count += 1
                    logger.info(f"Registered tool: {func._tool_name} from {module_name}")
                    
        except ImportError as e:
            logger.warning(f"Could not import {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error registering tools from {module_name}: {e}")
    
    logger.info(f"Successfully registered {registered_count} tools via auto-discovery")

# Call before main()
register_all_tools()
```

#### Step 2: Fix Missing Tool Files

The `tools/__init__.py` imports modules that don't exist. Create stub files:

```bash
# Create missing tool files in tools/ directory
touch tools/system.py tools/file.py tools/web.py tools/debug.py 
touch tools/notification.py tools/data.py tools/accessibility.py 
touch tools/performance.py tools/security.py
```

Each should have:
```python
# tools/system.py (example)
"""System management tools for PyWinAuto MCP."""

from .utils import register_tool

__all__ = []

# TODO: Implement system tools
# @register_tool(name="get_system_info", description="Get system information")
# def get_system_info(): pass
```

### Option B: Direct Registration (Alternative)

Replace `@register_tool` with `@mcp.tool()` directly in all tool files.

#### Step 1: Update tools/utils.py

```python
# Replace register_tool function with:
def register_tool(name=None, description="", category="general", **kwargs):
    """Wrapper that delegates to FastMCP's @mcp.tool() decorator."""
    from pywinauto_mcp.main import mcp  # Import the global mcp instance
    
    def decorator(func):
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or ""
        
        # Apply FastMCP decorator directly
        mcp_decorated = mcp.tool(name=tool_name, description=tool_desc)(func)
        
        # Preserve metadata
        mcp_decorated._tool_category = category
        return mcp_decorated
    
    return decorator
```

#### Step 2: Import All Tool Modules

Add to `main.py` after FastMCP initialization:

```python
# Import all tool modules to trigger registration
try:
    from pywinauto_mcp.tools import *  # This imports everything from __init__.py
    logger.info("Successfully imported all tool modules")
except Exception as e:
    logger.error(f"Error importing tool modules: {e}")
```

## Testing the Fix

### Before Fix
```bash
# Should show only 9 tools
python -c "from pywinauto_mcp.main import mcp; print(f'Tools: {len(mcp._tools)}')"
```

### After Fix  
```bash
# Should show 40+ tools
python -c "from pywinauto_mcp.main import mcp; print(f'Tools: {len(mcp._tools)}')"
python list_mcp_tools.py  # Should list all tools with descriptions
```

### Integration Test
```bash
# Test MCP server responds with all tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m pywinauto_mcp
```

## Windsurf Implementation Steps

1. **Open `main.py`** 
   - Add auto-discovery function after `mcp = FastMCP("pywinauto-mcp")`
   - Call `register_all_tools()` before `main()`

2. **Create missing tool files**
   - Use Windsurf terminal: `New-Item tools/system.py, tools/file.py, tools/web.py, tools/debug.py, tools/notification.py, tools/data.py, tools/accessibility.py, tools/performance.py, tools/security.py`
   - Add basic structure with `__all__ = []`

3. **Test registration**
   - Run: `python list_mcp_tools.py`
   - Verify 40+ tools are listed

4. **Debug issues**
   - Check logs for import errors
   - Verify all `@register_tool` functions have `_is_tool = True`
   - Ensure FastMCP decorates correctly

## Expected Results

- **Before**: 9 tools available via MCP
- **After**: 44+ tools available via MCP
- **Categories**: window, element, input, visual, system, file, web, debug, notification, data, accessibility, performance, security

## Verification

All these tools should become available:

**Window Management**: maximize_window, minimize_window, restore_window, set_window_position, get_active_window, close_window, get_window_rect, get_window_title, get_window_state, set_window_foreground, get_all_windows

**Element Interaction**: click_element, double_click_element, right_click_element, hover_element, get_element_info, get_element_text, set_element_text, get_element_rect, is_element_visible, is_element_enabled, get_all_elements

**Input/Keyboard**: Plus 12+ input tools from input.py

**Visual/OCR**: Plus 4+ visual tools from visual.py

This fix will expose the full power of the already-implemented PyWinAuto MCP server! 🎯