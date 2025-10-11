#!/usr/bin/env python3
"""
Test script for enhanced FontManager with manager registration and plugin support.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.font_manager import FontManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_font_loading():
    """Test basic font loading and caching."""
    print("\n=== Test: Basic Font Loading ===")
    
    fm = FontManager({})
    
    # Load a font
    font = fm.get_font("pressstart2p-regular", 10)
    print(f"✓ Loaded font: {type(font).__name__}")
    
    # Load same font again (should hit cache)
    font2 = fm.get_font("pressstart2p-regular", 10)
    print(f"✓ Cached font: {font is font2}")
    
    stats = fm.get_performance_stats()
    print(f"✓ Cache hit rate: {stats['cache_hit_rate']*100:.1f}%")
    print(f"✓ Cache hits: {stats['cache_hits']}, misses: {stats['cache_misses']}")

def test_manager_registration():
    """Test manager font registration and detection."""
    print("\n=== Test: Manager Font Registration ===")
    
    fm = FontManager({})
    
    # Register fonts for a manager
    fm.register_manager_font(
        manager_id="test_manager",
        element_key="test_manager.title",
        family="pressstart2p-regular",
        size_px=12,
        color=(255, 255, 0)
    )
    
    fm.register_manager_font(
        manager_id="test_manager",
        element_key="test_manager.body",
        family="4x6-font",
        size_px=6,
        color=(255, 255, 255)
    )
    
    # Get detected fonts
    detected = fm.get_detected_fonts()
    print(f"✓ Detected {len(detected)} font usages")
    
    for element_key, font_info in detected.items():
        print(f"  - {element_key}: {font_info['family']}@{font_info['size_px']}px "
              f"[{font_info.get('color', 'N/A')}] (used {font_info['usage_count']}x)")
    
    # Get manager fonts
    manager_fonts = fm.get_manager_fonts("test_manager")
    print(f"✓ Manager has {len(manager_fonts)} registered fonts")

def test_font_resolution_with_overrides():
    """Test font resolution with manual overrides."""
    print("\n=== Test: Font Resolution with Overrides ===")
    
    fm = FontManager({})
    
    # Register manager's choice
    element_key = "test_manager.score"
    fm.register_manager_font(
        manager_id="test_manager",
        element_key=element_key,
        family="pressstart2p-regular",
        size_px=10
    )
    
    # Resolve without override
    font1 = fm.resolve_font(element_key, "pressstart2p-regular", 10)
    print(f"✓ Resolved font (no override): {type(font1).__name__}")
    
    # Set override
    fm.set_override(element_key, family="4x6-font", size_px=8)
    print(f"✓ Set override: 4x6-font@8px")
    
    # Resolve with override
    font2 = fm.resolve_font(element_key, "pressstart2p-regular", 10)
    print(f"✓ Resolved font (with override): {type(font2).__name__}")
    print(f"✓ Fonts are different: {font1 is not font2}")
    
    # Get overrides
    overrides = fm.get_overrides()
    print(f"✓ Active overrides: {overrides}")
    
    # Remove override
    fm.remove_override(element_key)
    print(f"✓ Removed override")

def test_text_measurement():
    """Test text measurement functionality."""
    print("\n=== Test: Text Measurement ===")
    
    fm = FontManager({})
    
    font = fm.get_font("pressstart2p-regular", 10)
    
    # Measure text
    text = "Hello World"
    width, height, baseline = fm.measure_text(text, font)
    print(f"✓ Text '{text}' dimensions:")
    print(f"  - Width: {width}px")
    print(f"  - Height: {height}px")
    print(f"  - Baseline: {baseline}px")
    
    # Get font height
    font_height = fm.get_font_height(font)
    print(f"✓ Font height: {font_height}px")

def test_available_fonts():
    """Test font catalog and discovery."""
    print("\n=== Test: Available Fonts ===")
    
    fm = FontManager({})
    
    # Get available fonts
    fonts = fm.get_available_fonts()
    print(f"✓ Found {len(fonts)} available fonts:")
    for family, path in sorted(fonts.items())[:10]:  # Show first 10
        print(f"  - {family}: {path}")
    
    # Get size tokens
    tokens = fm.get_size_tokens()
    print(f"✓ Available size tokens: {tokens}")

def test_plugin_font_registration():
    """Test plugin font registration."""
    print("\n=== Test: Plugin Font Registration ===")
    
    fm = FontManager({})
    
    # Create a mock plugin manifest
    plugin_manifest = {
        "fonts": [
            {
                "family": "test_font",
                "source": "assets/fonts/PressStart2P-Regular.ttf",  # Use existing font for test
                "metadata": {
                    "description": "Test plugin font",
                    "license": "MIT"
                }
            }
        ]
    }
    
    # Register plugin fonts
    success = fm.register_plugin_fonts("test-plugin", plugin_manifest)
    print(f"✓ Plugin registration: {'Success' if success else 'Failed'}")
    
    # Get plugin fonts
    plugin_fonts = fm.get_plugin_fonts("test-plugin")
    print(f"✓ Plugin has {len(plugin_fonts)} fonts: {plugin_fonts}")
    
    # Try to use plugin font
    if success:
        font = fm.resolve_font(
            element_key="test-plugin.text",
            family="test_font",
            size_px=10,
            plugin_id="test-plugin"
        )
        print(f"✓ Loaded plugin font: {type(font).__name__}")
    
    # Unregister plugin
    fm.unregister_plugin_fonts("test-plugin")
    print(f"✓ Unregistered plugin fonts")

def test_performance_stats():
    """Test performance monitoring."""
    print("\n=== Test: Performance Stats ===")
    
    fm = FontManager({})
    
    # Perform some operations
    for i in range(10):
        fm.get_font("pressstart2p-regular", 10)
        fm.get_font("4x6-font", 8)
    
    # Get stats
    stats = fm.get_performance_stats()
    print(f"✓ Performance Statistics:")
    print(f"  - Uptime: {stats['uptime_seconds']:.2f}s")
    print(f"  - Cache hit rate: {stats['cache_hit_rate']*100:.1f}%")
    print(f"  - Total fonts cached: {stats['total_fonts_cached']}")
    print(f"  - Total metrics cached: {stats['total_metrics_cached']}")
    print(f"  - Failed loads: {stats['failed_loads']}")
    print(f"  - Manager fonts: {stats['manager_fonts']}")
    print(f"  - Plugin fonts: {stats['plugin_fonts']}")

def test_complete_workflow():
    """Test complete manager workflow."""
    print("\n=== Test: Complete Manager Workflow ===")
    
    fm = FontManager({})
    
    # Simulate a manager defining its fonts
    manager_id = "nfl_live"
    font_specs = {
        "score": {"family": "pressstart2p-regular", "size_px": 12, "color": (255, 255, 0)},
        "time": {"family": "4x6-font", "size_px": 8, "color": (255, 255, 255)},
        "team": {"family": "4x6-font", "size_px": 8, "color": (200, 200, 200)}
    }
    
    # Register all fonts
    print(f"✓ Registering fonts for {manager_id}...")
    for element_type, spec in font_specs.items():
        element_key = f"{manager_id}.{element_type}"
        fm.register_manager_font(
            manager_id=manager_id,
            element_key=element_key,
            family=spec["family"],
            size_px=spec["size_px"],
            color=spec["color"]
        )
        print(f"  - Registered {element_key}")
    
    # Simulate rendering
    print(f"✓ Resolving fonts for rendering...")
    for element_type, spec in font_specs.items():
        element_key = f"{manager_id}.{element_type}"
        font = fm.resolve_font(
            element_key=element_key,
            family=spec["family"],
            size_px=spec["size_px"]
        )
        print(f"  - Resolved {element_key}: {type(font).__name__}")
    
    # Show detected fonts
    detected = fm.get_detected_fonts()
    print(f"✓ Detected {len(detected)} font usages")
    
    # Simulate user override
    override_element = f"{manager_id}.score"
    print(f"✓ User applies override to {override_element}...")
    fm.set_override(override_element, family="4x6-font", size_px=10)
    
    # Resolve with override
    font_overridden = fm.resolve_font(
        element_key=override_element,
        family=font_specs["score"]["family"],
        size_px=font_specs["score"]["size_px"]
    )
    print(f"  - Resolved with override: {type(font_overridden).__name__}")
    
    # Show final stats
    stats = fm.get_performance_stats()
    print(f"✓ Final cache hit rate: {stats['cache_hit_rate']*100:.1f}%")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Enhanced FontManager Test Suite")
    print("="*60)
    
    tests = [
        test_basic_font_loading,
        test_manager_registration,
        test_font_resolution_with_overrides,
        test_text_measurement,
        test_available_fonts,
        test_plugin_font_registration,
        test_performance_stats,
        test_complete_workflow
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"✓ PASSED\n")
        except Exception as e:
            failed += 1
            print(f"✗ FAILED: {e}\n")
            logger.error(f"Test failed", exc_info=True)
    
    print("="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

