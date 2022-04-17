from talon import Module


module = Module()
module.tag("tiling_window_manager", "Active when a tiling window manager is active")


@module.action_class
class Actions:
    def tiling_switch_workspace(digit: int) -> None:
        """Switch to a numbered workspace on the current monitor."""

    def tiling_move_workspace_and_switch(digit: int) -> None:
        """Move window to workspace and switch to it."""
        actions.self.tiling_move_workspace_no_switch(digit)
        actions.self.tiling_switch_workspace(digit)

    def tiling_move_workspace_no_switch(digit: int) -> None:
        """Move window to workspace without switching to it."""

    def tiling_flip_workspace() -> None:
        """Flip the workspace on the current monitor with the other monitor.

        "Other monitor" is contextual.

        """

    def tiling_focus_direction(arrow_key: str) -> None:
        """Select a window in the specified direction."""

    def tiling_move_direction(arrow_key: str) -> None:
        """Move a window in the specified direction."""

    def tiling_resize_mode() -> None:
        """Toggle resize mode."""

    def tiling_split_vertical() -> None:
        """Split the current window in the vertical direction."""

    def tiling_split_horizontal() -> None:
        """Split the current window in the horizontal direction."""

    def tiling_toggle_floating() -> None:
        """Toggle the current window's floating status."""

    def tiling_switch_window() -> None:
        """Switch between this and the current window.

        This command will only work if there are two windows.

        """
