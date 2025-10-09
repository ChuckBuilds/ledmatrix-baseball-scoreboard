# Complete Manager Guide

This comprehensive guide covers every display manager in the LEDMatrix system, their configuration options, features, and how they work.

## Overview

The LEDMatrix system uses a modular architecture where each feature is implemented as a separate "Display Manager". Each manager handles a specific type of content and can be independently enabled, configured, and customized.

### Manager Types

1. **Core Display Managers** - Essential system components
2. **Sports Managers** - All sports leagues and displays
3. **Financial Managers** - Stocks, crypto, and financial news
4. **Content Managers** - News, text, multimedia content
5. **Utility Managers** - System utilities and special functions

---

## Core Display Managers

### 🕐 Clock Manager (`src/clock.py`)

**Purpose**: Displays current time with various formatting options.

**Configuration Section**: `clock`

```json
{
  "clock": {
    "enabled": true,
    "format": "%I:%M %p",
    "update_interval": 1,
    "timezone": "America/Chicago"
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable/disable clock display
- **`format`** (string): Time format using Python strftime codes
  - `"%I:%M %p"` - 12-hour format with AM/PM (default)
  - `"%H:%M"` - 24-hour format
  - `"%I:%M:%S %p"` - Include seconds
- **`update_interval`** (integer): Update frequency in seconds
- **`timezone`** (string): Timezone for display (uses system timezone if not specified)

**Features**:
- Real-time clock display
- Automatic timezone handling
- Configurable time formats
- Minimal resource usage
- Always-on display capability

**Display Examples**:
- `12:34 PM` (12-hour format)
- `14:34` (24-hour format)
- `12:34:56 PM` (with seconds)

---

### 🌤️ Weather Manager (`src/weather_manager.py`)

**Purpose**: Displays current weather conditions, hourly forecasts, and daily forecasts using OpenWeatherMap API.

**Configuration Section**: `weather`

```json
{
  "weather": {
    "enabled": true,
    "api_key": "your_openweathermap_api_key",
    "update_interval": 1800,
    "units": "imperial",
    "display_format": "{temp}°F\\n{condition}",
    "show_feels_like": true,
    "show_humidity": true,
    "show_wind": true,
    "show_uv_index": true,
    "icon_set": "animated"
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable/disable weather display
- **`api_key`** (string): OpenWeatherMap API key (required)
- **`update_interval`** (integer): Update frequency in seconds (default: 1800)
- **`units`** (string): Temperature units
  - `"imperial"` - Fahrenheit (default)
  - `"metric"` - Celsius
  - `"kelvin"` - Kelvin
- **`display_format`** (string): Custom display format template
- **`show_feels_like`** (boolean): Display "feels like" temperature
- **`show_humidity`** (boolean): Display humidity percentage
- **`show_wind`** (boolean): Display wind speed and direction
- **`show_uv_index`** (boolean): Display UV index with color coding
- **`icon_set`** (string): Weather icon style
  - `"animated"` - Animated weather icons
  - `"static"` - Static weather icons

**Features**:
- Current weather conditions with animated icons
- Hourly forecast for next 24 hours
- Daily forecast for next 7 days
- UV index display with color coding
- Wind speed and direction
- Humidity and pressure data
- Automatic error recovery and caching
- Multiple display modes (current/hourly/daily)

**Display Modes**:
1. **Current Weather**: Temperature, condition, icon
2. **Hourly Forecast**: Temperature trend with time markers
3. **Daily Forecast**: High/low temperatures with day labels

**API Requirements**:
- OpenWeatherMap API key (free tier available)
- Internet connection for data updates
- Location configured in main config

---

### 🎯 Display Manager (`src/display_manager.py`)

**Purpose**: Low-level hardware interface and graphics rendering engine.

**Configuration Section**: `display`

```json
{
  "display": {
    "hardware": {
      "rows": 32,
      "cols": 64,
      "chain_length": 2,
      "parallel": 1,
      "brightness": 95,
      "hardware_mapping": "adafruit-hat-pwm",
      "scan_mode": 0,
      "pwm_bits": 9,
      "pwm_dither_bits": 1,
      "pwm_lsb_nanoseconds": 130,
      "disable_hardware_pulsing": false,
      "inverse_colors": false,
      "show_refresh_rate": false,
      "limit_refresh_rate_hz": 120
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

**Hardware Configuration Options**:
- **`rows`** (integer): LED matrix height in pixels (32 for 32x64 panels)
- **`cols`** (integer): LED matrix width in pixels (64 for 32x64 panels)
- **`chain_length`** (integer): Number of panels chained together (2 for 128x32 total)
- **`parallel`** (integer): Number of parallel chains (usually 1)
- **`brightness`** (integer): Display brightness (0-100)
- **`hardware_mapping`** (string): HAT/Bonnet configuration
  - `"adafruit-hat-pwm"` - With jumper mod (recommended)
  - `"adafruit-hat"` - Without jumper mod
  - `"regular"` - Direct GPIO connection
- **`scan_mode`** (integer): Panel scan mode (0 for most panels)
- **`pwm_bits`** (integer): Color depth (8-11, higher = better colors, slower)
- **`pwm_dither_bits`** (integer): Dithering bits for smoother gradients
- **`pwm_lsb_nanoseconds`** (integer): PWM timing adjustment
- **`disable_hardware_pulsing`** (boolean): Disable hardware PWM
- **`inverse_colors`** (boolean): Invert all colors
- **`show_refresh_rate`** (boolean): Display refresh rate on screen
- **`limit_refresh_rate_hz`** (integer): Maximum refresh rate

**Runtime Configuration Options**:
- **`gpio_slowdown`** (integer): GPIO timing adjustment
  - `2-3` for Raspberry Pi 3
  - `4` for Raspberry Pi 4
  - `5` for faster Pi models

**Display Duration Options**:
- Configure how long each display mode shows before rotating
- All durations in seconds
- Can be overridden by dynamic duration system

**Features**:
- Hardware RGB LED matrix initialization
- Font loading and management
- Drawing primitives (text, shapes, images)
- Color management and gamma correction
- Performance optimization
- Error recovery and fallback modes

---

## Sports Managers

### 🏒 NHL Managers (`src/nhl_managers.py`)

**Purpose**: Display NHL games, scores, and standings.

**Configuration Section**: `nhl_scoreboard`

```json
{
  "nhl_scoreboard": {
    "enabled": true,
    "favorite_teams": ["TB", "FLA"],
    "show_odds": true,
    "show_records": true,
    "test_mode": false,
    "logo_dir": "assets/sports/nhl_logos",
    "update_interval_seconds": 60,
    "live_update_interval": 60,
    "recent_game_hours": 48,
    "live_priority": true
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable NHL display
- **`favorite_teams`** (array): List of favorite team abbreviations
- **`show_odds`** (boolean): Display betting odds for games
- **`show_records`** (boolean): Show team win-loss records
- **`test_mode`** (boolean): Use test data instead of live API
- **`logo_dir`** (string): Directory for team logos
- **`update_interval_seconds`** (integer): General update frequency
- **`live_update_interval`** (integer): Live game update frequency
- **`recent_game_hours`** (integer): Hours to consider games "recent"
- **`live_priority`** (boolean): Prioritize live games in rotation

**Manager Types**:
1. **NHLLiveManager**: Live games in progress
2. **NHLRecentManager**: Recently completed games
3. **NHLUpcomingManager**: Future scheduled games

**Features**:
- Live game scores with period information
- Team logos and colors
- Betting odds integration
- Win-loss records
- Game status (Pre-game, Live, Final)
- Automatic live game detection and prioritization

**Team Abbreviations**: Standard NHL team codes (TB, NYR, BOS, etc.)

---

### 🏀 NBA Managers (`src/nba_managers.py`)

**Purpose**: Display NBA games, scores, and standings.

**Configuration Section**: `nba_scoreboard`

```json
{
  "nba_scoreboard": {
    "enabled": true,
    "favorite_teams": ["MIA", "LAL"],
    "show_odds": true,
    "show_records": true,
    "test_mode": false,
    "logo_dir": "assets/sports/nba_logos",
    "update_interval_seconds": 300,
    "live_update_interval": 60,
    "live_priority": true
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable NBA display
- **`favorite_teams`** (array): List of favorite team abbreviations
- **`show_odds`** (boolean): Display betting odds
- **`show_records`** (boolean): Show team records
- **`test_mode`** (boolean): Use test data
- **`logo_dir`** (string): Team logos directory
- **`update_interval_seconds`** (integer): Update frequency
- **`live_update_interval`** (integer): Live game updates
- **`live_priority`** (boolean): Prioritize live games

**Manager Types**:
1. **NBALiveManager**: Live games
2. **NBARecentManager**: Recent games
3. **NBAUpcomingManager**: Upcoming games

**Features**:
- Live scores with quarter information
- Team logos and records
- Betting odds
- Game status tracking
- Playoff indicators

---

### ⚾ MLB Managers (`src/mlb_manager.py`)

**Purpose**: Display MLB games, scores, and standings.

**Configuration Section**: `mlb`

```json
{
  "mlb": {
    "enabled": true,
    "favorite_teams": ["TB", "NYY"],
    "show_odds": true,
    "show_records": false,
    "test_mode": false,
    "logo_dir": "assets/sports/mlb_logos",
    "update_interval_seconds": 300,
    "live_update_interval": 60,
    "live_priority": true
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable MLB display
- **`favorite_teams`** (array): Team abbreviations
- **`show_odds`** (boolean): Display betting odds
- **`show_records`** (boolean): Show team records
- **`test_mode`** (boolean): Test mode
- **`logo_dir`** (string): Logo directory
- **`update_interval_seconds`** (integer): Update frequency
- **`live_update_interval`** (integer): Live updates
- **`live_priority`** (boolean): Prioritize live games

**Manager Types**:
1. **MLBLiveManager**: Live games
2. **MLBRecentManager**: Recent games  
3. **MLBUpcomingManager**: Upcoming games

**Features**:
- Live scores with inning information
- Pitcher information
- Base runners display
- Team logos and standings

---

### 🏈 NFL Managers (`src/nfl_managers.py`)

**Purpose**: Display NFL games, scores, and standings.

**Configuration Section**: `nfl_scoreboard`

```json
{
  "nfl_scoreboard": {
    "enabled": true,
    "favorite_teams": ["TB", "MIA"],
    "show_odds": true,
    "show_records": true,
    "test_mode": false,
    "logo_dir": "assets/sports/nfl_logos",
    "update_interval_seconds": 300,
    "live_update_interval": 60,
    "live_priority": true
  }
}
```

**Features**:
- Live scores with down and distance
- Quarter information
- Team records and standings
- Playoff implications

---

### ⚽ Soccer Managers (`src/soccer_managers.py`)

**Purpose**: Display soccer matches from multiple leagues.

**Configuration Section**: `soccer_scoreboard`

```json
{
  "soccer_scoreboard": {
    "enabled": true,
    "favorite_teams": ["Real Madrid", "Barcelona"],
    "show_odds": true,
    "show_records": false,
    "test_mode": false,
    "logo_dir": "assets/sports/soccer_logos",
    "update_interval_seconds": 60,
    "live_update_interval": 60,
    "target_leagues": ["uefa.champions", "eng.1", "esp.1"],
    "live_priority": true
  }
}
```

**Configuration Options**:
- **`target_leagues`** (array): League identifiers to display
  - `"uefa.champions"` - UEFA Champions League
  - `"eng.1"` - English Premier League
  - `"esp.1"` - Spanish La Liga
  - `"ger.1"` - German Bundesliga
  - `"ita.1"` - Italian Serie A
  - `"fra.1"` - French Ligue 1

**Features**:
- Live match scores
- Multiple league support
- Team logos and colors
- Match status and time

---

### 🏈 NCAA Football Managers (`src/ncaa_fb_managers.py`)

**Purpose**: Display college football games and scores.

**Configuration Section**: `ncaa_fb_scoreboard`

```json
{
  "ncaa_fb_scoreboard": {
    "enabled": true,
    "favorite_teams": ["Florida", "Georgia"],
    "show_odds": true,
    "show_records": true,
    "test_mode": false,
    "logo_dir": "assets/sports/ncaa_fbs_logos",
    "update_interval_seconds": 300,
    "live_update_interval": 60,
    "live_priority": true
  }
}
```

**Features**:
- College football scores
- Conference standings
- Playoff rankings
- Bowl game information

---

### ⚾ NCAA Baseball Managers (`src/ncaa_baseball_managers.py`)

**Purpose**: Display college baseball games and tournaments.

**Configuration Section**: `ncaa_baseball_scoreboard`

```json
{
  "ncaa_baseball_scoreboard": {
    "enabled": true,
    "favorite_teams": ["Florida", "Vanderbilt"],
    "show_odds": false,
    "show_records": true,
    "test_mode": false,
    "logo_dir": "assets/sports/ncaa_baseball_logos",
    "update_interval_seconds": 300,
    "live_update_interval": 60,
    "live_priority": true
  }
}
```

**Features**:
- College baseball scores
- Tournament brackets
- Conference standings
- Regional and super regional games

---

### 🏀 NCAA Basketball Managers (`src/ncaam_basketball_managers.py`)

**Purpose**: Display college basketball games and March Madness.

**Configuration Section**: `ncaam_basketball_scoreboard`

```json
{
  "ncaam_basketball_scoreboard": {
    "enabled": true,
    "favorite_teams": ["Duke", "North Carolina"],
    "show_odds": true,
    "show_records": true,
    "test_mode": false,
    "logo_dir": "assets/sports/ncaa_basketball_logos",
    "update_interval_seconds": 300,
    "live_update_interval": 60,
    "live_priority": true
  }
}
```

**Features**:
- College basketball scores
- March Madness bracket
- Conference tournaments
- AP and Coaches poll rankings

---

### ⚾ MiLB Manager (`src/milb_manager.py`)

**Purpose**: Display Minor League Baseball games.

**Configuration Section**: `milb`

```json
{
  "milb": {
    "enabled": true,
    "favorite_teams": ["Durham Bulls", "Norfolk Tides"],
    "show_odds": false,
    "show_records": false,
    "test_mode": false,
    "logo_dir": "assets/sports/milb_logos",
    "update_interval_seconds": 300,
    "live_update_interval": 60,
    "live_priority": true
  }
}
```

**Features**:
- Minor league scores
- Multiple league levels (AAA, AA, A+, A, etc.)
- Team affiliations
- Playoff information

---

## Financial Managers

### 💰 Stock Manager (`src/stock_manager.py`)

**Purpose**: Display stock prices, crypto prices, and financial market data.

**Configuration Section**: `stocks` and `crypto`

```json
{
  "stocks": {
    "enabled": true,
    "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
    "update_interval": 600,
    "scroll_speed": 1,
    "scroll_delay": 0.01,
    "toggle_chart": false,
    "dynamic_duration": true,
    "min_duration": 30,
    "max_duration": 300,
    "duration_buffer": 0.1
  },
  "crypto": {
    "enabled": true,
    "symbols": ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD"],
    "update_interval": 300
  }
}
```

**Stock Configuration Options**:
- **`enabled`** (boolean): Enable stock display
- **`symbols`** (array): Stock ticker symbols to display
- **`update_interval`** (integer): Update frequency in seconds
- **`scroll_speed`** (integer): Scrolling speed (1-5)
- **`scroll_delay`** (float): Delay between scroll steps
- **`toggle_chart`** (boolean): Show mini price charts
- **`dynamic_duration`** (boolean): Adjust display time based on content
- **`min_duration`** (integer): Minimum display duration
- **`max_duration`** (integer): Maximum display duration
- **`duration_buffer`** (float): Buffer time for scrolling completion

**Crypto Configuration Options**:
- **`enabled`** (boolean): Enable crypto display
- **`symbols`** (array): Cryptocurrency symbols (format: SYMBOL-USD)
- **`update_interval`** (integer): Update frequency

**Features**:
- Real-time stock prices
- Cryptocurrency prices
- Price change indicators (green/red)
- Percentage change display
- Optional mini price charts
- Company/crypto logos
- Market hours awareness
- Pre-market and after-hours data
- Scrolling ticker format

**Supported Assets**:
- **Stocks**: Any symbol on major exchanges (NYSE, NASDAQ)
- **Crypto**: Major cryptocurrencies (BTC, ETH, ADA, SOL, etc.)
- **ETFs**: Exchange-traded funds
- **Indices**: Market indices (SPY, QQQ, etc.)

---

### 📰 Stock News Manager (`src/stock_news_manager.py`)

**Purpose**: Display financial news headlines related to your stock portfolio.

**Configuration Section**: `stock_news`

```json
{
  "stock_news": {
    "enabled": true,
    "update_interval": 3600,
    "scroll_speed": 1,
    "scroll_delay": 0.005,
    "max_headlines_per_symbol": 1,
    "headlines_per_rotation": 3,
    "dynamic_duration": true,
    "min_duration": 30,
    "max_duration": 180,
    "duration_buffer": 0.1
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable stock news display
- **`update_interval`** (integer): News update frequency
- **`scroll_speed`** (integer): Text scrolling speed
- **`scroll_delay`** (float): Scroll step delay
- **`max_headlines_per_symbol`** (integer): Headlines per stock
- **`headlines_per_rotation`** (integer): Headlines shown per cycle
- **`dynamic_duration`** (boolean): Auto-adjust display duration
- **`min_duration`** (integer): Minimum display time
- **`max_duration`** (integer): Maximum display time
- **`duration_buffer`** (float): Buffer for scroll completion

**Features**:
- Financial news headlines
- Stock-specific news filtering
- Scrolling news ticker
- Dynamic duration based on content length
- News source attribution
- Automatic headline rotation

---

## Content Managers

### 📺 YouTube Display (`src/youtube_display.py`)

**Purpose**: Display YouTube channel statistics and subscriber counts.

**Configuration Section**: `youtube`

```json
{
  "youtube": {
    "enabled": true,
    "api_key": "your_youtube_api_key",
    "channels": [
      {
        "name": "Channel Name",
        "channel_id": "UCxxxxxxxxxxxxxxxxxx",
        "display_name": "Custom Display Name"
      }
    ],
    "update_interval": 3600,
    "show_subscriber_count": true,
    "show_video_count": true,
    "show_view_count": true
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable YouTube display
- **`api_key`** (string): YouTube Data API v3 key
- **`channels`** (array): Channel configuration objects
- **`update_interval`** (integer): Update frequency
- **`show_subscriber_count`** (boolean): Display subscriber count
- **`show_video_count`** (boolean): Display total videos
- **`show_view_count`** (boolean): Display total views

**Channel Object Options**:
- **`name`** (string): Channel identifier
- **`channel_id`** (string): YouTube channel ID
- **`display_name`** (string): Custom name for display

**Features**:
- YouTube channel statistics
- Subscriber count tracking
- Video count display
- Total view count
- Custom channel names
- YouTube logo integration

---

### 📝 Text Display (`src/text_display.py`)

**Purpose**: Display custom text messages and announcements.

**Configuration Section**: `text_display`

```json
{
  "text_display": {
    "enabled": true,
    "messages": [
      "Welcome to LEDMatrix!",
      "Custom message here",
      "Another announcement"
    ],
    "scroll_speed": 2,
    "scroll_delay": 0.02,
    "text_color": [255, 255, 255],
    "background_color": [0, 0, 0],
    "font_size": "medium",
    "rotation_interval": 10
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable text display
- **`messages`** (array): List of text messages to display
- **`scroll_speed`** (integer): Text scrolling speed
- **`scroll_delay`** (float): Delay between scroll steps
- **`text_color`** (array): RGB color for text [R, G, B]
- **`background_color`** (array): RGB background color
- **`font_size`** (string): Font size ("small", "medium", "large")
- **`rotation_interval`** (integer): Seconds between message rotation

**Features**:
- Custom text messages
- Scrolling text display
- Configurable colors and fonts
- Message rotation
- Multi-line text support

---

### 🎵 Music Manager (`src/music_manager.py`)

**Purpose**: Display currently playing music from Spotify or YouTube Music.

**Configuration Section**: `music`

```json
{
  "music": {
    "enabled": true,
    "preferred_source": "spotify",
    "POLLING_INTERVAL_SECONDS": 2,
    "spotify": {
      "client_id": "your_spotify_client_id",
      "client_secret": "your_spotify_client_secret",
      "redirect_uri": "http://localhost:8888/callback"
    },
    "ytm": {
      "enabled": true
    }
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable music display
- **`preferred_source`** (string): Primary music source
  - `"spotify"` - Spotify (default)
  - `"ytm"` - YouTube Music
- **`POLLING_INTERVAL_SECONDS`** (integer): Update frequency
- **`spotify`** (object): Spotify API configuration
- **`ytm`** (object): YouTube Music configuration

**Spotify Configuration**:
- **`client_id`** (string): Spotify app client ID
- **`client_secret`** (string): Spotify app client secret
- **`redirect_uri`** (string): OAuth redirect URI

**Features**:
- Currently playing track info
- Artist and album display
- Album artwork
- Progress bar
- Play/pause status
- Spotify and YouTube Music support
- Automatic source switching

---

### 📅 Calendar Manager (`src/calendar_manager.py`)

**Purpose**: Display upcoming calendar events from Google Calendar.

**Configuration Section**: `calendar`

```json
{
  "calendar": {
    "enabled": true,
    "credentials_file": "credentials.json",
    "token_file": "token.pickle",
    "calendars": ["primary", "birthdays"],
    "max_events": 3,
    "update_interval": 300,
    "timezone": "America/Chicago"
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable calendar display
- **`credentials_file`** (string): Google API credentials file
- **`token_file`** (string): OAuth token storage file
- **`calendars`** (array): Calendar names to display
- **`max_events`** (integer): Maximum events to show
- **`update_interval`** (integer): Update frequency
- **`timezone`** (string): Timezone for event display

**Features**:
- Upcoming calendar events
- Multiple calendar support
- Event times and dates
- All-day event handling
- Timezone conversion
- Google Calendar integration

---

### 📰 News Manager (`src/news_manager.py`)

**Purpose**: Display scrolling news headlines from RSS feeds.

**Configuration Section**: `news_manager`

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
    "scroll_delay": 0.01,
    "update_interval": 300,
    "rotation_enabled": true,
    "rotation_threshold": 3,
    "dynamic_duration": true,
    "min_duration": 30,
    "max_duration": 300,
    "font_size": 12,
    "text_color": [255, 255, 255],
    "separator_color": [255, 0, 0]
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable news display
- **`enabled_feeds`** (array): Default feeds to enable
- **`custom_feeds`** (object): Custom RSS feed URLs
- **`headlines_per_feed`** (integer): Headlines per feed
- **`scroll_speed`** (integer): Text scrolling speed
- **`scroll_delay`** (float): Scroll step delay
- **`update_interval`** (integer): News update frequency
- **`rotation_enabled`** (boolean): Enable headline rotation
- **`rotation_threshold`** (integer): Cycles before rotation
- **`dynamic_duration`** (boolean): Auto-adjust duration
- **`min_duration`** (integer): Minimum display time
- **`max_duration`** (integer): Maximum display time
- **`font_size`** (integer): Text font size
- **`text_color`** (array): RGB text color
- **`separator_color`** (array): RGB separator color

**Default RSS Feeds**:
- **MLB**: ESPN MLB News
- **NFL**: ESPN NFL News
- **NCAA FB**: ESPN College Football
- **NHL**: ESPN NHL News
- **NBA**: ESPN NBA News
- **TOP SPORTS**: ESPN Top Sports
- **BIG10**: ESPN Big Ten Blog
- **NCAA**: ESPN NCAA News

**Features**:
- RSS feed parsing
- Custom feed support
- Scrolling news ticker
- Headline rotation
- Dynamic duration adjustment
- Multiple news sources
- Color-coded separators

---

### 🌟 "Of The Day" Manager (`src/of_the_day_manager.py`)

**Purpose**: Display daily content like word of the day, bible verse, etc.

**Configuration Section**: `of_the_day`

```json
{
  "of_the_day": {
    "enabled": true,
    "sources": ["word_of_the_day", "bible_verse", "slovenian_word"],
    "update_interval": 3600,
    "scroll_speed": 1,
    "scroll_delay": 0.02,
    "rotation_enabled": true
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable "of the day" display
- **`sources`** (array): Content sources to enable
- **`update_interval`** (integer): Update frequency
- **`scroll_speed`** (integer): Text scrolling speed
- **`scroll_delay`** (float): Scroll step delay
- **`rotation_enabled`** (boolean): Rotate between sources

**Available Sources**:
- **`word_of_the_day`** - English word with definition
- **`bible_verse`** - Daily bible verse
- **`slovenian_word`** - Slovenian word of the day

**Features**:
- Daily content rotation
- Multiple content sources
- Scrolling text display
- Automatic daily updates

---

## Utility Managers

### 🎯 Odds Ticker Manager (`src/odds_ticker_manager.py`)

**Purpose**: Display scrolling sports betting odds for multiple leagues.

**Configuration Section**: `odds_ticker`

```json
{
  "odds_ticker": {
    "enabled": true,
    "enabled_leagues": ["nfl", "nba", "mlb", "nhl"],
    "show_favorite_teams_only": false,
    "games_per_favorite_team": 1,
    "max_games_per_league": 5,
    "show_odds_only": false,
    "fetch_odds": true,
    "sort_order": "soonest",
    "update_interval": 3600,
    "scroll_speed": 2,
    "scroll_delay": 0.05,
    "display_duration": 30,
    "future_fetch_days": 7,
    "loop": true,
    "show_channel_logos": true,
    "broadcast_logo_height_ratio": 0.8,
    "broadcast_logo_max_width_ratio": 0.8,
    "request_timeout": 30,
    "dynamic_duration": true,
    "min_duration": 30,
    "max_duration": 180
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable odds ticker
- **`enabled_leagues`** (array): Sports leagues to include
- **`show_favorite_teams_only`** (boolean): Only show favorite teams
- **`games_per_favorite_team`** (integer): Games per favorite team
- **`max_games_per_league`** (integer): Maximum games per league
- **`show_odds_only`** (boolean): Show only odds (no scores)
- **`fetch_odds`** (boolean): Fetch betting odds data
- **`sort_order`** (string): Game sorting order
  - `"soonest"` - Earliest games first
  - `"latest"` - Latest games first
- **`update_interval`** (integer): Update frequency
- **`scroll_speed`** (integer): Scrolling speed
- **`scroll_delay`** (float): Scroll step delay
- **`display_duration`** (integer): Display time per cycle
- **`future_fetch_days`** (integer): Days ahead to fetch
- **`loop`** (boolean): Loop ticker continuously
- **`show_channel_logos`** (boolean): Show broadcast logos
- **`broadcast_logo_height_ratio`** (float): Logo height ratio
- **`broadcast_logo_max_width_ratio`** (float): Logo width ratio
- **`request_timeout`** (integer): API request timeout
- **`dynamic_duration`** (boolean): Auto-adjust duration
- **`min_duration`** (integer): Minimum display time
- **`max_duration`** (integer): Maximum display time

**Features**:
- Multi-league odds display
- Betting lines and spreads
- Broadcast channel information
- Team logos and colors
- Scrolling ticker format
- Dynamic content duration
- Favorite team filtering

---

### 🏆 Leaderboard Manager (`src/leaderboard_manager.py`)

**Purpose**: Display league standings and leaderboards for multiple sports.

**Configuration Section**: `leaderboard`

```json
{
  "leaderboard": {
    "enabled": true,
    "enabled_sports": {
      "nfl": {
        "enabled": true,
        "top_teams": 10,
        "season": 2025,
        "level": 1,
        "sort": "winpercent:desc,gamesbehind:asc"
      },
      "nba": {
        "enabled": true,
        "top_teams": 10
      },
      "mlb": {
        "enabled": true,
        "top_teams": 10
      }
    },
    "update_interval": 3600,
    "scroll_speed": 1,
    "scroll_delay": 0.02,
    "display_duration": 60,
    "show_logos": true,
    "show_records": true,
    "dynamic_duration": true,
    "min_duration": 45,
    "max_duration": 120
  }
}
```

**Configuration Options**:
- **`enabled`** (boolean): Enable leaderboard display
- **`enabled_sports`** (object): Sports-specific configurations
- **`update_interval`** (integer): Update frequency
- **`scroll_speed`** (integer): Scrolling speed
- **`scroll_delay`** (float): Scroll step delay
- **`display_duration`** (integer): Display time
- **`show_logos`** (boolean): Show team logos
- **`show_records`** (boolean): Show win-loss records
- **`dynamic_duration`** (boolean): Auto-adjust duration
- **`min_duration`** (integer): Minimum display time
- **`max_duration`** (integer): Maximum display time

**Sport-Specific Options**:
- **`enabled`** (boolean): Enable this sport
- **`top_teams`** (integer): Number of teams to show
- **`season`** (integer): Season year (NFL)
- **`level`** (integer): League level (NFL)
- **`sort`** (string): Sorting criteria (NFL)

**Features**:
- League standings
- Team records and statistics
- Multiple sport support
- Scrolling leaderboard display
- Team logos and colors
- Customizable team count

---

## System Managers

### ⚙️ Config Manager (`src/config_manager.py`)

**Purpose**: Manage configuration loading, validation, and hot-reloading.

**Features**:
- JSON configuration file loading
- Configuration validation
- Hot-reload capability
- Default value handling
- Error recovery

---

### 🗄️ Cache Manager (`src/cache_manager.py`)

**Purpose**: Intelligent caching system for API data and assets.

**Features**:
- Multi-tier caching strategy
- Time-based cache invalidation
- Content-based cache validation
- Market-aware caching (stocks)
- Cache statistics and monitoring
- Automatic cache cleanup

---

### 🎨 Layout Manager (`src/layout_manager.py`)

**Purpose**: Manage display layouts and positioning.

**Features**:
- Dynamic layout calculation
- Multi-panel support
- Text positioning
- Image scaling and positioning
- Color management

---

### 🔤 Font Test Manager (`src/font_test_manager.py`)

**Purpose**: Test and preview different fonts on the display.

**Features**:
- Font rendering tests
- Size comparison
- Character set validation
- Performance testing

---

## Authentication Utilities

### 🎵 Spotify Authentication (`src/authenticate_spotify.py`)

**Purpose**: Handle Spotify OAuth authentication flow.

**Features**:
- OAuth 2.0 flow
- Token refresh handling
- Credential storage
- Error handling

---

### 🎵 YouTube Music Authentication (`src/authenticate_ytm.py`)

**Purpose**: Handle YouTube Music authentication.

**Features**:
- YouTube Music API setup
- Authentication flow
- Session management

---

## Client Libraries

### 🎵 Spotify Client (`src/spotify_client.py`)

**Purpose**: Spotify API client for music data.

**Features**:
- Currently playing track info
- Playlist access
- User library access
- Real-time updates

---

### 🎵 YouTube Music Client (`src/ytm_client.py`)

**Purpose**: YouTube Music API client.

**Features**:
- Track information
- Playback status
- Library access
- Real-time monitoring

---

## Display Duration System

### Dynamic Duration

Many managers support dynamic duration adjustment based on content length:

```json
{
  "manager_name": {
    "dynamic_duration": true,
    "min_duration": 30,
    "max_duration": 300,
    "duration_buffer": 0.1
  }
}
```

**How it works**:
1. Calculate content scroll time
2. Add buffer time for readability
3. Ensure duration is within min/max bounds
4. Adjust display rotation accordingly

### Static Duration

Configure fixed display durations in the main display configuration:

```json
{
  "display": {
    "display_durations": {
      "clock": 15,
      "weather": 30,
      "stocks": 30,
      "nhl_live": 30,
      "nba_live": 30
    }
  }
}
```

---

## Live Game Priority System

Sports managers support live game prioritization:

```json
{
  "sport_scoreboard": {
    "live_priority": true,
    "live_update_interval": 60
  }
}
```

**How it works**:
1. Check for live games every update interval
2. If live games exist, prioritize them in rotation
3. Use faster update intervals during live games
4. Return to normal rotation when games end

---

## Error Handling and Recovery

All managers include robust error handling:

- **API Failures**: Automatic retry with exponential backoff
- **Network Issues**: Graceful degradation and cached data usage
- **Invalid Data**: Data validation and sanitization
- **Configuration Errors**: Default value fallbacks
- **Hardware Issues**: Software fallback modes

---

## Performance Optimization

### Caching Strategy
- Intelligent cache invalidation
- Market-aware caching for financial data
- Time-based cache expiration
- Content-based cache validation

### Resource Management
- Memory-efficient image handling
- Font caching and reuse
- Connection pooling for APIs
- Background data fetching

### Display Optimization
- Hardware-accelerated rendering
- Graceful update system
- Frame rate optimization
- Scrolling performance tuning

---

This comprehensive guide covers every manager in the LEDMatrix system. Each manager is designed to be modular, configurable, and performant, allowing you to create a fully customized LED matrix display experience.
