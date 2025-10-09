"""
LEDMatrix Plugin System

This module provides the core plugin infrastructure for the LEDMatrix project.
It enables dynamic loading, management, and discovery of display plugins.

API Version: 1.0.0
"""

__version__ = "1.0.0"
__api_version__ = "1.0.0"

from .base_plugin import BasePlugin
from .plugin_manager import PluginManager
from .store_manager import PluginStoreManager

__all__ = [
    'BasePlugin',
    'PluginManager',
    'PluginStoreManager',
]

