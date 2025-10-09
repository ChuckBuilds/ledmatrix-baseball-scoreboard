# Complete Web UI Guide

The LEDMatrix Web Interface V2 provides a comprehensive, modern web-based control panel for managing your LED matrix display. This guide covers every feature, tab, and configuration option available in the web interface.

## Overview

The web interface runs on port 5001 and provides real-time control, monitoring, and configuration of your LEDMatrix system. It features a tabbed interface with different sections for various aspects of system management.

### Accessing the Web Interface

```
http://your-pi-ip:5001
```

### Auto-Start Configuration

To automatically start the web interface on boot, set this in your config:

```json
{
  "web_display_autostart": true
}
```

---

## Interface Layout

The web interface uses a modern tabbed layout with the following main sections:

1. **Overview** - System monitoring and status
2. **Schedule** - Display timing control
3. **Display** - Hardware configuration
4. **Sports** - Sports leagues settings
5. **Weather** - Weather service configuration
6. **Stocks** - Financial data settings
7. **Features** - Additional display features
8. **Music** - Music integration settings
9. **Calendar** - Google Calendar integration
10. **News** - RSS news feeds management
11. **API Keys** - Secure API key management
12. **Editor** - Visual display editor
13. **Actions** - System control actions
14. **Raw JSON** - Direct configuration editing
15. **Logs** - System logs viewer

---

## Tab Details

### 🏠 Overview Tab

**Purpose**: Real-time system monitoring and status display.

**Features**:
- **System Statistics**:
  - CPU utilization percentage (real-time)
  - Memory usage with available/total display
  - Disk usage percentage
  - CPU temperature monitoring
  - System uptime
  - Service status (running/stopped)

- **Display Preview**:
  - Live preview of LED matrix display (8x scaling)
  - 20fps update rate for smooth viewing
  - Fallback display when no data available
  - Enhanced border and styling

- **Quick Status**:
  - Current display mode
  - Active managers
  - Connection status
  - WebSocket connectivity indicator

**Auto-Refresh**: Updates every 2 seconds for real-time monitoring.

---

### ⏰ Schedule Tab

**Purpose**: Configure when the display is active.

**Configuration Options**:

```json
{
  "schedule": {
    "enabled": true,
    "start_time": "07:00",
    "end_time": "23:00"
  }
}
```

**Features**:
- **Enable/Disable Scheduling**: Toggle automatic display scheduling
- **Start Time**: Time to turn display on (24-hour format)
- **End Time**: Time to turn display off (24-hour format)
- **Timezone Awareness**: Uses system timezone
- **Immediate Apply**: Changes take effect immediately

**Form Controls**:
- Checkbox to enable/disable scheduling
- Time pickers for start and end times
- Save button with async submission
- Success/error notifications

---

### 🖥️ Display Tab

**Purpose**: Complete LED matrix hardware configuration.

**Hardware Settings**:

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
    }
  }
}
```

**Configuration Options**:

**Physical Configuration**:
- **Rows**: LED matrix height (typically 32)
- **Columns**: LED matrix width (typically 64)
- **Chain Length**: Number of panels connected in series
- **Parallel**: Number of parallel chains

**Display Quality**:
- **Brightness**: Display brightness (0-100) with real-time slider
- **PWM Bits**: Color depth (8-11, higher = better colors)
- **PWM Dither Bits**: Smoothing for gradients
- **PWM LSB Nanoseconds**: Timing precision

**Hardware Interface**:
- **Hardware Mapping**: HAT/Bonnet configuration
  - `adafruit-hat-pwm` - With jumper mod (recommended)
  - `adafruit-hat` - Without jumper mod
  - `regular` - Direct GPIO
  - `pi1` - Raspberry Pi 1 compatibility
- **GPIO Slowdown**: Timing adjustment for different Pi models
- **Scan Mode**: Panel scanning method

**Advanced Options**:
- **Disable Hardware Pulsing**: Software PWM override
- **Inverse Colors**: Color inversion
- **Show Refresh Rate**: Display refresh rate on screen
- **Limit Refresh Rate**: Maximum refresh rate (Hz)

**Form Features**:
- Real-time brightness slider with immediate preview
- Dropdown selectors for hardware mapping
- Number inputs with validation
- Checkbox controls for boolean options
- Tooltips explaining each setting

---

### 🏈 Sports Tab

**Purpose**: Configure sports leagues and display options.

**Supported Sports**:
- NFL (National Football League)
- NBA (National Basketball Association)
- MLB (Major League Baseball)
- NHL (National Hockey League)
- NCAA Football
- NCAA Basketball
- NCAA Baseball
- MiLB (Minor League Baseball)
- Soccer (Multiple leagues)

**Configuration Per Sport**:

```json
{
  "nfl_scoreboard": {
    "enabled": true,
    "favorite_teams": ["TB", "MIA"],
    "show_odds": true,
    "show_records": true,
    "live_priority": true,
    "test_mode": false
  }
}
```

**Common Options**:
- **Enable/Disable**: Toggle each sport individually
- **Favorite Teams**: List of team abbreviations to prioritize
- **Show Odds**: Display betting odds for games
- **Show Records**: Display team win-loss records
- **Live Priority**: Prioritize live games in rotation
- **Test Mode**: Use test data instead of live API

**Features**:
- Individual sport configuration sections
- Team selection with dropdown menus
- Checkbox controls for display options
- Real-time form validation
- Bulk enable/disable options

---

### 🌤️ Weather Tab

**Purpose**: Configure weather display and data sources.

**Configuration Options**:

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

**Settings**:
- **Enable Weather**: Toggle weather display
- **API Key**: OpenWeatherMap API key (secure input)
- **Update Interval**: Data refresh frequency (seconds)
- **Units**: Temperature units (imperial/metric/kelvin)
- **Display Options**:
  - Show "feels like" temperature
  - Show humidity percentage
  - Show wind speed and direction
  - Show UV index with color coding

**Location Settings**:
- Uses location from main configuration
- Automatic timezone handling
- Multiple display modes (current/hourly/daily)

**Form Features**:
- Secure API key input (password field)
- Unit selection dropdown
- Update interval slider
- Checkbox controls for display options
- API key validation

---

### 💰 Stocks Tab

**Purpose**: Configure stock ticker, cryptocurrency, and financial news.

**Stock Configuration**:

```json
{
  "stocks": {
    "enabled": true,
    "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA"],
    "update_interval": 600,
    "scroll_speed": 1,
    "scroll_delay": 0.01,
    "toggle_chart": false,
    "dynamic_duration": true
  }
}
```

**Cryptocurrency Configuration**:

```json
{
  "crypto": {
    "enabled": true,
    "symbols": ["BTC-USD", "ETH-USD", "ADA-USD"],
    "update_interval": 300
  }
}
```

**Stock Options**:
- **Enable Stocks**: Toggle stock ticker display
- **Symbols**: List of stock symbols to display
- **Update Interval**: Data refresh frequency
- **Scroll Speed**: Ticker scrolling speed (1-5)
- **Scroll Delay**: Delay between scroll steps
- **Toggle Chart**: Show mini price charts
- **Dynamic Duration**: Auto-adjust display time

**Crypto Options**:
- **Enable Crypto**: Toggle cryptocurrency display
- **Symbols**: Crypto symbols (format: SYMBOL-USD)
- **Update Interval**: Crypto data refresh rate

**Features**:
- Symbol input with validation
- Real-time price change indicators
- Scrolling ticker configuration
- Market hours awareness
- Logo display for supported symbols

---

### 🎯 Features Tab

**Purpose**: Configure additional display features and utilities.

**Available Features**:

**Clock Configuration**:
```json
{
  "clock": {
    "enabled": true,
    "format": "%I:%M %p",
    "update_interval": 1
  }
}
```

**Text Display Configuration**:
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

**YouTube Display Configuration**:
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

**"Of The Day" Configuration**:
```json
{
  "of_the_day": {
    "enabled": true,
    "sources": ["word_of_the_day", "bible_verse"],
    "rotation_enabled": true
  }
}
```

**Feature Controls**:
- Enable/disable toggles for each feature
- Configuration forms for each feature
- Real-time preview where applicable
- Input validation and error handling

---

### 🎵 Music Tab

**Purpose**: Configure music display integration with Spotify and YouTube Music.

**Configuration Options**:

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

**Settings**:
- **Enable Music**: Toggle music display
- **Preferred Source**: Choose primary music source
  - Spotify
  - YouTube Music
- **Polling Interval**: Update frequency for track info
- **Spotify Configuration**:
  - Client ID (from Spotify Developer Dashboard)
  - Client Secret (secure input)
  - Redirect URI for OAuth
- **YouTube Music Configuration**:
  - Enable/disable YTM integration

**Features**:
- Currently playing track display
- Artist and album information
- Album artwork display
- Progress bar
- Play/pause status
- Automatic source switching
- Authentication status indicators

---

### 📅 Calendar Tab

**Purpose**: Configure Google Calendar integration for event display.

**Configuration Options**:

```json
{
  "calendar": {
    "enabled": true,
    "credentials_file": "credentials.json",
    "token_file": "token.pickle",
    "calendars": ["primary", "birthdays"],
    "max_events": 3,
    "update_interval": 300
  }
}
```

**Settings**:
- **Enable Calendar**: Toggle calendar display
- **Credentials File**: Google API credentials file path
- **Token File**: OAuth token storage file
- **Calendars**: List of calendar names to display
- **Max Events**: Maximum number of events to show
- **Update Interval**: Event refresh frequency

**Features**:
- Multiple calendar support
- Upcoming events display
- All-day event handling
- Timezone-aware event times
- Google OAuth integration
- Authentication status display

---

### 📰 News Tab

**Purpose**: Manage RSS news feeds and display configuration.

**Configuration Options**:

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
    "update_interval": 300,
    "dynamic_duration": true
  }
}
```

**Built-in Feeds**:
- MLB (ESPN MLB News)
- NFL (ESPN NFL News)
- NCAA FB (ESPN College Football)
- NHL (ESPN NHL News)
- NBA (ESPN NBA News)
- TOP SPORTS (ESPN Top Sports)
- BIG10 (ESPN Big Ten Blog)
- NCAA (ESPN NCAA News)

**Features**:
- **Feed Management**:
  - Enable/disable built-in feeds
  - Add custom RSS feeds
  - Remove custom feeds
  - Feed URL validation

- **Display Configuration**:
  - Headlines per feed
  - Scroll speed adjustment
  - Update interval setting
  - Dynamic duration control

- **Custom Feeds**:
  - Add custom RSS feed URLs
  - Custom feed name assignment
  - Real-time feed validation
  - Delete custom feeds

**Form Controls**:
- Checkboxes for built-in feeds
- Text inputs for custom feed names and URLs
- Add/remove buttons for custom feeds
- Sliders for numeric settings
- Real-time validation feedback

---

### 🔑 API Keys Tab

**Purpose**: Secure management of API keys for various services.

**Supported Services**:
- **Weather**: OpenWeatherMap API key
- **YouTube**: YouTube Data API v3 key
- **Spotify**: Client ID and Client Secret
- **Sports**: ESPN API keys (if required)
- **News**: RSS feed API keys (if required)

**Security Features**:
- Password-type input fields for sensitive data
- Masked display of existing keys
- Secure transmission to server
- No client-side storage of keys
- Server-side encryption

**Key Management**:
- Add new API keys
- Update existing keys
- Remove unused keys
- Test key validity
- Status indicators for each service

**Form Features**:
- Service-specific input sections
- Secure input fields
- Save/update buttons
- Validation feedback
- Help text for obtaining keys

---

### 🎨 Editor Tab

**Purpose**: Visual display editor for creating custom layouts and content.

**Features** (Planned/In Development):
- Visual layout designer
- Drag-and-drop interface
- Real-time preview
- Custom content creation
- Layout templates
- Color picker
- Font selection
- Animation controls

**Current Implementation**:
- Placeholder for future visual editor
- Link to configuration documentation
- Manual layout guidance

---

### ⚡ Actions Tab

**Purpose**: System control and maintenance actions.

**Available Actions**:

**Service Control**:
- **Start Display**: Start the LED matrix display service
- **Stop Display**: Stop the display service gracefully
- **Restart Display**: Restart the display service
- **Service Status**: Check current service status

**System Control**:
- **Reboot System**: Safely reboot the Raspberry Pi
- **Shutdown System**: Safely shutdown the system
- **Restart Web Interface**: Restart the web interface

**Maintenance**:
- **Git Pull**: Update LEDMatrix from repository
- **Clear Cache**: Clear all cached data
- **Reset Configuration**: Reset to default configuration
- **Backup Configuration**: Create configuration backup

**Features**:
- Confirmation dialogs for destructive actions
- Real-time action feedback
- Progress indicators
- Error handling and reporting
- Safe shutdown procedures

**Safety Features**:
- Confirmation prompts for system actions
- Graceful service stopping
- Cache cleanup before restarts
- Configuration backup before resets

---

### 📝 Raw JSON Tab

**Purpose**: Direct JSON configuration editing with advanced features.

**Features**:

**JSON Editor**:
- Syntax highlighting
- Line numbers
- Monospace font
- Auto-indentation
- Bracket matching

**Validation**:
- Real-time JSON syntax validation
- Color-coded status indicators:
  - Green: Valid JSON
  - Red: Invalid JSON
  - Yellow: Warning/Incomplete
- Detailed error messages with line numbers
- Error highlighting

**Tools**:
- **Format JSON**: Automatic formatting and indentation
- **Validate**: Manual validation trigger
- **Save**: Save configuration changes
- **Reset**: Restore from last saved version

**Status Display**:
- Current validation status
- Error count and details
- Character count
- Line count

**Advanced Features**:
- Undo/redo functionality
- Find and replace
- Configuration backup before changes
- Automatic save prompts
- Conflict detection

---

### 📋 Logs Tab

**Purpose**: View system logs and troubleshooting information.

**Log Sources**:
- **System Logs**: General system messages
- **Service Logs**: LED matrix service logs
- **Web Interface Logs**: Web UI operation logs
- **Error Logs**: Error and exception logs
- **API Logs**: External API call logs

**Features**:
- **Real-time Updates**: Auto-refresh log display
- **Log Filtering**: Filter by log level or source
- **Search**: Search through log entries
- **Download**: Download logs for offline analysis
- **Clear**: Clear log display (not files)

**Log Levels**:
- DEBUG: Detailed diagnostic information
- INFO: General information messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical error messages

**Controls**:
- Refresh button for manual updates
- Auto-refresh toggle
- Log level filter dropdown
- Search input box
- Clear display button
- Download logs button

---

## Advanced Features

### WebSocket Integration

The web interface uses WebSocket connections for real-time updates:

- **Live Preview**: Real-time display preview updates
- **System Monitoring**: Live CPU, memory, and temperature data
- **Status Updates**: Real-time service status changes
- **Notifications**: Instant feedback for user actions

### Responsive Design

The interface adapts to different screen sizes:

- **Desktop**: Full tabbed interface with sidebar
- **Tablet**: Responsive grid layout
- **Mobile**: Stacked layout with collapsible tabs
- **Touch-Friendly**: Large buttons and touch targets

### Error Handling

Comprehensive error handling throughout:

- **Form Validation**: Client-side and server-side validation
- **Network Errors**: Graceful handling of connection issues
- **API Failures**: Fallback displays and retry mechanisms
- **Configuration Errors**: Detailed error messages and recovery options

### Performance Optimization

- **Lazy Loading**: Tabs load content on demand
- **Caching**: Client-side caching of configuration data
- **Compression**: Gzip compression for faster loading
- **Minification**: Optimized CSS and JavaScript

---

## Usage Tips

### Getting Started
1. Access the web interface at `http://your-pi-ip:5001`
2. Start with the Overview tab to check system status
3. Configure basic settings in Display and Schedule tabs
4. Add API keys in the API Keys tab
5. Enable desired features in their respective tabs

### Best Practices
- **Regular Monitoring**: Check the Overview tab regularly
- **Configuration Backup**: Use Raw JSON tab to backup configuration
- **Gradual Changes**: Make incremental configuration changes
- **Test Mode**: Use test modes when available for new configurations
- **Log Review**: Check logs when troubleshooting issues

### Troubleshooting
- **Connection Issues**: Check WebSocket status indicator
- **Configuration Problems**: Use Raw JSON tab for validation
- **Service Issues**: Use Actions tab to restart services
- **Performance Issues**: Monitor CPU and memory in Overview tab

---

## API Reference

The web interface exposes several API endpoints for programmatic access:

### Configuration Endpoints
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `GET /api/config/validate` - Validate configuration

### System Endpoints
- `GET /api/system/status` - Get system status
- `POST /api/system/action` - Execute system actions
- `GET /api/system/logs` - Get system logs

### Display Endpoints
- `GET /api/display/preview` - Get display preview image
- `POST /api/display/control` - Control display state
- `GET /api/display/modes` - Get available display modes

### Service Endpoints
- `GET /api/service/status` - Get service status
- `POST /api/service/control` - Control services
- `GET /api/service/logs` - Get service logs

---

The LEDMatrix Web Interface V2 provides complete control over your LED matrix display system through an intuitive, modern web interface. Every aspect of the system can be monitored, configured, and controlled remotely through any web browser.
