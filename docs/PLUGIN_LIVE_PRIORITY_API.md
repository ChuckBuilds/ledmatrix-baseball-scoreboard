# Plugin Live Priority API

## Overview

The Plugin Live Priority API allows plugins to declare that they should take over the display when they have urgent/live content (e.g., live sports games, breaking news, emergency alerts).

This is a fully dynamic, plugin-driven system with no hard-coded sport or content types.

## API Version

**1.0.0** - Introduced in plugin refactor (2024)

## How It Works

### 1. Plugin Declaration

Plugins declare live priority capability in their **config**:

```json
{
  "hockey-scoreboard": {
    "enabled": true,
    "live_priority": true,
    "favorite_teams": ["BOS", "TOR"],
    "display_duration": 30
  }
}
```

### 2. Plugin Implementation

Plugins implement these methods from `BasePlugin`:

#### `has_live_priority() -> bool`
Checks if live priority is enabled in config (automatically handled by base class)

#### `has_live_content() -> bool` ⭐ **REQUIRED TO OVERRIDE**
Determines if plugin currently has live content

#### `get_live_modes() -> list`
Returns which display modes should show during live priority (optional override)

## Implementation Guide

### Basic Sports Plugin Example

```python
from src.plugin_system import BasePlugin

class HockeyScoreboardPlugin(BasePlugin):
    def __init__(self, plugin_id, config, display_manager, cache_manager, plugin_manager):
        super().__init__(plugin_id, config, display_manager, cache_manager, plugin_manager)
        self.live_games = []
        self.recent_games = []
        self.upcoming_games = []
    
    def update(self):
        """Fetch game data from API"""
        # Fetch and categorize games
        self.live_games = self._fetch_live_games()
        self.recent_games = self._fetch_recent_games()
        self.upcoming_games = self._fetch_upcoming_games()
    
    def has_live_content(self) -> bool:
        """Override to implement live game detection"""
        return len(self.live_games) > 0
    
    def get_live_modes(self) -> list:
        """Override to specify which modes to show during live games"""
        # Only show live games, not recent/upcoming
        return ['hockey_live']
    
    def display(self, force_clear=False):
        """Render the display"""
        if force_clear:
            self.display_manager.clear()
        
        # Display logic here
        self.display_manager.update_display()
```

### Breaking News Plugin Example

```python
from src.plugin_system import BasePlugin

class NewsPlugin(BasePlugin):
    def __init__(self, plugin_id, config, display_manager, cache_manager, plugin_manager):
        super().__init__(plugin_id, config, display_manager, cache_manager, plugin_manager)
        self.breaking_news = None
        self.regular_news = []
    
    def update(self):
        """Fetch news from API"""
        news_data = self._fetch_news()
        self.breaking_news = news_data.get('breaking')
        self.regular_news = news_data.get('regular', [])
    
    def has_live_content(self) -> bool:
        """Override to detect breaking news"""
        return self.breaking_news is not None
    
    def get_live_modes(self) -> list:
        """Show breaking news mode only"""
        return ['news_breaking']
    
    def display(self, force_clear=False):
        if force_clear:
            self.display_manager.clear()
        
        # Display breaking news or regular news
        if self.breaking_news:
            self._display_breaking(self.breaking_news)
        else:
            self._display_regular(self.regular_news)
        
        self.display_manager.update_display()
```

## Display Controller Behavior

### Live Priority Takeover Flow

1. **Detection**: Display controller calls `has_live_content()` on all plugins with `live_priority: true`

2. **Takeover**: If any plugin has live content:
   - Current display is interrupted
   - Switches to first live mode from live priority plugin
   - Logs: `"Live priority takeover! {previous} -> {live_mode}"`

3. **Rotation**: While live content exists:
   - Rotates through all live modes from all live priority plugins
   - Uses plugin's `display_duration` for timing
   - Logs: `"Rotating live priority modes: {mode1} -> {mode2}"`

4. **Release**: When live content ends:
   - Live modes are removed from rotation
   - Returns to normal display rotation
   - Logs: `"Removed live mode from rotation: {mode}"`

### Rotation Priority

When multiple plugins have live content simultaneously:
- All live modes from all plugins are combined
- They rotate in the order they were added
- Each uses its own `display_duration`

Example with 2 plugins:
```
hockey_live (30s) -> basketball_live (30s) -> hockey_live (30s) -> ...
```

## Configuration Schema

### Plugin Config

```json
{
  "my-plugin": {
    "enabled": true,
    "live_priority": false,           // Enable live priority (default: false)
    "display_duration": 15,            // Duration in seconds
    "display_modes": ["mode1", "mode2"], // Available modes
    // ... plugin-specific config
  }
}
```

### Manifest Definition

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "display_modes": ["mode1", "mode2"],
  "supports_live_priority": true,    // Indicates plugin supports live priority
  // ... other manifest fields
}
```

## API Reference

### BasePlugin Methods

#### `has_live_priority() -> bool`
**Provided by base class** - Reads from config

```python
def has_live_priority(self) -> bool:
    return self.config.get('live_priority', False)
```

#### `has_live_content() -> bool` 
**Must override** - Implement your live detection logic

```python
def has_live_content(self) -> bool:
    # Default implementation (always False)
    return False

# Your implementation:
def has_live_content(self) -> bool:
    return hasattr(self, 'live_games') and len(self.live_games) > 0
```

#### `get_live_modes() -> list`
**Optional override** - Specify which modes to show

```python
def get_live_modes(self) -> list:
    # Default: returns all display modes from manifest
    manifest = self.plugin_manager.plugin_manifests.get(self.plugin_id, {})
    return manifest.get('display_modes', [self.plugin_id])

# Your implementation:
def get_live_modes(self) -> list:
    # Only show live mode, not recent/upcoming
    return ['my_plugin_live']
```

### Display Controller Methods

#### `_get_live_priority_plugins() -> list`
Returns list of `(plugin_id, plugin_instance, live_modes)` tuples for plugins with live content

#### `_get_all_live_modes() -> list`
Returns all possible live modes from all plugins with live priority enabled

#### `_update_live_modes_in_rotation()`
Automatically adds/removes live modes based on `has_live_content()` status

## Testing Your Implementation

### 1. Enable Live Priority in Config

```bash
# Edit config/config.json
{
  "my-plugin": {
    "enabled": true,
    "live_priority": true  // Add this
  }
}
```

### 2. Test Live Content Detection

```python
# In your plugin
def update(self):
    self.live_games = [{'id': 1, 'status': 'live'}]  # Simulate live game
    self.logger.info(f"Live content detected: {self.has_live_content()}")
```

### 3. Monitor Logs

```bash
sudo journalctl -u ledmatrix -f | grep -i "live"
```

Expected output:
```
Live priority takeover! clock -> my_plugin_live
Added live mode to rotation: my_plugin_live (plugin: my-plugin)
Rotating live priority modes: my_plugin_live -> other_live
Removed live mode from rotation: my_plugin_live (plugin: my-plugin)
```

## Best Practices

### 1. Efficient Live Detection
```python
def has_live_content(self) -> bool:
    # Cache the result to avoid repeated calculations
    if not hasattr(self, '_cached_live_status'):
        self._cached_live_status = self._calculate_live_status()
    return self._cached_live_status

def update(self):
    # Clear cache when data updates
    if hasattr(self, '_cached_live_status'):
        delattr(self, '_cached_live_status')
    # Fetch new data...
```

### 2. Graceful Fallbacks
```python
def has_live_content(self) -> bool:
    try:
        return len(self.live_games) > 0
    except AttributeError:
        # Data not loaded yet
        return False
```

### 3. Mode Selection
```python
def get_live_modes(self) -> list:
    # Return different modes based on content
    if self.has_multiple_live_games():
        return ['game1_live', 'game2_live']
    else:
        return ['single_game_live']
```

### 4. Logging
```python
def has_live_content(self) -> bool:
    has_live = len(self.live_games) > 0
    if has_live != getattr(self, '_last_live_status', False):
        self.logger.info(f"Live status changed: {has_live} ({len(self.live_games)} games)")
        self._last_live_status = has_live
    return has_live
```

## Migration from Hard-Coded System

### Old System (Hard-Coded)
```python
# In display_controller.py
nhl_enabled = self.config.get('nhl_scoreboard', {}).get('enabled', False)
nhl_live_priority = self.config.get('nhl_scoreboard', {}).get('live_priority', False)
if nhl_live_priority and self.nhl_live and self.nhl_live.live_games:
    # Hard-coded takeover logic
```

### New System (Plugin-Driven)
```python
# In your plugin
def has_live_priority(self) -> bool:
    return self.config.get('live_priority', False)

def has_live_content(self) -> bool:
    return len(self.live_games) > 0
```

No display_controller.py changes needed!

## Troubleshooting

### Live Priority Not Working

1. **Check config:**
   ```json
   "my-plugin": {
     "enabled": true,
     "live_priority": true  // Must be true!
   }
   ```

2. **Verify has_live_content():**
   ```python
   def update(self):
       self.logger.info(f"Live content: {self.has_live_content()}")
   ```

3. **Check logs:**
   ```bash
   sudo journalctl -u ledmatrix -f | grep -i "live\|priority"
   ```

### Live Modes Not Rotating

1. **Verify get_live_modes():**
   ```python
   def get_live_modes(self):
       modes = ['mode1', 'mode2']
       self.logger.info(f"Live modes: {modes}")
       return modes
   ```

2. **Check display_duration:**
   ```json
   {
     "display_duration": 30  // Must be set
   }
   ```

### Multiple Plugins Conflicting

This is **not** a conflict - it's a feature! All live modes rotate together.

If you want priority between plugins, implement in your `has_live_content()`:
```python
def has_live_content(self) -> bool:
    # Only take over if no other plugin has live content
    other_live = self._check_other_plugins()
    return len(self.live_games) > 0 and not other_live
```

## Examples

See the following plugins for reference implementations:
- `hockey-scoreboard` - Sports live games
- `basketball-scoreboard` - Multi-mode live rotation
- `football-scoreboard` - Live game detection
- `news` (if available) - Breaking news alerts

## API Changelog

### Version 1.0.0 (2024)
- Initial implementation
- `has_live_priority()` - Check if enabled
- `has_live_content()` - Detect live content
- `get_live_modes()` - Specify live modes
- Full display controller integration

