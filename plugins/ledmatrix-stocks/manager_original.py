"""
Stock & Crypto Ticker Plugin for LEDMatrix

Displays scrolling stock tickers with prices, changes, and optional charts
for stocks and cryptocurrencies. Migrated from the original stock_manager.py
with improved architecture using common utilities and background data service.
"""

import time
import random
import urllib.parse
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from PIL import Image, ImageDraw
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import numpy as np

# Import common utilities
from src.common import ScrollHelper, APIHelper, LogoHelper, TextHelper
from src.plugin_system.base_plugin import BasePlugin

# Import background data service
try:
    from src.background_data_service import get_background_service
except ImportError:
    get_background_service = None

# Import API counter function from web interface
try:
    from web_interface_v2 import increment_api_counter
except ImportError:
    def increment_api_counter(_kind: str, _count: int = 1):
        pass


class StockTickerPlugin(BasePlugin):
    """
    Stock and cryptocurrency ticker plugin with scrolling display.
    
    Features:
    - Yahoo Finance API integration for stocks and crypto
    - Scrolling ticker with logos, prices, and changes
    - Optional mini price charts
    - Dynamic duration calculation
    - Background data fetching
    - Color-coded price changes
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], 
                 display_manager, cache_manager, plugin_manager):
        """Initialize the stock ticker plugin."""
        super().__init__(plugin_id, config, display_manager, cache_manager, plugin_manager)
        
        # Get display dimensions
        self.display_width = display_manager.matrix.width
        self.display_height = display_manager.matrix.height
        
        # Initialize basic attributes first
        self.stock_data = {}
        self.last_update = 0
        self.scroll_complete = False
        
        # Runtime configurable attributes (for setter methods)
        self.scroll_speed = self.config.get('scroll_speed', 1.0)
        self.scroll_delay = self.config.get('scroll_delay', 0.01)
        self.toggle_chart = self.config.get('toggle_chart', False)
        self.enable_scrolling = self.config.get('enable_scrolling', True)
        
        # Initialize common helpers
        self._init_helpers()
        
        # Load configuration
        self._load_config()
        
        # Initialize background service
        self.background_service = None
        self._init_background_service()
        
        # Initialize HTTP session with retry logic
        self._init_http_session()
        
        self.logger.info("Stock ticker plugin initialized - %dx%d", self.display_width, self.display_height)
        self.logger.info("Stocks enabled: %s, Crypto enabled: %s", self.stocks_enabled, self.crypto_enabled)
    
    def _init_helpers(self):
        """Initialize common helper classes."""
        self.scroll_helper = ScrollHelper(
            display_width=self.display_width,
            display_height=self.display_height,
            logger=self.logger
        )
        
        self.api_helper = APIHelper(
            cache_manager=self.cache_manager
        )
        
        self.logo_helper = LogoHelper(
            display_width=self.display_width,
            display_height=self.display_height,
            logger=self.logger
        )
        
        self.text_helper = TextHelper(logger=self.logger)
    
    def _load_config(self):
        """Load and validate plugin configuration."""
        # Basic settings
        self.stocks_enabled = self.config.get('enabled', True)
        self.stock_symbols = self.config.get('symbols', ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META'])
        
        # Crypto settings
        crypto_config = self.config.get('crypto', {})
        self.crypto_enabled = crypto_config.get('enabled', True)
        self.crypto_symbols = crypto_config.get('crypto_symbols', ['BTC', 'ETH', 'ADA', 'SOL', 'DOT'])
        
        # Display settings (already initialized in __init__)
        self.font_size = self.config.get('font_size', 10)
        
        # Dynamic duration settings
        self.dynamic_duration = self.config.get('dynamic_duration', True)
        self.min_duration = self.config.get('min_duration', 30)
        self.max_duration = self.config.get('max_duration', 300)
        self.duration_buffer = self.config.get('duration_buffer', 0.1)
        
        # Display options
        self.show_change = self.config.get('show_change', True)
        self.show_percentage = self.config.get('show_percentage', True)
        self.show_volume = self.config.get('show_volume', False)
        self.show_market_cap = self.config.get('show_market_cap', False)
        
        # Colors
        self.text_color = tuple(self.config.get('text_color', [255, 255, 255]))
        self.positive_color = tuple(self.config.get('positive_color', [0, 255, 0]))
        self.negative_color = tuple(self.config.get('negative_color', [255, 0, 0]))
        
        # Crypto colors (override defaults if specified)
        if 'crypto' in self.config:
            crypto_config = self.config['crypto']
            self.crypto_text_color = tuple(crypto_config.get('text_color', [255, 215, 0]))
            self.crypto_positive_color = tuple(crypto_config.get('positive_color', [0, 255, 0]))
            self.crypto_negative_color = tuple(crypto_config.get('negative_color', [255, 0, 0]))
        else:
            self.crypto_text_color = (255, 215, 0)  # Gold
            self.crypto_positive_color = (0, 255, 0)
            self.crypto_negative_color = (255, 0, 0)
        
        # Configure scroll helper (use pixels per frame like old stock manager)
        self.scroll_helper.set_scroll_speed(self.scroll_speed)  # Pixels per frame
        self.scroll_helper.set_scroll_delay(self.scroll_delay)
        self.scroll_helper.set_dynamic_duration_settings(
            enabled=self.dynamic_duration,
            min_duration=self.min_duration,
            max_duration=self.max_duration,
            buffer=self.duration_buffer
        )
    
    def _init_background_service(self):
        """Initialize background data service if available."""
        if get_background_service:
            try:
                self.background_service = get_background_service(
                    self.cache_manager,
                    max_workers=1
                )
                self.logger.info("Background service initialized")
            except (AttributeError, TypeError) as e:
                self.logger.warning("Could not initialize background service: %s", e)
    
    def _init_http_session(self):
        """Initialize HTTP session with retry logic."""
        self.session = requests.Session()
        
        # Set up headers
        self.headers = {
            'User-Agent': 'LEDMatrix/1.0 (https://github.com/ChuckBuilds/LEDMatrix; contact@example.com)',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def update(self) -> None:
        """Update stock and crypto data."""
        if not self.stocks_enabled and not self.crypto_enabled:
            return
        
        current_time = time.time()
        update_interval = self.config.get('update_interval', 600)
        
        # Check if we need to update
        if current_time - self.last_update < update_interval:
            return
        
        # Check if we're currently scrolling and defer if so
        if self.display_manager.is_currently_scrolling():
            self.logger.debug("Display is scrolling, deferring stock update")
            self.display_manager.defer_update(self._perform_update, priority=2)
            return
        
        self._perform_update()
    
    def _perform_update(self):
        """Perform the actual data update."""
        try:
            self.logger.debug("Updating stock and crypto data")
            
            # Update stocks if enabled
            if self.stocks_enabled and self.stock_symbols:
                for symbol in self.stock_symbols:
                    try:
                        data = self._fetch_stock_data(symbol, is_crypto=False)
                        if data:
                            self.stock_data[symbol] = data
                            self.logger.debug("Updated stock data for %s", symbol)
                    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
                        self.logger.error("Error fetching data for %s: %s", symbol, e)
            
            # Update crypto if enabled
            if self.crypto_enabled and self.crypto_symbols:
                for symbol in self.crypto_symbols:
                    try:
                        data = self._fetch_stock_data(symbol, is_crypto=True)
                        if data:
                            self.stock_data[symbol] = data
                            self.logger.debug("Updated crypto data for %s", symbol)
                    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
                        self.logger.error("Error fetching data for %s: %s", symbol, e)
            
            self.last_update = time.time()
            
            # Clear scroll cache to force regeneration
            self.scroll_helper.clear_cache()
            
        except (ValueError, KeyError, TypeError) as e:
            self.logger.error("Error updating stock data: %s", e)
    
    def _fetch_stock_data(self, symbol: str, is_crypto: bool = False) -> Optional[Dict[str, Any]]:
        """Fetch stock or crypto data from Yahoo Finance API."""
        # Try to get cached data first
        cache_key = f"stock_data_{symbol}"
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            self.logger.debug("Using cached data for %s", symbol)
            return cached_data
        
        try:
            # For crypto, append -USD if not already present
            if is_crypto and not symbol.endswith('-USD'):
                api_symbol = f"{symbol}-USD"
            else:
                api_symbol = symbol
            
            # Use background service if available, otherwise direct request
            if self.background_service:
                return self._fetch_via_background_service(api_symbol, symbol, is_crypto)
            else:
                return self._fetch_direct(api_symbol, symbol, is_crypto)
                
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            self.logger.error("Error fetching data for %s: %s", symbol, e)
            # Try to use cached data as fallback
            if cached_data:
                self.logger.info("Using cached data as fallback for %s", symbol)
                return cached_data
            return None
    
    def _fetch_via_background_service(self, api_symbol: str, display_symbol: str, 
                                    is_crypto: bool) -> Optional[Dict[str, Any]]:
        """Fetch data using background service."""
        def fetch_task():
            return self._fetch_direct(api_symbol, display_symbol, is_crypto)
        
        try:
            # Use the background service's submit method
            if hasattr(self.background_service, 'submit'):
                result = self.background_service.submit(
                    fetch_task,
                    cache_key=f"stock_data_{display_symbol}",
                    priority=2
                )
                return result
            else:
                # Fallback to direct fetch if background service doesn't support submit
                return self._fetch_direct(api_symbol, display_symbol, is_crypto)
        except (AttributeError, TypeError) as e:
            self.logger.error("Background service error for %s: %s", display_symbol, e)
            return None
    
    def _fetch_direct(self, api_symbol: str, display_symbol: str, 
                     is_crypto: bool) -> Optional[Dict[str, Any]]:
        """Fetch data directly from Yahoo Finance API."""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(api_symbol)}"
            params = {
                'interval': '5m',
                'range': '1d'
            }
            
            response = self.session.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30,
                verify=True
            )
            
            if response.status_code != 200:
                self.logger.error("Failed to fetch data for %s: HTTP %d", display_symbol, response.status_code)
                return None
            
            data = response.json()
            
            # Increment API counter
            increment_api_counter('stocks', 1)
            
            # Extract relevant data
            chart_data = data.get('chart', {}).get('result', [{}])[0]
            meta = chart_data.get('meta', {})
            
            if not meta:
                self.logger.error("No meta data found for %s", display_symbol)
                return None
            
            current_price = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('previousClose', current_price)
            
            # Get price history
            timestamps = chart_data.get('timestamp', [])
            indicators = chart_data.get('indicators', {}).get('quote', [{}])[0]
            close_prices = indicators.get('close', [])
            
            # Build price history
            price_history = []
            for i, ts in enumerate(timestamps):
                if i < len(close_prices) and close_prices[i] is not None:
                    price_history.append({
                        'timestamp': datetime.fromtimestamp(ts),
                        'price': close_prices[i]
                    })
            
            # Calculate change percentage
            change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
            
            # Get company name
            name = meta.get('symbol', display_symbol)
            
            stock_data = {
                "symbol": display_symbol,
                "name": name,
                "price": current_price,
                "change": change_pct,
                "open": prev_close,
                "price_history": price_history,
                "is_crypto": is_crypto
            }
            
            # Cache the data
            self.cache_manager.set(f"stock_data_{display_symbol}", stock_data)
            
            # Add delay between requests to avoid rate limiting
            time.sleep(random.uniform(1.0, 2.0))
            
            return stock_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error("Network error fetching data for %s: %s", display_symbol, e)
            return None
        except (ValueError, KeyError, TypeError) as e:
            self.logger.error("Unexpected error fetching data for %s: %s", display_symbol, e)
            return None
    
    def _get_stock_logo(self, symbol: str, is_crypto: bool = False) -> Optional[Image.Image]:
        """Get stock or crypto logo image - matching old stock manager sizing."""
        try:
            if is_crypto:
                # Try crypto icons first
                logo_path = f"assets/stocks/crypto_icons/{symbol}.png"
            else:
                # Try stock icons
                logo_path = f"assets/stocks/ticker_icons/{symbol}.png"
            
            # Use same sizing as old stock manager (display_width/1.2, display_height/1.2)
            max_size = min(int(self.display_width / 1.2), int(self.display_height / 1.2))
            return self.logo_helper.load_logo(symbol, logo_path, max_size, max_size)
            
        except (OSError, IOError) as e:
            self.logger.warning("Error loading logo for %s: %s", symbol, e)
            return None
    
    def _create_stock_display(self, symbol: str, data: Dict[str, Any]) -> Image.Image:
        """Create a display image for a single stock or crypto - matching old stock manager layout exactly."""
        # Create a wider image for scrolling - adjust width based on chart toggle
        width = int(self.display_width * (2 if self.toggle_chart else 1.2))  # Much more compact when no chart
        height = self.display_height
        image = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        is_crypto = data.get('is_crypto', False)
        
        # Draw large stock/crypto logo on the left
        logo = self._get_stock_logo(symbol, is_crypto)
        if logo:
            # Position logo on the left side with minimal spacing
            logo_x = 2  # Small margin from left edge
            logo_y = (height - logo.height) // 2
            image.paste(logo, (logo_x, logo_y), logo)
        
        # Load fonts - use the same fonts as old stock manager
        fonts = self.text_helper.load_fonts()
        
        # Create smaller versions of the fonts for symbol and price (matching old stock manager)
        symbol_font = fonts.get('score')  # Use regular font for symbol
        price_font = fonts.get('score')   # Use regular font for price
        change_font = fonts.get('time')   # Use small font for change
        
        # Create text elements
        display_symbol = symbol.replace('-USD', '') if is_crypto else symbol
        symbol_text = display_symbol
        price_text = f"${data['price']:.2f}"
        change_text = f"{data['change']:+.2f} ({data['change']:+.1f}%)"
        
        # Get colors based on change
        if data['change'] >= 0:
            change_color = self.positive_color if not is_crypto else self.crypto_positive_color
        else:
            change_color = self.negative_color if not is_crypto else self.crypto_negative_color
        
        text_color = self.text_color if not is_crypto else self.crypto_text_color
        
        # Calculate text dimensions for proper spacing (matching old stock manager)
        symbol_bbox = draw.textbbox((0, 0), symbol_text, font=symbol_font)
        price_bbox = draw.textbbox((0, 0), price_text, font=price_font)
        change_bbox = draw.textbbox((0, 0), change_text, font=change_font)
        
        # Calculate total height needed - adjust gaps based on chart toggle
        text_gap = 2 if self.toggle_chart else 1  # Reduced gap when no chart
        total_text_height = (symbol_bbox[3] - symbol_bbox[1]) + \
                           (price_bbox[3] - price_bbox[1]) + \
                           (change_bbox[3] - change_bbox[1]) + \
                           (text_gap * 2)  # Account for gaps between elements
        
        # Calculate starting y position to center all text
        start_y = (height - total_text_height) // 2
        
        # Calculate center x position for the column - adjust based on chart toggle
        if self.toggle_chart:
            # When chart is enabled, center text more to the left
            column_x = width // 2.85
        else:
            # When chart is disabled, position text closer to logo for more compact layout
            column_x = width // 1.8
        
        # Draw symbol
        symbol_width = symbol_bbox[2] - symbol_bbox[0]
        symbol_x = column_x - (symbol_width // 2)
        draw.text((symbol_x, start_y), symbol_text, font=symbol_font, fill=text_color)
        
        # Draw price
        price_width = price_bbox[2] - price_bbox[0]
        price_x = column_x - (price_width // 2)
        price_y = start_y + (symbol_bbox[3] - symbol_bbox[1]) + text_gap  # Adjusted gap
        draw.text((price_x, price_y), price_text, font=price_font, fill=text_color)
        
        # Draw change with color based on value
        change_width = change_bbox[2] - change_bbox[0]
        change_x = column_x - (change_width // 2)
        change_y = price_y + (price_bbox[3] - price_bbox[1]) + text_gap  # Adjusted gap
        draw.text((change_x, change_y), change_text, font=change_font, fill=change_color)
        
        # Draw mini chart on the right only if toggle_chart is enabled
        if self.toggle_chart and 'price_history' in data and len(data['price_history']) >= 2:
            self._draw_mini_chart(draw, data['price_history'], width, height, change_color)
        
        return image
    
    def _draw_mini_chart(self, draw: ImageDraw.ImageDraw, price_history: List[Dict], 
                        width: int, height: int, color: Tuple[int, int, int]):
        """Draw a mini price chart."""
        if len(price_history) < 2:
            return
        
        # Calculate chart dimensions
        chart_width = int(width // 2.5)
        chart_height = height // 1.5
        chart_x = width - chart_width - 4
        chart_y = (height - chart_height) // 2
        
        # Extract prices
        prices = [p['price'] for p in price_history]
        min_price = min(prices)
        max_price = max(prices)
        
        # Add padding to avoid flat lines
        price_range = max_price - min_price
        if price_range < 0.01:
            min_price -= 0.01
            max_price += 0.01
            price_range = 0.02
        
        # Draw chart points
        points = []
        for i, price in enumerate(prices):
            x = chart_x + (i * chart_width) // (len(prices) - 1)
            y = chart_y + chart_height - int(((price - min_price) / price_range) * chart_height)
            points.append((x, y))
        
        # Draw lines between points
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=color, width=1)
    
    def display(self, force_clear: bool = False) -> None:
        """Display the stock ticker with optional scrolling animation."""
        if not self.stocks_enabled and not self.crypto_enabled:
            return
        
        if not self.stock_data:
            self.logger.warning("No stock or crypto data available to display")
            return
        
        # Clear display if requested
        if force_clear:
            self.display_manager.clear()
        
        if self.enable_scrolling:
            # Scrolling mode
            self._display_scrolling(force_clear)
        else:
            # Static mode - show one stock at a time
            self._display_static(force_clear)
    
    def _display_scrolling(self, force_clear: bool = False) -> None:
        """Display stocks with smooth scrolling animation."""
        # Create scrolling image if needed
        if not self.scroll_helper.cached_image or force_clear:
            self._create_scrolling_display()
        
        if force_clear:
            self.scroll_helper.reset_scroll()
        
        # Signal scrolling state
        self.display_manager.set_scrolling_state(True)
        self.display_manager.process_deferred_updates()
        
        # Smooth scrolling with sub-pixel precision for anti-aliasing effect
        # Use fractional scroll position for smoother movement
        if not hasattr(self, '_smooth_scroll_position'):
            self._smooth_scroll_position = 0.0
        
        # Accumulate scroll position with fractional precision
        self._smooth_scroll_position += self.scroll_speed
        
        # Use integer position for actual display but keep fractional for smoothness
        self.scroll_helper.scroll_position = int(self._smooth_scroll_position) % self.scroll_helper.total_scroll_width
        
        # Get visible portion
        visible_portion = self.scroll_helper.get_visible_portion()
        if visible_portion:
            # Update display
            self.display_manager.image.paste(visible_portion, (0, 0))
            self.display_manager.update_display()
        
        # Log frame rate (less frequently to avoid spam)
        self.scroll_helper.log_frame_rate()
        
        # Check if scroll is complete (wrapped around)
        if self.scroll_helper.scroll_position == 0:
            self.scroll_complete = True
            self._smooth_scroll_position = 0.0  # Reset smooth position
    
    def _display_static(self, force_clear: bool = False) -> None:  # pylint: disable=unused-argument
        """Display stocks in static mode - one at a time without scrolling."""
        # Signal not scrolling
        self.display_manager.set_scrolling_state(False)
        self.display_manager.process_deferred_updates()
        
        # Get all symbols
        symbols = list(self.stock_data.keys())
        if not symbols:
            return
        
        # Use a simple cycling approach - show each stock for a few seconds
        current_time = time.time()
        stock_display_duration = 3.0  # Show each stock for 3 seconds
        
        # Calculate which stock to show based on time
        stock_index = int((current_time % (len(symbols) * stock_display_duration)) / stock_display_duration)
        current_symbol = symbols[stock_index]
        current_data = self.stock_data[current_symbol]
        
        # Create static display for current stock
        static_image = self._create_static_display(current_symbol, current_data)
        
        # Update display
        self.display_manager.image.paste(static_image, (0, 0))
        self.display_manager.update_display()
        
        # Small delay to prevent excessive updates
        time.sleep(0.1)
    
    def _create_static_display(self, symbol: str, data: Dict[str, Any]) -> Image.Image:
        """Create a static display image for a single stock (no scrolling)."""
        # Create image sized to display
        width = self.display_width
        height = self.display_height
        image = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        is_crypto = data.get('is_crypto', False)
        
        # Draw logo
        logo = self._get_stock_logo(symbol, is_crypto)
        if logo:
            # Center logo on the left side
            logo_x = 5
            logo_y = (height - logo.height) // 2
            image.paste(logo, (logo_x, logo_y), logo)
        
        # Load fonts
        fonts = self.text_helper.load_fonts()
        
        # Create text elements
        price_text = f"${data['price']:.2f}"
        change_text = f"{data['change']:+.2f} ({data['change']:+.1f}%)"
        
        # Get colors based on change
        if data['change'] >= 0:
            change_color = self.positive_color if not is_crypto else self.crypto_positive_color
        else:
            change_color = self.negative_color if not is_crypto else self.crypto_negative_color
        
        text_color = self.text_color if not is_crypto else self.crypto_text_color
        
        # Draw symbol (top)
        symbol_font = fonts.get('team', fonts.get('score'))
        self.text_helper.draw_text_with_outline(
            draw, symbol, (width // 2 - 20, 5), symbol_font, fill=text_color
        )
        
        # Draw price (center)
        price_font = fonts.get('score')
        self.text_helper.draw_text_with_outline(
            draw, price_text, (width // 2 - 30, height // 2 - 5), price_font, fill=text_color
        )
        
        # Draw change (bottom)
        change_font = fonts.get('time')
        self.text_helper.draw_text_with_outline(
            draw, change_text, (width // 2 - 40, height - 15), change_font, fill=change_color
        )
        
        # Draw mini chart if enabled
        if self.toggle_chart and 'price_history' in data and len(data['price_history']) >= 2:
            self._draw_mini_chart(draw, data['price_history'], width, height, change_color)
        
        return image
    
    def _draw_mini_chart(self, draw: ImageDraw.Draw, price_history: List[Dict], width: int, height: int, color: Tuple[int, int, int]) -> None:
        """Draw a mini chart on the right side of the display."""
        if len(price_history) < 2:
            return
        
        # Chart dimensions
        chart_width = width // 3
        chart_height = height // 2
        chart_x = width - chart_width - 5
        chart_y = (height - chart_height) // 2
        
        # Extract prices
        prices = [p['price'] for p in price_history]
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range < 0.01:
            min_price -= 0.01
            max_price += 0.01
            price_range = 0.02
        
        # Draw chart points
        points = []
        for i, price in enumerate(prices):
            x = chart_x + (i * chart_width) // (len(prices) - 1)
            y = chart_y + chart_height - int(((price - min_price) / price_range) * chart_height)
            points.append((x, y))
        
        # Draw lines between points
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=color, width=1)
    
    def _create_scrolling_display(self):
        """Create the full scrolling display with all stocks and crypto."""
        # Get all symbols
        symbols = list(self.stock_data.keys())
        if not symbols:
            return
        
        # Create display images for each symbol
        display_images = []
        for symbol in symbols:
            data = self.stock_data[symbol]
            display_img = self._create_stock_display(symbol, data)
            display_images.append(display_img)
        
        # Create scrolling image
        self.scroll_helper.create_scrolling_image(
            display_images,
            item_gap=self.display_width // 6,
            element_gap=self.display_width // 8
        )
    
    def get_display_duration(self) -> float:
        """Get the calculated display duration."""
        if self.dynamic_duration and self.scroll_helper.cached_image:
            return float(self.scroll_helper.get_dynamic_duration())
        return float(self.config.get('display_duration', 30))
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        info = super().get_info()
        info.update({
            'name': 'Stock & Crypto Ticker',
            'version': '2.0.0',
            'stocks_enabled': self.stocks_enabled,
            'crypto_enabled': self.crypto_enabled,
            'stock_symbols': self.stock_symbols,
            'crypto_symbols': self.crypto_symbols,
            'data_count': len(self.stock_data),
            'scroll_speed': self.scroll_speed,
            'scroll_delay': self.scroll_delay,
            'enable_scrolling': self.enable_scrolling,
            'toggle_chart': self.toggle_chart,
            'dynamic_duration': self.dynamic_duration,
            'last_update': self.last_update,
            'scroll_complete': self.scroll_complete
        })
        return info
    
    def _draw_chart(self, symbol: str, data: Dict[str, Any]) -> None:
        """Draw a full-screen price chart for the stock."""
        if not data.get('price_history'):
            return
            
        # Clear the display
        self.display_manager.clear()
        
        # Draw the symbol at the top with small font
        self.display_manager.draw_text(
            symbol,
            y=1,
            color=(255, 255, 255),
            small_font=True
        )
        
        # Calculate chart dimensions
        chart_height = 16
        chart_y = 8
        width = self.display_manager.matrix.width
        
        # Get min and max prices for scaling
        prices = [p['price'] for p in data['price_history']]
        if not prices:
            return
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            return
            
        # Draw chart points
        points = []
        color = self._get_stock_color(symbol)
        
        for i, point in enumerate(data['price_history']):
            x = int((i / len(data['price_history'])) * width)
            y = chart_y + chart_height - int(((point['price'] - min_price) / price_range) * chart_height)
            points.append((x, y))
            
        # Draw lines between points
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            self.display_manager.draw.line([x1, y1, x2, y2], fill=color, width=1)
            
        # Draw current price at the bottom with small font
        price_text = f"${data['price']:.2f} ({data['change']:+.1f}%)"
        self.display_manager.draw_text(
            price_text,
            y=28,
            color=color,
            small_font=True
        )
        
        # Update the display
        self.display_manager.update_display()
    
    def _get_stock_color(self, symbol: str) -> Tuple[int, int, int]:
        """Get color based on stock performance."""
        if symbol not in self.stock_data:
            return (255, 255, 255)  # White for unknown
        
        change = self.stock_data[symbol].get('change', 0)
        if change > 0:
            return (0, 255, 0)  # Green for positive
        elif change < 0:
            return (255, 0, 0)  # Red for negative
        return (255, 255, 0)  # Yellow for no change
    
    def _extract_json_from_html(self, html: str) -> Dict:
        """Extract the JSON data from Yahoo Finance HTML."""
        try:
            # Look for the finance data in the HTML
            patterns = [
                r'root\.App\.main = (.*?);\s*</script>',
                r'"QuotePageStore":\s*({.*?}),\s*"',
                r'{"regularMarketPrice":.*?"regularMarketChangePercent".*?}'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    try:
                        data = json.loads(json_str)
                        if isinstance(data, dict):
                            if 'context' in data:
                                # First pattern matched
                                context = data.get('context', {})
                                dispatcher = context.get('dispatcher', {})
                                stores = dispatcher.get('stores', {})
                                quote_data = stores.get('QuoteSummaryStore', {})
                                if quote_data:
                                    return quote_data
                            else:
                                # Direct quote data
                                return data
                    except json.JSONDecodeError:
                        continue
                        
            # If we get here, try one last attempt to find the price data directly
            price_match = re.search(r'"regularMarketPrice":{"raw":([\d.]+)', html)
            change_match = re.search(r'"regularMarketChangePercent":{"raw":([-\d.]+)', html)
            prev_close_match = re.search(r'"regularMarketPreviousClose":{"raw":([\d.]+)', html)
            name_match = re.search(r'"shortName":"([^"]+)"', html)
            
            if price_match:
                return {
                    "price": {
                        "regularMarketPrice": {"raw": float(price_match.group(1))},
                        "regularMarketChangePercent": {"raw": float(change_match.group(1)) if change_match else 0},
                        "regularMarketPreviousClose": {"raw": float(prev_close_match.group(1)) if prev_close_match else 0},
                        "shortName": name_match.group(1) if name_match else None
                    }
                }
            
            return {}
        except (ValueError, TypeError) as e:
            self.logger.error("Error extracting JSON data: %s", e)
            return {}
    
    def _update_stock_display(self, symbol: str, data: Dict[str, Any], width: int, height: int) -> None:
        """Update the stock display with smooth scrolling animation."""
        try:
            # Create the full scrolling image
            full_image = self._create_stock_display(symbol, data)
            scroll_width = width * 2  # Double width for smooth scrolling
            
            # Scroll the image smoothly
            for scroll_pos in range(0, scroll_width - width, 15):
                # Create visible portion
                visible_image = full_image.crop((scroll_pos, 0, scroll_pos + width, height))
                
                # Convert to RGB and create numpy array
                rgb_image = visible_image.convert('RGB')
                image_array = np.array(rgb_image)
                
                # Update display
                self.display_manager.update_display(image_array)
                
                # Small delay for smooth animation
                time.sleep(0.005)
            
            # Show final position briefly
            final_image = full_image.crop((scroll_width - width, 0, scroll_width, height))
            rgb_image = final_image.convert('RGB')
            image_array = np.array(rgb_image)
            self.display_manager.update_display(image_array)
            time.sleep(0.2)
            
        except (ValueError, TypeError, OSError) as e:
            self.logger.error("Error updating stock display for %s: %s", symbol, e)
            # Show error state
            self._show_error_state(width, height)
    
    def _show_error_state(self, width: int, height: int) -> None:
        """Show error state display."""
        try:
            # Create error image
            error_img = Image.new('RGB', (width, height), (50, 0, 0))  # Dark red background
            draw = ImageDraw.Draw(error_img)
            
            # Load fonts
            fonts = self.text_helper.load_fonts()
            error_font = fonts.get('time', fonts.get('score'))
            
            # Draw error message
            error_text = "ERROR"
            self.text_helper.draw_text_with_outline(
                draw, error_text, 
                (width // 2 - 20, height // 2 - 5), 
                error_font, fill=(255, 255, 255)
            )
            
            # Convert to numpy array and update display
            rgb_image = error_img.convert('RGB')
            image_array = np.array(rgb_image)
            self.display_manager.update_display(image_array)
            
        except (OSError, ValueError, TypeError) as e:
            self.logger.error("Error showing error state: %s", e)
    
    def _reload_config(self) -> None:
        """Reload configuration from file."""
        # Reset stock data if symbols have changed
        new_stock_symbols = set(self.stock_symbols)
        new_crypto_symbols = set(self.crypto_symbols)
        current_symbols = set(self.stock_data.keys())
        
        if new_stock_symbols != current_symbols or new_crypto_symbols != current_symbols:
            self.stock_data = {}
            self.last_update = 0  # Force immediate update
            self.logger.info("Stock symbols changed. New symbols: %s", new_stock_symbols | new_crypto_symbols)
            
        # Update scroll and chart settings
        self.scroll_speed = self.config.get('scroll_speed', 1.0)
        self.scroll_delay = self.config.get('scroll_delay', 0.01)
        self.toggle_chart = self.config.get('toggle_chart', False)
        
        # Update scroll helper settings
        self.scroll_helper.set_scroll_speed(self.scroll_speed)
        self.scroll_helper.set_scroll_delay(self.scroll_delay)
        
        # Clear cached image if settings changed
        self.scroll_helper.clear_cache()
        self.logger.info("Stock display settings changed, clearing cache")
    
    def get_dynamic_duration(self) -> int:
        """Get the calculated dynamic duration for display."""
        return self.scroll_helper.get_dynamic_duration()
    
    def set_toggle_chart(self, enabled: bool) -> None:
        """Enable or disable chart display in the scrolling ticker."""
        self.toggle_chart = enabled
        self.scroll_helper.clear_cache()  # Clear cache when switching modes
        self.logger.info("Chart toggle set to: %s", enabled)
        
    def set_scroll_speed(self, speed: float) -> None:
        """Set the scroll speed for the ticker."""
        self.scroll_speed = speed
        self.scroll_helper.set_scroll_speed(speed)  # Pixels per frame
        self.logger.info("Scroll speed set to: %s", speed)
        
    def set_scroll_delay(self, delay: float) -> None:
        """Set the scroll delay for the ticker."""
        self.scroll_delay = delay
        self.scroll_helper.set_scroll_delay(delay)
        self.logger.info("Scroll delay set to: %s", delay)
    
    def set_enable_scrolling(self, enabled: bool) -> None:
        """Enable or disable scrolling animation."""
        self.enable_scrolling = enabled
        self.scroll_helper.clear_cache()  # Clear cache when switching modes
        self.logger.info("Scrolling enabled: %s", enabled)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if hasattr(self, 'session'):
                self.session.close()
            if hasattr(self, 'background_service') and self.background_service:
                # Clean up background service if needed
                pass
            self.logger.info("Stock ticker plugin cleanup completed")
        except (AttributeError, OSError) as e:
            self.logger.error("Error during cleanup: %s", e)
