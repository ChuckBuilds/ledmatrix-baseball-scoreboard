"""
Baseball Scoreboard Plugin for LEDMatrix

Displays live, recent, and upcoming baseball games across MLB, MiLB, and NCAA Baseball.
Shows real-time scores, game status, innings, and team logos.

Features:
- Multiple league support (MLB, MiLB, NCAA Baseball)
- Live game tracking with innings and time
- Recent game results
- Upcoming game schedules
- Favorite team prioritization
- Background data fetching
- Granular per-league configuration

API Version: 1.0.0
"""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from pathlib import Path

from PIL import Image, ImageDraw

from src.plugin_system.base_plugin import BasePlugin

# Import modular components
from data_manager import BaseballDataManager
from game_filter import BaseballGameFilter
from logo_manager import BaseballLogoManager
from odds_manager import BaseballOddsManager
from rankings_manager import BaseballRankingsManager
from scorebug_renderer import BaseballScorebugRenderer

# Import dynamic team resolver
try:
    from src.dynamic_team_resolver import DynamicTeamResolver
except ImportError:
    DynamicTeamResolver = None

logger = logging.getLogger(__name__)


class BaseballScoreboardPlugin(BasePlugin):
    """
    Baseball scoreboard plugin for displaying games across multiple leagues.

    Supports MLB, MiLB, and NCAA Baseball with live, recent, and upcoming game modes.
    Orchestrates all modular components (DataManager, GameFilter, ScorebugRenderer, etc.)
    """

    def __init__(self, plugin_id: str, config: Dict[str, Any],
                 display_manager, cache_manager, plugin_manager):
        """Initialize the baseball scoreboard plugin."""
        super().__init__(plugin_id, config, display_manager, cache_manager, plugin_manager)

        # Initialize modular components
        self.data_manager = BaseballDataManager(cache_manager, self.logger)
        self.game_filter = BaseballGameFilter(self.logger)
        self.logo_manager = BaseballLogoManager(display_manager, self.logger)
        self.odds_manager = BaseballOddsManager(cache_manager, cache_manager.config_manager if hasattr(cache_manager, 'config_manager') else None, self.logger)
        self.rankings_manager = BaseballRankingsManager(self.logger)
        self.scorebug_renderer = BaseballScorebugRenderer(
            display_manager, self.logo_manager, self.odds_manager,
            self.rankings_manager, self.logger
        )

        # Initialize dynamic team resolver
        if DynamicTeamResolver:
            self.dynamic_resolver = DynamicTeamResolver()
        else:
            self.dynamic_resolver = None
            self.logger.warning("DynamicTeamResolver not available")

        # Build comprehensive league configurations with ALL granular settings
        self.leagues = self._build_league_configs(config)

        # Global settings
        self.global_config = config
        self.display_duration = config.get('display_duration', 15)

        # Mode cycling (like football plugin)
        self.current_mode_index = 0
        self.last_mode_switch = 0
        self.modes = self._get_available_modes()

        # Per-league state management
        # Structure: league_key -> mode -> state
        self.league_state = {}
        for league_key in self.leagues.keys():
            self.league_state[league_key] = {
                'live': {
                    'games_list': [],
                    'current_game': None,
                    'current_index': 0,
                    'last_update': 0,
                    'last_game_switch': 0,
                },
                'recent': {
                    'games_list': [],
                    'current_game': None,
                    'current_index': 0,
                    'last_update': 0,
                    'last_game_switch': 0,
                },
                'upcoming': {
                    'games_list': [],
                    'current_game': None,
                    'current_index': 0,
                    'last_update': 0,
                    'last_game_switch': 0,
                }
            }

        # Resolve favorite teams for each league
        self._resolve_favorite_teams()

        # Load MiLB team mapping if MiLB is enabled
        if self.leagues.get('milb', {}).get('enabled', False):
            self.data_manager.load_milb_team_mapping()

        # Initialize test mode games if enabled
        self._initialize_test_games()

        # Register fonts
        self._register_fonts()

        # Log enabled leagues and their settings
        enabled_leagues = []
        for league_key, league_config in self.leagues.items():
            if league_config.get('enabled', False):
                enabled_leagues.append(league_key)

        self.logger.info("Baseball scoreboard plugin initialized")
        self.logger.info("Enabled leagues: %s", enabled_leagues)
        for league_key in enabled_leagues:
            league_config = self.leagues[league_key]
            self.logger.info("  %s: live_priority=%s, favorite_teams=%d", league_key,
                           league_config.get('live_priority', False),
                           len(league_config.get('favorite_teams', [])))

        self.initialized = True

    def _build_league_configs(self, config: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Build comprehensive league configurations with ALL granular settings.

        Args:
            config: Plugin configuration dictionary

        Returns:
            Dictionary of league configurations
        """
        leagues = {}

        # MLB Configuration
        leagues['mlb'] = {
            'enabled': config.get('mlb_enabled', True),
            'live_priority': config.get('mlb_live_priority', False),
            'live_game_duration': config.get('mlb_live_game_duration', 20),
            'test_mode': config.get('mlb_test_mode', False),
            'update_interval_seconds': config.get('mlb_update_interval_seconds', 60),
            'live_update_interval': config.get('mlb_live_update_interval', 15),
            'recent_update_interval': config.get('mlb_recent_update_interval', 3600),
            'upcoming_update_interval': config.get('mlb_upcoming_update_interval', 3600),
            'recent_games_to_show': config.get('mlb_recent_games_to_show', 5),
            'upcoming_games_to_show': config.get('mlb_upcoming_games_to_show', 10),
            'show_records': config.get('mlb_show_records', False),
            'show_ranking': config.get('mlb_show_ranking', False),
            'show_odds': config.get('mlb_show_odds', False),
            'show_series_summary': config.get('mlb_show_series_summary', False),
            'show_favorite_teams_only': config.get('mlb_show_favorite_teams_only', False),
            'show_all_live': config.get('mlb_show_all_live', False),
            'favorite_teams': config.get('mlb_favorite_teams', []),
            'display_modes': {
                'live': config.get('mlb_display_modes_live', True),
                'recent': config.get('mlb_display_modes_recent', True),
                'upcoming': config.get('mlb_display_modes_upcoming', True)
            },
            'logo_dir': config.get('mlb_logo_dir', 'assets/sports/mlb_logos'),
            'background_service': {
                'enabled': config.get('mlb_background_service_enabled', True),
                'max_workers': config.get('mlb_background_service_max_workers', 3),
                'request_timeout': config.get('mlb_background_service_request_timeout', 30),
                'max_retries': config.get('mlb_background_service_max_retries', 3),
                'priority': config.get('mlb_background_service_priority', 2)
            }
        }

        # MiLB Configuration
        leagues['milb'] = {
            'enabled': config.get('milb_enabled', False),
            'live_priority': config.get('milb_live_priority', False),
            'live_game_duration': config.get('milb_live_game_duration', 30),
            'test_mode': config.get('milb_test_mode', False),
            'update_interval_seconds': config.get('milb_update_interval_seconds', 3600),
            'live_update_interval': config.get('milb_live_update_interval', 30),
            'recent_update_interval': config.get('milb_recent_update_interval', 3600),
            'upcoming_update_interval': config.get('milb_upcoming_update_interval', 3600),
            'recent_games_to_show': config.get('milb_recent_games_to_show', 5),
            'upcoming_games_to_show': config.get('milb_upcoming_games_to_show', 10),
            'show_records': config.get('milb_show_records', True),
            'show_ranking': config.get('milb_show_ranking', False),
            'show_odds': config.get('milb_show_odds', False),
            'show_series_summary': config.get('milb_show_series_summary', False),
            'show_favorite_teams_only': config.get('milb_show_favorite_teams_only', False),
            'show_all_live': config.get('milb_show_all_live', False),
            'favorite_teams': config.get('milb_favorite_teams', []),
            'display_modes': {
                'live': config.get('milb_display_modes_live', True),
                'recent': config.get('milb_display_modes_recent', True),
                'upcoming': config.get('milb_display_modes_upcoming', True)
            },
            'logo_dir': config.get('milb_logo_dir', 'assets/sports/milb_logos'),
            'upcoming_fetch_days': config.get('milb_upcoming_fetch_days', 7),
            'sport_ids': config.get('milb_sport_ids', [10, 11, 12, 13, 14, 15]),
            'team_mapping_path': config.get('milb_team_mapping_path'),
            'background_service': {
                'enabled': config.get('milb_background_service_enabled', True),
                'max_workers': config.get('milb_background_service_max_workers', 3),
                'request_timeout': config.get('milb_background_service_request_timeout', 30),
                'max_retries': config.get('milb_background_service_max_retries', 3),
                'priority': config.get('milb_background_service_priority', 2)
            }
        }

        # NCAA Baseball Configuration
        leagues['ncaa_baseball'] = {
            'enabled': config.get('ncaa_baseball_enabled', False),
            'live_priority': config.get('ncaa_baseball_live_priority', True),
            'live_game_duration': config.get('ncaa_baseball_live_game_duration', 20),
            'test_mode': config.get('ncaa_baseball_test_mode', False),
            'update_interval_seconds': config.get('ncaa_baseball_update_interval_seconds', 60),
            'live_update_interval': config.get('ncaa_baseball_live_update_interval', 15),
            'recent_update_interval': config.get('ncaa_baseball_recent_update_interval', 3600),
            'upcoming_update_interval': config.get('ncaa_baseball_upcoming_update_interval', 3600),
            'recent_games_to_show': config.get('ncaa_baseball_recent_games_to_show', 5),
            'upcoming_games_to_show': config.get('ncaa_baseball_upcoming_games_to_show', 10),
            'show_records': config.get('ncaa_baseball_show_records', False),
            'show_ranking': config.get('ncaa_baseball_show_ranking', False),
            'show_odds': config.get('ncaa_baseball_show_odds', False),
            'show_series_summary': config.get('ncaa_baseball_show_series_summary', False),
            'show_favorite_teams_only': config.get('ncaa_baseball_show_favorite_teams_only', False),
            'show_all_live': config.get('ncaa_baseball_show_all_live', False),
            'favorite_teams': config.get('ncaa_baseball_favorite_teams', []),
            'display_modes': {
                'live': config.get('ncaa_baseball_display_modes_live', True),
                'recent': config.get('ncaa_baseball_display_modes_recent', True),
                'upcoming': config.get('ncaa_baseball_display_modes_upcoming', True)
            },
            'logo_dir': config.get('ncaa_baseball_logo_dir', 'assets/sports/ncaa_logos'),
            'background_service': {
                'enabled': config.get('ncaa_baseball_background_service_enabled', True),
                'max_workers': config.get('ncaa_baseball_background_service_max_workers', 3),
                'request_timeout': config.get('ncaa_baseball_background_service_request_timeout', 30),
                'max_retries': config.get('ncaa_baseball_background_service_max_retries', 3),
                'priority': config.get('ncaa_baseball_background_service_priority', 2)
            }
        }

        return leagues

    def _resolve_favorite_teams(self):
        """Resolve favorite teams for each league using DynamicTeamResolver."""
        for league_key, league_config in self.leagues.items():
            if not league_config.get('enabled', False):
                continue

            raw_favorite_teams = league_config.get('favorite_teams', [])
            if not raw_favorite_teams:
                league_config['favorite_teams'] = []
                continue

            # Map league keys to sport keys for resolver
            sport_key_map = {
                'mlb': 'mlb',
                'milb': 'milb',
                'ncaa_baseball': 'ncaa_baseball'
            }
            sport_key = sport_key_map.get(league_key, league_key)

            if self.dynamic_resolver:
                resolved_teams = self.dynamic_resolver.resolve_teams(raw_favorite_teams, sport_key)
                if raw_favorite_teams != resolved_teams:
                    self.logger.info("[%s] Resolved dynamic teams: %s -> %s", league_key, raw_favorite_teams, resolved_teams)
                league_config['favorite_teams'] = resolved_teams
            else:
                league_config['favorite_teams'] = raw_favorite_teams

            if league_config['favorite_teams']:
                self.logger.info("[%s] Favorite teams: %s", league_key, league_config['favorite_teams'])

    def _initialize_test_games(self):
        """Initialize test mode games if enabled for any league."""
        for league_key, league_config in self.leagues.items():
            if not league_config.get('enabled', False):
                continue

            if league_config.get('test_mode', False):
                if league_key == 'mlb':
                    test_game = {
                        "home_abbr": "TB",
                        "home_id": "234",
                        "away_abbr": "TEX",
                        "away_id": "234",
                        "home_score": "3",
                        "away_score": "2",
                        "inning": 5,
                        "inning_half": "top",
                        "balls": 2,
                        "strikes": 1,
                        "outs": 1,
                        "bases_occupied": [True, False, True],
                        "home_logo_path": Path(league_config.get('logo_dir', 'assets/sports/mlb_logos'), "TB.png"),
                        "away_logo_path": Path(league_config.get('logo_dir', 'assets/sports/mlb_logos'), "TEX.png"),
                        "start_time": datetime.now(timezone.utc).isoformat(),
                        "is_live": True,
                        "is_final": False,
                        "is_upcoming": False,
                        "status_state": "in",
                        "id": "test_mlb_game",
                        "league": league_key,
                        "league_config": league_config
                    }
                    self.league_state[league_key]['live']['games_list'] = [test_game]
                    self.league_state[league_key]['live']['current_game'] = test_game
                    self.logger.info("[%s] Initialized test game: TB vs TEX", league_key)
                elif league_key == 'ncaa_baseball':
                    test_game = {
                        "home_abbr": "FLA",
                        "home_id": "234",
                        "away_abbr": "LSU",
                        "away_id": "234",
                        "home_score": "4",
                        "away_score": "5",
                        "status": "live",
                        "status_state": "in",
                        "inning": 8,
                        "inning_half": "top",
                        "balls": 1,
                        "strikes": 2,
                        "outs": 2,
                        "bases_occupied": [True, True, False],
                        "home_logo_path": Path(league_config.get('logo_dir', 'assets/sports/ncaa_logos'), "FLA.png"),
                        "away_logo_path": Path(league_config.get('logo_dir', 'assets/sports/ncaa_logos'), "LSU.png"),
                        "start_time": datetime.now(timezone.utc).isoformat(),
                        "is_live": True,
                        "is_final": False,
                        "is_upcoming": False,
                        "id": "test_ncaa_game",
                        "league": league_key,
                        "league_config": league_config
                    }
                    self.league_state[league_key]['live']['games_list'] = [test_game]
                    self.league_state[league_key]['live']['current_game'] = test_game
                    self.logger.info("[%s] Initialized test game: LSU vs FLA", league_key)
                elif league_key == 'milb':
                    test_game = {
                        "home_team": "TOL",
                        "away_team": "BUF",
                        "home_score": 3,
                        "away_score": 2,
                        "status": "status_in_progress",
                        "status_state": "in",
                        "inning": 7,
                        "inning_half": "bottom",
                        "balls": 2,
                        "strikes": 1,
                        "outs": 1,
                        "bases_occupied": [True, False, True],
                        "start_time": datetime.now(timezone.utc).isoformat(),
                        "id": "test_milb_game",
                        "league": league_key,
                        "league_config": league_config,
                        # Convert to ESPN format for rendering
                        "home_abbr": "TOL",
                        "away_abbr": "BUF",
                        "home_id": "test_tol",
                        "away_id": "test_buf",
                        "home_logo_path": Path(league_config.get('logo_dir', 'assets/sports/milb_logos'), "TOL.png"),
                        "away_logo_path": Path(league_config.get('logo_dir', 'assets/sports/milb_logos'), "BUF.png"),
                        "is_live": True,
                        "is_final": False,
                        "is_upcoming": False,
                    }
                    self.league_state[league_key]['live']['games_list'] = [test_game]
                    self.league_state[league_key]['live']['current_game'] = test_game
                    self.logger.info("[%s] Initialized test game: TOL vs BUF", league_key)

    def _register_fonts(self):
        """Register fonts with the font manager."""
        try:
            if not hasattr(self.plugin_manager, 'font_manager'):
                return

            font_manager = self.plugin_manager.font_manager

            # Team name font
            font_manager.register_manager_font(
                manager_id=self.plugin_id,
                element_key=f"{self.plugin_id}.team_name",
                family="press_start",
                size_px=10,
                color=(255, 255, 255)
            )

            # Score font
            font_manager.register_manager_font(
                manager_id=self.plugin_id,
                element_key=f"{self.plugin_id}.score",
                family="press_start",
                size_px=12,
                color=(255, 200, 0)
            )

            # Status font (inning, time)
            font_manager.register_manager_font(
                manager_id=self.plugin_id,
                element_key=f"{self.plugin_id}.status",
                family="four_by_six",
                size_px=6,
                color=(0, 255, 0)
            )

            # Detail font (records, rankings)
            font_manager.register_manager_font(
                manager_id=self.plugin_id,
                element_key=f"{self.plugin_id}.detail",
                family="four_by_six",
                size_px=6,
                color=(200, 200, 200)
            )

            self.logger.info("Baseball scoreboard fonts registered")
        except Exception as e:
            self.logger.warning(f"Error registering fonts: {e}")

    def update(self) -> None:
        """
        Update baseball game data for all enabled leagues.

        Replicates update logic from SportsLive, SportsRecent, and SportsUpcoming.
        """
        if not self.initialized:
            return

        current_time = time.time()

        # Update each enabled league independently
        for league_key, league_config in self.leagues.items():
            if not league_config.get('enabled', False):
                continue

            try:
                # Update live games
                if league_config.get('display_modes', {}).get('live', True):
                    self._update_live_games(league_key, league_config, current_time)

                # Update recent games
                if league_config.get('display_modes', {}).get('recent', True):
                    self._update_recent_games(league_key, league_config, current_time)

                # Update upcoming games
                if league_config.get('display_modes', {}).get('upcoming', True):
                    self._update_upcoming_games(league_key, league_config, current_time)

            except Exception as e:
                self.logger.error("Error updating %s: %s", league_key, e, exc_info=True)

    def _update_live_games(self, league_key: str, league_config: Dict, current_time: float):
        """
        Update live games for a specific league.

        Replicates SportsLive.update() logic.
        """
        state = self.league_state[league_key]['live']
        update_interval = league_config.get('live_update_interval', 15)
        no_data_interval = 300

        # Determine update interval
        interval = no_data_interval if not state['games_list'] and not league_config.get('test_mode', False) else update_interval

        if current_time - state['last_update'] < interval:
            return

        state['last_update'] = current_time

        # Fetch rankings if enabled
        if league_config.get('show_ranking', False):
            sport = "baseball"
            league_espn = "mlb" if league_key == "mlb" else "college-baseball" if league_key == "ncaa_baseball" else None
            if league_espn:
                self.rankings_manager.fetch_rankings(sport, league_espn, league_key)

        # Handle test mode
        if league_config.get('test_mode', False):
            self._update_test_mode_live(league_key, league_config)
            return

        # Fetch live game data
        games_data = None
        if league_key == 'milb':
            # MiLB uses different API
            games_dict = self.data_manager.fetch_milb_games(
                league_config,
                date_range=league_config.get('upcoming_fetch_days', 7),
                sport_ids=league_config.get('sport_ids', [10, 11, 12, 13, 14, 15])
            )
            # Convert to list of game dicts and extract details
            processed_games = []
            for game_data in games_dict.values():
                game_details = self.data_manager.extract_game_details(game_data, league_key, league_config, league_config.get('favorite_teams', []))
                if game_details:
                    game_details['league'] = league_key
                    game_details['league_config'] = league_config
                    processed_games.append(game_details)
            games_data = {'events': processed_games} if processed_games else None
        else:
            # ESPN leagues
            games_data = self.data_manager.fetch_todays_games(league_key, league_config)

        if not games_data:
            return

        # Extract and filter live games
        new_live_games = []
        events = games_data.get('events', [])

        for event in events:
            if league_key == 'milb':
                # MiLB games are already processed
                game = event
            else:
                game = self.data_manager.extract_game_details(event, league_key, league_config, league_config.get('favorite_teams', []))

            if not game:
                continue

            # Check if live
            is_live = game.get('is_live', False) or game.get('status_state') == 'in'
            is_halftime = game.get('is_halftime', False)

            if is_live or is_halftime:
                # Apply filters
                show_favorite_teams_only = league_config.get('show_favorite_teams_only', False)
                show_all_live = league_config.get('show_all_live', False)

                if show_favorite_teams_only and not show_all_live:
                    favorite_teams = league_config.get('favorite_teams', [])
                    if not favorite_teams:
                        continue
                    if not self.game_filter.is_favorite_game(game, favorite_teams):
                        continue

                # Fetch odds if enabled
                if league_config.get('show_odds', False):
                    sport = "baseball"
                    league_espn = "mlb" if league_key == "mlb" else "college-baseball" if league_key == "ncaa_baseball" else None
                    if league_espn:
                        self.odds_manager.fetch_odds(game, league_config, sport, league_espn)

                new_live_games.append(game)

        # Filter and sort using GameFilter
        if league_key == 'milb':
            # MiLB needs special handling with live feed probing
            filtered_games = self.game_filter.filter_live_games(new_live_games, league_config, league_key, self.data_manager)
        else:
            filtered_games = self.game_filter.filter_live_games(new_live_games, league_config, league_key)

        # Update game list
        updated_list, updated_game, updated_index = self.game_filter.update_game_list(
            state['games_list'], filtered_games, state['current_game'], state['current_index']
        )
        state['games_list'] = updated_list
        state['current_game'] = updated_game
        state['current_index'] = updated_index

        if updated_list and not state['games_list']:
            state['last_game_switch'] = current_time

    def _update_recent_games(self, league_key: str, league_config: Dict, current_time: float):
        """
        Update recent games for a specific league.

        Replicates SportsRecent.update() logic.
        """
        state = self.league_state[league_key]['recent']
        update_interval = league_config.get('recent_update_interval', 3600)

        if current_time - state['last_update'] < update_interval:
            return

        state['last_update'] = current_time

        # Fetch rankings if enabled
        if league_config.get('show_ranking', False):
            sport = "baseball"
            league_espn = "mlb" if league_key == "mlb" else "college-baseball" if league_key == "ncaa_baseball" else None
            if league_espn:
                self.rankings_manager.fetch_rankings(sport, league_espn, league_key)

        # Fetch season data
        if league_key == 'milb':
            games_dict = self.data_manager.fetch_milb_games(
                league_config,
                date_range=21,  # Recent games need 21 days
                sport_ids=league_config.get('sport_ids', [10, 11, 12, 13, 14, 15])
            )
            # Convert to list and extract details
            all_games = []
            for game_data in games_dict.values():
                game_details = self.data_manager.extract_game_details(game_data, league_key, league_config, league_config.get('favorite_teams', []))
                if game_details:
                    game_details['league'] = league_key
                    game_details['league_config'] = league_config
                    all_games.append(game_details)
            games_data = {'events': all_games} if all_games else None
        else:
            games_data = self.data_manager.fetch_season_data(league_key, league_config, use_cache=True)

        if not games_data:
            return

        # Extract and filter recent games
        processed_games = []
        events = games_data.get('events', [])

        for event in events:
            if league_key == 'milb':
                game = event  # Already processed
            else:
                game = self.data_manager.extract_game_details(event, league_key, league_config, league_config.get('favorite_teams', []))

            if not game:
                continue

            # Must be final
            is_final = game.get('is_final', False) or game.get('status_state') in ['post', 'final', 'completed']
            if not is_final:
                continue

            processed_games.append(game)

        # Filter using GameFilter
        filtered_games = self.game_filter.filter_recent_games(processed_games, league_config)

        # Update game list
        updated_list, updated_game, updated_index = self.game_filter.update_game_list(
            state['games_list'], filtered_games, state['current_game'], state['current_index']
        )
        state['games_list'] = updated_list
        state['current_game'] = updated_game
        state['current_index'] = updated_index

        if updated_list and not state['games_list']:
            state['last_game_switch'] = current_time

    def _update_upcoming_games(self, league_key: str, league_config: Dict, current_time: float):
        """
        Update upcoming games for a specific league.

        Replicates SportsUpcoming.update() logic.
        """
        state = self.league_state[league_key]['upcoming']
        update_interval = league_config.get('upcoming_update_interval', 3600)

        if current_time - state['last_update'] < update_interval:
            return

        state['last_update'] = current_time

        # Fetch rankings if enabled
        if league_config.get('show_ranking', False):
            sport = "baseball"
            league_espn = "mlb" if league_key == "mlb" else "college-baseball" if league_key == "ncaa_baseball" else None
            if league_espn:
                self.rankings_manager.fetch_rankings(sport, league_espn, league_key)

        # Fetch season data
        if league_key == 'milb':
            games_dict = self.data_manager.fetch_milb_games(
                league_config,
                date_range=league_config.get('upcoming_fetch_days', 7),
                sport_ids=league_config.get('sport_ids', [10, 11, 12, 13, 14, 15])
            )
            # Convert to list and extract details
            all_games = []
            for game_data in games_dict.values():
                game_details = self.data_manager.extract_game_details(game_data, league_key, league_config, league_config.get('favorite_teams', []))
                if game_details:
                    game_details['league'] = league_key
                    game_details['league_config'] = league_config
                    all_games.append(game_details)
            games_data = {'events': all_games} if all_games else None
        else:
            games_data = self.data_manager.fetch_season_data(league_key, league_config, use_cache=True)

        if not games_data:
            return

        # Extract and filter upcoming games
        processed_games = []
        events = games_data.get('events', [])

        for event in events:
            if league_key == 'milb':
                game = event  # Already processed
            else:
                game = self.data_manager.extract_game_details(event, league_key, league_config, league_config.get('favorite_teams', []))

            if not game:
                continue

            # Must be upcoming
            is_upcoming = game.get('is_upcoming', False) or game.get('status_state') == 'pre'
            if not is_upcoming:
                continue

            # Fetch odds if enabled
            if league_config.get('show_odds', False):
                sport = "baseball"
                league_espn = "mlb" if league_key == "mlb" else "college-baseball" if league_key == "ncaa_baseball" else None
                if league_espn:
                    self.odds_manager.fetch_odds(game, league_config, sport, league_espn)

            processed_games.append(game)

        # Filter using GameFilter
        filtered_games = self.game_filter.filter_upcoming_games(processed_games, league_config)

        # Update game list
        updated_list, updated_game, updated_index = self.game_filter.update_game_list(
            state['games_list'], filtered_games, state['current_game'], state['current_index']
        )
        state['games_list'] = updated_list
        state['current_game'] = updated_game
        state['current_index'] = updated_index

        if updated_list and not state['games_list']:
            state['last_game_switch'] = current_time

    def _update_test_mode_live(self, league_key: str, league_config: Dict):
        """Update test mode live game state."""
        state = self.league_state[league_key]['live']
        current_game = state['current_game']

        if current_game:
            # Update inning half
            if current_game.get("inning_half") == "top":
                current_game["inning_half"] = "bottom"
            else:
                current_game["inning_half"] = "top"
                current_game["inning"] = current_game.get("inning", 1) + 1

            # Update count
            current_game["balls"] = (current_game.get("balls", 0) + 1) % 4
            current_game["strikes"] = (current_game.get("strikes", 0) + 1) % 3

            # Update outs
            current_game["outs"] = (current_game.get("outs", 0) + 1) % 3

            # Update bases
            bases = current_game.get("bases_occupied", [False, False, False])
            current_game["bases_occupied"] = [not bases[0], not bases[1], not bases[2]]

            # Update score occasionally
            if current_game.get("inning", 1) % 2 == 0:
                current_game["home_score"] = str(int(current_game.get("home_score", 0)) + 1)
            else:
                current_game["away_score"] = str(int(current_game.get("away_score", 0)) + 1)

    def display(self, display_mode: str = None, force_clear: bool = False) -> None:
        """
        Display baseball games with mode cycling (like football plugin).

        Args:
            display_mode: Ignored - plugin cycles through modes internally
            force_clear: If True, clear display before rendering
        """
        if not self.initialized:
            self._display_error("Baseball plugin not initialized")
            return

        current_time = time.time()

        # Handle mode cycling (like football plugin)
        if current_time - self.last_mode_switch >= self.display_duration:
            self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
            self.last_mode_switch = current_time
            force_clear = True

            current_mode = self.modes[self.current_mode_index]
            self.logger.info(f"Switching to display mode: {current_mode}")

        # Get current mode from internal cycling
        display_mode = self.modes[self.current_mode_index]

        # Get current game for the selected mode across all leagues
        current_game, league_key = self._get_current_game_for_mode(display_mode, current_time)

        # If no current game found, clear display to avoid showing stale content (like "Initializing")
        # This matches old manager behavior but ensures display is cleared when no games available
        if not current_game:
            self.display_manager.clear()
            self.display_manager.update_display()
            return

        # Render the game
        # Extract mode suffix (live/recent/upcoming) and league from mode like "mlb_live", "milb_recent"
        parts = display_mode.split('_')
        if len(parts) >= 2:
            mode_suffix = parts[-1]  # "live", "recent", or "upcoming"
        else:
            mode_suffix = "live"  # fallback
        league_config = current_game.get('league_config', {})
        
        if mode_suffix == 'live':
            self.scorebug_renderer.render_live_scorebug(current_game, league_config, league_key)
        elif mode_suffix == 'recent':
            self.scorebug_renderer.render_recent_scorebug(current_game, league_config, league_key)
        elif mode_suffix == 'upcoming':
            self.scorebug_renderer.render_upcoming_scorebug(current_game, league_config, league_key)

    def _get_available_modes(self) -> list:
        """Get list of available display modes based on enabled leagues (like football plugin)."""
        modes = []

        for league_key, league_config in self.leagues.items():
            if league_config.get('enabled', False):
                modes.extend([f"{league_key}_live", f"{league_key}_recent", f"{league_key}_upcoming"])

        # Default to MLB if no leagues enabled
        if not modes:
            modes = ["mlb_live", "mlb_recent", "mlb_upcoming"]

        return modes

    def _get_current_game_for_mode(self, display_mode: str, current_time: float):
        """
        Get current game for display mode, handling game switching.

        Args:
            display_mode: Display mode (e.g., "mlb_live", "milb_recent", "ncaa_baseball_upcoming")
            current_time: Current timestamp

        Returns:
            Tuple of (current_game, league_key) or (None, None)
        """
        # Extract league and mode suffix from mode like "mlb_live", "milb_recent", "ncaa_baseball_upcoming"
        parts = display_mode.split('_')
        if len(parts) >= 2:
            # For modes like "mlb_live", "milb_recent" - league is first part, mode is last
            # For "ncaa_baseball_live" - league is "ncaa_baseball", mode is "live"
            if len(parts) == 2:
                # Simple case: "mlb_live"
                league_key = parts[0]
                mode_suffix = parts[1]
            else:
                # Complex case: "ncaa_baseball_live"
                mode_suffix = parts[-1]  # "live", "recent", or "upcoming"
                league_key = '_'.join(parts[:-1])  # "ncaa_baseball"
        else:
            mode_suffix = "live"  # fallback
            league_key = "mlb"  # fallback

        # Get games from the specific league for this mode (like football plugin)
        league_config = self.leagues.get(league_key)
        if league_config and league_config.get('enabled', False):
            state = self.league_state[league_key][mode_suffix]
            games_list = state['games_list']

            if not games_list:
                return None, None

            # Handle game switching
            game_display_duration = league_config.get('live_game_duration', 20) if mode_suffix == 'live' else 15

            if self.game_filter.should_switch_game(games_list, state['current_index'], state['last_game_switch'], game_display_duration):
                new_index = self.game_filter.get_next_game_index(games_list, state['current_index'])
                state['current_index'] = new_index
                state['current_game'] = games_list[new_index] if games_list else None
                state['last_game_switch'] = current_time

            # Return current game for this league/mode
            if state['current_game']:
                return state['current_game'], league_key

        return None, None

    def _display_no_games(self, mode: str):
        """Display message when no games are available."""
        # Get display dimensions safely
        if hasattr(self.display_manager, 'matrix') and self.display_manager.matrix is not None:
            width = self.display_manager.matrix.width
            height = self.display_manager.matrix.height
        elif hasattr(self.display_manager, 'display_width'):
            width = self.display_manager.display_width
            height = self.display_manager.display_height
        else:
            width = 128
            height = 32
        
        img = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        message = {
            'baseball_live': "No Live Games",
            'baseball_recent': "No Recent Games",
            'baseball_upcoming': "No Upcoming Games"
        }.get(mode, "No Games")

        draw.text((5, 12), message, fill=(150, 150, 150))

        self.display_manager.image = img.copy()
        self.display_manager.update_display()

    def _display_error(self, message: str):
        """Display error message."""
        # Get display dimensions safely
        if hasattr(self.display_manager, 'matrix') and self.display_manager.matrix is not None:
            width = self.display_manager.matrix.width
            height = self.display_manager.matrix.height
        elif hasattr(self.display_manager, 'display_width'):
            width = self.display_manager.display_width
            height = self.display_manager.display_height
        else:
            width = 128
            height = 32
        
        img = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((5, 12), message, fill=(255, 0, 0))

        self.display_manager.image = img.copy()
        self.display_manager.update_display()

    def get_display_duration(self) -> float:
        """Get display duration from config."""
        return self.display_duration

    def has_live_content(self) -> bool:
        """
        Check if there are any live games across all leagues.

        Returns:
            True if any live games exist, False otherwise
        """
        for league_key, league_config in self.leagues.items():
            if not league_config.get('enabled', False):
                continue

            live_state = self.league_state[league_key]['live']
            if live_state['games_list']:
                return True

        return False

    def has_live_priority(self) -> bool:
        """
        Check if any league has live_priority enabled and has live games.

        Returns:
            True if live_priority league has live games, False otherwise
        """
        for league_key, league_config in self.leagues.items():
            if not league_config.get('enabled', False):
                continue

            if league_config.get('live_priority', False):
                live_state = self.league_state[league_key]['live']
                if live_state['games_list']:
                    return True

        return False

    def get_live_modes(self) -> List[str]:
        """
        Get list of display modes that have live content.

        Returns:
            List of display mode strings
        """
        modes = []
        if self.has_live_content():
            modes.append('baseball_live')
        return modes

    def get_info(self) -> Dict[str, Any]:
        """Return plugin info for web UI."""
        info = super().get_info()

        # Get league-specific configurations
        leagues_config = {}
        for league_key, league_config in self.leagues.items():
            leagues_config[league_key] = {
                'enabled': league_config.get('enabled', False),
                'live_priority': league_config.get('live_priority', False),
                'favorite_teams': league_config.get('favorite_teams', []),
                'display_modes': league_config.get('display_modes', {}),
                'recent_games_to_show': league_config.get('recent_games_to_show', 5),
                'upcoming_games_to_show': league_config.get('upcoming_games_to_show', 10),
                'update_interval_seconds': league_config.get('update_interval_seconds', 60),
                'show_records': league_config.get('show_records', False),
                'show_ranking': league_config.get('show_ranking', False),
                'show_odds': league_config.get('show_odds', False),
            }

        # Count games by mode
        total_live = sum(len(self.league_state[k]['live']['games_list']) for k in self.leagues.keys())
        total_recent = sum(len(self.league_state[k]['recent']['games_list']) for k in self.leagues.keys())
        total_upcoming = sum(len(self.league_state[k]['upcoming']['games_list']) for k in self.leagues.keys())

        info.update({
            'total_games': total_live + total_recent + total_upcoming,
            'enabled_leagues': [k for k, v in self.leagues.items() if v.get('enabled', False)],
            'last_update': time.time(),
            'display_duration': self.display_duration,
            'live_games': total_live,
            'recent_games': total_recent,
            'upcoming_games': total_upcoming,
            'leagues_config': leagues_config,
            'global_config': self.global_config
        })
        return info

    def cleanup(self) -> None:
        """Cleanup resources."""
        for league_key in self.leagues.keys():
            for mode in ['live', 'recent', 'upcoming']:
                self.league_state[league_key][mode]['games_list'] = []
                self.league_state[league_key][mode]['current_game'] = None

        self.logo_manager.clear_cache()
        self.logger.info("Baseball scoreboard plugin cleaned up")
