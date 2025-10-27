"""
Display Transition System for LEDMatrix

Provides smooth transitions between display content with configurable
direction and speed. Supports horizontal/vertical scrolling and simple redraw.

API Version: 1.0.0
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw
from enum import Enum

logger = logging.getLogger(__name__)


class TransitionType(Enum):
    """Available transition types."""

    SCROLL_LEFT = "scroll_left"
    SCROLL_RIGHT = "scroll_right"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    REDRAW = "redraw"


class DisplayTransitions:
    """
    Handles smooth transitions between display content.

    Provides frame-by-frame animation for scrolling transitions and
    simple redraw for instant content changes.
    """

    def __init__(self, display_manager):
        """
        Initialize the transition system.

        Args:
            display_manager: LEDMatrix display manager instance
        """
        self.display_manager = display_manager
        self.width = display_manager.matrix.width
        self.height = display_manager.matrix.height
        self.logger = logging.getLogger(f"{__name__}.DisplayTransitions")

        # Performance settings
        self.target_fps = 30  # Target frames per second
        self.frame_delay = 1.0 / self.target_fps
        self.max_transition_time = 2.0  # Maximum transition duration in seconds

        self.logger.info(
            f"DisplayTransitions initialized for {self.width}x{self.height} display"
        )

    def transition(
        self,
        from_image: Optional[Image.Image],
        to_image: Image.Image,
        transition_config: Dict[str, Any],
    ) -> None:
        """
        Execute transition from one image to another.

        Args:
            from_image: Source image (None for first display)
            to_image: Target image to transition to
            transition_config: Configuration dict with 'type' and 'speed' keys
        """
        if not transition_config.get("enabled", True):
            self._redraw(to_image)
            return

        transition_type = transition_config.get("type", "redraw")
        speed = transition_config.get("speed", 2)

        # Validate speed
        speed = max(1, min(10, speed))  # Clamp between 1-10

        try:
            if transition_type == TransitionType.REDRAW.value:
                self._redraw(to_image)
            elif transition_type in [
                TransitionType.SCROLL_LEFT.value,
                TransitionType.SCROLL_RIGHT.value,
            ]:
                self._scroll_horizontal(from_image, to_image, transition_type, speed)
            elif transition_type in [
                TransitionType.SCROLL_UP.value,
                TransitionType.SCROLL_DOWN.value,
            ]:
                self._scroll_vertical(from_image, to_image, transition_type, speed)
            else:
                self.logger.warning(
                    f"Unknown transition type: {transition_type}, using redraw"
                )
                self._redraw(to_image)

        except Exception as e:
            self.logger.error(f"Error during transition: {e}")
            self._redraw(to_image)

    def _scroll_horizontal(
        self,
        from_image: Optional[Image.Image],
        to_image: Image.Image,
        direction: str,
        speed: int,
    ) -> None:
        """
        Execute horizontal scrolling transition.

        Args:
            from_image: Source image (None for first display)
            to_image: Target image
            direction: 'scroll_left' or 'scroll_right'
            speed: Pixels to move per frame
        """
        if from_image is None:
            self._redraw(to_image)
            return

        # Calculate scroll distance and frames
        scroll_distance = self.width
        total_frames = max(1, scroll_distance // speed)

        # Limit transition time
        max_frames = int(self.max_transition_time * self.target_fps)
        if total_frames > max_frames:
            total_frames = max_frames
            speed = scroll_distance // total_frames

        self.logger.debug(
            f"Horizontal scroll: {direction}, {total_frames} frames, speed {speed}"
        )

        # Create composite image for smooth scrolling
        composite_width = self.width * 2
        composite_height = self.height

        # Position images based on direction
        if direction == TransitionType.SCROLL_LEFT.value:
            # New content slides in from right
            composite = Image.new("RGB", (composite_width, composite_height), (0, 0, 0))
            composite.paste(from_image, (0, 0))
            composite.paste(to_image, (self.width, 0))
        else:  # scroll_right
            # New content slides in from left
            composite = Image.new("RGB", (composite_width, composite_height), (0, 0, 0))
            composite.paste(to_image, (0, 0))
            composite.paste(from_image, (self.width, 0))

        # Animate the scroll
        for frame in range(total_frames):
            start_time = time.time()

            # Calculate current offset
            if direction == TransitionType.SCROLL_LEFT.value:
                offset = frame * speed
            else:  # scroll_right
                offset = self.width - (frame * speed)

            # Extract visible portion
            visible_area = (offset, 0, offset + self.width, self.height)
            frame_image = composite.crop(visible_area)

            # Update display
            self.display_manager.image = frame_image.copy()
            self.display_manager.update_display()

            # Maintain frame rate
            elapsed = time.time() - start_time
            if elapsed < self.frame_delay:
                time.sleep(self.frame_delay - elapsed)

    def _scroll_vertical(
        self,
        from_image: Optional[Image.Image],
        to_image: Image.Image,
        direction: str,
        speed: int,
    ) -> None:
        """
        Execute vertical scrolling transition.

        Args:
            from_image: Source image (None for first display)
            to_image: Target image
            direction: 'scroll_up' or 'scroll_down'
            speed: Pixels to move per frame
        """
        if from_image is None:
            self._redraw(to_image)
            return

        # Calculate scroll distance and frames
        scroll_distance = self.height
        total_frames = max(1, scroll_distance // speed)

        # Limit transition time
        max_frames = int(self.max_transition_time * self.target_fps)
        if total_frames > max_frames:
            total_frames = max_frames
            speed = scroll_distance // total_frames

        self.logger.debug(
            f"Vertical scroll: {direction}, {total_frames} frames, speed {speed}"
        )

        # Create composite image for smooth scrolling
        composite_width = self.width
        composite_height = self.height * 2

        # Position images based on direction
        if direction == TransitionType.SCROLL_UP.value:
            # New content slides in from bottom
            composite = Image.new("RGB", (composite_width, composite_height), (0, 0, 0))
            composite.paste(from_image, (0, 0))
            composite.paste(to_image, (0, self.height))
        else:  # scroll_down
            # New content slides in from top
            composite = Image.new("RGB", (composite_width, composite_height), (0, 0, 0))
            composite.paste(to_image, (0, 0))
            composite.paste(from_image, (0, self.height))

        # Animate the scroll
        for frame in range(total_frames):
            start_time = time.time()

            # Calculate current offset
            if direction == TransitionType.SCROLL_UP.value:
                offset = frame * speed
            else:  # scroll_down
                offset = self.height - (frame * speed)

            # Extract visible portion
            visible_area = (0, offset, self.width, offset + self.height)
            frame_image = composite.crop(visible_area)

            # Update display
            self.display_manager.image = frame_image.copy()
            self.display_manager.update_display()

            # Maintain frame rate
            elapsed = time.time() - start_time
            if elapsed < self.frame_delay:
                time.sleep(self.frame_delay - elapsed)

    def _redraw(self, image: Image.Image) -> None:
        """
        Simple redraw transition (instant).

        Args:
            image: Image to display
        """
        self.display_manager.image = image.copy()
        self.display_manager.update_display()

    def get_recommended_transitions(self) -> Dict[str, list]:
        """
        Get recommended transition types based on display dimensions.

        Returns:
            Dict with aspect ratio category and recommended transitions
        """
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

    def validate_transition_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate transition configuration.

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

        # Check speed
        speed = config.get("speed", 2)
        if not isinstance(speed, (int, float)) or speed < 1 or speed > 10:
            return False, "Speed must be a number between 1 and 10"

        # Check enabled flag
        enabled = config.get("enabled", True)
        if not isinstance(enabled, bool):
            return False, "Enabled must be a boolean"

        return True, ""
