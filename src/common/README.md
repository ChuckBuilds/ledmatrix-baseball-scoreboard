# LEDMatrix Common Utilities

A shared library of common utilities for LEDMatrix plugins. This module provides reusable components that help keep plugins lightweight and independent while sharing common functionality.

## Features

- **LogoHelper**: Logo loading, caching, resizing, and management
- **TextHelper**: Text rendering with outlines, fonts, and positioning
- **APIHelper**: HTTP requests, caching, and ESPN API integration
- **DisplayHelper**: Common display operations and layout utilities
- **GameHelper**: Game data extraction and processing utilities
- **ConfigHelper**: Configuration management and validation

## Quick Start

```python
from src.common import LogoHelper, TextHelper, APIHelper

# Initialize helpers
logo_helper = LogoHelper(display_width=128, display_height=64)
text_helper = TextHelper()
api_helper = APIHelper()

# Load and resize a logo
logo = logo_helper.load_logo("LAL", "assets/logos/lakers.png")

# Render text with outline
text_helper.draw_text_with_outline(
    draw, "Lakers 120", (10, 10), font, fill=(255, 255, 255)
)

# Fetch game data
games = api_helper.fetch_espn_scoreboard("basketball", "nba")
```

## Plugin Integration

### Basic Usage

```python
from src.common import LogoHelper, TextHelper, APIHelper
from src.plugin_system.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self, plugin_id, config, display_manager, cache_manager, plugin_manager):
        super().__init__(plugin_id, config, display_manager, cache_manager, plugin_manager)
        
        # Initialize common helpers
        self.logo_helper = LogoHelper(
            display_width=self.display_manager.matrix.width,
            display_height=self.display_manager.matrix.height
        )
        self.text_helper = TextHelper()
        self.api_helper = APIHelper()
```

### Advanced Usage with Caching

```python
from src.common import APIHelper, GameHelper

class SportsPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize with caching
        self.api_helper = APIHelper(
            cache_manager=self.cache_manager,
            cache_ttl=3600  # 1 hour cache
        )
        self.game_helper = GameHelper()
    
    def update(self):
        # Fetch data with automatic caching
        data = self.api_helper.fetch_espn_scoreboard(
            sport="basketball", 
            league="nba",
            cache_key="nba_games"
        )
        
        # Process games
        games = self.game_helper.process_games(data)
        self.current_games = games
```

## API Reference

### LogoHelper

Handles logo loading, caching, and resizing for LED matrix displays.

```python
from src.common import LogoHelper

logo_helper = LogoHelper(display_width=128, display_height=64)

# Load logo with caching
logo = logo_helper.load_logo("LAL", "assets/logos/lakers.png")

# Load with automatic download if missing
logo = logo_helper.load_logo_with_download(
    "LAL", "assets/logos/lakers.png", "https://example.com/lakers.png"
)

# Get logo variations
variations = logo_helper.get_logo_variations("TA&M")
```

### TextHelper

Provides text rendering utilities with outlines and font management.

```python
from src.common import TextHelper

text_helper = TextHelper()

# Load fonts
fonts = text_helper.load_fonts()

# Draw text with outline
text_helper.draw_text_with_outline(
    draw, "Score: 120-118", (10, 10), fonts['score'], 
    fill=(255, 255, 255), outline_color=(0, 0, 0)
)

# Calculate text positioning
width = text_helper.get_text_width("Score: 120-118", fonts['score'])
```

### APIHelper

Handles HTTP requests, caching, and ESPN API integration.

```python
from src.common import APIHelper

api_helper = APIHelper(cache_manager=cache_manager)

# Fetch ESPN data with caching
data = api_helper.fetch_espn_scoreboard("basketball", "nba")

# Custom API requests
response = api_helper.get("https://api.example.com/games", timeout=30)

# Cache management
api_helper.set_cache("games", data, ttl=3600)
cached = api_helper.get_cache("games")
```

### DisplayHelper

Common display operations and layout utilities.

```python
from src.common import DisplayHelper

display_helper = DisplayHelper(display_width=128, display_height=64)

# Create base image
img = display_helper.create_base_image()

# Create overlay
overlay = display_helper.create_overlay()

# Composite images
final = display_helper.composite_images(base_img, overlay)

# Common layouts
display_helper.draw_scorebug_layout(img, game_data, fonts)
```

### GameHelper

Game data extraction and processing utilities.

```python
from src.common import GameHelper

game_helper = GameHelper()

# Extract game details from ESPN data
game = game_helper.extract_game_details(event)

# Filter games by criteria
live_games = game_helper.filter_live_games(games)
favorite_games = game_helper.filter_favorite_teams(games, ["LAL", "GSW"])

# Process game data
processed = game_helper.process_games(events, sport="basketball")
```

### ConfigHelper

Configuration management and validation.

```python
from src.common import ConfigHelper

config_helper = ConfigHelper()

# Validate configuration
is_valid = config_helper.validate_config(config, schema)

# Get configuration with defaults
logo_dir = config_helper.get_config_value(config, "logo_dir", "assets/logos")

# Merge configurations
merged = config_helper.merge_configs(base_config, plugin_config)
```

## Example: Basketball Plugin

See `basketball_plugin_example.py` for a complete example of how to refactor a plugin to use the common helpers.

## Benefits

1. **Cleaner Code**: Plugins are much shorter and more readable
2. **Reusable Components**: Common functionality is shared across plugins
3. **Better Testing**: Each helper can be tested independently
4. **Easier Maintenance**: Bug fixes in helpers benefit all plugins
5. **Consistent Behavior**: All plugins use the same underlying logic
6. **Reduced Dependencies**: Plugins don't need to import LEDMatrix core
7. **Better Error Handling**: Centralized error handling in helpers
8. **Configuration Management**: Consistent config handling across plugins

## Development

The common utilities are designed to be:
- **Lightweight**: Minimal dependencies
- **Independent**: No dependencies on LEDMatrix core
- **Well-tested**: Each helper can be tested in isolation
- **Well-documented**: Clear API documentation and examples
- **Extensible**: Easy to add new functionality
