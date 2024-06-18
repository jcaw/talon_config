from typing import List

from talon import Module


module = Module()


@module.action_class
class Actions:
    def maximize() -> None:
        """Maximize the current window."""

    def minimize() -> None:
        """Minimize the current window."""

    def all_programs() -> None:
        """Show an outline of all programs"""

    def toggle_fullscreen() -> None:
        """Toggle fullscreen mode for the current window."""

    def lock_screen() -> None:
        """Lock the screen."""

    def snap_window_right() -> None:
        """Snap the current window to the right half of the screen."""

    def snap_window_left() -> None:
        """Snap the current window to the right half of the screen."""
