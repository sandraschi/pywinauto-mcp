"""
Base plugin system for PyWinAutoMCP.

This module provides the base class for all PyWinAutoMCP plugins.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from fastmcp import FastMCP


class PyWinAutoPlugin(ABC):
    """Base class for all PyWinAutoMCP plugins.
    
    Plugins should inherit from this class and implement the required methods.
    """
    
    def __init__(self, app: FastMCP, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin.
        
        Args:
            app: The FastMCP application instance
            config: Optional configuration dictionary for the plugin
        """
        self.app = app
        self.config = config or {}
        self._logger = app.logger.getChild(f"plugin.{self.get_name()}")
    
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Return the plugin's unique name.
        
        Returns:
            str: The plugin's unique identifier (lowercase, no spaces)
        """
        pass
    
    @abstractmethod
    def register_tools(self) -> None:
        """Register MCP tools provided by this plugin.
        
        This method should use the @mcp.tool() decorator to register
        any tools that this plugin provides.
        """
        pass
    
    def on_startup(self) -> None:
        """Called when the plugin is loaded.
        
        Override this method to perform any initialization that needs to happen
        when the plugin is first loaded.
        """
        self._logger.info(f"Initialized {self.get_name()} plugin")
    
    def on_shutdown(self) -> None:
        """Called when the plugin is unloaded.
        
        Override this method to perform any cleanup when the plugin is unloaded.
        """
        self._logger.info(f"Shutting down {self.get_name()} plugin")


class PluginManager:
    """Manages loading and registration of plugins.
    
    This class is responsible for discovering, loading, and managing
    PyWinAutoMCP plugins.
    """
    
    def __init__(self, app: FastMCP):
        """Initialize the plugin manager.
        
        Args:
            app: The FastMCP application instance
        """
        self.app = app
        self.plugins: Dict[str, PyWinAutoPlugin] = {}
        self._logger = app.logger.getChild("plugin_manager")
    
    def load_plugin(
        self, 
        plugin_name: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> PyWinAutoPlugin:
        """Load a plugin by name.
        
        Args:
            plugin_name: The name of the plugin to load
            config: Optional configuration for the plugin
            
        Returns:
            PyWinAutoPlugin: The loaded plugin instance
            
        Raises:
            ImportError: If the plugin cannot be imported
            RuntimeError: If the plugin is already loaded or fails to initialize
        """
        if plugin_name in self.plugins:
            raise RuntimeError(f"Plugin '{plugin_name}' is already loaded")
        
        try:
            # Try to import the plugin module
            module_name = f"pywinauto_mcp.plugins.{plugin_name}"
            self._logger.debug(f"Importing plugin module: {module_name}")
            module = __import__(module_name, fromlist=[""])
            
            # Get the plugin class (convention: PluginNamePlugin)
            plugin_class_name = f"{plugin_name.title()}Plugin"
            plugin_class: Type[PyWinAutoPlugin] = getattr(module, plugin_class_name, None)
            
            if not plugin_class or not issubclass(plugin_class, PyWinAutoPlugin):
                raise RuntimeError(
                    f"Plugin module '{module_name}' does not contain a valid "
                    f"{plugin_class_name} class"
                )
            
            # Initialize and register the plugin
            self._logger.info(f"Initializing plugin: {plugin_name}")
            plugin = plugin_class(self.app, config or {})
            plugin.register_tools()
            plugin.on_startup()
            
            self.plugins[plugin_name] = plugin
            return plugin
            
        except ImportError as e:
            self._logger.error(f"Failed to import plugin '{plugin_name}': {str(e)}")
            raise ImportError(f"Failed to load plugin '{plugin_name}': {str(e)}")
        except Exception as e:
            self._logger.error(
                f"Error initializing plugin '{plugin_name}': {str(e)}", 
                exc_info=True
            )
            raise RuntimeError(f"Failed to initialize plugin '{plugin_name}': {str(e)}")
    
    def load_from_config(self, config: Dict[str, Any]) -> None:
        """Load plugins from configuration.
        
        Args:
            config: Dictionary containing plugin configurations
            
        Example config format:
            {
                "ocr": {
                    "enabled": True,
                    "tesseract_cmd": "path/to/tesseract"
                },
                "security": {
                    "enabled": False
                }
            }
        """
        if not isinstance(config, dict):
            self._logger.warning("Invalid plugin configuration: expected a dictionary")
            return
        
        for plugin_name, plugin_config in config.items():
            if not isinstance(plugin_config, dict):
                self._logger.warning(
                    f"Invalid config for plugin '{plugin_name}': expected a dictionary"
                )
                continue
                
            if not plugin_config.get("enabled", True):
                self._logger.info(f"Plugin '{plugin_name}' is disabled, skipping")
                continue
                
            try:
                self.load_plugin(plugin_name, plugin_config)
            except Exception as e:
                self._logger.error(
                    f"Failed to load plugin '{plugin_name}': {str(e)}", 
                    exc_info=True
                )
    
    def get_plugin(self, name: str) -> Optional[PyWinAutoPlugin]:
        """Get a loaded plugin by name.
        
        Args:
            name: The name of the plugin to retrieve
            
        Returns:
            Optional[PyWinAutoPlugin]: The plugin instance, or None if not found
        """
        return self.plugins.get(name)
    
    def shutdown(self) -> None:
        """Shutdown all plugins."""
        for plugin in self.plugins.values():
            try:
                plugin.on_shutdown()
            except Exception as e:
                self._logger.error(
                    f"Error shutting down plugin '{plugin.get_name()}': {str(e)}",
                    exc_info=True
                )
        self.plugins.clear()
