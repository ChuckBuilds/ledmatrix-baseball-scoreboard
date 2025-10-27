#!/usr/bin/env python3
"""
Standalone LEDMatrix Transition Test

This script tests the transition logic directly without requiring the full display manager.
It creates a simple mock display manager and tests all transition types.
"""

import time
import sys
import os
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont


class MockDisplayManager:
    """Mock display manager for testing transitions."""

    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        self.image = None

        # Create a mock matrix object
        self.matrix = type("Matrix", (), {"width": width, "height": height})()

    def update_display(self):
        """Mock display update - just print info."""
        if self.image:
            print(f"  Display updated: {self.image.size}")
        else:
            print("  Display cleared")


class MockDisplayTransitions:
    """Mock transition system for testing."""

    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.width = display_manager.matrix.width
        self.height = display_manager.matrix.height
        print(
            f"Mock DisplayTransitions initialized for {self.width}x{self.height} display"
        )

    def transition(self, from_image, to_image, transition_config):
        """Execute transition from one image to another."""
        if not transition_config.get("enabled", True):
            self._redraw(to_image)
            return

        transition_type = transition_config.get("type", "redraw")
        speed = transition_config.get("speed", 2)

        print(f"    Executing {transition_type} transition at speed {speed}")

        try:
            if transition_type == "redraw":
                self._redraw(to_image)
            elif transition_type in ["scroll_left", "scroll_right"]:
                self._scroll_horizontal(from_image, to_image, transition_type, speed)
            elif transition_type in ["scroll_up", "scroll_down"]:
                self._scroll_vertical(from_image, to_image, transition_type, speed)
            else:
                print(f"    Unknown transition type: {transition_type}, using redraw")
                self._redraw(to_image)

        except Exception as e:
            print(f"    Error during transition: {e}")
            self._redraw(to_image)

    def _scroll_horizontal(self, from_image, to_image, direction, speed):
        """Execute horizontal scrolling transition."""
        if from_image is None:
            self._redraw(to_image)
            return

        print(f"      Horizontal scroll: {direction}, speed {speed}")
        print(f"      From: {from_image.size} -> To: {to_image.size}")

        # Simulate scroll animation
        scroll_distance = self.width
        total_frames = max(1, scroll_distance // speed)

        print(f"      Scroll distance: {scroll_distance}px, {total_frames} frames")

        # Simulate frame-by-frame animation
        for frame in range(min(total_frames, 5)):  # Limit to 5 frames for demo
            offset = frame * speed
            print(f"        Frame {frame}: offset {offset}px")
            time.sleep(0.1)  # Small delay to show progression

        self._redraw(to_image)

    def _scroll_vertical(self, from_image, to_image, direction, speed):
        """Execute vertical scrolling transition."""
        if from_image is None:
            self._redraw(to_image)
            return

        print(f"      Vertical scroll: {direction}, speed {speed}")
        print(f"      From: {from_image.size} -> To: {to_image.size}")

        # Simulate scroll animation
        scroll_distance = self.height
        total_frames = max(1, scroll_distance // speed)

        print(f"      Scroll distance: {scroll_distance}px, {total_frames} frames")

        # Simulate frame-by-frame animation
        for frame in range(min(total_frames, 5)):  # Limit to 5 frames for demo
            offset = frame * speed
            print(f"        Frame {frame}: offset {offset}px")
            time.sleep(0.1)  # Small delay to show progression

        self._redraw(to_image)

    def _redraw(self, image):
        """Simple redraw transition (instant)."""
        print(f"      Instant redraw: {image.size}")
        self.display_manager.image = image.copy()
        self.display_manager.update_display()

    def get_recommended_transitions(self):
        """Get recommended transition types based on display dimensions."""
        aspect_ratio = self.width / self.height

        if aspect_ratio > 2.0:  # Very wide
            return {
                "aspect_ratio": "very_wide",
                "recommended": ["scroll_left", "scroll_right"],
                "avoid": ["scroll_up", "scroll_down"],
            }
        elif aspect_ratio > 1.5:  # Wide
            return {
                "aspect_ratio": "wide",
                "recommended": ["scroll_left", "scroll_right", "redraw"],
                "avoid": [],
            }
        elif aspect_ratio < 0.5:  # Very tall
            return {
                "aspect_ratio": "very_tall",
                "recommended": ["scroll_up", "scroll_down"],
                "avoid": ["scroll_left", "scroll_right"],
            }
        elif aspect_ratio < 0.75:  # Tall
            return {
                "aspect_ratio": "tall",
                "recommended": ["scroll_up", "scroll_down", "redraw"],
                "avoid": [],
            }
        else:  # Square-ish
            return {
                "aspect_ratio": "square",
                "recommended": ["scroll_left", "scroll_up", "redraw"],
                "avoid": [],
            }


class StandaloneTransitionTester:
    """Standalone test class for LEDMatrix transitions."""

    def __init__(self, width=64, height=32):
        """Initialize the transition tester."""
        self.width = width
        self.height = height
        self.display_manager = MockDisplayManager(width, height)
        self.transition_manager = MockDisplayTransitions(self.display_manager)

        # Test configuration
        self.test_duration = 1.0  # seconds per test
        self.test_speeds = [1, 3, 5]  # speeds to test
        self.test_transitions = [
            "scroll_left",
            "scroll_right",
            "scroll_up",
            "scroll_down",
            "redraw",
        ]

        # Sample content for testing
        self.sample_images = []

    def create_sample_images(self):
        """Create sample images for testing transitions."""
        print(f"Creating sample images for {self.width}x{self.height} display...")

        # Image 1: Welcome message
        img1 = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        draw1 = ImageDraw.Draw(img1)
        font = ImageFont.load_default()

        text1 = "LEDMatrix"
        text2 = "Transitions"

        # Simple text positioning
        draw1.text((5, self.height // 2 - 10), text1, fill=(255, 255, 255), font=font)
        draw1.text((5, self.height // 2 + 5), text2, fill=(0, 255, 255), font=font)

        # Image 2: Color bars
        img2 = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        draw2 = ImageDraw.Draw(img2)

        # Draw colored rectangles
        if self.width >= 4:
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            rect_width = self.width // 4
            for i, color in enumerate(colors):
                x_start = i * rect_width
                x_end = (i + 1) * rect_width
                draw2.rectangle([x_start, 0, x_end, self.height], fill=color)

        # Image 3: Pattern
        img3 = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        draw3 = ImageDraw.Draw(img3)

        # Draw a simple pattern
        for x in range(0, self.width, 2):
            for y in range(0, self.height, 2):
                if (x + y) % 4 == 0:
                    draw3.point((x, y), fill=(255, 255, 255))

        # Image 4: Text pattern
        img4 = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        draw4 = ImageDraw.Draw(img4)

        # Draw text at different positions
        font_small = ImageFont.load_default()
        texts = ["A", "B", "C", "D"]
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

        for i, (text, color) in enumerate(zip(texts, colors)):
            x = (i * self.width) // 4 + 5
            y = self.height // 2
            draw4.text((x, y), text, fill=color, font=font_small)

        self.sample_images = [img1, img2, img3, img4]
        print(f"Created {len(self.sample_images)} sample images")

    def test_transition(
        self,
        transition_type: str,
        speed: int,
        from_image: Image.Image,
        to_image: Image.Image,
    ):
        """Test a specific transition type and speed."""
        config = {"type": transition_type, "speed": speed, "enabled": True}

        print(f"  Testing {transition_type} at speed {speed}...")

        # Apply the transition
        self.transition_manager.transition(from_image, to_image, config)

        # Wait for the specified duration
        time.sleep(self.test_duration)

    def run_transition_tests(self):
        """Run all transition tests."""
        if not self.sample_images:
            print("No sample images available!")
            return

        print("\n" + "=" * 60)
        print("LEDMatrix Transition Test Suite (Standalone)")
        print("=" * 60)
        print(f"Display: {self.width}x{self.height}")
        print(f"Test duration per transition: {self.test_duration} seconds")
        print(f"Testing speeds: {self.test_speeds}")
        print(f"Testing transitions: {self.test_transitions}")
        print("=" * 60)

        # Start with a welcome screen
        welcome_img = self.sample_images[0]
        self.display_manager.image = welcome_img.copy()
        self.display_manager.update_display()
        time.sleep(1)

        test_count = 0
        total_tests = (
            len(self.test_transitions)
            * len(self.test_speeds)
            * (len(self.sample_images) - 1)
        )

        for transition_type in self.test_transitions:
            print(f"\n--- Testing {transition_type.upper()} ---")

            for speed in self.test_speeds:
                # Test transitions between different image pairs
                for i in range(len(self.sample_images) - 1):
                    from_image = self.sample_images[i]
                    to_image = self.sample_images[i + 1]

                    test_count += 1
                    print(
                        f"\nTest {test_count}/{total_tests}: {transition_type} speed {speed}"
                    )

                    self.test_transition(transition_type, speed, from_image, to_image)

        print("\n" + "=" * 60)
        print("All transition tests completed!")
        print("=" * 60)

        # Show final summary
        self.show_summary()

    def show_summary(self):
        """Show a summary of the test results."""
        print("\nTransition Test Summary:")
        print("-" * 40)

        recommendations = self.transition_manager.get_recommended_transitions()
        print(f"Display aspect ratio: {recommendations['aspect_ratio']}")
        print(f"Recommended transitions: {', '.join(recommendations['recommended'])}")

        if recommendations["avoid"]:
            print(f"Transitions to avoid: {', '.join(recommendations['avoid'])}")

        print("\nSpeed recommendations:")
        print("- Speed 1-2: Very smooth, slower transitions")
        print("- Speed 3-5: Good balance of smoothness and speed")
        print("- Speed 6-8: Faster transitions, may appear choppy")
        print("- Speed 9-10: Very fast, likely choppy on most displays")

        print("\nNext steps:")
        print("1. Note which transitions looked best on your display")
        print("2. Choose optimal speed settings for your use case")
        print("3. Update your plugin configurations with these settings")


def main():
    """Main function."""
    print("LEDMatrix Transition Test Script (Standalone)")
    print("=============================================")

    # Test different display sizes
    test_sizes = [
        (64, 32),  # Wide display
        (32, 64),  # Tall display
        (64, 64),  # Square display
    ]

    for width, height in test_sizes:
        print(f"\n{'='*60}")
        print(f"Testing {width}x{height} display")
        print(f"{'='*60}")

        tester = StandaloneTransitionTester(width, height)

        # Create sample images
        tester.create_sample_images()

        # Run tests
        tester.run_transition_tests()

        print(f"\nCompleted testing for {width}x{height} display")
        time.sleep(1)

    print("\n" + "=" * 60)
    print("All display size tests completed!")
    print("=" * 60)
    print(
        "This demonstrates how the transition system adapts to different display sizes."
    )
    print("The actual LEDMatrix system will work similarly with your hardware.")


if __name__ == "__main__":
    main()
