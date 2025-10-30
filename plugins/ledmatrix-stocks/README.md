# Stock & Crypto Ticker Plugin

A plugin for LEDMatrix that displays scrolling stock tickers with prices, changes, and optional charts for stocks and cryptocurrencies.

## Features

- **Stock Price Tracking**: Real-time stock prices and changes from Yahoo Finance
- **Cryptocurrency Support**: Bitcoin, Ethereum, and other crypto prices
- **Change Indicators**: Color-coded positive/negative changes
- **Percentage Display**: Show percentage changes alongside dollar amounts
- **Optional Charts**: Toggle chart display for visual price trends
- **Full-Screen Charts**: Dedicated chart display mode for individual stocks
- **Market Data**: Volume and market cap information (optional)
- **Configurable Display**: Adjustable scroll speed, colors, and timing
- **Background Data Fetching**: Efficient API calls without blocking display
- **Dynamic Duration**: Auto-calculate display time based on content width
- **Logo Support**: Display company/crypto logos from asset files
- **Runtime Configuration**: Change settings dynamically without restart
- **Error Handling**: Graceful error states with fallback displays
- **HTML Parsing**: Fallback parsing for Yahoo Finance HTML responses
- **Individual Stock Display**: Smooth scrolling for single stock displays

## Configuration

### Global Settings

```json
{
  "enabled": true,
  "display_duration": 30,
  "scroll_speed": 1.0,
  "scroll_delay": 0.01,
  "enable_scrolling": true,
  "dynamic_duration": true,
  "min_duration": 30,
  "max_duration": 300,
  "toggle_chart": false,
  "font_size": 10,
  "update_interval": 600
}
```

### Stock Settings

```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META"],
  "show_change": true,
  "show_percentage": true,
  "show_volume": false,
  "show_market_cap": false,
  "text_color": [255, 255, 255],
  "positive_color": [0, 255, 0],
  "negative_color": [255, 0, 0]
}
```

### Cryptocurrency Settings

```json
{
  "crypto": {
    "enabled": true,
    "crypto_symbols": ["BTC", "ETH", "ADA", "SOL", "DOT"],
    "show_change": true,
    "show_percentage": true,
    "text_color": [255, 215, 0],
    "positive_color": [0, 255, 0],
    "negative_color": [255, 0, 0]
  }
}
```

### Background Service Settings

```json
{
  "background_service": {
    "request_timeout": 30,
    "max_retries": 5,
    "priority": 2
  }
}
```

## Display Format

The stocks ticker displays information in a scrolling format showing:

- **Symbol**: Stock/crypto ticker symbol
- **Price**: Current price (e.g., "$150.25")
- **Change**: Dollar change with color coding (green for positive, red for negative)
- **Percentage**: Percentage change (e.g., "+2.5%")
- **Logo**: Company or crypto logo (if available)
- **Chart**: Mini price chart (if enabled)

## Stock Symbol Format

Stock symbols should be in uppercase format:

- **AAPL**: Apple Inc.
- **GOOGL**: Alphabet Inc.
- **MSFT**: Microsoft Corporation
- **TSLA**: Tesla Inc.
- **AMZN**: Amazon.com Inc.
- **META**: Meta Platforms Inc.
- **NFLX**: Netflix Inc.

## Cryptocurrency Symbols

Common cryptocurrency symbols:

- **BTC**: Bitcoin
- **ETH**: Ethereum
- **ADA**: Cardano
- **SOL**: Solana
- **DOT**: Polkadot
- **AVAX**: Avalanche
- **MATIC**: Polygon
- **LINK**: Chainlink

## Asset Requirements

### Stock Icons
Place stock company logos in:
```
assets/stocks/ticker_icons/{SYMBOL}.png
```

Example:
- `assets/stocks/ticker_icons/AAPL.png`
- `assets/stocks/ticker_icons/GOOGL.png`

### Crypto Icons
Place cryptocurrency logos in:
```
assets/stocks/crypto_icons/{SYMBOL}.png
```

Example:
- `assets/stocks/crypto_icons/BTC.png`
- `assets/stocks/crypto_icons/ETH.png`

**Note**: Use the symbol without the `-USD` suffix for crypto icons.

## API Integration

The plugin uses the Yahoo Finance public API:

- **Endpoint**: `https://query1.finance.yahoo.com/v8/finance/chart/`
- **Rate Limiting**: Built-in delays between requests (1-2 seconds)
- **Caching**: 10-minute cache for API responses
- **Retry Logic**: Up to 5 retries with exponential backoff
- **Error Handling**: Graceful fallback to cached data

## Background Data Service

The plugin integrates with LEDMatrix's background data service for non-blocking API calls:

- **Priority Level**: 2 (medium priority)
- **Request Timeout**: 30 seconds (configurable)
- **Max Retries**: 5 (configurable)
- **Cache TTL**: 600 seconds (matches update_interval)
- **Deferred Updates**: Updates are deferred during scrolling

## Performance Features

### Dynamic Duration
When enabled, the plugin automatically calculates display duration based on:
- Content width (number of symbols × display width)
- Scroll speed and delay settings
- Configurable buffer percentage

### Frame Rate Tracking
The plugin logs frame rate statistics every second:
- Average FPS over last 100 frames
- Current instantaneous FPS
- Frame time in milliseconds

### Scrolling Optimization
- Pre-rendered scrolling images for smooth animation
- Wrap-around scrolling for continuous display
- Configurable scroll speed and delay
- Integration with display manager scrolling state

## Troubleshooting

### No Data Showing
1. Check if symbols are valid and APIs are accessible
2. Verify internet connection
3. Check plugin logs for API errors
4. Ensure symbols are in correct format (uppercase)

### API Errors
1. Verify API keys and rate limits (if using premium APIs)
2. Check network connectivity
3. Review request timeout settings
4. Monitor background service logs

### Slow Scrolling
1. Adjust `scroll_speed` setting (0.5-5.0)
2. Reduce `scroll_delay` (0.001-0.1)
3. Check system performance
4. Monitor frame rate logs

### Missing Logos
1. Verify logo files exist in correct directories
2. Check file permissions
3. Ensure PNG format with transparency
4. Use appropriate image sizes (32x32 recommended)

### Network Errors
1. Check internet connection
2. Verify firewall settings
3. Test API endpoints manually
4. Review proxy settings if applicable

## Advanced Features

### Chart Display
When `toggle_chart` is enabled, the plugin displays:
- **Price Charts**: Simple line charts showing price trends
- **Time Periods**: 5-minute intervals over 1 day
- **Color Coding**: Charts use the same colors as price changes
- **Scaling**: Automatic min/max scaling with padding

### Runtime Configuration
The plugin supports dynamic configuration changes without restart:
- **`set_toggle_chart(enabled)`**: Enable/disable chart display
- **`set_scroll_speed(speed)`**: Change scroll speed (0.5-5.0)
- **`set_scroll_delay(delay)`**: Change scroll delay (0.001-0.1)
- **`set_enable_scrolling(enabled)`**: Enable/disable scrolling animation
- **`_reload_config()`**: Reload configuration from file
- **`get_dynamic_duration()`**: Get calculated display duration

### Display Modes
The plugin supports two display modes:

#### Scrolling Mode (Default)
- **`enable_scrolling: true`**: Continuous scrolling ticker
- Shows all stocks in sequence with smooth scrolling
- Uses ScrollHelper for efficient rendering
- Supports dynamic duration calculation

#### Static Mode
- **`enable_scrolling: false`**: Static display without scrolling
- Shows one stock at a time for 3 seconds each
- Cycles through all configured stocks
- Clean, centered layout with logo and price info
- Still supports mini charts if enabled

### Full-Screen Chart Mode
The plugin includes a dedicated chart display method:
- **`_draw_chart(symbol, data)`**: Draw full-screen chart for individual stocks
- **Clear Display**: Dedicated chart view with symbol and price info
- **Smooth Lines**: Connected price points with color coding
- **Price Display**: Current price and percentage change at bottom

### Error Handling
Robust error handling with graceful fallbacks:
- **`_show_error_state()`**: Display error message on screen
- **HTML Parsing**: `_extract_json_from_html()` for fallback data extraction
- **Cached Data**: Automatic fallback to cached data on API errors
- **Network Resilience**: Retry logic with exponential backoff

### Color Customization
- **Text Color**: Default color for all text elements
- **Positive Color**: Green color for positive changes
- **Negative Color**: Red color for negative changes
- **Crypto Colors**: Separate color scheme for cryptocurrencies

### Display Modes
The plugin supports different display modes:
- **Stocks Only**: Traditional stock ticker
- **Crypto Only**: Cryptocurrency ticker
- **Mixed Mode**: Both stocks and crypto in one ticker

## Integration Notes

This plugin is designed to work alongside other LEDMatrix plugins:

- **Stock News Plugin**: Show tickers while news scrolls in background
- **Weather Plugin**: Rotate between weather and financial data
- **Sports Plugin**: Display financial data during sports breaks

## Performance Notes

- The plugin is designed to be lightweight and not impact display performance
- Price data fetching happens in background to avoid blocking
- Configurable update intervals balance freshness vs. API load
- Caching reduces unnecessary network requests
- Frame rate monitoring helps identify performance issues

## Example Display

```
[AAPL] $150.25 +2.50 (+1.7%) [chart]
[GOOGL] $2750.80 -15.20 (-0.5%) [chart]
[BTC] $43250.00 +1250.00 (+3.0%) [chart]
[ETH] $2850.75 -75.25 (-2.6%) [chart]
```

## Dependencies

- **requests**: HTTP library for API calls
- **Pillow**: Image processing for logos and charts
- **urllib3**: HTTP connection pooling and retries

## Version History

### v2.0.0
- Migrated from old stock manager
- Added ScrollHelper integration
- Background data service support
- Improved error handling and logging
- Enhanced configuration options
- Better performance monitoring

## Support

For issues, feature requests, or questions:
- Check the plugin logs for error messages
- Review the configuration schema
- Test with minimal symbol list first
- Verify asset file locations and permissions
