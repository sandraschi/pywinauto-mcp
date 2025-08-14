#!/usr/bin/env python3
"""Test imports for pywinauto-mcp."""

import sys
import traceback
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

print(f"Testing imports from: {src_path}")
print(f"Python version: {sys.version}")
print("=" * 50)

# Test basic imports
try:
    print("Testing basic imports...")
    import pywinauto
    print("✅ pywinauto imported successfully")
    
    import fastmcp
    print("✅ fastmcp imported successfully")
    
    import win32gui
    print("✅ win32gui imported successfully")
    
    import psutil
    print("✅ psutil imported successfully")
    
except ImportError as e:
    print(f"❌ Basic import failed: {e}")
    traceback.print_exc()

# Test pywinauto_mcp imports
try:
    print("\nTesting pywinauto_mcp imports...")
    
    from pywinauto_mcp.config import settings
    print("✅ pywinauto_mcp.config imported successfully")
    
    from pywinauto_mcp.core.config import get_config
    print("✅ pywinauto_mcp.core.config imported successfully")
    
    from pywinauto_mcp.core.plugin import PyWinAutoPlugin, PluginManager
    print("✅ pywinauto_mcp.core.plugin imported successfully")
    
except ImportError as e:
    print(f"❌ pywinauto_mcp import failed: {e}")
    traceback.print_exc()

# Test main module
try:
    print("\nTesting main module...")
    from pywinauto_mcp import main
    print("✅ pywinauto_mcp.main imported successfully")
    
except ImportError as e:
    print(f"❌ main module import failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 50)
print("Import test completed!")
