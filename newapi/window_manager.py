from typing import List

from talon import Module


module = Module()
module.list("window_align_position", desc="list of window alignment positions")


@module.capture
def window_align_position(m) -> str:
    """Get a specific direction to align the window to."""


@module.action_class
class Actions:
    def align_window(position: List[str]) -> None:
        """Align the window to a specific position.

        Position should be a list of one item, a string.

        """

    def maximize() -> None:
        """Maximize the current window."""

    def all_programs() -> None:
        """Show an outline of all programs"""

    def toggle_fullscreen() -> None:
        """Toggle fullscreen mode for the current window."""
