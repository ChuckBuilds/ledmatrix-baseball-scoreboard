# Plugin Priority Management Guide

## Overview

With the transition to a plugin-only architecture, individual plugins now manage their own display priority and rotation logic. This document explains how to implement self-managed priority in plugins, particularly for sports scoreboard plugins.

## Architecture Change

### Before (Built-in Managers)
- Display controller managed live priority globally
- `live_priority` flags in main config
- Complex rotation logic in display_controller
- Separate managers for live/recent/upcoming

### After (Plugin System)
- **Plugins manage their own priority**
- Display controller simply rotates through enabled plugins
- Each plugin decides what content to show when its turn comes
- Cleaner separation of concerns

## Implementation Pattern

### Basic Plugin Priority Structure

```python
class SportsPlugin(BasePlugin):
    """Sports scoreboard plugin with self-managed priority."""
    
    def __init__(self, plugin_id, config, display_manager, cache_manager, plugin_manager):
        super().__init__(plugin_id, config, display_manager, cache_manager, plugin_manager)
        
        # Priority settings from plugin config
        self.show_live = config.get('show_live', True)
        self.show_recent = config.get('show_recent', True)
        self.show_upcoming = config.get('show_upcoming', True)
        self.live_priority = config.get('live_priority', True)
        
        # Data storage
        self.live_games = []
        self.recent_games = []
        self.upcoming_games = []
    
    def update(self):
        """Fetch and categorize game data."""
        # Fetch all games from API
        all_games = self._fetch_games_from_api()
        
        # Categorize by status
        self.live_games = [g for g in all_games if g['status'] == 'live']
        self.recent_games = [g for g in all_games if g['status'] == 'final']
        self.upcoming_games = [g for g in all_games if g['status'] == 'scheduled']
    
    def display(self, force_clear=False):
        """
        Display content with internal priority logic.
        This is called when it's this plugin's turn in the rotation.
        """
        if force_clear:
            self.display_manager.clear()
        
        # Priority 1: Live games (if enabled and priority is on)
        if self.live_priority and self.show_live and self.live_games:
            self._display_live_games()
            return
        
        # Priority 2: Recent games
        if self.show_recent and self.recent_games:
            self._display_recent_games()
            return
        
        # Priority 3: Upcoming games
        if self.show_upcoming and self.upcoming_games:
            self._display_upcoming_games()
            return
        
        # Priority 4: Live games (if priority is off but show_live is on)
        if not self.live_priority and self.show_live and self.live_games:
            self._display_live_games()
            return
        
        # No games available
        self._display_no_games()
    
    def get_display_duration(self) -> int:
        """
        Return duration based on current content.
        Live games might want longer display time.
        """
        if self.live_games and self.live_priority:
            return self.config.get('live_duration', 60)
        elif self.recent_games:
            return self.config.get('recent_duration', 30)
        else:
            return self.config.get('upcoming_duration', 30)
    
    def _display_live_games(self):
        """Display live game(s) with score updates."""
        # Implementation specific to your display format
        game = self.live_games[0]  # Or rotate through multiple
        self.display_manager.draw_game(game, show_live_indicator=True)
    
    def _display_recent_games(self):
        """Display recent final scores."""
        game = self.recent_games[0]
        self.display_manager.draw_game(game, show_final=True)
    
    def _display_upcoming_games(self):
        """Display upcoming scheduled games."""
        game = self.upcoming_games[0]
        self.display_manager.draw_game(game, show_time=True)
    
    def _display_no_games(self):
        """Display message when no games are available."""
        self.display_manager.draw_text("No games scheduled", centered=True)
```

## Plugin Configuration Schema

Add priority settings to your `config_schema.json`:

```json
{
  "type": "object",
  "properties": {
    "enabled": {
      "type": "boolean",
      "title": "Enable Plugin",
      "default": true
    },
    "live_priority": {
      "type": "boolean",
      "title": "Live Game Priority",
      "description": "Show live games first when available",
      "default": true
    },
    "show_live": {
      "type": "boolean",
      "title": "Show Live Games",
      "default": true
    },
    "show_recent": {
      "type": "boolean",
      "title": "Show Recent Games",
      "default": true
    },
    "show_upcoming": {
      "type": "boolean",
      "title": "Show Upcoming Games",
      "default": true
    },
    "live_duration": {
      "type": "integer",
      "title": "Live Game Display Duration (seconds)",
      "minimum": 10,
      "maximum": 300,
      "default": 60
    },
    "recent_duration": {
      "type": "integer",
      "title": "Recent Game Display Duration (seconds)",
      "minimum": 10,
      "maximum": 300,
      "default": 30
    },
    "upcoming_duration": {
      "type": "integer",
      "title": "Upcoming Game Display Duration (seconds)",
      "minimum": 10,
      "maximum": 300,
      "default": 30
    }
  }
}
```

## Advanced: Multi-Game Rotation

If you want to rotate through multiple games within a single plugin turn:

```python
class SportsPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_game_index = 0
        self.games_per_rotation = self.config.get('games_per_rotation', 3)
        self.time_per_game = self.config.get('time_per_game', 20)
    
    def display(self, force_clear=False):
        """Display with internal game rotation."""
        # Get current game set based on priority
        games = self._get_priority_games()
        
        if not games:
            self._display_no_games()
            return
        
        # Rotate through multiple games
        game = games[self.current_game_index % len(games)]
        self._display_game(game)
        
        # Increment for next display call
        self.current_game_index = (self.current_game_index + 1) % min(len(games), self.games_per_rotation)
    
    def _get_priority_games(self):
        """Return games in priority order."""
        if self.live_priority and self.show_live and self.live_games:
            return self.live_games
        elif self.show_recent and self.recent_games:
            return self.recent_games
        elif self.show_upcoming and self.upcoming_games:
            return self.upcoming_games
        return []
```

## Benefits of Self-Managed Priority

### 1. **Modularity**
- Each plugin is independent
- No global state in display_controller
- Easier to maintain and debug

### 2. **Flexibility**
- Different sports can have different priority strategies
- Easy to customize per-user preferences
- Plugin updates don't affect core system

### 3. **Simplicity**
- Display controller just rotates through plugins
- No complex live priority logic at system level
- Plugins are self-contained

### 4. **Performance**
- Plugins only fetch data they need
- No unnecessary API calls for disabled modes
- Better resource management

## Migration Checklist

When converting old managers to plugins:

- [ ] Move priority logic into plugin's `display()` method
- [ ] Add priority config options to `config_schema.json`
- [ ] Implement `get_display_duration()` for dynamic timing
- [ ] Test with live games to verify priority works
- [ ] Test with no games to ensure graceful handling
- [ ] Document priority behavior in plugin README
- [ ] Update plugin version and manifest
- [ ] Test rotation with multiple plugins enabled

## Example: Hockey Scoreboard Plugin

See `ledmatrix-hockey-scoreboard` plugin for a complete reference implementation:
- `/plugins/hockey-scoreboard/manager.py` - Full priority logic
- `/plugins/hockey-scoreboard/config_schema.json` - Priority settings
- `/plugins/hockey-scoreboard/README.md` - User documentation

## Testing Priority

Test your plugin priority with different scenarios:

```python
# Test cases:
# 1. Live game available -> Should show live
# 2. No live, recent available -> Should show recent  
# 3. No live/recent, upcoming available -> Should show upcoming
# 4. No games -> Should show "no games" message
# 5. live_priority=False -> Should follow configured order
```

## Troubleshooting

**Plugin not showing live games:**
- Check `live_priority` is `true` in config
- Verify `show_live` is `true`
- Check that games are categorized correctly as "live"
- Add logging to `_get_priority_games()` method

**Display duration not respected:**
- Ensure `get_display_duration()` returns correct value
- Check that display_controller is calling the method
- Verify no override in main config

**Games not updating:**
- Check `update()` is being called based on `update_interval`
- Verify API is returning current data
- Check cache expiration settings

## Additional Resources

- [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)
- [Base Plugin API Reference](BASE_PLUGIN_API.md)
- [Display Manager Documentation](DISPLAY_MANAGER.md)

---

*Last Updated: 2025-10-15*
*Architecture Version: 2.0 (Plugin-Only)*

