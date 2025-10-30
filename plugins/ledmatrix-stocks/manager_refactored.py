"""
Stock & Crypto Ticker Plugin for LEDMatrix (Refactored)

Displays scrolling stock tickers with prices, changes, and optional charts
for stocks and cryptocurrencies. This refactored version splits functionality
into focused modules for better maintainability.
"""

import time
from typing import Dict, Any

from src.plugin_system.base_plugin import BasePlugin

# Import our modular components
from data_fetcher import StockDataFetcher
from display_renderer import StockDisplayRenderer
from chart_renderer import StockChartRenderer
from config_manager import StockConfigManager


class StockTickerPlugin(BasePlugin):
    """
    Stock and cryptocurrency ticker plugin with scrolling display.
    
    This refactored version uses modular components:
    - StockDataFetcher: Handles API calls and data fetching
    - StockDisplayRenderer: Handles display creation and layout
    - StockChartRenderer: Handles chart drawing functionality
    - StockConfigManager: Handles configuration management
    """
    
    def __init__(self, plugin_id: str, config: Dict[str, Any], 
                 display_manager, cache_manager, logger):
        """Initialize the stock ticker plugin."""
        super().__init__(plugin_id, config, display_manager, cache_manager, logger)
        
        # Get display dimensions
        self.display_width = display_manager.width
        self.display_height = display_manager.height
        
        # Initialize modular components
        self.config_manager = StockConfigManager(config, logger)
        self.data_fetcher = StockDataFetcher(self.config_manager.plugin_config, logger)
        self.display_renderer = StockDisplayRenderer(
            self.config_manager.plugin_config, 
            self.display_width, 
            self.display_height, 
            logger
        )
        self.chart_renderer = StockChartRenderer(
            self.config_manager.plugin_config,
            self.display_width,
            self.display_height,
            logger
        )
        
        # Plugin state
        self.stock_data = {}
        self.current_stock_index = 0
        self.scroll_complete = False
        self.last_update_time = 0
        
        # Initialize scroll helper
        self.scroll_helper = self.display_renderer.get_scroll_helper()
        self.scroll_helper.set_scroll_speed(self.config_manager.scroll_speed)
        
        self.logger.info("Stock ticker plugin initialized - %dx%d", 
                        self.display_width, self.display_height)
    
    def update(self) -> None:
        """Update stock and crypto data."""
        current_time = time.time()
        
        # Check if it's time to update
        if current_time - self.last_update_time >= self.config_manager.update_interval:
            try:
                self.logger.debug("Updating stock and crypto data")
                self.stock_data = self.data_fetcher.fetch_all_data()
                self.last_update_time = current_time
                
                # Clear scroll cache when data updates
                if hasattr(self.scroll_helper, 'cached_image'):
                    self.scroll_helper.cached_image = None
                
                self.logger.debug("Data update completed")
                
            except Exception as e:
                self.logger.error("Error updating data: %s", e)
    
    def display(self, force_clear: bool = False) -> None:
        """Display stocks with scrolling or static mode."""
        if not self.stock_data:
            self._show_error_state()
            return
        
        if self.config_manager.enable_scrolling:
            self._display_scrolling(force_clear)
        else:
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
        if not hasattr(self, '_smooth_scroll_position'):
            self._smooth_scroll_position = 0.0
        
        # Accumulate scroll position with fractional precision
        self._smooth_scroll_position += self.config_manager.scroll_speed
        
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
        
        # Get current stock
        symbols = list(self.stock_data.keys())
        if not symbols:
            self._show_error_state()
            return
        
        current_symbol = symbols[self.current_stock_index % len(symbols)]
        current_data = self.stock_data[current_symbol]
        
        # Create static display
        static_image = self.display_renderer.create_static_display(current_symbol, current_data)
        
        # Update display
        self.display_manager.image.paste(static_image, (0, 0))
        self.display_manager.update_display()
        
        # Move to next stock after a delay
        time.sleep(2)  # Show each stock for 2 seconds
        self.current_stock_index += 1
    
    def _create_scrolling_display(self):
        """Create the wide scrolling image with all stocks."""
        try:
            # Create scrolling image using display renderer
            scrolling_image = self.display_renderer.create_scrolling_display(self.stock_data)
            
            # Set up scroll helper
            self.scroll_helper.set_image(scrolling_image)
            self.scroll_helper.reset_scroll()
            
            self.logger.debug("Created scrolling image: %dx%d", 
                            scrolling_image.width, scrolling_image.height)
            
        except Exception as e:
            self.logger.error("Error creating scrolling display: %s", e)
    
    def _show_error_state(self):
        """Show error state when no data is available."""
        try:
            error_image = self.display_renderer._create_error_display()
            self.display_manager.image.paste(error_image, (0, 0))
            self.display_manager.update_display()
        except Exception as e:
            self.logger.error("Error showing error state: %s", e)
    
    def get_display_duration(self) -> float:
        """Get the display duration in seconds."""
        return self.config_manager.get_display_duration()
    
    def get_dynamic_duration(self) -> int:
        """Get the dynamic duration setting."""
        return self.config_manager.get_dynamic_duration()
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return self.config_manager.get_plugin_info()
    
    # Configuration methods
    def set_toggle_chart(self, enabled: bool) -> None:
        """Set whether to show mini charts."""
        self.config_manager.set_toggle_chart(enabled)
        self.display_renderer.set_toggle_chart(enabled)
    
    def set_scroll_speed(self, speed: float) -> None:
        """Set the scroll speed."""
        self.config_manager.set_scroll_speed(speed)
        self.scroll_helper.set_scroll_speed(speed)
    
    def set_scroll_delay(self, delay: float) -> None:
        """Set the scroll delay."""
        self.config_manager.set_scroll_delay(delay)
    
    def set_enable_scrolling(self, enabled: bool) -> None:
        """Set whether scrolling is enabled."""
        self.config_manager.set_enable_scrolling(enabled)
    
    def reload_config(self) -> None:
        """Reload configuration."""
        self.config_manager.reload_config()
        # Update components with new config
        self.data_fetcher.config = self.config_manager.plugin_config
        self.display_renderer.config = self.config_manager.plugin_config
        self.chart_renderer.config = self.config_manager.plugin_config
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if hasattr(self.data_fetcher, 'cleanup'):
                self.data_fetcher.cleanup()
            self.logger.info("Stock ticker plugin cleanup completed")
        except Exception as e:
            self.logger.error("Error during cleanup: %s", e)
