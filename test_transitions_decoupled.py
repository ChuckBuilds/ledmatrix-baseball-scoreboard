#!/usr/bin/env python3
"""
Decoupled Frame Rate and Scroll Speed Demo

This script demonstrates how frame rate and scroll speed are now completely
independent in the high-performance transition system.
"""

import time
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List


class MockDisplayManager:
    """Mock display manager for testing decoupled transitions."""

    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        self.image = None
        self.matrix = type("Matrix", (), {"width": width, "height": height})()

    def update_display(self):
        """Mock display update - simulate hardware update time."""
        time.sleep(0.001)  # 1ms hardware update time


class DecoupledTransitionDemo:
    """Demo class showing decoupled frame rate and scroll speed."""

    def __init__(self, width=64, height=32):
        """Initialize the demo."""
        self.width = width
        self.height = height
        self.display_manager = MockDisplayManager(width, height)

        # Import the high-performance transition system
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
        from high_performance_transitions import HighPerformanceDisplayTransitions

        self.transition_manager = HighPerformanceDisplayTransitions(
            self.display_manager
        )

        # Create test content
        self.test_images = self.create_test_content()

    def create_test_content(self):
        """Create test content for scrolling."""
        images = []

        # Create a wide image for horizontal scrolling
        wide_width = self.width * 3
        img1 = Image.new("RGB", (wide_width, self.height), (0, 0, 0))
        draw1 = ImageDraw.Draw(img1)
        font = ImageFont.load_default()

        text = "This is a long scrolling text message that demonstrates how frame rate and scroll speed are now completely decoupled. "
        draw1.text((5, self.height // 2 - 5), text, fill=(255, 255, 255), font=font)

        # Create a tall image for vertical scrolling
        tall_height = self.height * 3
        img2 = Image.new("RGB", (self.width, tall_height), (0, 0, 0))
        draw2 = ImageDraw.Draw(img2)

        lines = [
            "Line 1: Frame rate and scroll speed are independent",
            "Line 2: You can have 120 FPS with slow scrolling",
            "Line 3: Or 30 FPS with fast scrolling",
            "Line 4: The choice is yours!",
            "Line 5: This enables smooth text reading",
            "Line 6: While maintaining high visual quality",
        ]

        for i, line in enumerate(lines):
            y_pos = i * (self.height // 3) + 5
            draw2.text((5, y_pos), line, fill=(0, 255, 255), font=font)

        return [img1, img2]

    def demonstrate_decoupled_transitions(self):
        """Demonstrate decoupled frame rate and scroll speed."""
        print("Decoupled Frame Rate and Scroll Speed Demo")
        print("=" * 50)
        print(f"Display: {self.width}x{self.height}")
        print("=" * 50)

        # Test scenarios
        scenarios = [
            {
                "name": "High FPS + Slow Scroll",
                "fps": 120,
                "duration": 3.0,  # 3 seconds for full scroll
                "description": "120 FPS with slow, readable scrolling",
            },
            {
                "name": "High FPS + Fast Scroll",
                "fps": 120,
                "duration": 0.5,  # 0.5 seconds for full scroll
                "description": "120 FPS with fast scrolling",
            },
            {
                "name": "Low FPS + Slow Scroll",
                "fps": 30,
                "duration": 3.0,  # 3 seconds for full scroll
                "description": "30 FPS with slow scrolling",
            },
            {
                "name": "Low FPS + Fast Scroll",
                "fps": 30,
                "duration": 0.5,  # 0.5 seconds for full scroll
                "description": "30 FPS with fast scrolling",
            },
        ]

        for scenario in scenarios:
            print(f"\n--- {scenario['name']} ---")
            print(f"Description: {scenario['description']}")

            # Set performance mode
            if scenario["fps"] >= 120:
                self.transition_manager.set_performance_mode("high")
            elif scenario["fps"] >= 60:
                self.transition_manager.set_performance_mode("balanced")
            else:
                self.transition_manager.set_performance_mode("low")

            print(f"Target FPS: {self.transition_manager.target_fps}")
            print(f"Scroll Duration: {scenario['duration']}s")

            # Test horizontal scrolling
            self.test_scroll_performance(
                "scroll_left", scenario["duration"], self.test_images[0]
            )

            # Test vertical scrolling
            self.test_scroll_performance(
                "scroll_up", scenario["duration"], self.test_images[1]
            )

            print(f"Completed {scenario['name']}")
            time.sleep(1)

    def test_scroll_performance(
        self, transition_type: str, duration: float, content_image: Image.Image
    ):
        """Test scroll performance with specific parameters."""
        print(f"\n  Testing {transition_type} for {duration}s...")

        # Create transition config with duration (decoupled from FPS)
        config = self.transition_manager.create_transition_config(
            transition_type=transition_type, duration=duration, enabled=True
        )

        # Measure performance
        start_time = time.perf_counter()
        frame_count = 0

        # Simulate the transition
        if transition_type in ["scroll_left", "scroll_right"]:
            frame_count = self._simulate_horizontal_scroll_decoupled(
                content_image, transition_type, duration
            )
        elif transition_type in ["scroll_up", "scroll_down"]:
            frame_count = self._simulate_vertical_scroll_decoupled(
                content_image, transition_type, duration
            )

        end_time = time.perf_counter()
        total_time = end_time - start_time
        actual_fps = frame_count / total_time if total_time > 0 else 0

        print(f"    Frames rendered: {frame_count}")
        print(f"    Total time: {total_time:.3f}s")
        print(f"    Actual FPS: {actual_fps:.1f}")
        print(f"    Target FPS: {self.transition_manager.target_fps}")
        print(
            f"    FPS achievement: {(actual_fps / self.transition_manager.target_fps) * 100:.1f}%"
        )

    def _simulate_horizontal_scroll_decoupled(self, content_image, direction, duration):
        """Simulate horizontal scroll with decoupled frame rate and speed."""
        # Create composite image
        composite_width = self.width * 2
        composite_height = self.height

        composite = Image.new("RGB", (composite_width, composite_height), (0, 0, 0))

        if direction == "scroll_left":
            composite.paste(content_image, (0, 0))
            composite.paste(content_image, (self.width, 0))
        else:  # scroll_right
            composite.paste(content_image, (self.width, 0))
            composite.paste(content_image, (0, 0))

        composite_array = np.array(composite)

        # Calculate frames based on duration and target FPS (DECOUPLED)
        total_frames = int(duration * self.transition_manager.target_fps)
        scroll_distance = self.width

        print(f"    Scroll distance: {scroll_distance}px")
        print(f"    Total frames: {total_frames}")
        print(
            f"    Effective scroll speed: {scroll_distance / duration:.1f} pixels/second"
        )

        # Simulate frame loop with consistent frame rate
        for frame in range(total_frames):
            frame_start = time.perf_counter()

            # Calculate offset based on progress (not speed)
            progress = frame / (total_frames - 1) if total_frames > 1 else 0
            offset = int(progress * scroll_distance)
            offset = min(offset, scroll_distance - 1)

            # Apply direction
            if direction == "scroll_right":
                offset = scroll_distance - offset

            # Fast numpy slice
            frame_array = composite_array[:, offset : offset + self.width]
            frame_image = Image.fromarray(frame_array)

            # Simulate display update
            self.display_manager.image = frame_image
            self.display_manager.update_display()

            # Maintain consistent frame rate
            frame_time = time.perf_counter() - frame_start
            target_frame_time = self.transition_manager.frame_delay

            if frame_time < target_frame_time:
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0.001:
                    time.sleep(sleep_time)

        return total_frames

    def _simulate_vertical_scroll_decoupled(self, content_image, direction, duration):
        """Simulate vertical scroll with decoupled frame rate and speed."""
        # Create composite image
        composite_width = self.width
        composite_height = self.height * 2

        composite = Image.new("RGB", (composite_width, composite_height), (0, 0, 0))

        if direction == "scroll_up":
            composite.paste(content_image, (0, 0))
            composite.paste(content_image, (0, self.height))
        else:  # scroll_down
            composite.paste(content_image, (0, self.height))
            composite.paste(content_image, (0, 0))

        composite_array = np.array(composite)

        # Calculate frames based on duration and target FPS (DECOUPLED)
        total_frames = int(duration * self.transition_manager.target_fps)
        scroll_distance = self.height

        print(f"    Scroll distance: {scroll_distance}px")
        print(f"    Total frames: {total_frames}")
        print(
            f"    Effective scroll speed: {scroll_distance / duration:.1f} pixels/second"
        )

        # Simulate frame loop with consistent frame rate
        for frame in range(total_frames):
            frame_start = time.perf_counter()

            # Calculate offset based on progress (not speed)
            progress = frame / (total_frames - 1) if total_frames > 1 else 0
            offset = int(progress * scroll_distance)
            offset = min(offset, scroll_distance - 1)

            # Apply direction
            if direction == "scroll_down":
                offset = scroll_distance - offset

            # Fast numpy slice
            frame_array = composite_array[offset : offset + self.height, :]
            frame_image = Image.fromarray(frame_array)

            # Simulate display update
            self.display_manager.image = frame_image
            self.display_manager.update_display()

            # Maintain consistent frame rate
            frame_time = time.perf_counter() - frame_start
            target_frame_time = self.transition_manager.frame_delay

            if frame_time < target_frame_time:
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0.001:
                    time.sleep(sleep_time)

        return total_frames

    def show_configuration_examples(self):
        """Show examples of how to configure decoupled transitions."""
        print("\n" + "=" * 60)
        print("CONFIGURATION EXAMPLES")
        print("=" * 60)

        print("\n1. Duration-based configuration (recommended for text):")
        config1 = self.transition_manager.create_transition_config(
            transition_type="scroll_left",
            duration=2.0,  # 2 seconds for full scroll
            enabled=True,
        )
        print(f"   Config: {config1}")
        print("   Result: Smooth scrolling at target FPS for exactly 2 seconds")

        print("\n2. Speed-based configuration (legacy mode):")
        config2 = self.transition_manager.create_transition_config(
            transition_type="scroll_left", speed=4, enabled=True  # 4 pixels per frame
        )
        print(f"   Config: {config2}")
        print(
            "   Result: Scrolls 4 pixels per frame (duration depends on content length)"
        )

        print("\n3. Optimal text scrolling configuration:")
        config3 = self.transition_manager.get_optimal_scroll_config(
            transition_type="scroll_left", content_length=200  # 200 pixels of content
        )
        print(f"   Config: {config3}")
        print("   Result: Automatically calculated duration for comfortable reading")

        print("\n4. High-performance mode for smooth text:")
        self.transition_manager.optimize_for_text_scrolling()
        stats = self.transition_manager.get_performance_stats()
        print(f"   Performance stats: {stats}")


def main():
    """Main function."""
    print("Decoupled Frame Rate and Scroll Speed Demo")
    print("==========================================")

    # Test different display sizes
    test_sizes = [
        (64, 32),  # Wide display
        (32, 64),  # Tall display
    ]

    for width, height in test_sizes:
        print(f"\n{'='*60}")
        print(f"Testing {width}x{height} display")
        print(f"{'='*60}")

        demo = DecoupledTransitionDemo(width, height)
        demo.demonstrate_decoupled_transitions()
        demo.show_configuration_examples()

        print(f"\nCompleted testing for {width}x{height} display")
        time.sleep(1)

    print("\n" + "=" * 60)
    print("KEY BENEFITS OF DECOUPLED FRAME RATE AND SCROLL SPEED")
    print("=" * 60)
    print("1. Consistent visual quality regardless of scroll speed")
    print("2. Smooth text reading with high FPS")
    print("3. Flexible configuration options")
    print("4. Better performance monitoring")
    print("5. Optimal user experience for different content types")


if __name__ == "__main__":
    main()
