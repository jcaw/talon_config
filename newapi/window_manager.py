from typing import List

from talon import Module


module = Module()
module.list("position", desc="list of window alignment positions")


@module.capture
def position(m) -> str:
    """Align the window to a specific direction."""


@module.action_class
class Actions:
    def align_window(position: List[str]) -> None:
        """Align the window to a specific position.

        Position should be a list of one item, a string.

        """

    def maximize() -> None:
        """Maximize the current window."""
