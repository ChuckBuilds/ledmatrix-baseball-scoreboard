# Configuration Cleanup Summary

## What Was Removed

The following configuration sections were removed from `config.json` and `config.template.json` as they are now handled by plugins:

### Sports Managers
- `nhl_live`, `nhl_recent`, `nhl_upcoming`
- `nba_live`, `nba_recent`, `nba_upcoming`
- `wnba_live`, `wnba_recent`, `wnba_upcoming`
- `mlb_live`, `mlb_recent`, `mlb_upcoming`
- `milb_live`, `milb_recent`, `milb_upcoming`
- `nfl_live`, `nfl_recent`, `nfl_upcoming`
- `ncaa_fb_live`, `ncaa_fb_recent`, `ncaa_fb_upcoming`
- `ncaa_baseball_live`, `ncaa_baseball_recent`, `ncaa_baseball_upcoming`
- `ncaam_basketball_live`, `ncaam_basketball_recent`, `ncaam_basketball_upcoming`
- `ncaaw_basketball_live`, `ncaaw_basketball_recent`, `ncaaw_basketball_upcoming`
- `ncaam_hockey_live`, `ncaam_hockey_recent`, `ncaam_hockey_upcoming`
- `ncaaw_hockey_live`, `ncaaw_hockey_recent`, `ncaaw_hockey_upcoming`
- `soccer_live`, `soccer_recent`, `soccer_upcoming`

### Content Managers
- `weather` (now handled by weather plugin)
- `stocks` (now handled by stocks plugin)
- `stock_news` (now handled by stock-news plugin)
- `odds_ticker` (now handled by odds-ticker plugin)
- `leaderboard` (now handled by leaderboard plugin)
- `youtube` (not yet available as plugin)
- `text_display` (now handled by text-display plugin)
- `static_image` (now handled by static-image plugin)
- `music` (now handled by music plugin)
- `of_the_day` (now handled by of-the-day plugin)
- `news_manager` (now handled by news plugin)

### Display Durations
All old manager display durations were removed from `display_durations` section, keeping only:
- `calendar` (core system component)

## What Remains

### Core System Settings
- `web_display_autostart`: Web interface settings
- `schedule`: Display schedule configuration
- `timezone`: System timezone
- `location`: Default location for location-based plugins

### Display Hardware
- `display.hardware`: LED matrix hardware configuration
- `display.runtime`: Runtime display settings
- `display.display_durations`: Display duration settings (minimal)
- `display.use_short_date_format`: Date format preference

### Core Components
- `calendar`: Calendar manager (core system component, not a plugin)

### Plugin System
- `plugin_system`: Plugin system configuration
  - `plugins_directory`: Where plugins are stored
  - `auto_discover`: Auto-discover plugins
  - `auto_load_enabled`: Auto-load enabled plugins

## Backup Files Created

- `config_backup.json`: Backup of original config.json
- `config.template_backup.json`: Backup of original config.template.json

## New Configuration Structure

The new configuration is much cleaner and focuses on:
1. **Core system settings** (display hardware, schedule, timezone)
2. **Plugin system configuration** (where to find plugins, auto-discovery)
3. **Core components only** (calendar manager)

All other functionality is now handled by plugins, which have their own configuration sections when enabled.

## Benefits of New Structure

1. **Cleaner configuration**: Only essential settings in main config
2. **Plugin isolation**: Each plugin manages its own configuration
3. **Easier maintenance**: No more complex manager configurations
4. **Better organization**: Clear separation between core system and plugins
5. **Simplified deployment**: Plugins can be added/removed without config changes

## Migration Path

To migrate existing configurations:

1. **Backup current config**: Already done
2. **Install plugins**: Add desired plugins to plugin-repos directory
3. **Configure plugins**: Add plugin configurations to config.json
4. **Test in emulator**: Use `./run_emulator.sh` to test
5. **Deploy to hardware**: Once tested, deploy to Raspberry Pi

## Next Steps

1. **Install plugins**: Add desired plugins to the system
2. **Configure plugins**: Set up plugin-specific configurations
3. **Test functionality**: Use emulator to test all features
4. **Deploy to hardware**: Once everything works, deploy to Pi
