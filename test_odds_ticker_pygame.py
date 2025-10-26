#!/usr/bin/env python3
"""
Test script to display odds ticker using pygame
This will help us see if the odds ticker content is working correctly
"""

import sys
import os
import pygame
import time
from PIL import Image
import threading
import queue

# Add the LEDMatrix src directory to the path
sys.path.insert(0, '/home/chuck/Github/LEDMatrix/src')

# Import the odds ticker plugin
sys.path.insert(0, '/home/chuck/Github/ledmatrix-odds-ticker')
from manager import OddsTickerPlugin

class MockDisplayManager:
    """Mock display manager for testing"""
    def __init__(self):
        self.matrix = MockMatrix()
        self.image = None
        self.draw = None
        
    def update_display(self):
        """Mock update display"""
        pass
        
    def is_currently_scrolling(self):
        """Mock scrolling check"""
        return False
        
    def set_scrolling_state(self, state):
        """Mock scrolling state"""
        pass
        
    def process_deferred_updates(self):
        """Mock deferred updates"""
        pass

class MockMatrix:
    """Mock matrix for testing"""
    def __init__(self):
        self.width = 128
        self.height = 32

class MockCacheManager:
    """Mock cache manager for testing"""
    def get(self, key, max_age=None):
        return None
        
    def set(self, key, value, ttl=None):
        pass
        
    def get_with_auto_strategy(self, key, max_age=None):
        return None

class MockPluginManager:
    """Mock plugin manager for testing"""
    def get_config(self):
        return {}

def main():
    """Main test function"""
    print("🎯 Testing Odds Ticker with Pygame")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    
    # Set up display
    width, height = 128, 32
    scale = 8  # Scale up for better visibility
    screen = pygame.display.set_mode((width * scale, height * scale))
    pygame.display.set_caption("Odds Ticker Test")
    
    # Create mock objects
    display_manager = MockDisplayManager()
    cache_manager = MockCacheManager()
    plugin_manager = MockPluginManager()
    
    # Load configuration
    import json
    with open('/home/chuck/Github/LEDMatrix/config/config.json', 'r') as f:
        config = json.load(f)
    
    odds_config = config.get('odds-ticker', {})
    print(f"📊 Configuration loaded: {odds_config.get('enabled', False)}")
    
    # Create odds ticker plugin
    try:
        odds_ticker = OddsTickerPlugin(
            plugin_id="odds-ticker",
            config=odds_config,
            display_manager=display_manager,
            cache_manager=cache_manager,
            plugin_manager=plugin_manager
        )
        print("✅ Odds ticker plugin created successfully")
    except Exception as e:
        print(f"❌ Error creating odds ticker: {e}")
        return
    
    # Test update
    print("🔄 Testing data update...")
    try:
        odds_ticker.update()
        print("✅ Update completed")
    except Exception as e:
        print(f"❌ Error during update: {e}")
        return
    
    # Check if we have data
    if not odds_ticker.games_data:
        print("❌ No games data available")
        return
    
    print(f"📈 Found {len(odds_ticker.games_data)} games")
    for i, game in enumerate(odds_ticker.games_data[:3]):
        print(f"  Game {i+1}: {game.get('away_team', 'N/A')} @ {game.get('home_team', 'N/A')}")
    
    # Test image creation
    print("🖼️ Testing image creation...")
    try:
        odds_ticker._create_ticker_image()
        if odds_ticker.ticker_image:
            print(f"✅ Ticker image created: {odds_ticker.ticker_image.size}")
        else:
            print("❌ No ticker image created")
            return
    except Exception as e:
        print(f"❌ Error creating ticker image: {e}")
        return
    
    # Main display loop
    print("🎮 Starting pygame display loop...")
    print("Press ESC to exit, SPACE to update data")
    
    clock = pygame.time.Clock()
    scroll_position = 0
    scroll_speed = 2
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    print("🔄 Updating data...")
                    try:
                        odds_ticker.update()
                        odds_ticker._create_ticker_image()
                        scroll_position = 0
                        print("✅ Data updated")
                    except Exception as e:
                        print(f"❌ Error updating: {e}")
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Get the ticker image
        if odds_ticker.ticker_image:
            # Convert PIL image to pygame surface
            pil_image = odds_ticker.ticker_image
            
            # Create a surface for the visible portion
            visible_width = min(width, pil_image.width - scroll_position)
            if visible_width > 0:
                # Crop the visible portion
                crop_box = (scroll_position, 0, scroll_position + visible_width, height)
                visible_image = pil_image.crop(crop_box)
                
                # Convert to pygame surface
                mode = visible_image.mode
                size = visible_image.size
                data = visible_image.tobytes()
                pygame_surface = pygame.image.fromstring(data, size, mode)
                
                # Scale up for visibility
                scaled_surface = pygame.transform.scale(pygame_surface, (visible_width * scale, height * scale))
                screen.blit(scaled_surface, (0, 0))
            
            # Update scroll position
            scroll_position += scroll_speed
            if scroll_position >= pil_image.width:
                scroll_position = 0  # Loop back to start
        
        # Update display
        pygame.display.flip()
        clock.tick(20)  # 20 FPS
    
    pygame.quit()
    print("👋 Test completed")

if __name__ == "__main__":
    main()
