#!/usr/bin/env python3
"""
Generate a preview of the odds ticker image for inspection.
This creates the same ticker image that the plugin generates.
"""

import sys
import os
import json
from datetime import datetime

# Add the plugin directory to Python path for imports
plugin_dir = "/home/chuck/Github/ledmatrix-odds-ticker"
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

# Import the odds renderer
from odds_renderer import OddsRenderer

def create_sample_games():
    """Create sample game data for testing."""
    return [
        {
            'game_id': '401772867',
            'league': 'nfl',
            'home_team': 'PHI',
            'away_team': 'MIN',
            'start_time': '2025-10-24T00:15Z',
            'status': 'scheduled',
            'broadcast': 'ESPN',
            'odds': {
                'details': 'PHI -7.5',
                'over_under': 43.5,
                'spread': -7.5,
                'home_team_odds': {
                    'money_line': -400,
                    'spread_odds': None
                },
                'away_team_odds': {
                    'money_line': 300,
                    'spread_odds': None
                }
            }
        },
        {
            'game_id': '401809297',
            'league': 'mlb',
            'home_team': 'TOR',
            'away_team': 'LAD',
            'start_time': '2025-10-25T00:00Z',
            'status': 'scheduled',
            'broadcast': 'FOX',
            'odds': {
                'details': 'LAD -150',
                'over_under': 7.5,
                'spread': 1.5,
                'home_team_odds': {
                    'money_line': 125,
                    'spread_odds': 0.0
                },
                'away_team_odds': {
                    'money_line': -150,
                    'spread_odds': None
                }
            }
        },
        {
            'game_id': '401752885',
            'league': 'ncaa_fb',
            'home_team': 'IU',
            'away_team': 'UCLA',
            'start_time': '2025-10-25T16:00Z',
            'status': 'scheduled',
            'broadcast': 'ABC',
            'odds': {
                'details': 'UCLA -3.5',
                'over_under': 58.5,
                'spread': -3.5,
                'home_team_odds': {
                    'money_line': 140,
                    'spread_odds': None
                },
                'away_team_odds': {
                    'money_line': -170,
                    'spread_odds': None
                }
            }
        }
    ]

def main():
    print("Generating odds ticker preview...")
    
    # Create sample games
    games = create_sample_games()
    
    # Mock managers for the renderer
    class MockMatrix:
        def __init__(self):
            self.width = 64
            self.height = 32
    
    class MockDisplayManager:
        def __init__(self):
            self.matrix = MockMatrix()
        
        def get_matrix_dimensions(self):
            return (64, 32)
    
    class MockFontManager:
        def get_font(self, size):
            # Return a simple font path - this might need adjustment based on your system
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    
    class MockCacheManager:
        pass
    
    # Create renderer
    display_manager = MockDisplayManager()
    
    config = {
        'scroll_speed': 1,
        'scroll_delay': 0.01,
        'show_channel_logos': True,
        'dynamic_duration': True,
        'min_duration': 30,
        'max_duration': 300,
        'duration_buffer': 0.1
    }
    
    renderer = OddsRenderer(display_manager, config)
    
    # Create the ticker image
    print(f"Creating ticker image for {len(games)} games...")
    ticker_image = renderer.create_ticker_image(games)
    
    if ticker_image:
        # Save the image
        output_path = "/home/chuck/Github/LEDMatrix/odds_ticker_preview.png"
        ticker_image.save(output_path)
        print(f"✅ Ticker image saved to: {output_path}")
        print(f"📏 Image dimensions: {ticker_image.size}")
        
        # Also save a zoomed version for better viewing
        zoomed_image = ticker_image.resize((ticker_image.width * 4, ticker_image.height * 4))
        zoomed_path = "/home/chuck/Github/LEDMatrix/odds_ticker_preview_zoomed.png"
        zoomed_image.save(zoomed_path)
        print(f"🔍 Zoomed image (4x) saved to: {zoomed_path}")
        
        return True
    else:
        print("❌ Failed to create ticker image")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
