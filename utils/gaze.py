"""Gaze tracking utilities using the modern Talon tracking API.

Replaces the broken eye_mouse.mouse.eye_hist pattern with talon.tracking_system.
"""

from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple

import talon
from talon import ui
from talon.types import Point2d


@dataclass
class GazePoint:
    """A single gaze sample with left/right eye data."""

    gaze: Point2d  # Combined gaze (normalized 0-1)
    left_gaze: Optional[Point2d] = None
    right_gaze: Optional[Point2d] = None
    ts: float = 0.0


class GazeHistory:
    """Maintains a rolling history of gaze positions.

    Usage:
        gaze = GazeHistory()
        gaze.start()
        # ... later ...
        recent = gaze.history[-3:]  # last 3 samples
        gaze.stop()
    """

    def __init__(self, max_history: int = 30):
        self._max_history = max_history
        self._history: deque[GazePoint] = deque(maxlen=max_history)
        self._active = False

    def start(self):
        """Start collecting gaze samples."""
        if not self._active:
            talon.tracking_system.register("gaze", self._on_gaze)
            self._active = True

    def stop(self):
        """Stop collecting gaze samples."""
        if self._active:
            talon.tracking_system.unregister("gaze", self._on_gaze)
            self._active = False

    def _on_gaze(self, frame):
        """Handle incoming gaze frame."""
        point = GazePoint(
            gaze=frame.gaze,
            left_gaze=frame.left.gaze if hasattr(frame.left, "gaze") else None,
            right_gaze=frame.right.gaze if hasattr(frame.right, "gaze") else None,
            ts=frame.ts,
        )
        self._history.append(point)

    @property
    def history(self) -> list[GazePoint]:
        """Get the gaze history as a list."""
        return list(self._history)

    @property
    def latest(self) -> Optional[GazePoint]:
        """Get the most recent gaze sample."""
        return self._history[-1] if self._history else None

    def clear(self):
        """Clear the history buffer."""
        self._history.clear()


def gaze_to_pixels(gaze: Point2d, screen=None) -> Point2d:
    """Convert normalized gaze coordinates to screen pixels.

    Args:
        gaze: Normalized gaze position (0-1 range)
        screen: Screen to use. Defaults to main screen.

    Returns:
        Pixel coordinates on the screen.
    """
    if screen is None:
        screen = ui.main_screen()
    return Point2d(
        gaze.x * screen.width + screen.x,
        gaze.y * screen.height + screen.y,
    )


def pixels_to_gaze(pixels: Point2d, screen=None) -> Point2d:
    """Convert screen pixel coordinates to normalized gaze coordinates.

    Args:
        pixels: Pixel position on screen
        screen: Screen to use. Defaults to main screen.

    Returns:
        Normalized gaze position (0-1 range).
    """
    if screen is None:
        screen = ui.main_screen()
    return Point2d(
        (pixels.x - screen.x) / screen.width,
        (pixels.y - screen.y) / screen.height,
    )


def mean_gaze(points: list[GazePoint]) -> Optional[Point2d]:
    """Calculate the mean gaze position from a list of samples.

    Args:
        points: List of GazePoint samples

    Returns:
        Mean gaze position, or None if no points.
    """
    if not points:
        return None
    x = sum(p.gaze.x for p in points) / len(points)
    y = sum(p.gaze.y for p in points) / len(points)
    return Point2d(x, y)


# Global gaze history instance for shared use
_global_gaze = None


def get_gaze_history() -> GazeHistory:
    """Get the global gaze history instance.

    Automatically starts tracking on first call.
    """
    global _global_gaze
    if _global_gaze is None:
        _global_gaze = GazeHistory()
        _global_gaze.start()
    return _global_gaze


def get_current_gaze() -> Optional[Point2d]:
    """Get the current gaze position (normalized).

    Returns None if no gaze data is available.
    """
    gaze = get_gaze_history().latest
    return gaze.gaze if gaze else None


def get_current_gaze_pixels(screen=None) -> Optional[Point2d]:
    """Get the current gaze position in screen pixels.

    Returns None if no gaze data is available.
    """
    gaze = get_current_gaze()
    return gaze_to_pixels(gaze, screen) if gaze else None
