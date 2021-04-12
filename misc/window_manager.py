from typing import List

from talon import Module


module = Module()


@module.action_class
class Actions:
    def maximize() -> None:
        """Maximize the current window."""

    def all_programs() -> None:
        """Show an outline of all programs"""

    def toggle_fullscreen() -> None:
        """Toggle fullscreen mode for the current window."""

    def lock_screen() -> None:
        """Lock the screen."""
