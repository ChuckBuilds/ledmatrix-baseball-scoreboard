# Display Transitions System

The LEDMatrix Display Transitions System provides smooth, configurable transitions between content on LED matrix displays. This system allows plugins to choose how content transitions on and off the display with granular control over direction and speed.

## Overview

The transition system supports:
- **Horizontal scrolling**: Left and right directions
- **Vertical scrolling**: Up and down directions  
- **Simple redraw**: Instant content change (default behavior)
- **Configurable speed**: 1-10 pixels per frame
- **Display size awareness**: Automatic adaptation to any display dimensions

## Architecture

### Core Components

1. **`DisplayTransitions`** (`src/display_transitions.py`): Core transition engine
2. **`BasePlugin`** integration: Automatic transition support for all plugins
3. **Plugin-specific implementations**: Scoreboard and ticker plugins with transition support

### Key Classes

#### DisplayTransitions
```python
class DisplayTransitions:
    def __init__(self, display_manager)
    def transition(self, from_image, to_image, transition_config)
    def get_recommended_transitions(self)
    def validate_transition_config(self, config)
```

#### BasePlugin Integration
```python
class BasePlugin:
    def apply_transition(self, new_image, transition_config=None)
    def get_transition_recommendations(self)
    def _load_transition_config(self)
```

## Configuration

### Global Plugin Configuration

Add transition settings to your plugin configuration:

```json
{
  "transition": {
    "type": "scroll_left",
    "speed": 2,
    "enabled": true
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | `"redraw"` | Transition type: `scroll_left`, `scroll_right`, `scroll_up`, `scroll_down`, `redraw` |
| `speed` | integer | `2` | Scroll speed in pixels per frame (1-10) |
| `enabled` | boolean | `true` | Enable transition effects |

### Per-League Configuration (Scoreboard Plugins)

For scoreboard plugins, you can configure transitions per league:

```json
{
  "nfl": {
    "transition": {
      "type": "scroll_left",
      "speed": 3,
      "enabled": true
    }
  },
  "ncaa_fb": {
    "transition": {
      "type": "scroll_right", 
      "speed": 2,
      "enabled": true
    }
  }
}
```

## Usage Examples

### Basic Plugin Integration

```python
from src.plugin_system.base_plugin import BasePlugin
from PIL import Image

class MyPlugin(BasePlugin):
    def display(self, force_clear=False):
        # Create your content image
        new_image = self._render_content()
        
        # Use transition system
        self.apply_transition(new_image)
```

### Custom Transition Configuration

```python
def display(self, force_clear=False):
    new_image = self._render_content()
    
    # Custom transition config
    custom_config = {
        'type': 'scroll_up',
        'speed': 4,
        'enabled': True
    }
    
    self.apply_transition(new_image, custom_config)
```

### Manual Transition Control

```python
def display(self, force_clear=False):
    if self.transition_manager:
        current_image = self.display_manager.image
        new_image = self._render_content()
        
        config = {
            'type': 'scroll_left',
            'speed': self.scroll_speed,
            'enabled': True
        }
        
        self.transition_manager.transition(current_image, new_image, config)
    else:
        # Fallback to simple redraw
        self.display_manager.image = new_image
        self.display_manager.update_display()
```

## Display Size Recommendations

The system automatically detects display dimensions and provides recommendations:

### Very Wide Displays (aspect ratio > 2.0)
- **Recommended**: `scroll_left`, `scroll_right`
- **Avoid**: `scroll_up`, `scroll_down`
- **Example**: 128x32, 256x32

### Wide Displays (aspect ratio > 1.5)
- **Recommended**: `scroll_left`, `scroll_right`, `redraw`
- **Example**: 64x32, 96x32

### Very Tall Displays (aspect ratio < 0.5)
- **Recommended**: `scroll_up`, `scroll_down`
- **Avoid**: `scroll_left`, `scroll_right`
- **Example**: 32x128, 32x256

### Tall Displays (aspect ratio < 0.75)
- **Recommended**: `scroll_up`, `scroll_down`, `redraw`
- **Example**: 32x64, 32x96

### Square Displays (aspect ratio 0.75-1.5)
- **Recommended**: `scroll_left`, `scroll_up`, `redraw`
- **Example**: 64x64, 32x32

## Performance Considerations

### Frame Rate
- Target: 30 FPS for smooth scrolling
- Maximum transition time: 2 seconds
- Automatic speed adjustment for long transitions

### Memory Usage
- Efficient PIL image compositing
- Reused image buffers
- Minimal memory overhead

### CPU Usage
- Frame-by-frame rendering optimized for LED matrices
- Configurable speed limits prevent excessive CPU usage

## Migration Guide

### Existing Plugins

Existing plugins automatically get transition support through `BasePlugin`:

1. **No changes required** - plugins continue to work with `redraw` transitions
2. **Opt-in enhancement** - add transition configuration to enable smooth scrolling
3. **Backwards compatible** - all existing functionality preserved

### Plugin Updates

To add transition support to existing plugins:

1. **Add configuration schema**:
```json
{
  "transition": {
    "type": "object",
    "properties": {
      "type": {"enum": ["scroll_left", "scroll_right", "scroll_up", "scroll_down", "redraw"]},
      "speed": {"type": "integer", "minimum": 1, "maximum": 10},
      "enabled": {"type": "boolean"}
    }
  }
}
```

2. **Update display method**:
```python
def display(self, force_clear=False):
    new_image = self._render_content()
    self.apply_transition(new_image)
```

3. **Test with different display sizes** to ensure optimal performance

## Troubleshooting

### Common Issues

#### Transitions Not Working
- Check that `transition.enabled` is `true`
- Verify `DisplayTransitions` is properly initialized
- Ensure `display_manager` is available

#### Poor Performance
- Reduce `speed` value (1-3 recommended)
- Use `redraw` for instant updates if needed
- Check display dimensions match recommendations

#### Configuration Validation Errors
- Ensure `type` is one of the valid enum values
- Verify `speed` is between 1-10
- Check JSON syntax in configuration files

### Debug Information

Enable debug logging to see transition system status:

```python
import logging
logging.getLogger('src.display_transitions').setLevel(logging.DEBUG)
```

### Getting Recommendations

```python
recommendations = self.get_transition_recommendations()
print(f"Aspect ratio: {recommendations['recommendations']['aspect_ratio']}")
print(f"Recommended: {recommendations['recommendations']['recommended']}")
print(f"Avoid: {recommendations['recommendations']['avoid']}")
```

## Best Practices

### Configuration
- Start with `redraw` for testing, then enable transitions
- Use recommended transitions for your display size
- Test different speeds to find optimal performance
- Configure per-league transitions for scoreboard plugins

### Performance
- Use speed 1-3 for smooth scrolling
- Avoid transitions on very small displays (< 32 pixels)
- Consider `redraw` for frequently updating content

### User Experience
- Provide configuration options in web UI
- Show transition previews when possible
- Allow users to disable transitions if performance is poor
- Document recommended settings for common display sizes

## API Reference

### DisplayTransitions Methods

#### `transition(from_image, to_image, transition_config)`
Execute transition between two images.

**Parameters:**
- `from_image` (Image): Source image (None for first display)
- `to_image` (Image): Target image
- `transition_config` (dict): Configuration with 'type', 'speed', 'enabled'

#### `get_recommended_transitions()`
Get transition recommendations based on display dimensions.

**Returns:** Dict with aspect ratio info and recommendations

#### `validate_transition_config(config)`
Validate transition configuration.

**Parameters:**
- `config` (dict): Configuration to validate

**Returns:** Tuple of (is_valid, error_message)

### BasePlugin Methods

#### `apply_transition(new_image, transition_config=None)`
Apply transition to display new image.

**Parameters:**
- `new_image` (Image): PIL Image to transition to
- `transition_config` (dict): Optional override configuration

#### `get_transition_recommendations()`
Get transition recommendations and current configuration.

**Returns:** Dict with recommendations and current config

## Examples

### Football Scoreboard with Transitions
```json
{
  "transition": {
    "type": "scroll_left",
    "speed": 3,
    "enabled": true
  },
  "nfl": {
    "transition": {
      "type": "scroll_left",
      "speed": 3
    }
  },
  "ncaa_fb": {
    "transition": {
      "type": "scroll_right", 
      "speed": 2
    }
  }
}
```

### Odds Ticker Configuration
```json
{
  "transition": {
    "type": "scroll_left",
    "speed": 2,
    "enabled": true
  },
  "scroll_speed": 2,
  "display_duration": 30
}
```

### Tall Display Configuration
```json
{
  "transition": {
    "type": "scroll_up",
    "speed": 1,
    "enabled": true
  }
}
```

This transition system provides a powerful, flexible way to enhance the visual experience of LED matrix displays while maintaining excellent performance and backwards compatibility.
