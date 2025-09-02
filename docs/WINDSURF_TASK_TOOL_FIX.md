# Windsurf Task: Fix PyWinAuto MCP Tool Registration

## 🎯 OBJECTIVE
Expose all 44+ implemented tools in PyWinAuto MCP instead of just the 9 currently available.

## 🔍 PROBLEM ANALYSIS
- **Current**: Only 9 tools available via MCP (manually registered in main.py)
- **Hidden**: 35+ tools implemented with `@register_tool` but never exposed
- **Root Cause**: `@register_tool` decorator sets metadata but doesn't register with FastMCP

## 🛠️ IMPLEMENTATION STEPS

### Step 1: Create Missing Tool Files
Some tool modules are imported but don't exist. Create stubs:

```powershell
# In PyWinAuto MCP root directory
Set-Location "D:\Dev\repos\pywinauto-mcp\src\pywinauto_mcp\tools"

# Create missing tool files
@(
    "system.py", "file.py", "web.py", "debug.py",
    "notification.py", "data.py", "accessibility.py", 
    "performance.py", "security.py"
) | ForEach-Object {
    if (-not (Test-Path $_)) {
        @"
"""
$($_ -replace '.py','') tools for PyWinAuto MCP.
Currently a stub - implementation needed.
"""

from .utils import register_tool

__all__ = []

# TODO: Implement tools
"@ | Out-File -FilePath $_ -Encoding UTF8
        Write-Host "Created stub: $_" -ForegroundColor Green
    }
}
```

### Step 2: Update main.py

#### A. Add imports after existing imports:
```python
# Add after existing imports
from pywinauto_mcp.tools.auto_discovery import (
    discover_and_register_tools, 
    create_missing_tool_files,
    validate_tool_registration
)
```

#### B. Add setup function after existing tool definitions:
```python
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
```

#### C. Modify main() function:
Find this section in main():
```python
def main() -> None:
    try:
        # Load environment and configuration
        load_environment()
        log_system_info()
        
        # ADD THESE LINES HERE:
        # Set up auto-discovery BEFORE starting server
        setup_auto_discovery()
        
        # Register shutdown handler
        import signal
        # ... rest unchanged
```

### Step 3: Test the Fix

#### A. Test tool discovery:
```powershell
Set-Location "D:\Dev\repos\pywinauto-mcp"

# Test direct import
python -c "
from src.pywinauto_mcp.tools.auto_discovery import validate_tool_registration
print('Tool validation:', validate_tool_registration())
"

# List tools via script
python list_mcp_tools.py
```

#### B. Test MCP server:
```powershell
# Start server in test mode
python -m src.pywinauto_mcp.main 2>&1 | Tee-Object -FilePath "C:\temp\mcp_test.log"

# Check logs for registration messages
Select-String -Path "C:\temp\mcp_test.log" -Pattern "Registered tool|Auto-discovery"
```

### Step 4: Verify Results

Expected output should show ~44 tools:

#### Tool Categories:
- **Window Management** (11 tools): maximize_window, minimize_window, restore_window, set_window_position, get_active_window, close_window, get_window_rect, get_window_title, get_window_state, set_window_foreground, get_all_windows

- **Element Interaction** (12 tools): click_element, double_click_element, right_click_element, hover_element, get_element_info, get_element_text, set_element_text, get_element_rect, is_element_visible, is_element_enabled, get_all_elements

- **Input/Keyboard** (12 tools): send_keys, send_key_combination, type_text_advanced, clear_text, select_all_text, copy_text, paste_text, undo, redo, tab_navigation, enter_key, escape_key

- **Visual/OCR** (4 tools): capture_screenshot, save_screenshot, compare_images, get_pixel_color

#### Verification Commands:
```powershell
# Count registered tools
python -c "
import sys
sys.path.append('src')
from pywinauto_mcp.main import mcp
from pywinauto_mcp.tools.auto_discovery import setup_auto_discovery
setup_auto_discovery()
print(f'Total tools registered: {len(mcp._tools) if hasattr(mcp, \"_tools\") else \"unknown\"}')
"

# List all tools by category
python -c "
import sys
sys.path.append('src')
from pywinauto_mcp.tools.auto_discovery import list_registered_tools
from pywinauto_mcp.main import mcp, setup_auto_discovery
setup_auto_discovery()
tools = list_registered_tools(mcp)
for tool in tools:
    print(f'{tool[\"category\"]}: {tool[\"name\"]} - {tool[\"description\"][:50]}...')
"
```

## 🚨 TROUBLESHOOTING

### Issue: Import Errors
```powershell
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Test specific imports
python -c "
import sys
sys.path.append('src')
try:
    from pywinauto_mcp.tools.window import maximize_window
    print('✅ Window tools import OK')
except Exception as e:
    print(f'❌ Window tools import failed: {e}')
"
```

### Issue: No Tools Registered
```powershell
# Debug tool discovery
python -c "
import sys
sys.path.append('src')
import logging
logging.basicConfig(level=logging.DEBUG)
from pywinauto_mcp.tools.auto_discovery import discover_and_register_tools
from pywinauto_mcp.main import mcp
count = discover_and_register_tools(mcp)
print(f'Registered: {count} tools')
"
```

### Issue: FastMCP Registration Fails
Check that `@register_tool` functions have required attributes:
```powershell
python -c "
import sys
sys.path.append('src')
from pywinauto_mcp.tools.window import maximize_window
attrs = ['_is_tool', '_tool_name', '_tool_description', '_tool_category']
for attr in attrs:
    print(f'{attr}: {getattr(maximize_window, attr, \"MISSING\")}')
"
```

## ✅ SUCCESS CRITERIA

1. **Tool Count**: 40+ tools available (vs 9 before)
2. **Categories**: window, element, input, visual tools all working
3. **MCP Response**: `tools/list` returns complete tool inventory
4. **Health Check**: Server starts without errors, logs show successful registration
5. **Functionality**: Can call window management tools like `maximize_window`, `get_all_windows`

## 📋 COMPLETION CHECKLIST

- [ ] Created missing tool stub files
- [ ] Added auto_discovery.py module  
- [ ] Updated main.py with imports
- [ ] Added setup_auto_discovery() function
- [ ] Modified main() to call setup
- [ ] Tested tool discovery works
- [ ] Verified 40+ tools registered
- [ ] Tested MCP server starts successfully
- [ ] Confirmed tool categories are complete
- [ ] Documented changes in git commit

## 🎯 EXPECTED OUTCOME

**Before Fix**: 9 basic tools  
**After Fix**: 44+ comprehensive Windows automation tools

This unlocks the full power of the already-implemented PyWinAuto MCP server! 🚀