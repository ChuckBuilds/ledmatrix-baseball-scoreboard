# AP Top 25 Dynamic Teams Feature

## Overview

The AP Top 25 Dynamic Teams feature allows you to automatically follow the current AP Top 25 ranked teams in NCAA Football without manually updating your configuration each week. This feature dynamically resolves special team names like `"AP_TOP_25"` into the actual team abbreviations that are currently ranked in the AP Top 25.

## How It Works

When you add `"AP_TOP_25"` to your `favorite_teams` list, the system:

1. **Fetches Current Rankings**: Automatically retrieves the latest AP Top 25 rankings from ESPN API
2. **Resolves Dynamic Names**: Converts `"AP_TOP_25"` into the actual team abbreviations (e.g., `["UGA", "MICH", "OSU", ...]`)
3. **Updates Automatically**: Rankings are cached for 1 hour and automatically refresh
4. **Filters Games**: Only shows games involving the current AP Top 25 teams

## Supported Dynamic Team Names

| Dynamic Team Name | Description | Teams Returned |
|------------------|-------------|----------------|
| `"AP_TOP_25"` | Current AP Top 25 teams | All 25 ranked teams |
| `"AP_TOP_10"` | Current AP Top 10 teams | Top 10 ranked teams |
| `"AP_TOP_5"` | Current AP Top 5 teams | Top 5 ranked teams |

## Configuration Examples

### Basic AP Top 25 Configuration

```json
{
  "ncaa_fb_scoreboard": {
    "enabled": true,
    "show_favorite_teams_only": true,
    "favorite_teams": [
      "AP_TOP_25"
    ]
  }
}
```

### Mixed Regular and Dynamic Teams

```json
{
  "ncaa_fb_scoreboard": {
    "enabled": true,
    "show_favorite_teams_only": true,
    "favorite_teams": [
      "UGA",
      "AUB", 
      "AP_TOP_25"
    ]
  }
}
```

### Top 10 Teams Only

```json
{
  "ncaa_fb_scoreboard": {
    "enabled": true,
    "show_favorite_teams_only": true,
    "favorite_teams": [
      "AP_TOP_10"
    ]
  }
}
```

## Technical Details

### Caching Strategy

- **Cache Duration**: Rankings are cached for 1 hour to reduce API calls
- **Automatic Refresh**: Cache automatically expires and refreshes
- **Manual Clear**: Cache can be cleared programmatically if needed

### API Integration

- **Data Source**: ESPN College Football Rankings API
- **Update Frequency**: Rankings update weekly (typically Tuesday)
- **Fallback**: If rankings unavailable, dynamic teams resolve to empty list

### Performance Impact

- **Minimal Overhead**: Only fetches rankings when dynamic teams are used
- **Efficient Caching**: 1-hour cache reduces API calls
- **Background Updates**: Rankings fetched in background, doesn't block display

## Usage Examples

### Example 1: Follow All Top 25 Teams

```json
{
  "ncaa_fb_scoreboard": {
    "enabled": true,
    "show_favorite_teams_only": true,
    "favorite_teams": ["AP_TOP_25"],
    "display_modes": {
      "ncaa_fb_live": true,
      "ncaa_fb_recent": true,
      "ncaa_fb_upcoming": true
    }
  }
}
```

**Result**: Shows all live, recent, and upcoming games for the current AP Top 25 teams.

### Example 2: Follow Your Team + Top 25

```json
{
  "ncaa_fb_scoreboard": {
    "enabled": true,
    "show_favorite_teams_only": true,
    "favorite_teams": [
      "UGA",      // Your favorite team
      "AP_TOP_25" // Plus all top 25 teams
    ]
  }
}
```

**Result**: Shows games for UGA plus all current AP Top 25 teams.

### Example 3: Top 10 Teams Only

```json
{
  "ncaa_fb_scoreboard": {
    "enabled": true,
    "show_favorite_teams_only": true,
    "favorite_teams": ["AP_TOP_10"]
  }
}
```

**Result**: Shows games only for the current AP Top 10 teams.

## Integration with Other Features

### Odds Ticker

The odds ticker automatically respects dynamic team resolution:

```json
{
  "odds_ticker": {
    "enabled": true,
    "enabled_leagues": ["ncaa_fb"],
    "show_favorite_teams_only": true
  },
  "ncaa_fb_scoreboard": {
    "favorite_teams": ["AP_TOP_25"]
  }
}
```

### Leaderboard

The leaderboard will show current AP Top 25 teams when using dynamic teams.

### Background Service

Dynamic teams work seamlessly with the background service for efficient data fetching.

## Troubleshooting

### Common Issues

1. **No Games Showing**
   - Check if `"show_favorite_teams_only": true` is set
   - Verify `"enabled": true` for the sport
   - Check logs for ranking fetch errors

2. **Rankings Not Updating**
   - Rankings update weekly (typically Tuesday)
   - Check ESPN API availability
   - Clear cache if needed

3. **Too Many Games**
   - Use `"AP_TOP_10"` or `"AP_TOP_5"` instead of `"AP_TOP_25"`
   - Adjust `"recent_games_to_show"` and `"upcoming_games_to_show"`

### Debug Information

Check the logs for dynamic team resolution:

```
INFO: Resolved dynamic teams: ['AP_TOP_25'] -> ['UGA', 'MICH', 'OSU', ...]
INFO: Favorite teams: ['UGA', 'MICH', 'OSU', ...]
```

### Cache Management

To force refresh rankings:

```python
from src.dynamic_team_resolver import DynamicTeamResolver
resolver = DynamicTeamResolver()
resolver.clear_cache()
```

## Best Practices

1. **Use Sparingly**: AP_TOP_25 can generate many games - consider AP_TOP_10 or AP_TOP_5
2. **Combine with Regular Teams**: Mix dynamic teams with your specific favorites
3. **Monitor Performance**: Check logs for API call frequency
4. **Seasonal Usage**: Most useful during college football season

## Future Enhancements

Potential future dynamic team types:

- `"PLAYOFF_TEAMS"`: Teams in playoff contention
- `"CONFERENCE_LEADERS"`: Conference leaders
- `"HEISMAN_CANDIDATES"`: Teams with Heisman candidates
- `"RIVALRY_GAMES"`: Traditional rivalry matchups

## API Reference

### DynamicTeamResolver Class

```python
from src.dynamic_team_resolver import DynamicTeamResolver

# Initialize resolver
resolver = DynamicTeamResolver()

# Resolve dynamic teams
teams = resolver.resolve_teams(["UGA", "AP_TOP_25"], 'ncaa_fb')

# Check if team is dynamic
is_dynamic = resolver.is_dynamic_team("AP_TOP_25")

# Get available dynamic teams
available = resolver.get_available_dynamic_teams()

# Clear cache
resolver.clear_cache()
```

### Convenience Function

```python
from src.dynamic_team_resolver import resolve_dynamic_teams

# Simple resolution
teams = resolve_dynamic_teams(["UGA", "AP_TOP_25"], 'ncaa_fb')
```

## Changelog

- **v1.0.0**: Initial implementation of AP Top 25 dynamic teams
- Added support for AP_TOP_25, AP_TOP_10, AP_TOP_5
- Integrated with existing favorite teams system
- Added caching and error handling
- Added comprehensive documentation
