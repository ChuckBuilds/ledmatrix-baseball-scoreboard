# Plugin-Only Dynamic Structure Refactor

## Overview
Refactored the display controller to be fully plugin-driven, removing all hard-coded sport-specific references. This creates a more scalable, maintainable architecture where new plugins can be added without modifying core code.

## Changes Made

### 1. Dynamic Favorite Teams Logging (display_controller.py)
**Before:** Hard-coded checks for each sport (NHL, NBA, MLB, etc.)
```python
if nhl_enabled:
    logger.info(f"NHL Favorite teams: {self.nhl_favorite_teams}")
if nba_enabled:
    logger.info(f"NBA Favorite teams: {self.nba_favorite_teams}")
# ... repeated for 13+ sports
```

**After:** Dynamic loop that works for any plugin
```python
for plugin_id, plugin_config in self.config.items():
    if isinstance(plugin_config, dict) and plugin_config.get('enabled', False):
        favorite_teams = plugin_config.get('favorite_teams', [])
        if favorite_teams:
            display_name = plugin_id.replace('_', ' ').replace('-', ' ').title()
            logger.info(f"{display_name} Favorite teams: {favorite_teams}")
```

### 2. Removed Hard-Coded Rotation State (display_controller.py)
**Removed:** All hard-coded sport-specific rotation state variables
- `self.nhl_current_team_index`, `self.nhl_showing_recent`, `self.nhl_favorite_teams`, `self.in_nhl_rotation`
- `self.nba_current_team_index`, ... (repeated for 13+ sports)

**Reasoning:** Plugins now handle their own state. No need for controller to track state for individual sports.

### 3. Refactored Live Priority Logic (display_controller.py)
**Before:** Hard-coded list of sports with priority checks
```python
for sport, attr, priority in [
    ('nhl', 'nhl_live', self.nhl_live_priority),
    ('nba', 'nba_live', self.nba_live_priority),
    # ... 13+ hard-coded sports
]:
    manager = getattr(self, attr, None)
    # complex checking logic
```

**After:** Stubbed out for plugin handling
```python
# NOTE: Live priority logic removed - plugins now handle their own priority
is_currently_live = self.current_display_mode.endswith('_live')
live_priority_takeover = False  # Disabled - plugins handle their own priority
live_priority_sports = []  # Empty - no hard-coded sports
```

### 4. Simplified Live Modes Rotation (display_controller.py)
**Before:** 50+ lines of hard-coded sport checking and mode updates

**After:** Simple stub delegating to plugins
```python
def _update_live_modes_in_rotation(self):
    """Update live modes in rotation - delegated to plugins.
    
    NOTE: Live priority logic is now handled by individual plugins.
    This method is kept as a stub for backward compatibility.
    """
    # Plugins handle their own live priority and mode rotation
    pass
```

### 5. Fixed Plugin Dependency Installation (plugin_manager.py)
**Before:** Permission errors when installing dependencies
```python
['pip3', 'install', '--break-system-packages', '--root-user-action=ignore', '-r', str(requirements_file)]
```

**After:** Smart installation based on execution context
```python
# Check if running as root (systemd service context)
running_as_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False

if running_as_root:
    # System-wide installation for root (systemd service)
    cmd = ['pip3', 'install', '--break-system-packages', '-r', str(requirements_file)]
else:
    # User installation for development/testing
    cmd = ['pip3', 'install', '--user', '-r', str(requirements_file)]
```

## Benefits

### Scalability
- **No core code changes** needed to add new sport plugins
- New plugins automatically show up in favorite teams logging
- System adapts to any plugin configuration

### Maintainability
- **Reduced code complexity**: Removed ~100+ lines of hard-coded sport logic
- **Single source of truth**: Plugin configuration drives behavior
- **DRY principle**: No repetition of similar logic for each sport

### Flexibility
- Plugins can implement their own priority logic
- Plugins handle their own state and rotation
- Display controller is now sport-agnostic

## Migration Notes

### For Plugin Developers
- Plugins should handle their own:
  - Live priority logic
  - Rotation state
  - Favorite team filtering
  
### For Users
- **No configuration changes needed**
- Existing plugin configurations work as-is
- Favorite teams logging now works for any plugin

## Files Modified

1. `src/display_controller.py`
   - Removed hard-coded sport variables (~50 lines removed)
   - Dynamic favorite teams logging
   - Stubbed out legacy live priority logic
   
2. `src/plugin_system/plugin_manager.py`
   - Fixed pip permission issues with `--user` flag

## Testing

After these changes, test that:
1. Service starts without errors
2. Plugins load correctly
3. Favorite teams are logged for enabled plugins
4. Display modes rotate properly
5. Plugin dependencies install without permission errors

## Plugin Live Priority API (NEW!)

Added a complete plugin-driven live priority system:

### BasePlugin New Methods:
- `has_live_priority()` - Check if plugin has live priority enabled
- `has_live_content()` - Override to detect live content
- `get_live_modes()` - Override to specify which modes during live takeover

### Display Controller Integration:
- `_get_live_priority_plugins()` - Get plugins with live content
- `_get_all_live_modes()` - Get all live modes from plugins
- `_update_live_modes_in_rotation()` - Auto add/remove live modes

### How It Works:
1. Plugin sets `"live_priority": true` in config
2. Plugin overrides `has_live_content()` to detect live events
3. Display controller automatically:
   - Detects live content
   - Takes over display
   - Rotates through live modes
   - Releases when content ends

**Full documentation:** See `PLUGIN_LIVE_PRIORITY_API.md`

## Future Enhancements

Consider implementing:
1. ~~Plugin-level priority system~~ ✅ **COMPLETED** - See Plugin Live Priority API
2. ~~Dynamic live game takeover through plugin API~~ ✅ **COMPLETED** - See Plugin Live Priority API
3. Plugin state management framework
4. Inter-plugin communication API

