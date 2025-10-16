# Plugin Live Priority - Quick Start Guide

## 🎯 What Is It?

Live Priority allows your plugin to **take over the display** when it has urgent/live content (sports games, breaking news, etc.)

## 🚀 Quick Implementation (3 Steps)

### Step 1: Enable in Config

```json
{
  "my-plugin": {
    "enabled": true,
    "live_priority": true  // ← Add this!
  }
}
```

### Step 2: Implement `has_live_content()`

```python
class MyPlugin(BasePlugin):
    def has_live_content(self) -> bool:
        # Return True when you have live content
        return len(self.live_games) > 0
```

### Step 3: Done! 🎉

The display controller automatically:
- Detects when your plugin has live content
- Takes over the display
- Shows your live modes
- Returns to normal when live content ends

## 📋 Complete Example

```python
from src.plugin_system import BasePlugin

class SportsPlugin(BasePlugin):
    def __init__(self, plugin_id, config, display_manager, cache_manager, plugin_manager):
        super().__init__(plugin_id, config, display_manager, cache_manager, plugin_manager)
        self.live_games = []
    
    def update(self):
        """Fetch games from API"""
        self.live_games = self._fetch_live_games()
    
    def has_live_content(self) -> bool:
        """Called by display controller to check for live content"""
        return len(self.live_games) > 0
    
    def get_live_modes(self) -> list:
        """Optional: Specify which modes to show (default: all modes)"""
        return ['sports_live']  # Only show live games, not upcoming/recent
    
    def display(self, force_clear=False):
        """Render your content"""
        if force_clear:
            self.display_manager.clear()
        
        # Your display logic here
        self._draw_live_game()
        
        self.display_manager.update_display()
```

## 🔧 Optional: Control Which Modes Show

By default, ALL your display modes show during live priority. To customize:

```python
def get_live_modes(self) -> list:
    # Only show specific modes
    return ['hockey_live', 'hockey_score']  
    
    # NOT these:
    # return ['hockey_recent', 'hockey_upcoming']
```

## 📊 How It Works

```
Normal rotation: clock → weather → calendar → ...
                                    ↓
          🚨 Your plugin detects live game!
                                    ↓
Live takeover:   hockey_live → hockey_live → ...
                                    ↓
          ✅ Game ends (has_live_content returns False)
                                    ↓
Back to normal:  clock → weather → calendar → ...
```

## 🐛 Testing

### 1. Add Debug Logging

```python
def has_live_content(self) -> bool:
    has_live = len(self.live_games) > 0
    self.logger.info(f"🎮 Live content check: {has_live} ({len(self.live_games)} games)")
    return has_live
```

### 2. Watch Logs

```bash
sudo journalctl -u ledmatrix -f | grep -i "live\|priority"
```

### 3. Expected Output

```
Live priority takeover! clock -> hockey_live
Added live mode to rotation: hockey_live (plugin: hockey-scoreboard)
Rotating live priority modes: hockey_live -> basketball_live
Removed live mode from rotation: hockey_live (plugin: hockey-scoreboard)
```

## ❓ FAQ

### Q: Can multiple plugins have live priority?
**A:** Yes! All live modes rotate together:
```
hockey_live → basketball_live → hockey_live → ...
```

### Q: How long does each mode display?
**A:** Uses your `display_duration` from config (default: 15 seconds)

### Q: What if I don't override `has_live_content()`?
**A:** Default is always `False` - no live priority takeover

### Q: Can I disable live priority temporarily?
**A:** Yes, set `"live_priority": false` in config

## 📚 Full Documentation

See `PLUGIN_LIVE_PRIORITY_API.md` for:
- Complete API reference
- Advanced examples
- Troubleshooting guide
- Best practices

## ⚡ Key Points

1. **Enable in config:** `"live_priority": true`
2. **Implement detection:** Override `has_live_content()`
3. **Automatic takeover:** Display controller handles everything
4. **No hard-coding:** Fully dynamic, works with any content type

That's it! Your plugin now supports live priority! 🚀

