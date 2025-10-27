#!/usr/bin/env python3
"""
High-Performance LEDMatrix Transition Test

This script tests the high-performance transition system and measures
actual FPS to ensure smooth 100+ FPS scrolling for text.
"""

import time
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List


class MockDisplayManager:
    """Mock display manager for testing high-performance transitions."""

    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        self.image = None
        
        # Create a mock matrix object
        self.matrix = type("Matrix", (), {"width": width, "height": height})()

    def update_display(self):
        """Mock display update - simulate hardware update time."""
        # Simulate realistic hardware update time (typically 1-2ms)
        time.sleep(0.001)  # 1ms hardware update time


class HighPerformanceTransitionTester:
    """Test class for high-performance transitions."""

    def __init__(self, width=64, height=32):
        """Initialize the high-performance tester."""
        self.width = width
        self.height = height
        self.display_manager = MockDisplayManager(width, height)
        
        # Import the high-performance transition system
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from high_performance_transitions import HighPerformanceDisplayTransitions
        
        self.transition_manager = HighPerformanceDisplayTransitions(self.display_manager)
        
        # Performance tracking
        self.performance_data = []
        
        # Test images
        self.sample_images = self.create_text_images()

    def create_text_images(self):
        """Create sample text images for testing."""
        images = []
        
        # Image 1: Long scrolling text
        img1 = Image.new("RGB", (self.width * 3, self.height), (0, 0, 0))  # 3x width for scrolling
        draw1 = ImageDraw.Draw(img1)
        font = ImageFont.load_default()
        
        text = "This is a long scrolling text message that demonstrates smooth high-FPS transitions for LED matrix displays. "
        draw1.text((5, self.height // 2 - 5), text, fill=(255, 255, 255), font=font)
        
        # Image 2: Different text
        img2 = Image.new("RGB", (self.width * 3, self.height), (0, 0, 0))
        draw2 = ImageDraw.Draw(img2)
        
        text2 = "High-performance scrolling at 120 FPS ensures smooth, readable text transitions on LED matrices. "
        draw2.text((5, self.height // 2 - 5), text2, fill=(0, 255, 255), font=font)
        
        # Image 3: Numbers and symbols
        img3 = Image.new("RGB", (self.width * 3, self.height), (0, 0, 0))
        draw3 = ImageDraw.Draw(img3)
        
        text3 = "1234567890 ABCDEFGHIJKLMNOPQRSTUVWXYZ !@#$%^&*()_+-=[]{}|;':\",./<>? "
        draw3.text((5, self.height // 2 - 5), text3, fill=(255, 0, 255), font=font)
        
        return [img1, img2, img3]

    def test_fps_performance(self, transition_type: str, speed: int, duration: float = 2.0):
        """Test FPS performance for a specific transition."""
        print(f"\nTesting {transition_type} at speed {speed} for {duration}s...")
        
        # Use first two images
        from_image = self.sample_images[0]
        to_image = self.sample_images[1]
        
        # Configure transition
        config = {
            "type": transition_type,
            "speed": speed,
            "enabled": True
        }
        
        # Measure performance
        start_time = time.perf_counter()
        frame_count = 0
        
        # Simulate the transition with performance monitoring
        if transition_type == "redraw":
            # Instant redraw
            self.transition_manager._redraw(to_image)
            frame_count = 1
        elif transition_type in ["scroll_left", "scroll_right"]:
            # Horizontal scroll with FPS measurement
            frame_count = self._simulate_horizontal_scroll_with_fps(from_image, to_image, transition_type, speed, duration)
        elif transition_type in ["scroll_up", "scroll_down"]:
            # Vertical scroll with FPS measurement
            frame_count = self._simulate_vertical_scroll_with_fps(from_image, to_image, transition_type, speed, duration)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        actual_fps = frame_count / total_time if total_time > 0 else 0
        
        # Record performance data
        performance_data = {
            "transition_type": transition_type,
            "speed": speed,
            "duration": duration,
            "frame_count": frame_count,
            "total_time": total_time,
            "actual_fps": actual_fps,
            "target_fps": self.transition_manager.target_fps,
            "fps_achievement": (actual_fps / self.transition_manager.target_fps) * 100
        }
        
        self.performance_data.append(performance_data)
        
        print(f"  Frames: {frame_count}")
        print(f"  Time: {total_time:.3f}s")
        print(f"  Actual FPS: {actual_fps:.1f}")
        print(f"  Target FPS: {self.transition_manager.target_fps}")
        print(f"  Achievement: {performance_data['fps_achievement']:.1f}%")
        
        return performance_data

    def _simulate_horizontal_scroll_with_fps(self, from_image, to_image, direction, speed, duration):
        """Simulate horizontal scroll with FPS measurement."""
        # Create composite image
        composite_width = self.width * 2
        composite_height = self.height
        
        composite = Image.new("RGB", (composite_width, composite_height), (0, 0, 0))
        
        if direction == "scroll_left":
            composite.paste(from_image, (0, 0))
            composite.paste(to_image, (self.width, 0))
        else:  # scroll_right
            composite.paste(to_image, (0, 0))
            composite.paste(from_image, (self.width, 0))
        
        # Convert to numpy for fast operations
        composite_array = np.array(composite)
        
        # Calculate scroll parameters
        scroll_distance = self.width
        total_frames = max(1, scroll_distance // speed)
        
        # Limit by duration
        max_frames_by_time = int(duration * self.transition_manager.target_fps)
        total_frames = min(total_frames, max_frames_by_time)
        
        # Simulate frame loop
        frame_times = []
        for frame in range(total_frames):
            frame_start = time.perf_counter()
            
            # Calculate offset
            if direction == "scroll_left":
                offset = frame * speed
            else:  # scroll_right
                offset = self.width - (frame * speed)
            
            # Fast numpy slice
            frame_array = composite_array[:, offset:offset + self.width]
            frame_image = Image.fromarray(frame_array)
            
            # Simulate display update
            self.display_manager.image = frame_image
            self.display_manager.update_display()
            
            # Frame timing
            frame_time = time.perf_counter() - frame_start
            frame_times.append(frame_time)
            
            # Maintain target FPS
            target_frame_time = self.transition_manager.frame_delay
            if frame_time < target_frame_time:
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0.001:
                    time.sleep(sleep_time)
        
        return total_frames

    def _simulate_vertical_scroll_with_fps(self, from_image, to_image, direction, speed, duration):
        """Simulate vertical scroll with FPS measurement."""
        # Create composite image
        composite_width = self.width
        composite_height = self.height * 2
        
        composite = Image.new("RGB", (composite_width, composite_height), (0, 0, 0))
        
        if direction == "scroll_up":
            composite.paste(from_image, (0, 0))
            composite.paste(to_image, (0, self.height))
        else:  # scroll_down
            composite.paste(to_image, (0, 0))
            composite.paste(from_image, (0, self.height))
        
        # Convert to numpy for fast operations
        composite_array = np.array(composite)
        
        # Calculate scroll parameters
        scroll_distance = self.height
        total_frames = max(1, scroll_distance // speed)
        
        # Limit by duration
        max_frames_by_time = int(duration * self.transition_manager.target_fps)
        total_frames = min(total_frames, max_frames_by_time)
        
        # Simulate frame loop
        frame_times = []
        for frame in range(total_frames):
            frame_start = time.perf_counter()
            
            # Calculate offset
            if direction == "scroll_up":
                offset = frame * speed
            else:  # scroll_down
                offset = self.height - (frame * speed)
            
            # Fast numpy slice
            frame_array = composite_array[offset:offset + self.height, :]
            frame_image = Image.fromarray(frame_array)
            
            # Simulate display update
            self.display_manager.image = frame_image
            self.display_manager.update_display()
            
            # Frame timing
            frame_time = time.perf_counter() - frame_start
            frame_times.append(frame_time)
            
            # Maintain target FPS
            target_frame_time = self.transition_manager.frame_delay
            if frame_time < target_frame_time:
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0.001:
                    time.sleep(sleep_time)
        
        return total_frames

    def run_performance_tests(self):
        """Run comprehensive performance tests."""
        print("High-Performance LEDMatrix Transition Test")
        print("=" * 50)
        print(f"Display: {self.width}x{self.height}")
        print(f"Target FPS: {self.transition_manager.target_fps}")
        print("=" * 50)
        
        # Test different performance modes
        performance_modes = ["high", "balanced", "low"]
        
        for mode in performance_modes:
            print(f"\n--- Testing {mode.upper()} Performance Mode ---")
            self.transition_manager.set_performance_mode(mode)
            
            # Test different transition types
            transitions = ["scroll_left", "scroll_right", "scroll_up", "scroll_down", "redraw"]
            speeds = [2, 4, 6, 8]
            
            for transition in transitions:
                for speed in speeds:
                    if transition == "redraw":
                        # Redraw is instant, only test once
                        self.test_fps_performance(transition, speed, 0.1)
                        break
                    else:
                        self.test_fps_performance(transition, speed, 1.0)
        
        # Show performance summary
        self.show_performance_summary()

    def show_performance_summary(self):
        """Show performance test summary."""
        print("\n" + "=" * 60)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        if not self.performance_data:
            print("No performance data collected.")
            return
        
        # Group by performance mode
        modes = {}
        for data in self.performance_data:
            mode = data.get("target_fps", "unknown")
            if mode not in modes:
                modes[mode] = []
            modes[mode].append(data)
        
        for target_fps, data_list in modes.items():
            print(f"\nTarget FPS: {target_fps}")
            print("-" * 30)
            
            # Calculate averages
            avg_actual_fps = sum(d["actual_fps"] for d in data_list) / len(data_list)
            avg_achievement = sum(d["fps_achievement"] for d in data_list) / len(data_list)
            
            print(f"Average Actual FPS: {avg_actual_fps:.1f}")
            print(f"Average Achievement: {avg_achievement:.1f}%")
            
            # Show best and worst performers
            best = max(data_list, key=lambda x: x["fps_achievement"])
            worst = min(data_list, key=lambda x: x["fps_achievement"])
            
            print(f"Best: {best['transition_type']} speed {best['speed']} - {best['fps_achievement']:.1f}%")
            print(f"Worst: {worst['transition_type']} speed {worst['speed']} - {worst['fps_achievement']:.1f}%")
        
        # Recommendations
        print("\n" + "=" * 60)
        print("RECOMMENDATIONS FOR 100+ FPS")
        print("=" * 60)
        
        high_perf_data = [d for d in self.performance_data if d["target_fps"] >= 120]
        if high_perf_data:
            best_high_perf = max(high_perf_data, key=lambda x: x["fps_achievement"])
            print(f"Best high-FPS configuration:")
            print(f"  Transition: {best_high_perf['transition_type']}")
            print(f"  Speed: {best_high_perf['speed']}")
            print(f"  Achieved: {best_high_perf['actual_fps']:.1f} FPS")
        
        print("\nGeneral recommendations:")
        print("- Use 'high' performance mode for 120 FPS target")
        print("- Speed 2-4 works best for smooth text scrolling")
        print("- Horizontal scrolling typically performs better than vertical")
        print("- Pre-compute images when possible to reduce frame time")
        print("- Use numpy operations for image manipulation")


def main():
    """Main function."""
    print("High-Performance LEDMatrix Transition Test")
    print("==========================================")
    
    # Test different display sizes
    test_sizes = [
        (64, 32),   # Wide display
        (32, 64),   # Tall display
        (64, 64),   # Square display
    ]
    
    for width, height in test_sizes:
        print(f"\n{'='*60}")
        print(f"Testing {width}x{height} display")
        print(f"{'='*60}")
        
        tester = HighPerformanceTransitionTester(width, height)
        tester.run_performance_tests()
        
        print(f"\nCompleted testing for {width}x{height} display")
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("All performance tests completed!")
    print("=" * 60)
    print("Use the high-performance transition system for smooth 100+ FPS scrolling.")


if __name__ == "__main__":
    main()
