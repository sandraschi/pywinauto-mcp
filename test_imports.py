"""
Test script to verify all imports and basic functionality.

Run this script to check if all dependencies are properly installed and imports work.
"""
import sys
import importlib
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def test_imports():
    """Test importing all main modules."""
    modules_to_test = [
        # Core modules
        'pywinauto_mcp.core.plugin',
        'pywinauto_mcp.core.config',
        'pywinauto_mcp.app',
        'pywinauto_mcp.main',
        
        # API modules
        'pywinauto_mcp.api.v1.endpoints',
        'pywinauto_mcp.api.v1.models',
        
        # Plugins
        'pywinauto_mcp.plugins',
        'pywinauto_mcp.plugins.ocr',
        
        # Other modules
        'pywinauto_mcp.security',
        'pywinauto_mcp.security_endpoints',
    ]
    
    print("=" * 80)
    print("Testing imports...")
    print("=" * 80)
    
    success = True
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ Successfully imported: {module_name}")
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {str(e)}")
            success = False
        except Exception as e:
            print(f"⚠️  Error importing {module_name}: {str(e)}")
            success = False
    
    print("\n" + "=" * 80)
    if success:
        print("✅ All imports successful!")
    else:
        print("❌ Some imports failed. Please check the error messages above.")
    
    return success

def test_plugin_loading():
    """Test plugin loading functionality."""
    try:
        from pywinauto_mcp.core.plugin import PluginManager
        from unittest.mock import MagicMock
        
        print("\nTesting plugin loading...")
        print("-" * 40)
        
        # Create a mock app object with a logger
        mock_app = MagicMock()
        mock_logger = MagicMock()
        mock_logger.getChild.return_value = mock_logger
        mock_app.logger = mock_logger
        
        # Initialize PluginManager with the mock app
        plugin_manager = PluginManager(app=mock_app)
        
        # Test discovering plugins
        plugins = plugin_manager.discover_plugins()
        print(f"Discovered {len(plugins)} plugins:")
        for name, plugin in plugins.items():
            print(f"- {name}: {plugin}")
            
        print("\n✅ Plugin loading test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error testing plugin loading: {str(e)}")
        return False

if __name__ == "__main__":
    import_ok = test_imports()
    plugin_ok = test_plugin_loading()
    
    print("\n" + "=" * 80)
    if import_ok and plugin_ok:
        print("✅ All tests passed! The application should be ready to run.")
        print("You can now run the application with: python -m pywinauto_mcp.main")
    else:
        print("❌ Some tests failed. Please check the error messages above and fix the issues.")
    print("=" * 80)
