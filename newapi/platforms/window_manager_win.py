import time
from typing import List

from talon import Context, actions, ctrl


context = Context()


# Spoken positions, mapped to alignment key sequences.
_positions = {
    "right": ("right", "right"),
    "left": ("left", "left"),
    "top right": ("right", "right", "up"),
    "top left": ("left", "left", "up"),
    "bottom right": ("right", "right", "down"),
    "bottom left": ("left", "left", "down"),
}


context.lists["user.newapi.window_manager.position"] = _positions.keys()


def _with_win_press(key_names):
    """Press ``keys`` with the windows key held down."""
    # TODO: Convert this to newapi once up/down implemented
    ctrl.key_press("win", down=True)
    try:
        for key_name in key_names:
            actions.key(f"{key_name}")
            # Need a relatively long pause to eliminate errors.
            time.sleep(0.1)
    finally:
        ctrl.key_press("win", up=True)


@context.action_class("user.newapi.window_manager")
class UserActions:
    def align_window(position: List[str]) -> None:
        position = position[0]
        if position not in _positions:
            raise ValueError("This direction is not implemented on Windows.")
        keys = _positions[position]
        _with_win_press(keys)

    def maximize() -> None:
        _with_win_press(["up"] * 3)


@context.action_class("app")
class BuiltInActions:
    def window_hide():
        # This doesn't actually minimize the window, just moves it to the back.
        # The effect should be similar though.
        actions.key("alt-esc")
