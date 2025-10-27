#!/usr/bin/env python3
"""
LEDMatrix Transition Configuration Helper

This script helps you determine the best transition settings for your LED matrix display.
It analyzes your display dimensions and provides recommendations.

Usage:
    python transition_config_helper.py [width] [height]

If no dimensions are provided, it will try to detect them from your display manager.
"""

import sys
import os
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from display_transitions import DisplayTransitions, TransitionType
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the LEDMatrix root directory")
    sys.exit(1)


class TransitionConfigHelper:
    """Helper class for transition configuration."""

    def __init__(self, width: int, height: int):
        """Initialize with display dimensions."""
        self.width = width
        self.height = height
        self.aspect_ratio = width / height

    def get_recommendations(self) -> Dict[str, Any]:
        """Get transition recommendations based on display dimensions."""
        recommendations = {
            "dimensions": f"{self.width}x{self.height}",
            "aspect_ratio": round(self.aspect_ratio, 2),
            "category": self._get_aspect_category(),
            "recommended_transitions": [],
            "avoid_transitions": [],
            "speed_recommendations": {},
            "example_configs": [],
        }

        # Determine aspect ratio category
        if self.aspect_ratio > 2.0:  # Very wide
            recommendations["category"] = "very_wide"
            recommendations["recommended_transitions"] = ["scroll_left", "scroll_right"]
            recommendations["avoid_transitions"] = ["scroll_up", "scroll_down"]
            recommendations["speed_recommendations"] = {
                "scroll_left": "2-4 (smooth horizontal scrolling)",
                "scroll_right": "2-4 (smooth horizontal scrolling)",
                "redraw": "N/A (instant)",
            }
        elif self.aspect_ratio > 1.5:  # Wide
            recommendations["category"] = "wide"
            recommendations["recommended_transitions"] = [
                "scroll_left",
                "scroll_right",
                "redraw",
            ]
            recommendations["avoid_transitions"] = []
            recommendations["speed_recommendations"] = {
                "scroll_left": "2-5 (good horizontal scrolling)",
                "scroll_right": "2-5 (good horizontal scrolling)",
                "redraw": "N/A (instant)",
            }
        elif self.aspect_ratio < 0.5:  # Very tall
            recommendations["category"] = "very_tall"
            recommendations["recommended_transitions"] = ["scroll_up", "scroll_down"]
            recommendations["avoid_transitions"] = ["scroll_left", "scroll_right"]
            recommendations["speed_recommendations"] = {
                "scroll_up": "1-3 (smooth vertical scrolling)",
                "scroll_down": "1-3 (smooth vertical scrolling)",
                "redraw": "N/A (instant)",
            }
        elif self.aspect_ratio < 0.75:  # Tall
            recommendations["category"] = "tall"
            recommendations["recommended_transitions"] = [
                "scroll_up",
                "scroll_down",
                "redraw",
            ]
            recommendations["avoid_transitions"] = []
            recommendations["speed_recommendations"] = {
                "scroll_up": "2-4 (good vertical scrolling)",
                "scroll_down": "2-4 (good vertical scrolling)",
                "redraw": "N/A (instant)",
            }
        else:  # Square-ish
            recommendations["category"] = "square"
            recommendations["recommended_transitions"] = [
                "scroll_left",
                "scroll_up",
                "redraw",
            ]
            recommendations["avoid_transitions"] = []
            recommendations["speed_recommendations"] = {
                "scroll_left": "2-5 (good horizontal scrolling)",
                "scroll_up": "2-5 (good vertical scrolling)",
                "redraw": "N/A (instant)",
            }

        # Generate example configurations
        recommendations["example_configs"] = self._generate_example_configs(
            recommendations
        )

        return recommendations

    def _get_aspect_category(self) -> str:
        """Get the aspect ratio category."""
        if self.aspect_ratio > 2.0:
            return "very_wide"
        elif self.aspect_ratio > 1.5:
            return "wide"
        elif self.aspect_ratio < 0.5:
            return "very_tall"
        elif self.aspect_ratio < 0.75:
            return "tall"
        else:
            return "square"

    def _generate_example_configs(self, recommendations: Dict[str, Any]) -> list:
        """Generate example configuration snippets."""
        configs = []

        # Global transition config
        global_config = {
            "transition": {
                "type": recommendations["recommended_transitions"][0],
                "speed": 3,
                "enabled": True,
            }
        }
        configs.append(
            {
                "name": "Global Plugin Configuration",
                "description": "Add this to any plugin config for basic transitions",
                "config": global_config,
            }
        )

        # Scoreboard-specific config
        if "scroll_left" in recommendations["recommended_transitions"]:
            scoreboard_config = {
                "transition": {"type": "scroll_left", "speed": 3, "enabled": True},
                "nfl": {"transition": {"type": "scroll_left", "speed": 3}},
                "ncaa_fb": {"transition": {"type": "scroll_right", "speed": 2}},
            }
            configs.append(
                {
                    "name": "Football Scoreboard Configuration",
                    "description": "Different transitions for different leagues",
                    "config": scoreboard_config,
                }
            )

        # Ticker-specific config
        ticker_config = {
            "transition": {
                "type": recommendations["recommended_transitions"][0],
                "speed": 2,
                "enabled": True,
            }
        }
        configs.append(
            {
                "name": "Ticker Plugin Configuration",
                "description": "Smooth continuous scrolling for tickers",
                "config": ticker_config,
            }
        )

        return configs

    def print_recommendations(self):
        """Print formatted recommendations."""
        rec = self.get_recommendations()

        print("LEDMatrix Transition Configuration Helper")
        print("=" * 50)
        print(f"Display Dimensions: {rec['dimensions']}")
        print(f"Aspect Ratio: {rec['aspect_ratio']}")
        print(f"Category: {rec['category']}")
        print()

        print("Recommended Transitions:")
        for transition in rec["recommended_transitions"]:
            print(f"  ✓ {transition}")

        if rec["avoid_transitions"]:
            print("\nTransitions to Avoid:")
            for transition in rec["avoid_transitions"]:
                print(f"  ✗ {transition}")

        print("\nSpeed Recommendations:")
        for transition, speed_desc in rec["speed_recommendations"].items():
            print(f"  {transition}: {speed_desc}")

        print("\nExample Configurations:")
        print("-" * 30)

        for example in rec["example_configs"]:
            print(f"\n{example['name']}:")
            print(f"Description: {example['description']}")
            print("Configuration:")
            self._print_config(example["config"], indent=2)

    def _print_config(self, config: Dict[str, Any], indent: int = 0):
        """Print configuration in a readable format."""
        spaces = " " * indent

        if isinstance(config, dict):
            print(f"{spaces}{{")
            for key, value in config.items():
                if isinstance(value, dict):
                    print(f'{spaces}  "{key}": {{')
                    self._print_config(value, indent + 4)
                    print(f"{spaces}  }}")
                elif isinstance(value, str):
                    print(f'{spaces}  "{key}": "{value}"')
                elif isinstance(value, bool):
                    print(f'{spaces}  "{key}": {str(value).lower()}')
                else:
                    print(f'{spaces}  "{key}": {value}')
            print(f"{spaces}}}")
        else:
            print(f"{spaces}{config}")


def detect_display_dimensions():
    """Try to detect display dimensions from display manager."""
    try:
        from display_manager import DisplayManager

        display_manager = DisplayManager()
        return display_manager.matrix.width, display_manager.matrix.height
    except Exception as e:
        print(f"Could not detect display dimensions: {e}")
        return None, None


def main():
    """Main function."""
    width = None
    height = None

    # Parse command line arguments
    if len(sys.argv) >= 3:
        try:
            width = int(sys.argv[1])
            height = int(sys.argv[2])
        except ValueError:
            print("Error: Width and height must be integers")
            return 1
    elif len(sys.argv) == 1:
        # Try to detect dimensions
        print("No dimensions provided, attempting to detect...")
        width, height = detect_display_dimensions()

        if width is None or height is None:
            print("Could not detect display dimensions.")
            print("Usage: python transition_config_helper.py [width] [height]")
            print("Example: python transition_config_helper.py 64 32")
            return 1
    else:
        print("Usage: python transition_config_helper.py [width] [height]")
        print("Example: python transition_config_helper.py 64 32")
        return 1

    # Create helper and show recommendations
    helper = TransitionConfigHelper(width, height)
    helper.print_recommendations()

    print("\n" + "=" * 50)
    print("Next Steps:")
    print("1. Run test_transitions.py to see transitions in action")
    print("2. Update your plugin configurations with recommended settings")
    print("3. Test with your actual content to fine-tune speeds")

    return 0


if __name__ == "__main__":
    sys.exit(main())
