# LEDMatrix Transition Testing Guide

This guide covers how to test the LEDMatrix transition system, including basic functionality, high-performance features, and decoupled frame rate capabilities.

## Quick Start

### Run All Tests
```bash
python test_transitions.py --all
```

### List Available Tests
```bash
python test_transitions.py --list
```

### Run Specific Test
```bash
python test_transitions.py --test basic
python test_transitions.py --test performance
python test_transitions.py --test decoupled
```

### Run Tests by Category
```bash
python test_transitions.py --category functionality
python test_transitions.py --category performance
python test_transitions.py --category advanced
```

## Available Tests

### 1. Basic Functionality Test (`test_transitions_basic.py`)
**Category**: Functionality  
**Description**: Tests basic transition functionality without hardware dependencies

**What it tests**:
- All transition types (scroll_left, scroll_right, scroll_up, scroll_down, redraw)
- Different scroll speeds (1, 3, 5)
- Different display sizes (64x32, 32x64, 64x64)
- Transition recommendations based on aspect ratio

**Usage**:
```bash
python test_transitions_basic.py
```

**Expected Output**:
- Mock display updates showing transition progression
- Performance metrics for each transition type
- Recommendations for optimal settings

### 2. Performance Test (`test_transitions_performance.py`)
**Category**: Performance  
**Description**: Tests high-performance transition system with FPS monitoring

**What it tests**:
- High-performance transition system (120 FPS target)
- Performance monitoring and statistics
- Different performance modes (high, balanced, low)
- Frame rate achievement metrics

**Usage**:
```bash
python test_transitions_performance.py
```

**Expected Output**:
- Detailed FPS measurements
- Performance statistics
- Recommendations for optimal configurations
- Frame time analysis

### 3. Decoupled Frame Rate Test (`test_transitions_decoupled.py`)
**Category**: Advanced  
**Description**: Demonstrates decoupled frame rate and scroll speed functionality

**What it tests**:
- Duration-based vs speed-based configurations
- Frame rate independence from scroll speed
- Different scenarios (high FPS + slow scroll, low FPS + fast scroll)
- Configuration examples and best practices

**Usage**:
```bash
python test_transitions_decoupled.py
```

**Expected Output**:
- Performance comparisons across different scenarios
- Configuration examples
- Demonstration of decoupled architecture benefits

## Test Categories

### Functionality Tests
- Basic transition operations
- Transition type validation
- Display size adaptation
- Configuration validation

### Performance Tests
- High-performance system testing
- FPS monitoring and achievement
- Performance mode comparisons
- Optimization effectiveness

### Advanced Tests
- Decoupled frame rate and scroll speed
- Duration-based configurations
- Optimal text scrolling settings
- Advanced configuration options

## Configuration Helper

### Get Transition Recommendations
```bash
python transition_config_helper.py [width] [height]
```

**Examples**:
```bash
# Auto-detect display dimensions
python transition_config_helper.py

# Specify dimensions
python transition_config_helper.py 64 32
python transition_config_helper.py 128 64
```

**Output**:
- Recommended transition types for your display
- Optimal speed settings
- Performance mode suggestions
- Configuration examples

## Understanding Test Results

### Basic Test Results
- **Transition Types**: Shows which transitions work best for your display
- **Speed Recommendations**: Optimal speed settings for smooth scrolling
- **Aspect Ratio Analysis**: Recommendations based on display dimensions

### Performance Test Results
- **Target FPS**: The FPS the system is trying to achieve
- **Actual FPS**: The FPS actually achieved during testing
- **FPS Achievement**: Percentage of target FPS achieved
- **Frame Time**: Average time per frame in milliseconds

### Decoupled Test Results
- **Duration Independence**: Shows how frame rate stays constant regardless of scroll speed
- **Configuration Examples**: Different ways to configure transitions
- **Performance Comparisons**: Side-by-side comparison of different scenarios

## Troubleshooting

### Common Issues

**1. Import Errors**
```
Error importing modules: No module named 'rgbmatrix'
```
**Solution**: Tests use mock display managers, so this shouldn't occur. If it does, check Python path.

**2. Performance Warnings**
```
Frame time exceeded target: 0.012s > 0.008s
```
**Solution**: This indicates the system is struggling to maintain target FPS. Consider:
- Using a lower performance mode
- Reducing scroll speed
- Optimizing content complexity

**3. Low FPS Achievement**
```
FPS achievement: 85.2%
```
**Solution**: 
- Check system resources
- Use balanced or low performance mode
- Optimize transition configuration

### Performance Optimization Tips

1. **For Text Scrolling**:
   - Use duration-based configuration
   - Set duration to 2-3 seconds for comfortable reading
   - Enable high-performance mode

2. **For Visual Effects**:
   - Use speed-based configuration for precise control
   - Consider balanced mode for efficiency
   - Monitor FPS achievement

3. **For Different Display Sizes**:
   - Wide displays: Prefer horizontal scrolling
   - Tall displays: Prefer vertical scrolling
   - Square displays: Both directions work well

## Integration with Plugins

### Enable High-Performance Transitions
```json
{
  "high_performance_transitions": true,
  "transition": {
    "type": "scroll_left",
    "duration": 2.0,
    "enabled": true
  }
}
```

### Monitor Performance in Production
```python
# Get performance statistics
stats = plugin.get_transition_performance_stats()
print(f"Actual FPS: {stats['actual_fps']:.1f}")
print(f"FPS Achievement: {stats['fps_achievement']:.1f}%")
```

## Best Practices

1. **Test Before Deployment**: Always run tests before deploying to production
2. **Monitor Performance**: Use performance statistics to optimize settings
3. **Use Appropriate Mode**: Choose performance mode based on hardware capabilities
4. **Optimize for Content**: Use duration-based config for text, speed-based for effects
5. **Regular Testing**: Run tests periodically to ensure optimal performance

## Next Steps

After running tests:
1. Note which transitions work best for your display
2. Choose optimal speed/duration settings
3. Update plugin configurations with recommended settings
4. Monitor performance in production
5. Adjust settings based on real-world usage