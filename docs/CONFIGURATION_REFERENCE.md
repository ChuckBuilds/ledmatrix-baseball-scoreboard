# Configuration Reference Guide

This guide provides a complete cross-reference between configuration options and their corresponding managers, helping you understand exactly what each setting does and where to find detailed documentation.

## Quick Configuration Lookup

### Core System Settings

| Configuration Section | Manager | Documentation | Purpose |
|----------------------|---------|---------------|---------|
| `clock` | Clock Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-clock-manager) | Time display |
| `display` | Display Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-display-manager) | Hardware control |
| `schedule` | Display Controller | [Web UI Guide](WEB_UI_COMPLETE_GUIDE.md#-schedule-tab) | Display timing |
| `timezone` | System-wide | [Configuration Guide](WIKI_CONFIGURATION.md) | Global timezone |
| `location` | System-wide | [Configuration Guide](WIKI_CONFIGURATION.md) | Geographic location |

### Weather & Environment

| Configuration Section | Manager | Documentation | Purpose |
|----------------------|---------|---------------|---------|
| `weather` | Weather Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-weather-manager) | Weather display |

### Financial Data

| Configuration Section | Manager | Documentation | Purpose |
|----------------------|---------|---------------|---------|
| `stocks` | Stock Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-stock-manager) | Stock ticker |
| `crypto` | Stock Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-stock-manager) | Cryptocurrency |
| `stock_news` | Stock News Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-stock-news-manager) | Financial news |

### Sports Leagues

| Configuration Section | Manager | Documentation | Purpose |
|----------------------|---------|---------------|---------|
| `nhl_scoreboard` | NHL Managers | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-nhl-managers) | NHL games |
| `nba_scoreboard` | NBA Managers | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-nba-managers) | NBA games |
| `mlb` | MLB Managers | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-mlb-managers) | MLB games |
| `nfl_scoreboard` | NFL Managers | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-nfl-managers) | NFL games |
| `soccer_scoreboard` | Soccer Managers | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-soccer-managers) | Soccer matches |
| `ncaa_fb_scoreboard` | NCAA FB Managers | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-ncaa-football-managers) | College football |
| `ncaa_baseball_scoreboard` | NCAA Baseball Managers | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-ncaa-baseball-managers) | College baseball |
| `ncaam_basketball_scoreboard` | NCAA Basketball Managers | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-ncaa-basketball-managers) | College basketball |
| `milb` | MiLB Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-milb-manager) | Minor league baseball |

### Content & Media

| Configuration Section | Manager | Documentation | Purpose |
|----------------------|---------|---------------|---------|
| `music` | Music Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-music-manager) | Music display |
| `youtube` | YouTube Display | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-youtube-display) | YouTube stats |
| `text_display` | Text Display | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-text-display) | Custom messages |
| `calendar` | Calendar Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-calendar-manager) | Calendar events |
| `news_manager` | News Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-news-manager) | RSS news feeds |
| `of_the_day` | Of The Day Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-of-the-day-manager) | Daily content |

### Utilities & Analysis

| Configuration Section | Manager | Documentation | Purpose |
|----------------------|---------|---------------|---------|
| `odds_ticker` | Odds Ticker Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-odds-ticker-manager) | Betting odds |
| `leaderboard` | Leaderboard Manager | [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md#-leaderboard-manager) | League standings |

---

## Configuration by Feature Type

### 🕐 Time & Scheduling

**Clock Display**:
```json
{
  "clock": {
    "enabled": true,
    "format": "%I:%M %p",
    "update_interval": 1
  }
}
```
📖 **Documentation**: [Clock Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-clock-manager)

**Display Schedule**:
```json
{
  "schedule": {
    "enabled": true,
    "start_time": "07:00",
    "end_time": "23:00"
  }
}
```
📖 **Documentation**: [Web UI Schedule Tab](WEB_UI_COMPLETE_GUIDE.md#-schedule-tab)

**Global Timezone**:
```json
{
  "timezone": "America/Chicago"
}
```

### 🖥️ Display Hardware

**Hardware Configuration**:
```json
{
  "display": {
    "hardware": {
      "rows": 32,
      "cols": 64,
      "chain_length": 2,
      "brightness": 95,
      "hardware_mapping": "adafruit-hat-pwm"
    },
    "runtime": {
      "gpio_slowdown": 3
    },
    "display_durations": {
      "clock": 15,
      "weather": 30,
      "stocks": 30
    }
  }
}
```
📖 **Documentation**: [Display Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-display-manager)

### 🌤️ Weather & Location

**Weather Display**:
```json
{
  "weather": {
    "enabled": true,
    "api_key": "your_openweathermap_api_key",
    "update_interval": 1800,
    "units": "imperial",
    "show_feels_like": true,
    "show_humidity": true,
    "show_wind": true,
    "show_uv_index": true
  }
}
```
📖 **Documentation**: [Weather Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-weather-manager)

**Location Settings**:
```json
{
  "location": {
    "city": "Dallas",
    "state": "Texas",
    "country": "US"
  }
}
```

### 💰 Financial Data

**Stock Ticker**:
```json
{
  "stocks": {
    "enabled": true,
    "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA"],
    "update_interval": 600,
    "scroll_speed": 1,
    "dynamic_duration": true
  }
}
```
📖 **Documentation**: [Stock Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-stock-manager)

**Cryptocurrency**:
```json
{
  "crypto": {
    "enabled": true,
    "symbols": ["BTC-USD", "ETH-USD", "ADA-USD"],
    "update_interval": 300
  }
}
```
📖 **Documentation**: [Stock Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-stock-manager)

**Financial News**:
```json
{
  "stock_news": {
    "enabled": true,
    "scroll_speed": 1,
    "max_headlines_per_symbol": 1,
    "dynamic_duration": true
  }
}
```
📖 **Documentation**: [Stock News Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-stock-news-manager)

### 🏈 Sports Configuration

**NHL Hockey**:
```json
{
  "nhl_scoreboard": {
    "enabled": true,
    "favorite_teams": ["TB", "FLA"],
    "show_odds": true,
    "show_records": true,
    "live_priority": true,
    "live_update_interval": 60
  }
}
```
📖 **Documentation**: [NHL Managers](MANAGER_GUIDE_COMPREHENSIVE.md#-nhl-managers)

**NBA Basketball**:
```json
{
  "nba_scoreboard": {
    "enabled": true,
    "favorite_teams": ["MIA", "LAL"],
    "show_odds": true,
    "show_records": true,
    "live_priority": true
  }
}
```
📖 **Documentation**: [NBA Managers](MANAGER_GUIDE_COMPREHENSIVE.md#-nba-managers)

**MLB Baseball**:
```json
{
  "mlb": {
    "enabled": true,
    "favorite_teams": ["TB", "NYY"],
    "show_odds": true,
    "live_priority": true
  }
}
```
📖 **Documentation**: [MLB Managers](MANAGER_GUIDE_COMPREHENSIVE.md#-mlb-managers)

**NFL Football**:
```json
{
  "nfl_scoreboard": {
    "enabled": true,
    "favorite_teams": ["TB", "MIA"],
    "show_odds": true,
    "show_records": true,
    "live_priority": true
  }
}
```
📖 **Documentation**: [NFL Managers](MANAGER_GUIDE_COMPREHENSIVE.md#-nfl-managers)

**Soccer**:
```json
{
  "soccer_scoreboard": {
    "enabled": true,
    "favorite_teams": ["Real Madrid", "Barcelona"],
    "target_leagues": ["uefa.champions", "eng.1", "esp.1"],
    "show_odds": true,
    "live_priority": true
  }
}
```
📖 **Documentation**: [Soccer Managers](MANAGER_GUIDE_COMPREHENSIVE.md#-soccer-managers)

### 🎵 Music & Entertainment

**Music Display**:
```json
{
  "music": {
    "enabled": true,
    "preferred_source": "spotify",
    "POLLING_INTERVAL_SECONDS": 2,
    "spotify": {
      "client_id": "your_spotify_client_id",
      "client_secret": "your_spotify_client_secret"
    }
  }
}
```
📖 **Documentation**: [Music Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-music-manager)

**YouTube Stats**:
```json
{
  "youtube": {
    "enabled": true,
    "api_key": "your_youtube_api_key",
    "channels": [
      {
        "name": "Channel Name",
        "channel_id": "UCxxxxxxxxxx",
        "display_name": "Custom Name"
      }
    ]
  }
}
```
📖 **Documentation**: [YouTube Display](MANAGER_GUIDE_COMPREHENSIVE.md#-youtube-display)

### 📰 News & Information

**News Manager**:
```json
{
  "news_manager": {
    "enabled": true,
    "enabled_feeds": ["NFL", "NBA", "TOP SPORTS"],
    "custom_feeds": {
      "TECH NEWS": "https://feeds.feedburner.com/TechCrunch"
    },
    "headlines_per_feed": 2,
    "scroll_speed": 2,
    "dynamic_duration": true
  }
}
```
📖 **Documentation**: [News Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-news-manager)

**Text Display**:
```json
{
  "text_display": {
    "enabled": true,
    "messages": ["Welcome to LEDMatrix!", "Custom message"],
    "scroll_speed": 2,
    "text_color": [255, 255, 255]
  }
}
```
📖 **Documentation**: [Text Display](MANAGER_GUIDE_COMPREHENSIVE.md#-text-display)

**Calendar Events**:
```json
{
  "calendar": {
    "enabled": true,
    "calendars": ["primary", "birthdays"],
    "max_events": 3,
    "update_interval": 300
  }
}
```
📖 **Documentation**: [Calendar Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-calendar-manager)

### 🎯 Utilities & Analysis

**Odds Ticker**:
```json
{
  "odds_ticker": {
    "enabled": true,
    "enabled_leagues": ["nfl", "nba", "mlb"],
    "show_favorite_teams_only": false,
    "scroll_speed": 2,
    "dynamic_duration": true
  }
}
```
📖 **Documentation**: [Odds Ticker Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-odds-ticker-manager)

**Leaderboards**:
```json
{
  "leaderboard": {
    "enabled": true,
    "enabled_sports": {
      "nfl": {
        "enabled": true,
        "top_teams": 10
      }
    },
    "scroll_speed": 1,
    "dynamic_duration": true
  }
}
```
📖 **Documentation**: [Leaderboard Manager](MANAGER_GUIDE_COMPREHENSIVE.md#-leaderboard-manager)

---

## Web Interface Configuration

The web interface provides GUI controls for all configuration options:

| Configuration Area | Web UI Tab | Documentation |
|-------------------|------------|---------------|
| System monitoring | Overview | [Web UI Overview](WEB_UI_COMPLETE_GUIDE.md#-overview-tab) |
| Display timing | Schedule | [Web UI Schedule](WEB_UI_COMPLETE_GUIDE.md#-schedule-tab) |
| Hardware settings | Display | [Web UI Display](WEB_UI_COMPLETE_GUIDE.md#-display-tab) |
| Sports leagues | Sports | [Web UI Sports](WEB_UI_COMPLETE_GUIDE.md#-sports-tab) |
| Weather service | Weather | [Web UI Weather](WEB_UI_COMPLETE_GUIDE.md#-weather-tab) |
| Financial data | Stocks | [Web UI Stocks](WEB_UI_COMPLETE_GUIDE.md#-stocks-tab) |
| Additional features | Features | [Web UI Features](WEB_UI_COMPLETE_GUIDE.md#-features-tab) |
| Music integration | Music | [Web UI Music](WEB_UI_COMPLETE_GUIDE.md#-music-tab) |
| Calendar events | Calendar | [Web UI Calendar](WEB_UI_COMPLETE_GUIDE.md#-calendar-tab) |
| News feeds | News | [Web UI News](WEB_UI_COMPLETE_GUIDE.md#-news-tab) |
| API keys | API Keys | [Web UI API Keys](WEB_UI_COMPLETE_GUIDE.md#-api-keys-tab) |
| Direct JSON editing | Raw JSON | [Web UI Raw JSON](WEB_UI_COMPLETE_GUIDE.md#-raw-json-tab) |

---

## Configuration File Locations

### Main Configuration
- **File**: `config/config.json`
- **Purpose**: All non-sensitive settings
- **Documentation**: [Configuration Guide](WIKI_CONFIGURATION.md)

### Secrets Configuration
- **File**: `config/config_secrets.json`
- **Purpose**: API keys and sensitive credentials
- **Documentation**: [Configuration Guide](WIKI_CONFIGURATION.md)

### Template Files
- **Main Template**: `config/config.template.json`
- **Secrets Template**: `config/config_secrets.template.json`
- **Purpose**: Default configuration examples

---

## Common Configuration Patterns

### Enable/Disable Pattern
Most managers use this pattern:
```json
{
  "manager_name": {
    "enabled": true,
    "other_options": "..."
  }
}
```

### Update Interval Pattern
Data-fetching managers use:
```json
{
  "manager_name": {
    "update_interval": 600,
    "live_update_interval": 60
  }
}
```

### Scrolling Display Pattern
Text-based displays use:
```json
{
  "manager_name": {
    "scroll_speed": 2,
    "scroll_delay": 0.02,
    "dynamic_duration": true
  }
}
```

### Favorite Teams Pattern
Sports managers use:
```json
{
  "sport_scoreboard": {
    "favorite_teams": ["TEAM1", "TEAM2"],
    "live_priority": true
  }
}
```

---

## Configuration Validation

### JSON Validation
- Use the [Raw JSON Tab](WEB_UI_COMPLETE_GUIDE.md#-raw-json-tab) for real-time validation
- Check syntax highlighting and error indicators
- Use the Format button for proper indentation

### Manager-Specific Validation
- Each manager validates its own configuration section
- Invalid configurations are logged with detailed error messages
- Fallback to default values when possible

### Web Interface Validation
- Client-side validation in web forms
- Server-side validation on submission
- Real-time feedback and error messages

---

## Troubleshooting Configuration

### Common Issues
1. **JSON Syntax Errors**: Use Raw JSON tab for validation
2. **Missing API Keys**: Check API Keys tab and secrets file
3. **Invalid Team Names**: Refer to [Team Abbreviations Guide](TEAM_ABBREVIATIONS_AND_LEAGUE_SLUGS.md)
4. **Permission Errors**: Run permission fix scripts
5. **Service Not Starting**: Check configuration syntax and required fields

### Debug Tools
- **Web UI Logs Tab**: View real-time logs
- **Raw JSON Tab**: Validate configuration syntax
- **System Actions**: Restart services with new configuration
- **Cache Management**: Clear cache when configuration changes

### Getting Help
- **Troubleshooting Guide**: [General Troubleshooting](WIKI_TROUBLESHOOTING.md)
- **Configuration Examples**: [Configuration Guide](WIKI_CONFIGURATION.md)
- **Manager Documentation**: [Complete Manager Guide](MANAGER_GUIDE_COMPREHENSIVE.md)
- **Web Interface Help**: [Complete Web UI Guide](WEB_UI_COMPLETE_GUIDE.md)

---

This reference guide connects every configuration option to its corresponding manager and documentation, making it easy to understand and configure your LEDMatrix system.
