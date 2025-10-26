"""
LEDMatrix Common Utilities

A shared library of common utilities for LEDMatrix plugins.
Provides logo loading, text rendering, API helpers, and more.
"""

__version__ = "1.0.0"
__author__ = "LEDMatrix Team"
__email__ = "contact@ledmatrix.dev"

# Import main helper classes
from .logo_helper import LogoHelper
from .text_helper import TextHelper
from .api_helper import APIHelper
from .display_helper import DisplayHelper
from .game_helper import GameHelper
from .config_helper import ConfigHelper

# Import utility functions
from .utils import (
    normalize_team_abbreviation,
    format_time,
    format_date,
    get_timezone,
    validate_dimensions,
)

__all__ = [
    # Main helper classes
    "LogoHelper",
    "TextHelper", 
    "APIHelper",
    "DisplayHelper",
    "GameHelper",
    "ConfigHelper",
    
    # Utility functions
    "normalize_team_abbreviation",
    "format_time",
    "format_date", 
    "get_timezone",
    "validate_dimensions",
]
