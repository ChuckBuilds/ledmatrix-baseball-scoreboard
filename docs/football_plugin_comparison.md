# Detailed Comparison: Old Football Managers vs New Plugin

## Executive Summary

The football plugin has been refactored into a modular architecture but is missing several critical features from the original working managers. This document identifies the exact differences that explain why the plugin isn't behaving like the old working system.

---

## Key Differences

### 1. Configuration Structure

#### Old Managers
```python
# In SportsCore.__init__()
self.mode_config = config.get(f"{sport_key}_scoreboard", {})
# Example: config.get("nfl_scoreboard", {})
#          config.get("ncaa_fb_scoreboard", {})
```

#### New Plugin
```python
# In manager.py __init__()
self.leagues = {
    "nfl": {
        "enabled": config.get("nfl", {}).get("enabled", False),
        "favorite_teams": config.get("nfl", {}).get("favorite_teams", []),
        # ...
    },
    "ncaa_fb": {
        "enabled": config.get("ncaa_fb", {}).get("enabled", False),
        # ...
    }
}
```

**Issue**: The plugin expects a flattened config structure (`config.get("nfl", {})`) while the old managers expect nested structure (`config.get("nfl_scoreboard", {})`).

---

### 2. Logo Loading - CRITICAL DIFFERENCE

#### Old Managers (football.py)
```python
def _load_and_resize_logo(self, team_id: str, team_abbrev: str, logo_path: Path, logo_url: str | None) -> Optional[Image.Image]:
    """Load and resize a team logo, with caching and automatic download if missing."""
    # Logo caching
    if team_abbrev in self._logo_cache:
        return self._logo_cache[team_abbrev]
    
    # Try filename variations (TA&M vs TAANDM)
    filename_variations = LogoDownloader.get_logo_filename_variations(team_abbrev)
    for filename in filename_variations:
        test_path = logo_path.parent / filename
        if test_path.exists():
            actual_logo_path = test_path
            break
    
    # Auto-download missing logos
    if not actual_logo_path and not logo_path.exists():
        download_missing_logo(self.sport_key, team_id, team_abbrev, logo_path, logo_url)
        actual_logo_path = logo_path
    
    # Resize as percentage of display
    max_width = int(self.display_width * 1.5)
    max_height = int(self.display_height * 1.5)
    logo.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Cache the logo
    self._logo_cache[team_abbrev] = logo
    return logo
```

#### New Plugin (scoreboard_renderer.py)
```python
def _load_team_logo(self, team_abbr: str, logo_dir: str) -> Optional[Image.Image]:
    """Load team logo image with proper sizing."""
    logo_path = Path(logo_dir) / f"{team_abbr}.png"
    if logo_path.exists():
        logo = Image.open(logo_path)
        # Resize as percentage of display
        max_width = int(self.display_width * 1.5)
        max_height = int(self.display_height * 1.5)
        logo.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return logo
    else:
        self.logger.warning(f"Logo not found for team: {team_abbr} at {logo_path}")
        return None
```

**Issues**:
1. ❌ No logo caching in plugin
2. ❌ No filename variation handling (TA&M vs TAANDM)
3. ❌ No automatic logo download
4. ❌ Just returns None if logo doesn't exist instead of trying alternatives
5. ❌ Hardcoded logo paths instead of using logo_path from game data

---

### 3. Data Fetching Strategy

#### Old Managers
```python
def _fetch_nfl_api_data(self, use_cache: bool = True) -> Optional[Dict]:
    """Fetches the full season schedule using background threading."""
    # 1. Check cache first
    cached_data = self.cache_manager.get(cache_key)
    if cached_data:
        return cached_data
    
    # 2. Start background fetch for full season
    request_id = self.background_service.submit_fetch_request(
        sport="nfl",
        year=season_year,
        url=ESPN_NFL_SCOREBOARD_URL,
        cache_key=cache_key,
        params={"dates": datestring, "limit": 1000},
        headers=self.headers,
        timeout=timeout,
        max_retries=max_retries,
        priority=priority,
        callback=fetch_callback
    )
    
    # 3. Return partial data immediately
    partial_data = self._get_weeks_data()  # Gets last 2 weeks + next week
    if partial_data:
        return partial_data
    
    return None
```

#### New Plugin
```python
def fetch_nfl_data(self, use_cache: bool = True) -> Optional[Dict]:
    """Fetches the full season schedule using background threading."""
    # 1. Check cache
    if use_cache and self.cache_manager:
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
    
    # 2. Start background fetch
    if self.background_service:
        self._start_background_fetch("nfl", season_year, datestring, cache_key)
    
    # 3. Return extended games (-7 to +14 days)
    return self._fetch_extended_games("nfl")
```

**Differences**:
- Old: Falls back to `_get_weeks_data()` (last 2 weeks + next week)
- New: Falls back to `_fetch_extended_games()` (last 7 days + next 14 days)
- Different date ranges could affect which games are shown

---

### 4. Logo Paths in Game Data

#### Old Managers
```python
# In _extract_game_details_common()
"home_logo_path": self.logo_dir / Path(f"{LogoDownloader.normalize_abbreviation(home_abbr)}.png"),
"away_logo_path": self.logo_dir / Path(f"{LogoDownloader.normalize_abbreviation(away_abbr)}.png"),
# Uses self.logo_dir from SportsCore initialization
# Uses LogoDownloader.normalize_abbreviation() for filename normalization
```

#### New Plugin
```python
# In data_fetcher.py _extract_game_details()
# NO logo paths added to game data!

# Later in scoreboard_renderer.py
# Hardcoded paths:
if league == "nfl":
    logo_dir = "/home/chuck/Github/LEDMatrix/assets/sports/nfl_logos"
else:  # ncaa_fb
    logo_dir = "/home/chuck/Github/LEDMatrix/assets/sports/ncaa_logos"

home_logo = self._load_team_logo(game.get("home_abbr", ""), logo_dir)
away_logo = self._load_team_logo(game.get("away_abbr", ""), logo_dir)
```

**Issues**:
1. ❌ Game data doesn't include logo paths/URLs
2. ❌ Hardcoded absolute paths instead of relative/configured paths
3. ❌ No logo URL in game data for auto-download
4. ❌ No abbreviation normalization

---

### 5. Display Update Behavior

#### Old Managers
```python
def _draw_scorebug_layout(self, game: Dict, force_clear: bool = False) -> None:
    """Draw the detailed scorebug layout for a live game."""
    # ... drawing code ...
    
    # Composite the text overlay onto the main image
    main_img = Image.alpha_composite(main_img, overlay)
    main_img = main_img.convert('RGB')
    
    # Display the final image
    self.display_manager.image.paste(main_img, (0, 0))
    self.display_manager.update_display()  # ← Calls update_display() HERE
```

#### New Plugin
```python
def _draw_scorebug_layout(self, game: Dict, force_clear: bool = False) -> None:
    """Draw the detailed scorebug layout following football.py structure exactly."""
    # ... drawing code ...
    
    # Composite the text overlay onto the main image
    main_img = Image.alpha_composite(main_img, overlay)
    main_img = main_img.convert("RGB")
    
    # Display the final image
    self.display_manager.image.paste(main_img, (0, 0))
    self.display_manager.update_display()  # ← Also calls update_display() HERE
```

**Status**: ✅ Same behavior - both call `update_display()`

---

### 6. Game Filtering Logic

#### Old Managers
```python
# In SportsUpcoming/SportsRecent base classes
def update(self):
    # Fetch data
    data = self._fetch_data()
    events = data['events']
    
    # Process events
    for event in events:
        game = self._extract_game_details(event)
        
        # Filter in-place based on mode
        if game and game['is_upcoming']:  # or is_recent, is_live
            if self.show_favorite_teams_only:
                if game['home_abbr'] not in self.favorite_teams and game['away_abbr'] not in self.favorite_teams:
                    continue
            
            # Limit to N games
            if len(processed_games) >= self.upcoming_games_to_show:
                break
            
            processed_games.append(game)
    
    self.games_list = processed_games
```

#### New Plugin
```python
# In manager.py update()
# Fetch all games
all_games = []
for league_key, league_config in self.leagues.items():
    if league_config.get("enabled", False):
        data = self.data_fetcher.fetch_nfl_data(use_cache=True)
        games = self.data_fetcher.process_api_response(data, league_key, league_config)
        all_games.extend(games)

self.current_games = all_games

# In display()
# Filter games by mode
self.games_list = self.game_filter.filter_games_by_mode(
    self.current_games, self.current_display_mode, self.leagues
)
```

**Differences**:
- Old: Filters during `update()` based on mode-specific criteria
- New: Fetches all games, then filters in `display()` by mode string
- Old: More efficient (only processes relevant games)
- New: Processes all games then filters

---

### 7. Font Loading

#### Old Managers
```python
def _load_fonts(self):
    """Load fonts used by the scoreboard."""
    fonts = {}
    try:
        fonts['score'] = ImageFont.truetype("assets/fonts/PressStart2P-Regular.ttf", 10)
        fonts['time'] = ImageFont.truetype("assets/fonts/PressStart2P-Regular.ttf", 8)
        fonts['team'] = ImageFont.truetype("assets/fonts/PressStart2P-Regular.ttf", 8)
        fonts['status'] = ImageFont.truetype("assets/fonts/4x6-font.ttf", 6)
        fonts['detail'] = ImageFont.truetype("assets/fonts/4x6-font.ttf", 6)
        fonts['rank'] = ImageFont.truetype("assets/fonts/PressStart2P-Regular.ttf", 10)
        logging.info("Successfully loaded fonts")
    except IOError:
        logging.warning("Fonts not found, using default PIL font.")
        # ... set all to ImageFont.load_default()
    return fonts
```

#### New Plugin
```python
def _load_fonts(self):
    """Load fonts used by the scoreboard."""
    fonts = {}
    try:
        fonts["score"] = ImageFont.truetype("assets/fonts/PressStart2P-Regular.ttf", 10)
        fonts["time"] = ImageFont.truetype("assets/fonts/PressStart2P-Regular.ttf", 8)
        fonts["team"] = ImageFont.truetype("assets/fonts/PressStart2P-Regular.ttf", 8)
        fonts["status"] = ImageFont.truetype("assets/fonts/4x6-font.ttf", 6)
        fonts["detail"] = ImageFont.truetype("assets/fonts/4x6-font.ttf", 6)
        fonts["rank"] = ImageFont.truetype("assets/fonts/PressStart2P-Regular.ttf", 10)
        self.logger.info("Successfully loaded fonts")
    except IOError as e:
        self.logger.warning(f"Fonts not found, using default PIL font: {e}")
        # ... set all to ImageFont.load_default()
    return fonts
```

**Status**: ✅ Identical behavior

---

### 8. Font Paths in ScoreboardRenderer

#### Old Managers
```python
# In _draw_scorebug_layout()
record_font = ImageFont.truetype("assets/fonts/4x6-font.ttf", 6)
```

#### New Plugin
```python
# In scoreboard_renderer.py _draw_scorebug_layout()
record_font = ImageFont.truetype("assets/fonts/4x6-font.ttf", 6)
```

**Status**: ✅ Both use relative paths. However, plugin might be running from different working directory.

---

### 9. Game State Detection

#### Old Managers
```python
# In Football._extract_game_details()
competition = game_event["competitions"][0]
status = competition["status"]

# Determine game state
type_code = status.get("type", {}).get("name", "")
status_state = status.get("type", {}).get("state", "")

is_live = status_state == "in"
is_final = status_state == "post"
is_upcoming = (status_state == "pre" or 
               type_code.lower() in ['scheduled', 'pre-game', 'status_scheduled'])
is_halftime = status_state == "halftime" or type_code == "STATUS_HALFTIME"
```

#### New Plugin
```python
# In data_fetcher.py _extract_game_details()
status = competition.get("status", {})
type_code = status.get("type", {}).get("name", "")
status_state = status.get("type", {}).get("state", "")

# Determine game state
is_live = type_code in ["STATUS_IN_PROGRESS", "STATUS_HALFTIME"]
is_final = type_code == "STATUS_FINAL"
is_upcoming = type_code in ["STATUS_SCHEDULED", "STATUS_PRE"]
is_halftime = type_code == "STATUS_HALFTIME" or status_state == "halftime"
```

**Differences**:
- Old: Uses `status_state` primarily (`"in"`, `"post"`, `"pre"`)
- New: Uses `type_code` primarily (`"STATUS_IN_PROGRESS"`, `"STATUS_FINAL"`, etc.)
- This could cause different games to be classified differently

---

### 10. Period Text Formatting

#### Old Managers
```python
# In Football._extract_game_details()
period_text = ""
if status_state == "in":
    if period == 0:
        period_text = "Start"
    elif period >= 1 and period <= 4:
        period_text = f"Q{period}"
    elif period > 4:
        period_text = f"OT{period - 4}"
elif status_state == "halftime" or type_code == "STATUS_HALFTIME":
    period_text = "HALF"
elif status_state == "post":
    if period > 4:
        period_text = "Final/OT"
    else:
        period_text = "Final"
elif status_state == "pre":
    period_text = details.get("game_time", "")
```

#### New Plugin
```python
# In data_fetcher.py _extract_game_details()
period_text = ""
if status_state == "in":
    if period == 0:
        period_text = "Start"
    elif period >= 1 and period <= 4:
        period_text = f"Q{period}"
    elif period > 4:
        period_text = f"OT{period - 4}"
elif status_state == "halftime" or type_code == "STATUS_HALFTIME":
    period_text = "HALF"
elif status_state == "post":
    if period > 4:
        period_text = "Final/OT"
    else:
        period_text = "Final"
elif status_state == "pre":
    try:
        game_time = game_date.strftime("%I:%M%p").lower()
        period_text = game_time
    except (ValueError, TypeError):
        period_text = "TBD"
```

**Differences**:
- Old: Gets `game_time` from `details` dictionary
- New: Computes `game_time` from `game_date` directly
- Could result in different time formats being displayed

---

### 11. Record Display Position

#### Old Managers
```python
# In Football._draw_scorebug_layout()
record_bbox = draw_overlay.textbbox((0,0), "0-0", font=record_font)
record_height = record_bbox[3] - record_bbox[1]
record_y = self.display_height - record_height - 4
```

#### New Plugin
```python
# In scoreboard_renderer.py _draw_scorebug_layout()
record_bbox = draw_overlay.textbbox((0, 0), "0-0", font=record_font)
record_height = record_bbox[3] - record_bbox[1]
# Position records/rankings exactly like old football.py
record_y = self.display_height - record_height - 4
```

**Status**: ✅ Identical positioning

---

### 12. Ranking vs Record Logic

#### Old Managers
```python
# Display away team info
if away_abbr:
    if self.show_ranking and self.show_records:
        # When both rankings and records are enabled, rankings replace records completely
        away_rank = self._team_rankings_cache.get(away_abbr, 0)
        if away_rank > 0:
            away_text = f"#{away_rank}"
        else:
            away_text = ''
    elif self.show_ranking:
        away_rank = self._team_rankings_cache.get(away_abbr, 0)
        if away_rank > 0:
            away_text = f"#{away_rank}"
        else:
            away_text = ''
    elif self.show_records:
        away_text = game.get('away_record', '')
    else:
        away_text = ''
```

#### New Plugin
```python
# Display away team info
if away_abbr:
    if hasattr(self, 'show_ranking') and self.show_ranking and hasattr(self, 'show_records') and self.show_records:
        # When both rankings and records are enabled, rankings replace records completely
        away_rank = getattr(self, '_team_rankings_cache', {}).get(away_abbr, 0)
        if away_rank > 0:
            away_text = f"#{away_rank}"
        else:
            away_text = ''
    elif hasattr(self, 'show_ranking') and self.show_ranking:
        away_rank = getattr(self, '_team_rankings_cache', {}).get(away_abbr, 0)
        if away_rank > 0:
            away_text = f"#{away_rank}"
        else:
            away_text = ''
    elif hasattr(self, 'show_records') and self.show_records:
        away_text = game.get('away_record', '')
    else:
        away_text = ''
```

**Differences**:
- New: Uses `hasattr()` checks (safer but slower)
- New: Uses `getattr()` with default dictionary
- Should behave the same but might fail silently if attributes not set properly

---

## Summary of Critical Issues

### 🔴 Critical - Will Cause Immediate Failures

1. **Logo Loading**: Plugin lacks caching, variation handling, and auto-download
2. **Logo Paths**: Hardcoded absolute paths instead of relative paths and missing logo URLs
3. **Game State Detection**: Different logic could classify games incorrectly
4. **Configuration Structure**: Expects different config structure than old managers

### 🟡 Medium - Will Cause Incorrect Behavior

5. **Date Range**: Different fallback date ranges for data fetching
6. **Font Paths**: Relative paths might not resolve correctly from plugin location
7. **Period Text**: Different method for computing game time for upcoming games

### 🟢 Minor - Behavioral Differences

8. **Game Filtering**: Processes all games then filters vs filtering during fetch
9. **Ranking Display**: Uses `hasattr()`/`getattr()` instead of direct attribute access

---

## Recommended Fixes

### Priority 1: Logo Loading
1. Add logo caching to `ScoreboardRenderer`
2. Implement filename variation handling
3. Add automatic logo download capability
4. Use logo paths from game data instead of hardcoded paths

### Priority 2: Game Data Structure
1. Add logo paths and URLs to game data in `_extract_game_details()`
2. Normalize team abbreviations using `LogoDownloader.normalize_abbreviation()`
3. Store `logo_dir` in game data based on league

### Priority 3: Configuration
1. Align plugin config structure with old managers
2. Or update plugin to work with existing config structure

### Priority 4: Font/Path Resolution
1. Ensure plugin uses correct working directory for font/logo paths
2. Or use absolute paths from config

### Priority 5: Game State Detection
1. Align state detection logic with old managers
2. Test edge cases to ensure consistent classification

