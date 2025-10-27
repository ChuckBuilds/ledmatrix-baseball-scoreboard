#!/usr/bin/env python3
"""
High-Performance LEDMatrix Transition System

Optimized for 100+ FPS smooth scrolling text with minimal CPU overhead.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class TransitionType(Enum):
    """Available transition types."""

    SCROLL_LEFT = "scroll_left"
    SCROLL_RIGHT = "scroll_right"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    REDRAW = "redraw"


class HighPerformanceDisplayTransitions:
    """
    High-performance transition system optimized for 100+ FPS.

    Key optimizations:
    - Pre-computed frame buffers
    - Minimal memory allocations
    - Optimized image operations
    - Adaptive frame timing
    - Hardware-accelerated operations where possible
    """

    def __init__(self, display_manager):
        """
        Initialize the high-performance transition system.

        Args:
            display_manager: LEDMatrix display manager instance
        """
        self.display_manager = display_manager
        self.width = display_manager.matrix.width
        self.height = display_manager.matrix.height
        self.logger = logging.getLogger(f"{__name__}.HighPerformanceDisplayTransitions")

        # High-performance settings
        self.target_fps = 120  # Target 120 FPS for ultra-smooth scrolling
        self.frame_delay = 1.0 / self.target_fps
        self.max_transition_time = 1.0  # Shorter transitions for better UX

        # Performance monitoring
        self.frame_times = []
        self.performance_mode = "high"  # high, balanced, low

        # Pre-allocated buffers for performance
        self._frame_buffer = None
        self._composite_buffer = None

        self.logger.info(
            f"HighPerformanceDisplayTransitions initialized for {self.width}x{self.height} display"
        )
        self.logger.info(
            f"Target FPS: {self.target_fps}, Frame delay: {self.frame_delay:.4f}s"
        )

    def set_performance_mode(self, mode: str):
        """
        Set performance mode to optimize for different scenarios.

        Args:
            mode: "high" (120 FPS), "balanced" (60 FPS), "low" (30 FPS)
        """
        if mode == "high":
            self.target_fps = 120
            self.max_transition_time = 0.8
        elif mode == "balanced":
            self.target_fps = 60
            self.max_transition_time = 1.2
        elif mode == "low":
            self.target_fps = 30
            self.max_transition_time = 2.0
        else:
            raise ValueError(f"Invalid performance mode: {mode}")

        self.frame_delay = 1.0 / self.target_fps
        self.performance_mode = mode

        self.logger.info(f"Performance mode set to {mode}: {self.target_fps} FPS")

    def transition(
        self,
        from_image: Optional[Image.Image],
        to_image: Image.Image,
        transition_config: Dict[str, Any],
    ) -> None:
        """
        Execute high-performance transition from one image to another.

        Args:
            from_image: Source image (None for first display)
            to_image: Target image to transition to
            transition_config: Configuration dict with 'type', 'speed', and 'duration' keys
        """
        if not transition_config.get("enabled", True):
            self._redraw(to_image)
            return

        transition_type = transition_config.get("type", "redraw")
        speed = transition_config.get("speed", 2)
        duration = transition_config.get(
            "duration", None
        )  # Duration in seconds (optional)

        # Validate and optimize speed for high FPS
        speed = max(1, min(20, speed))  # Allow higher speeds for high FPS

        try:
            if transition_type == TransitionType.REDRAW.value:
                self._redraw(to_image)
            elif transition_type in [
                TransitionType.SCROLL_LEFT.value,
                TransitionType.SCROLL_RIGHT.value,
            ]:
                self._scroll_horizontal_optimized(
                    from_image, to_image, transition_type, speed, duration
                )
            elif transition_type in [
                TransitionType.SCROLL_UP.value,
                TransitionType.SCROLL_DOWN.value,
            ]:
                self._scroll_vertical_optimized(
                    from_image, to_image, transition_type, speed, duration
                )
            else:
                self.logger.warning(
                    f"Unknown transition type: {transition_type}, using redraw"
                )
                self._redraw(to_image)

        except Exception as e:
            self.logger.error(f"Error during transition: {e}")
            self._redraw(to_image)

    def _scroll_horizontal_optimized(
        self,
        from_image: Optional[Image.Image],
        to_image: Image.Image,
        direction: str,
        speed: int,
        duration: Optional[float] = None,
    ) -> None:
        """
        High-performance horizontal scrolling transition with decoupled frame rate and scroll speed.

        Optimizations:
        - Pre-compute composite image
        - Use numpy for fast array operations
        - Minimize PIL operations
        - Adaptive frame timing
        - Frame rate independent of scroll speed
        """
        if from_image is None:
            self._redraw(to_image)
            return

        # Pre-compute composite image for maximum performance
        composite_width = self.width * 2
        composite_height = self.height

        # Use pre-allocated buffer if available
        if self._composite_buffer is None or self._composite_buffer.size != (
            composite_width,
            composite_height,
        ):
            self._composite_buffer = Image.new(
                "RGB", (composite_width, composite_height), (0, 0, 0)
            )

        composite = self._composite_buffer.copy()

        # Position images based on direction
        if direction == TransitionType.SCROLL_LEFT.value:
            composite.paste(from_image, (0, 0))
            composite.paste(to_image, (self.width, 0))
        else:  # scroll_right
            composite.paste(to_image, (0, 0))
            composite.paste(from_image, (self.width, 0))

        # Convert to numpy for fast operations
        composite_array = np.array(composite)

        # Calculate scroll parameters - DECOUPLED from frame rate
        scroll_distance = self.width

        # Determine total frames based on duration OR scroll distance
        if duration is not None:
            # Duration-based: Calculate frames based on target FPS and duration
            total_frames = int(duration * self.target_fps)
            # Calculate actual scroll speed based on duration
            actual_speed = scroll_distance / total_frames
        else:
            # Speed-based: Calculate frames based on scroll distance and speed
            total_frames = max(1, scroll_distance // speed)
            actual_speed = speed

        # Ensure minimum frames for smooth animation
        min_frames = max(1, int(self.target_fps * 0.1))  # At least 0.1 seconds
        total_frames = max(total_frames, min_frames)

        # Recalculate actual speed if we adjusted frames
        if duration is None:
            actual_speed = scroll_distance / total_frames

        self.logger.debug(
            f"Optimized horizontal scroll: {direction}, {total_frames} frames, "
            f"actual_speed {actual_speed:.2f}, target_fps {self.target_fps}"
        )

        # High-performance frame loop with consistent frame rate
        frame_times = []
        for frame in range(total_frames):
            frame_start = time.perf_counter()

            # Calculate current offset based on frame progress
            progress = frame / (total_frames - 1) if total_frames > 1 else 0
            offset = int(progress * scroll_distance)

            # Ensure offset doesn't exceed bounds
            offset = min(offset, scroll_distance - 1)

            # Apply direction
            if direction == TransitionType.SCROLL_RIGHT.value:
                offset = scroll_distance - offset

            # Fast numpy slice operation
            frame_array = composite_array[:, offset : offset + self.width]

            # Convert back to PIL (minimal overhead)
            frame_image = Image.fromarray(frame_array)

            # Update display
            self.display_manager.image = frame_image
            self.display_manager.update_display()

            # Maintain consistent frame rate regardless of scroll speed
            frame_time = time.perf_counter() - frame_start
            frame_times.append(frame_time)

            # Maintain target FPS with adaptive timing
            target_frame_time = self.frame_delay
            if frame_time < target_frame_time:
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0.001:  # Only sleep if significant time remaining
                    time.sleep(sleep_time)

            # Performance monitoring
            if len(frame_times) > 10:
                avg_frame_time = sum(frame_times[-10:]) / 10
                if avg_frame_time > self.frame_delay * 1.1:  # 10% tolerance
                    self.logger.warning(
                        f"Frame time exceeded target: {avg_frame_time:.4f}s > {self.frame_delay:.4f}s"
                    )

    def _scroll_vertical_optimized(
        self,
        from_image: Optional[Image.Image],
        to_image: Image.Image,
        direction: str,
        speed: int,
        duration: Optional[float] = None,
    ) -> None:
        """
        High-performance vertical scrolling transition with decoupled frame rate and scroll speed.

        Optimizations:
        - Pre-compute composite image
        - Use numpy for fast array operations
        - Minimize PIL operations
        - Adaptive frame timing
        - Frame rate independent of scroll speed
        """
        if from_image is None:
            self._redraw(to_image)
            return

        # Pre-compute composite image for maximum performance
        composite_width = self.width
        composite_height = self.height * 2

        # Use pre-allocated buffer if available
        if self._composite_buffer is None or self._composite_buffer.size != (
            composite_width,
            composite_height,
        ):
            self._composite_buffer = Image.new(
                "RGB", (composite_width, composite_height), (0, 0, 0)
            )

        composite = self._composite_buffer.copy()

        # Position images based on direction
        if direction == TransitionType.SCROLL_UP.value:
            composite.paste(from_image, (0, 0))
            composite.paste(to_image, (0, self.height))
        else:  # scroll_down
            composite.paste(to_image, (0, 0))
            composite.paste(from_image, (0, self.height))

        # Convert to numpy for fast operations
        composite_array = np.array(composite)

        # Calculate scroll parameters - DECOUPLED from frame rate
        scroll_distance = self.height

        # Determine total frames based on duration OR scroll distance
        if duration is not None:
            # Duration-based: Calculate frames based on target FPS and duration
            total_frames = int(duration * self.target_fps)
            # Calculate actual scroll speed based on duration
            actual_speed = scroll_distance / total_frames
        else:
            # Speed-based: Calculate frames based on scroll distance and speed
            total_frames = max(1, scroll_distance // speed)
            actual_speed = speed

        # Ensure minimum frames for smooth animation
        min_frames = max(1, int(self.target_fps * 0.1))  # At least 0.1 seconds
        total_frames = max(total_frames, min_frames)

        # Recalculate actual speed if we adjusted frames
        if duration is None:
            actual_speed = scroll_distance / total_frames

        self.logger.debug(
            f"Optimized vertical scroll: {direction}, {total_frames} frames, "
            f"actual_speed {actual_speed:.2f}, target_fps {self.target_fps}"
        )

        # High-performance frame loop with consistent frame rate
        frame_times = []
        for frame in range(total_frames):
            frame_start = time.perf_counter()

            # Calculate current offset based on frame progress
            progress = frame / (total_frames - 1) if total_frames > 1 else 0
            offset = int(progress * scroll_distance)

            # Ensure offset doesn't exceed bounds
            offset = min(offset, scroll_distance - 1)

            # Apply direction
            if direction == TransitionType.SCROLL_DOWN.value:
                offset = scroll_distance - offset

            # Fast numpy slice operation
            frame_array = composite_array[offset : offset + self.height, :]

            # Convert back to PIL (minimal overhead)
            frame_image = Image.fromarray(frame_array)

            # Update display
            self.display_manager.image = frame_image
            self.display_manager.update_display()

            # Maintain consistent frame rate regardless of scroll speed
            frame_time = time.perf_counter() - frame_start
            frame_times.append(frame_time)

            # Maintain target FPS with adaptive timing
            target_frame_time = self.frame_delay
            if frame_time < target_frame_time:
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0.001:  # Only sleep if significant time remaining
                    time.sleep(sleep_time)

            # Performance monitoring
            if len(frame_times) > 10:
                avg_frame_time = sum(frame_times[-10:]) / 10
                if avg_frame_time > self.frame_delay * 1.1:  # 10% tolerance
                    self.logger.warning(
                        f"Frame time exceeded target: {avg_frame_time:.4f}s > {self.frame_delay:.4f}s"
                    )

    def _redraw(self, image: Image.Image) -> None:
        """
        Simple redraw transition (instant).

        Optimized for maximum performance.
        """
        self.display_manager.image = image.copy()
        self.display_manager.update_display()

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for monitoring.

        Returns:
            Dict with performance metrics
        """
        if not self.frame_times:
            return {"status": "no_data"}

        recent_times = self.frame_times[-30:]  # Last 30 frames
        avg_frame_time = sum(recent_times) / len(recent_times)
        actual_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

        return {
            "target_fps": self.target_fps,
            "actual_fps": actual_fps,
            "avg_frame_time": avg_frame_time,
            "performance_mode": self.performance_mode,
            "frames_analyzed": len(recent_times),
            "fps_achievement": (actual_fps / self.target_fps) * 100,
        }

    def create_transition_config(
        self,
        transition_type: str,
        speed: Optional[int] = None,
        duration: Optional[float] = None,
        enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a transition configuration with decoupled frame rate and scroll speed.

        Args:
            transition_type: Type of transition (scroll_left, scroll_right, etc.)
            speed: Scroll speed in pixels per frame (optional)
            duration: Duration in seconds (optional)
            enabled: Whether transition is enabled

        Returns:
            Transition configuration dict

        Note:
            Either speed OR duration should be specified, not both.
            If both are specified, duration takes precedence.
        """
        if speed is None and duration is None:
            speed = 2  # Default speed

        config = {"type": transition_type, "enabled": enabled}

        if duration is not None:
            config["duration"] = duration
            self.logger.debug(
                f"Created duration-based config: {duration}s at {self.target_fps} FPS"
            )
        else:
            config["speed"] = speed
            self.logger.debug(f"Created speed-based config: {speed} pixels/frame")

        return config

    def get_optimal_scroll_config(
        self, transition_type: str, content_length: int
    ) -> Dict[str, Any]:
        """
        Get optimal scroll configuration for smooth text reading.

        Args:
            transition_type: Type of transition
            content_length: Length of content to scroll (pixels)

        Returns:
            Optimal transition configuration
        """
        # Calculate optimal duration for readability
        # Based on research: 150-300 words per minute for comfortable reading
        # For LED matrices: ~2-4 seconds for full scroll

        if transition_type in ["scroll_left", "scroll_right"]:
            optimal_duration = max(
                1.0, min(3.0, content_length / 50)
            )  # ~50 pixels per second
        else:  # vertical scrolling
            optimal_duration = max(
                1.0, min(3.0, content_length / 30)
            )  # ~30 pixels per second

        return self.create_transition_config(
            transition_type=transition_type, duration=optimal_duration, enabled=True
        )

    def optimize_for_text_scrolling(self):
        """
        Optimize settings specifically for smooth text scrolling.

        This method sets optimal parameters for reading text while scrolling.
        """
        self.set_performance_mode("high")  # 120 FPS

        # Text-specific optimizations
        self.max_transition_time = 0.6  # Shorter transitions for text
        self.frame_delay = 1.0 / 120  # 8.33ms per frame

        self.logger.info("Optimized for smooth text scrolling at 120 FPS")

    def validate_transition_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate transition configuration for high-performance mode.

        Args:
            config: Transition configuration dict

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(config, dict):
            return False, "Transition config must be a dictionary"

        # Check transition type
        transition_type = config.get("type", "redraw")
        valid_types = [t.value for t in TransitionType]
        if transition_type not in valid_types:
            return (
                False,
                f"Invalid transition type '{transition_type}'. Valid types: {valid_types}",
            )

        # Check speed (allow higher speeds for high FPS)
        speed = config.get("speed", 2)
        if not isinstance(speed, (int, float)) or speed < 1 or speed > 20:
            return (
                False,
                "Speed must be a number between 1 and 20 for high-performance mode",
            )

        # Check enabled flag
        enabled = config.get("enabled", True)
        if not isinstance(enabled, bool):
            return False, "Enabled must be a boolean"

        return True, ""


def create_high_performance_transition_manager(display_manager):
    """
    Factory function to create a high-performance transition manager.

    Args:
        display_manager: LEDMatrix display manager instance

    Returns:
        HighPerformanceDisplayTransitions instance
    """
    manager = HighPerformanceDisplayTransitions(display_manager)

    # Auto-optimize for text scrolling
    manager.optimize_for_text_scrolling()

    return manager
