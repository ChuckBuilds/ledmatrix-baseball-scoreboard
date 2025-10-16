import time
import logging
import sys
import os
from typing import Dict, Any, List
from datetime import datetime, time as time_obj

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(levelname)s:%(name)s:%(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout
)

from src.clock import Clock
from src.weather_manager import WeatherManager
from src.display_manager import DisplayManager
from src.config_manager import ConfigManager
from src.cache_manager import CacheManager
from src.stock_manager import StockManager
from src.stock_news_manager import StockNewsManager
from src.odds_ticker_manager import OddsTickerManager
from src.leaderboard_manager import LeaderboardManager
from src.nhl_managers import NHLLiveManager, NHLRecentManager, NHLUpcomingManager
from src.nba_managers import NBALiveManager, NBARecentManager, NBAUpcomingManager
from src.wnba_managers import WNBALiveManager, WNBARecentManager, WNBAUpcomingManager
from src.mlb_manager import MLBLiveManager, MLBRecentManager, MLBUpcomingManager
from src.milb_manager import MiLBLiveManager, MiLBRecentManager, MiLBUpcomingManager
from src.soccer_managers import SoccerLiveManager, SoccerRecentManager, SoccerUpcomingManager
from src.nfl_managers import NFLLiveManager, NFLRecentManager, NFLUpcomingManager
from src.ncaa_fb_managers import NCAAFBLiveManager, NCAAFBRecentManager, NCAAFBUpcomingManager
from src.ncaa_baseball_managers import NCAABaseballLiveManager, NCAABaseballRecentManager, NCAABaseballUpcomingManager
from src.ncaam_basketball_managers import NCAAMBasketballLiveManager, NCAAMBasketballRecentManager, NCAAMBasketballUpcomingManager
from src.ncaaw_basketball_managers import NCAAWBasketballLiveManager, NCAAWBasketballRecentManager, NCAAWBasketballUpcomingManager
from src.ncaam_hockey_managers import NCAAMHockeyLiveManager, NCAAMHockeyRecentManager, NCAAMHockeyUpcomingManager
from src.ncaaw_hockey_managers import NCAAWHockeyLiveManager, NCAAWHockeyRecentManager, NCAAWHockeyUpcomingManager
from src.youtube_display import YouTubeDisplay
from src.calendar_manager import CalendarManager
from src.text_display import TextDisplay
from src.static_image_manager import StaticImageManager
from src.music_manager import MusicManager
from src.of_the_day_manager import OfTheDayManager
from src.news_manager import NewsManager

# Get logger without configuring
logger = logging.getLogger(__name__)

class DisplayController:
    def __init__(self):
        start_time = time.time()
        logger.info("Starting DisplayController initialization")
        
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.cache_manager = CacheManager()
        logger.info("Config loaded in %.3f seconds", time.time() - start_time)
        
        config_time = time.time()
        self.display_manager = DisplayManager(self.config)
        logger.info("DisplayManager initialized in %.3f seconds", time.time() - config_time)
        
        # Initialize display modes
        # NOTE: All built-in managers disabled - use plugins instead
        init_time = time.time()
        self.clock = Clock(self.display_manager, self.config) if self.config.get('clock', {}).get('enabled', True) else None
        
        # All built-in modules disabled - use plugin versions instead
        self.weather = None  # Use weather plugin
        self.stocks = None  # Use stocks plugin
        self.news = None  # Use stock-news plugin
        self.odds_ticker = None  # Use odds-ticker plugin
        self.leaderboard = None  # Use leaderboard plugin
        self.calendar = None  # Use calendar plugin
        self.youtube = None  # Not yet available as plugin
        self.text_display = None  # Use text-display plugin
        self.static_image = None  # Use static-image plugin
        self.of_the_day = None  # Use of-the-day plugin
        self.news_manager = None  # Use news plugin
        logger.info(f"Calendar Manager initialized: {'Object' if self.calendar else 'None'}")
        logger.info(f"Text Display initialized: {'Object' if self.text_display else 'None'}")
        logger.info(f"Static Image Manager initialized: {'Object' if self.static_image else 'None'}")
        logger.info(f"OfTheDay Manager initialized: {'Object' if self.of_the_day else 'None'}")
        logger.info(f"News Manager initialized: {'Object' if self.news_manager else 'None'}")
        logger.info("Display modes initialized in %.3f seconds", time.time() - init_time)
        
        self.force_change = False
        # Music Manager - disabled, use music plugin instead
        music_init_time = time.time()
        self.music_manager = None  # Use music plugin
        logger.info("Built-in MusicManager disabled - use music plugin instead")
        logger.info("MusicManager initialized in %.3f seconds", time.time() - music_init_time)
        
        # NHL managers - disabled, use hockey-scoreboard plugin instead
        nhl_time = time.time()
        self.nhl_live = None
        self.nhl_recent = None
        self.nhl_upcoming = None
        logger.info("NHL managers disabled - use hockey-scoreboard plugin instead")
        logger.info("NHL managers initialized in %.3f seconds", time.time() - nhl_time)
            
        # NBA managers - disabled, use basketball-scoreboard plugin instead
        nba_time = time.time()
        self.nba_live = None
        self.nba_recent = None
        self.nba_upcoming = None
        logger.info("NBA managers disabled - use basketball-scoreboard plugin instead")
        logger.info("NBA managers initialized in %.3f seconds", time.time() - nba_time)
            
        # WNBA managers - disabled, use basketball-scoreboard plugin instead
        wnba_time = time.time()
        self.wnba_live = None
        self.wnba_recent = None
        self.wnba_upcoming = None
        logger.info("WNBA managers disabled - use basketball-scoreboard plugin instead")
        logger.info("WNBA managers initialized in %.3f seconds", time.time() - wnba_time)

        # MLB managers - disabled, use baseball-scoreboard plugin instead
        mlb_time = time.time()
        self.mlb_live = None
        self.mlb_recent = None
        self.mlb_upcoming = None
        logger.info("MLB managers disabled - use baseball-scoreboard plugin instead")
        logger.info("MLB managers initialized in %.3f seconds", time.time() - mlb_time)

        # MiLB managers - disabled, use baseball-scoreboard plugin instead
        milb_time = time.time()
        self.milb_live = None
        self.milb_recent = None
        self.milb_upcoming = None
        logger.info("MiLB managers disabled - use baseball-scoreboard plugin instead")
        logger.info("MiLB managers initialized in %.3f seconds", time.time() - milb_time)
            
        # Soccer managers - disabled, use soccer-scoreboard plugin instead
        soccer_time = time.time()
        self.soccer_live = None
        self.soccer_recent = None
        self.soccer_upcoming = None
        logger.info("Soccer managers disabled - use soccer-scoreboard plugin instead")
        logger.info("Soccer managers initialized in %.3f seconds", time.time() - soccer_time)
            
        # NFL managers - disabled, use football-scoreboard plugin instead
        nfl_time = time.time()
        self.nfl_live = None
        self.nfl_recent = None
        self.nfl_upcoming = None
        logger.info("NFL managers disabled - use football-scoreboard plugin instead")
        logger.info("NFL managers initialized in %.3f seconds", time.time() - nfl_time)
        
        # NCAA FB managers - disabled, use football-scoreboard plugin instead
        ncaa_fb_time = time.time()
        self.ncaa_fb_live = None
        self.ncaa_fb_recent = None
        self.ncaa_fb_upcoming = None
        logger.info("NCAA FB managers disabled - use football-scoreboard plugin instead")
        logger.info("NCAA FB managers initialized in %.3f seconds", time.time() - ncaa_fb_time)
        
        # NCAA Baseball managers - disabled, use baseball-scoreboard plugin instead
        ncaa_baseball_time = time.time()
        self.ncaa_baseball_live = None
        self.ncaa_baseball_recent = None
        self.ncaa_baseball_upcoming = None
        logger.info("NCAA Baseball managers disabled - use baseball-scoreboard plugin instead")
        logger.info("NCAA Baseball managers initialized in %.3f seconds", time.time() - ncaa_baseball_time)

        # NCAA Men's Basketball managers - disabled, use basketball-scoreboard plugin instead
        ncaam_basketball_time = time.time()
        self.ncaam_basketball_live = None
        self.ncaam_basketball_recent = None
        self.ncaam_basketball_upcoming = None
        logger.info("NCAA Men's Basketball managers disabled - use basketball-scoreboard plugin instead")
        logger.info("NCAA Men's Basketball managers initialized in %.3f seconds", time.time() - ncaam_basketball_time)

        # NCAA Women's Basketball managers - disabled, use basketball-scoreboard plugin instead
        ncaaw_basketball_time = time.time()
        self.ncaaw_basketball_live = None
        self.ncaaw_basketball_recent = None
        self.ncaaw_basketball_upcoming = None
        logger.info("NCAA Women's Basketball managers disabled - use basketball-scoreboard plugin instead")
        logger.info("NCAA Women's Basketball managers initialized in %.3f seconds", time.time() - ncaaw_basketball_time)

        # NCAA Men's Hockey managers - disabled, use hockey-scoreboard plugin instead
        ncaam_hockey_time = time.time()
        self.ncaam_hockey_live = None
        self.ncaam_hockey_recent = None
        self.ncaam_hockey_upcoming = None
        logger.info("NCAA Men's Hockey managers disabled - use hockey-scoreboard plugin instead")
        logger.info("NCAA Men's Hockey managers initialized in %.3f seconds", time.time() - ncaam_hockey_time)

        # NCAA Women's Hockey managers - disabled, use hockey-scoreboard plugin instead
        ncaaw_hockey_time = time.time()
        self.ncaaw_hockey_live = None
        self.ncaaw_hockey_recent = None
        self.ncaaw_hockey_upcoming = None
        logger.info("NCAA Women's Hockey managers disabled - use hockey-scoreboard plugin instead")
        logger.info("NCAA Women's Hockey managers initialized in %.3f seconds", time.time() - ncaaw_hockey_time)
        
        # NOTE: Rotation state and live priority now handled by individual plugins
        
        # List of available display modes
        # NOTE: Built-in managers disabled - plugins will be added below
        self.available_modes = []
        if self.clock: self.available_modes.append('clock')
        # Plugin modes will be added during plugin initialization
        
        # Initialize Plugin System (Phase 1: Foundation)
        import traceback
        plugin_time = time.time()
        self.plugin_manager = None
        self.plugin_modes = {}  # mode -> plugin_instance mapping for plugin-first dispatch
        
        try:
            logger.info("Attempting to import plugin system...")
            from src.plugin_system import PluginManager
            logger.info("Plugin system imported successfully")
            self.plugin_manager = PluginManager(
                plugins_dir=os.path.join(os.getcwd(), "plugins"),
                config_manager=self.config_manager,
                display_manager=self.display_manager,
                cache_manager=self.cache_manager
            )

            # Discover plugins
            discovered_plugins = self.plugin_manager.discover_plugins()
            logger.info(f"Discovered {len(discovered_plugins)} plugin(s)")

            # Load enabled plugins
            for plugin_id in discovered_plugins:
                plugin_config = self.config.get(plugin_id, {})
                if plugin_config.get('enabled', False):
                    if self.plugin_manager.load_plugin(plugin_id):
                        logger.info(f"Loaded plugin: {plugin_id}")
                        
                        # Get plugin instance and manifest
                        plugin_instance = self.plugin_manager.get_plugin(plugin_id)
                        manifest = self.plugin_manager.plugin_manifests.get(plugin_id, {})
                        display_modes = manifest.get('display_modes', [plugin_id])
                        
                        # Register plugin modes for dispatch
                        for mode in display_modes:
                            self.plugin_modes[mode] = plugin_instance
                            logger.info(f"Registered plugin mode: {mode} -> {plugin_id}")
                        
                        # Add plugin display modes to available_modes
                        for mode in display_modes:
                            if mode not in self.available_modes:
                                self.available_modes.append(mode)
                                logger.info(f"Added plugin mode to rotation: {mode}")
                    else:
                        logger.error(f"Failed to load plugin: {plugin_id}")
            
            logger.info(f"Plugin system initialized in {time.time() - plugin_time:.3f} seconds")
        except ImportError as e:
            logger.warning(f"Plugin system not available: {e}")
            logger.warning(f"Full traceback:\n{traceback.format_exc()}")
            self.plugin_manager = None
        except Exception as e:
            logger.error(f"Error initializing plugin system: {e}", exc_info=True)
            self.plugin_manager = None
        
        # Set initial display to first available mode (clock)
        self.current_mode_index = 0
        self.current_display_mode = "none"
        # Reset logged duration when mode is initialized
        if hasattr(self, '_last_logged_duration'):
            delattr(self, '_last_logged_duration')
        self.last_switch = time.time()
        self.force_clear = True
        self.update_interval = 0.01  # Reduced from 0.1 to 0.01 for smoother scrolling
        
        # NOTE: Team-based rotation states removed - plugins now handle their own state
        # No need for hard-coded sport-specific rotation tracking
        
        # On-demand display control
        self.on_demand_mode = None  # Plugin mode to display on-demand
        self.on_demand_duration = None  # How long to show on-demand (None = indefinite)
        self.on_demand_start_time = None  # When on-demand started
        self.on_demand_pinned = False  # If True, stays on this mode until unpinned
        
        # Update display durations to include all modes
        self.display_durations = self.config['display'].get('display_durations', {})
        # Backward-compatibility: map legacy weather keys to current keys if provided in config
        try:
            if 'weather' in self.display_durations and 'weather_current' not in self.display_durations:
                self.display_durations['weather_current'] = self.display_durations['weather']
            if 'hourly_forecast' in self.display_durations and 'weather_hourly' not in self.display_durations:
                self.display_durations['weather_hourly'] = self.display_durations['hourly_forecast']
            if 'daily_forecast' in self.display_durations and 'weather_daily' not in self.display_durations:
                self.display_durations['weather_daily'] = self.display_durations['daily_forecast']
        except Exception:
            pass
        # Add defaults for soccer if missing
        default_durations = {
            'clock': 15,
            'weather_current': 15,
            'weather_hourly': 15,
            'weather_daily': 15,
            'stocks': 45,
            'stock_news': 30,
            'calendar': 30,
            'youtube': 30,
            'nhl_live': 30,
            'nhl_recent': 20,
            'nhl_upcoming': 20,
            'nba_live': 30,
            'nba_recent': 20,
            'nba_upcoming': 20,
            'wnba_live': 30,
            'wnba_recent': 20,
            'wnba_upcoming': 20,
            'mlb_live': 30,
            'mlb_recent': 20,
            'mlb_upcoming': 20,
            'milb_live': 30,
            'milb_recent': 20,
            'milb_upcoming': 20,
            'soccer_live': 30, # Soccer durations
            'soccer_recent': 20,
            'soccer_upcoming': 20,
            'nfl_live': 30, # Added NFL durations
            'nfl_recent': 30,
            'nfl_upcoming': 30,
            'ncaa_fb_live': 30, # Added NCAA FB durations
            'ncaa_fb_recent': 15,
            'ncaa_fb_upcoming': 15,
            'music': 20, # Default duration for music, will be overridden by config if present
            'ncaa_baseball_live': 30, # Added NCAA Baseball durations
            'ncaa_baseball_recent': 15,
            'ncaa_baseball_upcoming': 15,
            'ncaam_basketball_live': 30, # Added NCAA Men's Basketball durations
            'ncaam_basketball_recent': 15,
            'ncaam_basketball_upcoming': 15,
            'ncaaw_basketball_live': 30, # Added NCAA Womens's Basketball durations
            'ncaaw_basketball_recent': 15,
            'ncaaw_basketball_upcoming': 15,
            'ncaam_hockey_live': 30, # Added NCAA Men's Hockey durations
            'ncaam_hockey_recent': 15,
            'ncaam_hockey_upcoming': 15,
            'ncaaw_hockey_live': 30, # Added NCAA Men's Hockey durations
            'ncaaw_hockey_recent': 15,
            'ncaaw_hockey_upcoming': 15
        }
        # Merge loaded durations with defaults
        for key, value in default_durations.items():
            if key not in self.display_durations:
                 self.display_durations[key] = value
        
        # Dynamically log favorite teams for any enabled plugin that has them configured
        # This works for any plugin without hard-coding specific sport names
        for plugin_id, plugin_config in self.config.items():
            if isinstance(plugin_config, dict) and plugin_config.get('enabled', False):
                favorite_teams = plugin_config.get('favorite_teams', [])
                if favorite_teams:
                    # Create a readable display name from plugin_id
                    display_name = plugin_id.replace('_', ' ').replace('-', ' ').title()
                    logger.info(f"{display_name} Favorite teams: {favorite_teams}")

        logger.info(f"Available display modes: {self.available_modes}")
        logger.info(f"Initial display mode: {self.current_display_mode}")
        logger.info("DisplayController initialized with display_manager: %s", id(self.display_manager))

        # --- SCHEDULING ---
        self.is_display_active = True
        self._load_schedule_config() # Load schedule config once at startup

    def _handle_music_update(self, track_info: Dict[str, Any], significant_change: bool = False):
        """Callback for when music track info changes."""
        # MusicManager now handles its own display state (album art, etc.)
        # This callback might still be useful if DisplayController needs to react to music changes
        # for reasons other than directly re-drawing the music screen (e.g., logging, global state).
        # For now, we'll keep it simple. If the music screen is active, it will redraw on its own.
        if track_info:
            logger.debug(f"DisplayController received music update (via callback): Title - {track_info.get('title')}, Playing - {track_info.get('is_playing')}")
        else:
            logger.debug("DisplayController received music update (via callback): Track is None or not playing.")

        if self.current_display_mode == 'music' and self.music_manager:
            if significant_change:
                logger.info("Music is current display mode and SIGNIFICANT track updated. Signaling immediate refresh.")
                self.force_clear = True # Tell the display method to clear before drawing
            else:
                logger.debug("Music is current display mode and received a MINOR update (e.g. progress). No force_clear.")
                # self.force_clear = False # Ensure it's false if not significant, or let run loop manage
        # If the current display mode is music, the MusicManager's display method will be called
        # in the main loop and will use its own updated internal state. No explicit action needed here
        # to force a redraw of the music screen itself, unless DisplayController wants to switch TO music mode.
        # Example: if self.current_display_mode == 'music': self.force_clear = True (but MusicManager.display handles this)

    def _try_display_plugin(self, mode, force_clear=False):
        """
        Try to display a plugin for the given mode.
        Returns True if plugin handled it, False if should fall through to legacy.
        """
        plugin = self.plugin_modes.get(mode)
        if not plugin:
            return False
        
        try:
            # Try calling with force_clear parameter (new plugin standard)
            plugin.display(force_clear=force_clear)
            return True
        except TypeError as e:
            # If plugin doesn't accept force_clear, try without it (backward compatibility)
            if "force_clear" in str(e):
                try:
                    plugin.display()
                    return True
                except Exception as inner_e:
                    logger.error(f"Error displaying plugin for mode {mode}: {inner_e}", exc_info=True)
                    return False
            else:
                logger.error(f"Error displaying plugin for mode {mode}: {e}", exc_info=True)
                return False
        except Exception as e:
            logger.error(f"Error displaying plugin for mode {mode}: {e}", exc_info=True)
            return False

    def get_current_duration(self) -> int:
        """Get the duration for the current display mode."""
        mode_key = self.current_display_mode
        
        # Check if current mode is a plugin and get its duration
        if mode_key in self.plugin_modes:
            try:
                plugin = self.plugin_modes[mode_key]
                duration = plugin.get_display_duration()
                # Only log if duration has changed or we haven't logged this duration yet
                if not hasattr(self, '_last_logged_plugin_duration') or self._last_logged_plugin_duration != (mode_key, duration):
                    logger.info(f"Using plugin duration for {mode_key}: {duration} seconds")
                    self._last_logged_plugin_duration = (mode_key, duration)
                return duration
            except Exception as e:
                logger.error(f"Error getting plugin duration for {mode_key}: {e}")
                # Fall back to configured duration
                return self.display_durations.get(mode_key, 15)

        # Handle dynamic duration for news manager
        if mode_key == 'news_manager' and self.news_manager:
            try:
                dynamic_duration = self.news_manager.get_dynamic_duration()
                # Only log if duration has changed or we haven't logged this duration yet
                if not hasattr(self, '_last_logged_duration') or self._last_logged_duration != dynamic_duration:
                    logger.info(f"Using dynamic duration for news_manager: {dynamic_duration} seconds")
                    self._last_logged_duration = dynamic_duration
                return dynamic_duration
            except Exception as e:
                logger.error(f"Error getting dynamic duration for news_manager: {e}")
                # Fall back to configured duration
                return self.display_durations.get(mode_key, 60)

        # Handle dynamic duration for stocks
        elif mode_key == 'stocks' and self.stocks:
            try:
                dynamic_duration = self.stocks.get_dynamic_duration()
                # Only log if duration has changed or we haven't logged this duration yet
                if not hasattr(self, '_last_logged_duration') or self._last_logged_duration != dynamic_duration:
                    logger.info(f"Using dynamic duration for stocks: {dynamic_duration} seconds")
                    self._last_logged_duration = dynamic_duration
                return dynamic_duration
            except Exception as e:
                logger.error(f"Error getting dynamic duration for stocks: {e}")
                # Fall back to configured duration
                return self.display_durations.get(mode_key, 60)

        # Handle dynamic duration for stock_news
        elif mode_key == 'stock_news' and self.news:
            try:
                dynamic_duration = self.news.get_dynamic_duration()
                # Only log if duration has changed or we haven't logged this duration yet
                if not hasattr(self, '_last_logged_duration') or self._last_logged_duration != dynamic_duration:
                    logger.info(f"Using dynamic duration for stock_news: {dynamic_duration} seconds")
                    self._last_logged_duration = dynamic_duration
                return dynamic_duration
            except Exception as e:
                logger.error(f"Error getting dynamic duration for stock_news: {e}")
                # Fall back to configured duration
                return self.display_durations.get(mode_key, 60)

        # Handle dynamic duration for odds_ticker
        elif mode_key == 'odds_ticker' and self.odds_ticker:
            try:
                dynamic_duration = self.odds_ticker.get_dynamic_duration()
                # Only log if duration has changed or we haven't logged this duration yet
                if not hasattr(self, '_last_logged_duration') or self._last_logged_duration != dynamic_duration:
                    logger.info(f"Using dynamic duration for odds_ticker: {dynamic_duration} seconds")
                    self._last_logged_duration = dynamic_duration
                return dynamic_duration
            except Exception as e:
                logger.error(f"Error getting dynamic duration for odds_ticker: {e}")
                # Fall back to configured duration
                return self.display_durations.get(mode_key, 60)

        # Handle leaderboard duration (user choice between fixed or dynamic)
        elif mode_key == 'leaderboard' and self.leaderboard:
            try:
                duration = self.leaderboard.get_duration()
                mode_type = "dynamic" if self.leaderboard.dynamic_duration else "fixed"
                # Only log if duration has changed or we haven't logged this duration yet
                if not hasattr(self, '_last_logged_leaderboard_duration') or self._last_logged_leaderboard_duration != duration:
                    logger.info(f"Using leaderboard {mode_type} duration: {duration} seconds")
                    self._last_logged_leaderboard_duration = duration
                return duration
            except Exception as e:
                logger.error(f"Error getting duration for leaderboard: {e}")
                # Fall back to configured duration
                return self.display_durations.get(mode_key, 600)

        # Simplify weather key handling
        elif mode_key.startswith('weather_'):
            return self.display_durations.get(mode_key, 15)
            # duration_key = mode_key.split('_', 1)[1]
            # if duration_key == 'current': duration_key = 'weather_current' # Keep specific keys
            # elif duration_key == 'hourly': duration_key = 'weather_hourly'
            # elif duration_key == 'daily': duration_key = 'weather_daily'
            # else: duration_key = 'weather_current' # Default to current
            # return self.display_durations.get(duration_key, 15)
        
        return self.display_durations.get(mode_key, 15)

    def _update_modules(self):
        """Call update methods on active managers."""
        # Check if we're currently scrolling and defer updates if so
        if self.display_manager.is_currently_scrolling():
            logger.debug("Display is currently scrolling, deferring module updates")
            # Defer updates for modules that might cause lag during scrolling
            if self.odds_ticker: 
                self.display_manager.defer_update(self.odds_ticker.update, priority=1)
            if self.leaderboard:
                self.display_manager.defer_update(self.leaderboard.update, priority=1)
            if self.stocks: 
                self.display_manager.defer_update(self.stocks.update_stock_data, priority=2)
            if self.news: 
                self.display_manager.defer_update(self.news.update_news_data, priority=2)
            # Defer sport manager updates that might do heavy API fetching
            if hasattr(self, 'ncaa_fb_live') and self.ncaa_fb_live:
                self.display_manager.defer_update(self.ncaa_fb_live.update, priority=3)
            if hasattr(self, 'ncaa_fb_recent') and self.ncaa_fb_recent:
                self.display_manager.defer_update(self.ncaa_fb_recent.update, priority=3)
            if hasattr(self, 'ncaa_fb_upcoming') and self.ncaa_fb_upcoming:
                self.display_manager.defer_update(self.ncaa_fb_upcoming.update, priority=3)
            if hasattr(self, 'nfl_live') and self.nfl_live:
                self.display_manager.defer_update(self.nfl_live.update, priority=3)
            if hasattr(self, 'nfl_recent') and self.nfl_recent:
                self.display_manager.defer_update(self.nfl_recent.update, priority=3)
            if hasattr(self, 'nfl_upcoming') and self.nfl_upcoming:
                self.display_manager.defer_update(self.nfl_upcoming.update, priority=3)
            # Continue with non-scrolling-sensitive updates
            if self.weather: self.weather.get_weather()
            if self.calendar: self.calendar.update(time.time())
            if self.youtube: self.youtube.update()
            if self.text_display: self.text_display.update()
            if self.static_image: self.static_image.update()
            if self.of_the_day: self.of_the_day.update(time.time())
        else:
            # Not scrolling, perform all updates normally
            if self.weather: self.weather.get_weather()
            if self.stocks: self.stocks.update_stock_data()
            if self.news: self.news.update_news_data()
            if self.odds_ticker: self.odds_ticker.update()
            if self.calendar: self.calendar.update(time.time())
            if self.youtube: self.youtube.update()
            if self.text_display: self.text_display.update()
            if self.static_image: self.static_image.update()
            if self.of_the_day: self.of_the_day.update(time.time())
            
            # Update sports managers for leaderboard data
            if self.leaderboard: self.leaderboard.update()
            
            # Update key sports managers that feed the leaderboard
            if self.nfl_live: self.nfl_live.update()
            if self.nfl_recent: self.nfl_recent.update()
            if self.nfl_upcoming: self.nfl_upcoming.update()
            if self.ncaa_fb_live: self.ncaa_fb_live.update()
            if self.ncaa_fb_recent: self.ncaa_fb_recent.update()
            if self.ncaa_fb_upcoming: self.ncaa_fb_upcoming.update()
        
        # News manager fetches data when displayed, not during updates
        # if self.news_manager: self.news_manager.fetch_news_data()
        
        # Only update the currently active sport manager to prevent confusing logs
        # and reduce unnecessary API calls
        current_sport = None
        if self.current_display_mode.endswith('_live'):
            current_sport = self.current_display_mode.replace('_live', '')
        elif self.current_display_mode.endswith('_recent'):
            current_sport = self.current_display_mode.replace('_recent', '')
        elif self.current_display_mode.endswith('_upcoming'):
            current_sport = self.current_display_mode.replace('_upcoming', '')
        
        # Update only the currently active sport manager
        if current_sport == 'nhl':
            if self.nhl_live: self.nhl_live.update()
            if self.nhl_recent: self.nhl_recent.update()
            if self.nhl_upcoming: self.nhl_upcoming.update()
        elif current_sport == 'nba':
            if self.nba_live: self.nba_live.update()
            if self.nba_recent: self.nba_recent.update()
            if self.nba_upcoming: self.nba_upcoming.update()
        elif current_sport == 'wnba':
            if self.wnba_live: self.wnba_live.update()
            if self.wnba_recent: self.wnba_recent.update()
            if self.wnba_upcoming: self.wnba_upcoming.update()
        elif current_sport == 'mlb':
            if self.mlb_live: self.mlb_live.update()
            if self.mlb_recent: self.mlb_recent.update()
            if self.mlb_upcoming: self.mlb_upcoming.update()
        elif current_sport == 'milb':
            if self.milb_live: self.milb_live.update()
            if self.milb_recent: self.milb_recent.update()
            if self.milb_upcoming: self.milb_upcoming.update()
        elif current_sport == 'soccer':
            if self.soccer_live: self.soccer_live.update()
            if self.soccer_recent: self.soccer_recent.update()
            if self.soccer_upcoming: self.soccer_upcoming.update()
        elif current_sport == 'nfl':
            if self.nfl_live: self.nfl_live.update()
            if self.nfl_recent: self.nfl_recent.update()
            if self.nfl_upcoming: self.nfl_upcoming.update()
        elif current_sport == 'ncaa_fb':
            if self.ncaa_fb_live: self.ncaa_fb_live.update()
            if self.ncaa_fb_recent: self.ncaa_fb_recent.update()
            if self.ncaa_fb_upcoming: self.ncaa_fb_upcoming.update()
        elif current_sport == 'ncaa_baseball':
            if self.ncaa_baseball_live: self.ncaa_baseball_live.update()
            if self.ncaa_baseball_recent: self.ncaa_baseball_recent.update()
            if self.ncaa_baseball_upcoming: self.ncaa_baseball_upcoming.update()
        elif current_sport == 'ncaam_basketball':
            if self.ncaam_basketball_live: self.ncaam_basketball_live.update()
            if self.ncaam_basketball_recent: self.ncaam_basketball_recent.update()
            if self.ncaam_basketball_upcoming: self.ncaam_basketball_upcoming.update()
        elif current_sport == 'ncaaw_basketball':
            if self.ncaaw_basketball_live: self.ncaaw_basketball_live.update()
            if self.ncaaw_basketball_recent: self.ncaaw_basketball_recent.update()
            if self.ncaaw_basketball_upcoming: self.ncaaw_basketball_upcoming.update()
        elif current_sport == 'ncaam_hockey':
            if self.ncaam_hockey_live: self.ncaam_hockey_live.update()
            if self.ncaam_hockey_recent: self.ncaam_hockey_recent.update()
            if self.ncaam_hockey_upcoming: self.ncaam_hockey_upcoming.update()
        elif current_sport == 'ncaaw_hockey':
            if self.ncaaw_hockey_live: self.ncaaw_hockey_live.update()
            if self.ncaaw_hockey_recent: self.ncaaw_hockey_recent.update()
            if self.ncaaw_hockey_upcoming: self.ncaaw_hockey_upcoming.update()
        else:
            # If no specific sport is active, update all managers (fallback behavior)
            # This ensures data is available when switching to a sport
            if self.nhl_live: self.nhl_live.update()
            if self.nhl_recent: self.nhl_recent.update()
            if self.nhl_upcoming: self.nhl_upcoming.update()
            
            if self.nba_live: self.nba_live.update()
            if self.nba_recent: self.nba_recent.update()
            if self.nba_upcoming: self.nba_upcoming.update()
            
            if self.wnba_live: self.wnba_live.update()
            if self.wnba_recent: self.wnba_recent.update()
            if self.wnba_upcoming: self.wnba_upcoming.update()
            
            if self.mlb_live: self.mlb_live.update()
            if self.mlb_recent: self.mlb_recent.update()
            if self.mlb_upcoming: self.mlb_upcoming.update()
            
            if self.milb_live: self.milb_live.update()
            if self.milb_recent: self.milb_recent.update()
            if self.milb_upcoming: self.milb_upcoming.update()
            
            if self.soccer_live: self.soccer_live.update()
            if self.soccer_recent: self.soccer_recent.update()
            if self.soccer_upcoming: self.soccer_upcoming.update()

            if self.nfl_live: self.nfl_live.update()
            if self.nfl_recent: self.nfl_recent.update()
            if self.nfl_upcoming: self.nfl_upcoming.update()

            if self.ncaa_fb_live: self.ncaa_fb_live.update()
            if self.ncaa_fb_recent: self.ncaa_fb_recent.update()
            if self.ncaa_fb_upcoming: self.ncaa_fb_upcoming.update()

            if self.ncaa_baseball_live: self.ncaa_baseball_live.update()
            if self.ncaa_baseball_recent: self.ncaa_baseball_recent.update()
            if self.ncaa_baseball_upcoming: self.ncaa_baseball_upcoming.update()

            if self.ncaam_basketball_live: self.ncaam_basketball_live.update()
            if self.ncaam_basketball_recent: self.ncaam_basketball_recent.update()
            if self.ncaam_basketball_upcoming: self.ncaam_basketball_upcoming.update()

            if self.ncaaw_basketball_live: self.ncaaw_basketball_live.update()
            if self.ncaaw_basketball_recent: self.ncaaw_basketball_recent.update()
            if self.ncaaw_basketball_upcoming: self.ncaaw_basketball_upcoming.update()

            if self.ncaam_hockey_live: self.ncaam_hockey_live.update()
            if self.ncaam_hockey_recent: self.ncaam_hockey_recent.update()
            if self.ncaam_hockey_upcoming: self.ncaam_hockey_upcoming.update()

            if self.ncaaw_hockey_live: self.ncaaw_hockey_live.update()
            if self.ncaaw_hockey_recent: self.ncaaw_hockey_recent.update()
            if self.ncaaw_hockey_upcoming: self.ncaaw_hockey_upcoming.update()
        
        # Update plugin managers if plugin system is available
        if self.plugin_manager:
            for plugin_id, plugin in self.plugin_manager.get_all_plugins().items():
                if plugin.enabled:
                    try:
                        plugin.update()
                    except Exception as e:
                        logger.error(f"Error updating plugin {plugin_id}: {e}", exc_info=True)

    def _check_live_games(self) -> tuple:
        """
        Check if there are any live games available.
        Returns:
            tuple: (has_live_games, sport_type)
            sport_type will be 'nhl', 'nba', 'mlb', 'milb', 'soccer' or None
        """
        # Only include sports that are enabled in config
        live_checks = {}
        if 'nhl_scoreboard' in self.config and self.config['nhl_scoreboard'].get('enabled', False):
            live_checks['nhl'] = self.nhl_live and self.nhl_live.live_games
        if 'nba_scoreboard' in self.config and self.config['nba_scoreboard'].get('enabled', False):
            live_checks['nba'] = self.nba_live and self.nba_live.live_games
        if 'wnba_scoreboard' in self.config and self.config['wnba_scoreboard'].get('enabled', False):
            live_checks['wnba'] = self.wnba_live and self.wnba_live.live_games
        if 'mlb' in self.config and self.config['mlb'].get('enabled', False):
            live_checks['mlb'] = self.mlb_live and self.mlb_live.live_games
        if 'milb' in self.config and self.config['milb'].get('enabled', False):
            live_checks['milb'] = self.milb_live and self.milb_live.live_games
        if 'nfl_scoreboard' in self.config and self.config['nfl_scoreboard'].get('enabled', False):
            live_checks['nfl'] = self.nfl_live and self.nfl_live.live_games
        if 'soccer_scoreboard' in self.config and self.config['soccer_scoreboard'].get('enabled', False):
            live_checks['soccer'] = self.soccer_live and self.soccer_live.live_games
        if 'ncaa_fb_scoreboard' in self.config and self.config['ncaa_fb_scoreboard'].get('enabled', False):
            live_checks['ncaa_fb'] = self.ncaa_fb_live and self.ncaa_fb_live.live_games
        if 'ncaa_baseball_scoreboard' in self.config and self.config['ncaa_baseball_scoreboard'].get('enabled', False):
            live_checks['ncaa_baseball'] = self.ncaa_baseball_live and self.ncaa_baseball_live.live_games
        if 'ncaam_basketball_scoreboard' in self.config and self.config['ncaam_basketball_scoreboard'].get('enabled', False):
            live_checks['ncaam_basketball'] = self.ncaam_basketball_live and self.ncaam_basketball_live.live_games
        if 'ncaaw_basketball_scoreboard' in self.config and self.config['ncaaw_basketball_scoreboard'].get('enabled', False):
            live_checks['ncaaw_basketball'] = self.ncaaw_basketball_live and self.ncaaw_basketball_live.live_games
        if 'ncaam_hockey_scoreboard' in self.config and self.config['ncaam_hockey_scoreboard'].get('enabled', False):
            live_checks['ncaam_hockey'] = self.ncaam_hockey_live and self.ncaam_hockey_live.live_games
        if 'ncaaw_hockey_scoreboard' in self.config and self.config['ncaaw_hockey_scoreboard'].get('enabled', False):
            live_checks['ncaaw_hockey'] = self.ncaaw_hockey_live and self.ncaaw_hockey_live.live_games

        for sport, has_live_games in live_checks.items():
            if has_live_games:
                logger.debug(f"{sport.upper()} live games available")
                return True, sport
            
        return False, None

    def _get_team_games(self, team: str, sport: str = 'nhl', is_recent: bool = True) -> bool:
        """
        Get games for a specific team and update the current game.
        Args:
            team: Team abbreviation
            sport: 'nhl', 'nba', 'mlb', 'milb', or 'soccer'
            is_recent: Whether to look for recent or upcoming games
        Returns:
            bool: True if games were found and set
        """
        manager_recent = None
        manager_upcoming = None
        games_list_attr = 'games_list' # Default for NHL/NBA
        abbr_key_home = 'home_abbr'
        abbr_key_away = 'away_abbr'

        if sport == 'nhl':
            manager_recent = self.nhl_recent
            manager_upcoming = self.nhl_upcoming
        elif sport == 'nba':
            manager_recent = self.nba_recent
            manager_upcoming = self.nba_upcoming
        elif sport == 'wnba':
            manager_recent = self.wnba_recent
            manager_upcoming = self.wnba_upcoming
        elif sport == 'mlb':
            manager_recent = self.mlb_recent
            manager_upcoming = self.mlb_upcoming
            games_list_attr = 'recent_games' if is_recent else 'upcoming_games'
            abbr_key_home = 'home_team' # MLB uses different keys
            abbr_key_away = 'away_team'
        elif sport == 'milb':
            manager_recent = self.milb_recent
            manager_upcoming = self.milb_upcoming
            games_list_attr = 'recent_games' if is_recent else 'upcoming_games'
            abbr_key_home = 'home_team' # MiLB uses different keys
            abbr_key_away = 'away_team'
        elif sport == 'soccer':
            manager_recent = self.soccer_recent
            manager_upcoming = self.soccer_upcoming
            games_list_attr = 'games_list' if is_recent else 'upcoming_games' # Soccer uses games_list/upcoming_games
        elif sport == 'nfl':
            manager_recent = self.nfl_recent
            manager_upcoming = self.nfl_upcoming
        elif sport == 'ncaa_fb': # Add NCAA FB case
            manager_recent = self.ncaa_fb_recent
            manager_upcoming = self.ncaa_fb_upcoming
        else:
            logger.warning(f"Unsupported sport '{sport}' for team game check")
            return False

        manager = manager_recent if is_recent else manager_upcoming

        if manager and hasattr(manager, games_list_attr):
            game_list = getattr(manager, games_list_attr, [])
            for game in game_list:
                # Need to handle potential missing keys gracefully
                home_team_abbr = game.get(abbr_key_home)
                away_team_abbr = game.get(abbr_key_away)
                if home_team_abbr == team or away_team_abbr == team:
                    manager.current_game = game
                    return True
        return False


    def _has_team_games(self, sport: str = 'nhl') -> bool:
        """Check if there are any games for favorite teams."""
        favorite_teams = []
        manager_recent = None
        manager_upcoming = None
        
        if sport == 'nhl':
            favorite_teams = self.nhl_favorite_teams
            manager_recent = self.nhl_recent
            manager_upcoming = self.nhl_upcoming
        elif sport == 'nba':
            favorite_teams = self.nba_favorite_teams
            manager_recent = self.nba_recent
            manager_upcoming = self.nba_upcoming
        elif sport == 'wnba':
            favorite_teams = self.wnba_favorite_teams
            manager_recent = self.wnba_recent
            manager_upcoming = self.wnba_upcoming
        elif sport == 'mlb':
            favorite_teams = self.mlb_favorite_teams
            manager_recent = self.mlb_recent
            manager_upcoming = self.mlb_upcoming
        elif sport == 'milb':
            favorite_teams = self.config.get('milb_scoreboard', {}).get('favorite_teams', [])
            manager_recent = self.milb_recent
            manager_upcoming = self.milb_upcoming
        elif sport == 'soccer':
            favorite_teams = self.soccer_favorite_teams
            manager_recent = self.soccer_recent
            manager_upcoming = self.soccer_upcoming
        elif sport == 'nfl':
            favorite_teams = self.nfl_favorite_teams
            manager_recent = self.nfl_recent
            manager_upcoming = self.nfl_upcoming
        elif sport == 'ncaa_fb': # Add NCAA FB case
            favorite_teams = self.ncaa_fb_favorite_teams
            manager_recent = self.ncaa_fb_recent
            manager_upcoming = self.ncaa_fb_upcoming
            
        return bool(favorite_teams and (manager_recent or manager_upcoming))

    # --- SCHEDULING METHODS ---
    def _load_schedule_config(self):
        """Load schedule configuration once at startup."""
        schedule_config = self.config.get('schedule', {})
        self.schedule_enabled = schedule_config.get('enabled', False)
        try:
            self.start_time = datetime.strptime(schedule_config.get('start_time', '07:00'), '%H:%M').time()
            self.end_time = datetime.strptime(schedule_config.get('end_time', '22:00'), '%H:%M').time()
            logger.info(f"Schedule loaded: enabled={self.schedule_enabled}, start={self.start_time}, end={self.end_time}")
        except (ValueError, TypeError):
            logger.warning("Invalid time format in schedule config. Using defaults.")
            self.start_time = time_obj(7, 0)
            self.end_time = time_obj(22, 0)

    def _check_schedule(self):
        """Check if the display should be active based on the schedule."""
        if not self.schedule_enabled:
            if not self.is_display_active:
                logger.info("Schedule is disabled. Activating display.")
                self.is_display_active = True
            return

        now_time = datetime.now().time()
        
        # Handle overnight schedules
        if self.start_time <= self.end_time:
            should_be_active = self.start_time <= now_time < self.end_time
        else: 
            should_be_active = now_time >= self.start_time or now_time < self.end_time

        if should_be_active and not self.is_display_active:
            logger.info("Within scheduled time. Activating display.")
            self.is_display_active = True
            self.force_clear = True # Force a redraw
        elif not should_be_active and self.is_display_active:
            logger.info("Outside of scheduled time. Deactivating display.")
            self.display_manager.clear()
            self.is_display_active = False

    def show_on_demand(self, mode: str, duration: float = None, pinned: bool = False) -> bool:
        """
        Display a specific mode on-demand, interrupting normal rotation.
        
        Args:
            mode: The display mode to show (e.g., 'weather', 'hockey_live')
            duration: How long to show in seconds (None = use mode's default, 0 = indefinite)
            pinned: If True, stays on this mode until unpinned
            
        Returns:
            True if mode exists and was activated, False otherwise
        """
        # Check if mode exists (either in available_modes or plugin_modes)
        if mode not in self.available_modes and mode not in self.plugin_modes:
            logger.warning(f"On-demand mode '{mode}' not found in available modes")
            return False
        
        self.on_demand_mode = mode
        self.on_demand_duration = duration
        self.on_demand_start_time = time.time()
        self.on_demand_pinned = pinned
        self.force_clear = True
        
        logger.info(f"On-demand display activated: {mode} (duration: {duration}s, pinned: {pinned})")
        return True
    
    def clear_on_demand(self) -> None:
        """Clear on-demand display and return to normal rotation."""
        if self.on_demand_mode:
            logger.info(f"Clearing on-demand display: {self.on_demand_mode}")
            self.on_demand_mode = None
            self.on_demand_duration = None
            self.on_demand_start_time = None
            self.on_demand_pinned = False
            self.force_clear = True
    
    def is_on_demand_active(self) -> bool:
        """Check if on-demand display is currently active."""
        return self.on_demand_mode is not None
    
    def get_on_demand_info(self) -> dict:
        """Get information about current on-demand display."""
        if not self.is_on_demand_active():
            return {'active': False}
        
        elapsed = time.time() - self.on_demand_start_time if self.on_demand_start_time else 0
        remaining = None
        if self.on_demand_duration is not None and self.on_demand_duration > 0:
            remaining = max(0, self.on_demand_duration - elapsed)
        
        return {
            'active': True,
            'mode': self.on_demand_mode,
            'duration': self.on_demand_duration,
            'elapsed': elapsed,
            'remaining': remaining,
            'pinned': self.on_demand_pinned
        }
    
    def _get_live_priority_plugins(self) -> list:
        """Get list of plugins that have live priority and live content.
        
        Returns:
            List of (plugin_id, plugin_instance, live_modes) tuples for plugins with live content
        """
        if not self.plugin_manager:
            return []
        
        live_plugins = []
        for plugin_id, plugin_instance in self.plugin_manager.plugins.items():
            if not plugin_instance:
                continue
            
            # Check if plugin has live priority enabled and has live content
            if plugin_instance.has_live_priority() and plugin_instance.has_live_content():
                live_modes = plugin_instance.get_live_modes()
                live_plugins.append((plugin_id, plugin_instance, live_modes))
                
        return live_plugins
    
    def _get_all_live_modes(self) -> list:
        """Get all possible live modes from all plugins.
        
        Returns:
            List of mode names that are considered live modes
        """
        if not self.plugin_manager:
            return []
        
        live_modes = []
        for plugin_id, plugin_instance in self.plugin_manager.plugins.items():
            if not plugin_instance:
                continue
            
            if plugin_instance.has_live_priority():
                live_modes.extend(plugin_instance.get_live_modes())
        
        return live_modes
    
    def _update_live_modes_in_rotation(self):
        """Update live modes in rotation based on plugin live priority.
        
        Checks all plugins with live priority enabled to see if they have live content.
        Manages rotation of live modes automatically.
        """
        if not self.plugin_manager:
            return
        
        # Get all loaded plugins
        for plugin_id, plugin_instance in self.plugin_manager.plugins.items():
            if not plugin_instance:
                continue
                
            # Check if plugin has live priority enabled
            if not plugin_instance.has_live_priority():
                continue
            
            # Check if plugin has live content
            has_live = plugin_instance.has_live_content()
            live_modes = plugin_instance.get_live_modes() if has_live else []
            
            # Add or remove live modes from rotation based on live content
            for mode in live_modes:
                if has_live and mode not in self.available_modes:
                    self.available_modes.append(mode)
                    logger.debug(f"Added live mode to rotation: {mode} (plugin: {plugin_id})")
                elif not has_live and mode in self.available_modes:
                    self.available_modes.remove(mode)
                    logger.debug(f"Removed live mode from rotation: {mode} (plugin: {plugin_id})")

    def run(self):
        """Run the display controller, switching between displays."""
        if not self.available_modes:
            logger.warning("No display modes are enabled. Exiting.")
            self.display_manager.cleanup()
            return
             
        try:
            logger.info("Clearing cache and refetching data to prevent stale data issues...")
            self.cache_manager.clear_cache()
            self._update_modules()
            logger.info("Cache cleared, waiting 5 seconds for fresh data fetch...")
            time.sleep(5)
            self.current_display_mode = self.available_modes[self.current_mode_index] if self.available_modes else 'none'
            while True:
                current_time = time.time()

                # Check the schedule (no config reload needed)
                self._check_schedule()
                if not self.is_display_active:
                    time.sleep(60)
                    continue
                
                # Update data for all modules first
                self._update_modules()
                
                # Process any deferred updates that may have accumulated
                self.display_manager.process_deferred_updates()
                
                # Update live modes in rotation if needed
                self._update_live_modes_in_rotation()

                manager_to_display = None
                
                # --- On-Demand Display (Highest Priority) ---
                if self.is_on_demand_active():
                    # Check if on-demand duration has expired (if not pinned)
                    if not self.on_demand_pinned and self.on_demand_duration is not None:
                        if self.on_demand_duration > 0:  # 0 means indefinite
                            elapsed = current_time - self.on_demand_start_time
                            if elapsed >= self.on_demand_duration:
                                logger.info(f"On-demand display expired after {elapsed:.1f}s")
                                self.clear_on_demand()
                    
                    # If still active, display the on-demand mode
                    if self.is_on_demand_active():
                        if self.current_display_mode != self.on_demand_mode:
                            self.current_display_mode = self.on_demand_mode
                            self.force_clear = True
                            self.last_switch = current_time
                        # Skip normal rotation logic - on-demand has control
                        # Continue to display section below

                # Check for live priority takeover from plugins (only if no on-demand)
                live_priority_plugins = self._get_live_priority_plugins()
                live_priority_takeover = len(live_priority_plugins) > 0 and not self.is_on_demand_active()
                is_currently_live = self.current_display_mode in self._get_all_live_modes()
                
                # --- Live Priority Takeover Logic ---
                if live_priority_takeover:
                    # Get all live modes from plugins with live content
                    all_live_modes = []
                    for plugin_id, plugin_instance, live_modes in live_priority_plugins:
                        all_live_modes.extend(live_modes)
                    
                    if is_currently_live:
                        # Already showing live content - check if we need to rotate
                        if self.current_display_mode in all_live_modes:
                            # Current mode is still valid live content
                            current_duration = self.get_current_duration()
                            if current_time - self.last_switch >= current_duration:
                                # Rotate to next live mode
                                current_index = all_live_modes.index(self.current_display_mode)
                                next_index = (current_index + 1) % len(all_live_modes)
                                self.current_display_mode = all_live_modes[next_index]
                                self.force_clear = True
                                self.last_switch = current_time
                                logger.info(f"Rotating live priority modes: {all_live_modes[current_index]} -> {self.current_display_mode}")
                        else:
                            # Current mode no longer has live content - switch to first live mode
                            self.current_display_mode = all_live_modes[0]
                            self.force_clear = True
                            self.last_switch = current_time
                            logger.info(f"Switching to live priority mode: {self.current_display_mode}")
                    else:
                        # Not currently showing live content - take over!
                        previous_mode = self.current_display_mode
                        self.current_display_mode = all_live_modes[0]
                        self.force_clear = True
                        self.last_switch = current_time
                        logger.info(f"Live priority takeover! {previous_mode} -> {self.current_display_mode}")
                
                # --- Normal Rotation Logic (when no live priority takeover and no on-demand) ---
                if not live_priority_takeover and not self.is_on_demand_active():
                        # Track current mode before switching (for music manager deactivation)
                        previous_mode = self.current_display_mode
                        
                        # No live_priority takeover, regular rotation
                        needs_switch = False
                        if self.current_display_mode.endswith('_live'):
                            # For live modes without live_priority, check if duration has elapsed
                            if current_time - self.last_switch >= self.get_current_duration():
                                needs_switch = True
                                self.current_mode_index = (self.current_mode_index + 1) % len(self.available_modes)
                                new_mode_after_timer = self.available_modes[self.current_mode_index]
                                if previous_mode == 'music' and self.music_manager and new_mode_after_timer != 'music':
                                    self.music_manager.deactivate_music_display()
                                if self.current_display_mode != new_mode_after_timer:
                                    logger.info(f"Switching to {new_mode_after_timer} from {self.current_display_mode}")
                                self.current_display_mode = new_mode_after_timer
                                # Reset logged duration when mode changes
                                if hasattr(self, '_last_logged_duration'):
                                    delattr(self, '_last_logged_duration')
                        elif current_time - self.last_switch >= self.get_current_duration() or self.force_change:
                            self.force_change = False
                            if self.current_display_mode == 'calendar' and self.calendar:
                                self.calendar.advance_event()
                            elif self.current_display_mode == 'of_the_day' and self.of_the_day:
                                self.of_the_day.advance_item()
                            needs_switch = True
                            self.current_mode_index = (self.current_mode_index + 1) % len(self.available_modes)
                            new_mode_after_timer = self.available_modes[self.current_mode_index]
                            if previous_mode == 'music' and self.music_manager and new_mode_after_timer != 'music':
                                self.music_manager.deactivate_music_display()
                            if self.current_display_mode != new_mode_after_timer:
                                logger.info(f"Switching to {new_mode_after_timer} from {self.current_display_mode}")
                            self.current_display_mode = new_mode_after_timer
                            # Reset logged duration when mode changes
                            if hasattr(self, '_last_logged_duration'):
                                delattr(self, '_last_logged_duration')
                        else:
                            needs_switch = False
                        if needs_switch:
                            self.force_clear = True
                            self.last_switch = current_time
                        else:
                            self.force_clear = False
                        # Only set manager_to_display if it hasn't been set by live priority logic
                        if manager_to_display is None:
                                if self.current_display_mode == 'clock' and self.clock:
                                    manager_to_display = self.clock
                                elif self.current_display_mode == 'weather_current' and self.weather:
                                    manager_to_display = self.weather
                                elif self.current_display_mode == 'weather_hourly' and self.weather:
                                    manager_to_display = self.weather
                                elif self.current_display_mode == 'weather_daily' and self.weather:
                                    manager_to_display = self.weather
                                elif self.current_display_mode == 'stocks' and self.stocks:
                                    manager_to_display = self.stocks
                                elif self.current_display_mode == 'stock_news' and self.news:
                                    manager_to_display = self.news
                                elif self.current_display_mode == 'odds_ticker' and self.odds_ticker:
                                    manager_to_display = self.odds_ticker
                                elif self.current_display_mode == 'leaderboard' and self.leaderboard:
                                    manager_to_display = self.leaderboard
                                elif self.current_display_mode == 'calendar' and self.calendar:
                                    manager_to_display = self.calendar
                                elif self.current_display_mode == 'youtube' and self.youtube:
                                    manager_to_display = self.youtube
                                elif self.current_display_mode == 'text_display' and self.text_display:
                                    manager_to_display = self.text_display
                                elif self.current_display_mode == 'static_image' and self.static_image:
                                    manager_to_display = self.static_image
                                elif self.current_display_mode == 'of_the_day' and self.of_the_day:
                                    manager_to_display = self.of_the_day
                                elif self.current_display_mode == 'news_manager' and self.news_manager:
                                    manager_to_display = self.news_manager
                                elif self.current_display_mode == 'nhl_recent' and self.nhl_recent:
                                    manager_to_display = self.nhl_recent
                                elif self.current_display_mode == 'nhl_upcoming' and self.nhl_upcoming:
                                    manager_to_display = self.nhl_upcoming
                                elif self.current_display_mode == 'nba_recent' and self.nba_recent:
                                    manager_to_display = self.nba_recent
                                elif self.current_display_mode == 'nba_upcoming' and self.nba_upcoming:
                                    manager_to_display = self.nba_upcoming
                                elif self.current_display_mode == 'wnba_recent' and self.wnba_recent:
                                    manager_to_display = self.wnba_recent
                                elif self.current_display_mode == 'wnba_upcoming' and self.wnba_upcoming:
                                    manager_to_display = self.wnba_upcoming
                                elif self.current_display_mode == 'nfl_recent' and self.nfl_recent:
                                    manager_to_display = self.nfl_recent
                                elif self.current_display_mode == 'nfl_upcoming' and self.nfl_upcoming:
                                    manager_to_display = self.nfl_upcoming
                                elif self.current_display_mode == 'ncaa_fb_recent' and self.ncaa_fb_recent:
                                    manager_to_display = self.ncaa_fb_recent
                                elif self.current_display_mode == 'ncaa_fb_upcoming' and self.ncaa_fb_upcoming:
                                    manager_to_display = self.ncaa_fb_upcoming
                                elif self.current_display_mode == 'ncaa_baseball_recent' and self.ncaa_baseball_recent:
                                    manager_to_display = self.ncaa_baseball_recent
                                elif self.current_display_mode == 'ncaa_baseball_upcoming' and self.ncaa_baseball_upcoming:
                                    manager_to_display = self.ncaa_baseball_upcoming
                                elif self.current_display_mode == 'ncaam_basketball_recent' and self.ncaam_basketball_recent:
                                    manager_to_display = self.ncaam_basketball_recent
                                elif self.current_display_mode == 'ncaam_basketball_upcoming' and self.ncaam_basketball_upcoming:
                                    manager_to_display = self.ncaam_basketball_upcoming
                                elif self.current_display_mode == 'ncaaw_basketball_recent' and self.ncaaw_basketball_recent:
                                    manager_to_display = self.ncaaw_basketball_recent
                                elif self.current_display_mode == 'ncaaw_basketball_upcoming' and self.ncaaw_basketball_upcoming:
                                    manager_to_display = self.ncaaw_basketball_upcoming
                                elif self.current_display_mode == 'mlb_recent' and self.mlb_recent:
                                    manager_to_display = self.mlb_recent
                                elif self.current_display_mode == 'mlb_upcoming' and self.mlb_upcoming:
                                    manager_to_display = self.mlb_upcoming
                                elif self.current_display_mode == 'milb_recent' and self.milb_recent:
                                    manager_to_display = self.milb_recent
                                elif self.current_display_mode == 'milb_upcoming' and self.milb_upcoming:
                                    manager_to_display = self.milb_upcoming
                                elif self.current_display_mode == 'soccer_recent' and self.soccer_recent:
                                    manager_to_display = self.soccer_recent
                                elif self.current_display_mode == 'soccer_upcoming' and self.soccer_upcoming:
                                    manager_to_display = self.soccer_upcoming
                                elif self.current_display_mode == 'music' and self.music_manager:
                                    manager_to_display = self.music_manager
                                elif self.current_display_mode == 'nhl_live' and self.nhl_live:
                                    manager_to_display = self.nhl_live
                                elif self.current_display_mode == 'nba_live' and self.nba_live:
                                    manager_to_display = self.nba_live
                                elif self.current_display_mode == 'wnba_live' and self.wnba_live:
                                    manager_to_display = self.wnba_live
                                elif self.current_display_mode == 'nfl_live' and self.nfl_live:
                                    manager_to_display = self.nfl_live
                                elif self.current_display_mode == 'ncaa_fb_live' and self.ncaa_fb_live:
                                    manager_to_display = self.ncaa_fb_live
                                elif self.current_display_mode == 'ncaa_baseball_live' and self.ncaa_baseball_live:
                                    manager_to_display = self.ncaa_baseball_live
                                elif self.current_display_mode == 'ncaam_basketball_live' and self.ncaam_basketball_live:
                                    manager_to_display = self.ncaam_basketball_live
                                elif self.current_display_mode == 'ncaaw_basketball_live' and self.ncaaw_basketball_live:
                                    manager_to_display = self.ncaaw_basketball_live
                                elif self.current_display_mode == 'ncaam_hockey_live' and self.ncaam_hockey_live:
                                    manager_to_display = self.ncaam_hockey_live
                                elif self.current_display_mode == 'ncaam_hockey_recent' and self.ncaam_hockey_recent:
                                    manager_to_display = self.ncaam_hockey_recent
                                elif self.current_display_mode == 'ncaam_hockey_upcoming' and self.ncaam_hockey_upcoming:
                                    manager_to_display = self.ncaam_hockey_upcoming
                                elif self.current_display_mode == 'ncaaw_hockey_live' and self.ncaaw_hockey_live:
                                    manager_to_display = self.ncaaw_hockey_live
                                elif self.current_display_mode == 'ncaaw_hockey_recent' and self.ncaaw_hockey_recent:
                                    manager_to_display = self.ncaaw_hockey_recent
                                elif self.current_display_mode == 'ncaaw_hockey_upcoming' and self.ncaaw_hockey_upcoming:
                                    manager_to_display = self.ncaaw_hockey_upcoming
                                elif self.current_display_mode == 'mlb_live' and self.mlb_live:
                                    manager_to_display = self.mlb_live
                                elif self.current_display_mode == 'milb_live' and self.milb_live:
                                    manager_to_display = self.milb_live
                                elif self.current_display_mode == 'soccer_live' and self.soccer_live:
                                    manager_to_display = self.soccer_live

                # --- Perform Display Update ---
                try:
                    # Log which display is being shown
                    if self.current_display_mode != getattr(self, '_last_logged_mode', None):
                        logger.info(f"Showing {self.current_display_mode}")
                        self._last_logged_mode = self.current_display_mode
                    
                    # Only log manager type when it changes to reduce spam
                    current_manager_type = type(manager_to_display).__name__ if manager_to_display else 'None'
                    if current_manager_type != getattr(self, '_last_logged_manager_type', None):
                        logger.info(f"manager_to_display is {current_manager_type}")
                        self._last_logged_manager_type = current_manager_type
                    
                    # Try plugin-first dispatch
                    if self._try_display_plugin(self.current_display_mode, force_clear=self.force_clear):
                        # Plugin handled it, reset force_clear and continue
                        if self.force_clear:
                            self.force_clear = False
                    elif self.current_display_mode == 'music' and self.music_manager:
                        # Call MusicManager's display method
                        self.music_manager.display(force_clear=self.force_clear)
                        # Reset force_clear if it was true for this mode
                        if self.force_clear:
                            self.force_clear = False
                    elif manager_to_display:
                        # Only log display attempts occasionally to reduce log spam
                        if not hasattr(self, '_last_display_log') or time.time() - self._last_display_log > 30:
                            logger.debug(f"Displaying mode: {self.current_display_mode} using {type(manager_to_display).__name__}")
                            self._last_display_log = time.time()

                        # Check if this is a plugin manager
                        if hasattr(manager_to_display, 'display') and hasattr(manager_to_display, 'plugin_id'):
                            # This is a plugin - use the generic display method
                            manager_to_display.display(force_clear=self.force_clear)
                            # Reset force_clear if it was true for this mode
                            if self.force_clear:
                                self.force_clear = False
                        else:
                            # This is a legacy manager - use the specific display methods
                            if self.current_display_mode == 'clock':
                                manager_to_display.display_time(force_clear=self.force_clear)
                            elif self.current_display_mode == 'weather_current':
                                manager_to_display.display_weather(force_clear=self.force_clear)
                            elif self.current_display_mode == 'weather_hourly':
                                manager_to_display.display_hourly_forecast(force_clear=self.force_clear)
                            elif self.current_display_mode == 'weather_daily':
                                manager_to_display.display_daily_forecast(force_clear=self.force_clear)
                            elif self.current_display_mode == 'stocks':
                                manager_to_display.display_stocks(force_clear=self.force_clear)
                            elif self.current_display_mode == 'stock_news':
                                manager_to_display.display_news() # Assumes internal clearing
                            elif self.current_display_mode in {'odds_ticker', 'leaderboard'}:
                                try:
                                    manager_to_display.display(force_clear=self.force_clear)
                                except StopIteration:
                                    self.force_change = True
                            elif self.current_display_mode == 'calendar':
                                manager_to_display.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'youtube':
                                manager_to_display.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'text_display':
                                manager_to_display.display() # Assumes internal clearing
                            elif self.current_display_mode == 'static_image':
                                manager_to_display.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'of_the_day':
                                manager_to_display.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'news_manager':
                                manager_to_display.display_news()
                            elif self.current_display_mode == 'ncaa_fb_upcoming' and self.ncaa_fb_upcoming:
                                self.ncaa_fb_upcoming.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaam_basketball_recent' and self.ncaam_basketball_recent:
                                self.ncaam_basketball_recent.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaam_basketball_upcoming' and self.ncaam_basketball_upcoming:
                                self.ncaam_basketball_upcoming.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaaw_basketball_recent' and self.ncaaw_basketball_recent:
                                self.ncaaw_basketball_recent.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaaw_basketball_upcoming' and self.ncaaw_basketball_upcoming:
                                self.ncaaw_basketball_upcoming.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaa_baseball_recent' and self.ncaa_baseball_recent:
                                self.ncaa_baseball_recent.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaa_baseball_upcoming' and self.ncaa_baseball_upcoming:
                                self.ncaa_baseball_upcoming.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaam_hockey_recent' and self.ncaam_hockey_recent:
                                self.ncaam_hockey_recent.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaam_hockey_upcoming' and self.ncaam_hockey_upcoming:
                                self.ncaam_hockey_upcoming.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaaw_hockey_recent' and self.ncaaw_hockey_recent:
                                self.ncaaw_hockey_recent.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'ncaaw_hockey_upcoming' and self.ncaaw_hockey_upcoming:
                                self.ncaaw_hockey_upcoming.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'milb_live' and self.milb_live and len(self.milb_live.live_games) > 0:
                                logger.debug(f"[DisplayController] Calling MiLB live display with {len(self.milb_live.live_games)} live games")
                                # Update data before displaying for live managers
                                self.milb_live.update()
                                self.milb_live.display(force_clear=self.force_clear)
                            elif self.current_display_mode == 'milb_live' and self.milb_live:
                                logger.debug(f"[DisplayController] MiLB live manager exists but has {len(self.milb_live.live_games)} live games, switching to next mode")
                                # Switch to next mode since there are no live games
                                self.current_mode_index = (self.current_mode_index + 1) % len(self.available_modes)
                                self.current_display_mode = self.available_modes[self.current_mode_index]
                                self.force_clear = True
                                self.last_switch = current_time
                                logger.info(f"[DisplayController] Switched from milb_live (no games) to {self.current_display_mode}")
                            elif hasattr(manager_to_display, 'display'): # General case for most managers
                                # Special handling for live managers that need update before display
                                if self.current_display_mode.endswith('_live') and hasattr(manager_to_display, 'update'):
                                    manager_to_display.update()
                                # Only log display method calls occasionally to reduce spam
                                current_time = time.time()
                                if not hasattr(self, '_last_display_method_log_time') or current_time - getattr(self, '_last_display_method_log_time', 0) >= 30:
                                    logger.info(f"Calling display method for {self.current_display_mode}")
                                    self._last_display_method_log_time = current_time
                                manager_to_display.display(force_clear=self.force_clear)
                            else:
                                logger.warning(f"Manager {type(manager_to_display).__name__} for mode {self.current_display_mode} does not have a standard 'display' method.")
                        
                        # Reset force_clear *after* a successful display call that used it
                        # Important: Only reset if the display method *might* have used it.
                        # Internal clearing methods (news, text) don't necessitate resetting it here.
                        if self.force_clear and self.current_display_mode not in ['stock_news', 'text_display']:
                            self.force_clear = False 
                    elif self.current_display_mode != 'none':
                         logger.warning(f"No manager found or selected for display mode: {self.current_display_mode}")
                         # If we can't display the current mode, switch to the next available mode
                         if self.available_modes:
                             self.current_mode_index = (self.current_mode_index + 1) % len(self.available_modes)
                             self.current_display_mode = self.available_modes[self.current_mode_index]
                             logger.info(f"Switching to next available mode: {self.current_display_mode}")
                         else:
                             logger.error("No available display modes found!")

                except Exception as e:
                    logger.error(f"Error during display update for mode {self.current_display_mode}: {e}", exc_info=True)
                    # Force clear on the next iteration after an error to be safe
                    self.force_clear = True 

                # Add a short sleep to prevent high CPU usage but ruin scrolling text
                # time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Display controller stopped by user")
        except Exception as e:
            logger.error(f"Critical error in display controller run loop: {e}", exc_info=True)
        finally:
            logger.info("Cleaning up display manager...")
            self.display_manager.cleanup()
            if self.music_manager: # Check if music_manager object exists
                logger.info("Stopping music polling...")
                self.music_manager.stop_polling()
            logger.info("Cleanup complete.")

def main():
    controller = DisplayController()
    controller.run()

if __name__ == "__main__":
    main()