import time
from typing import List

from talon import Context, Module, actions, ctrl


module = Module()
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
class DefaultUserActions:
    def align_window(position: List[str]) -> None:
        position = position[0]
        if position not in _positions:
            raise ValueError("This direction is not implemented on Windows.")
        keys = _positions[position]
        actions.user.newapi.window_manager.maximize()
        _with_win_press(keys)

    def maximize() -> None:
        _with_win_press(["up"] * 3)

    def all_programs() -> None:
        actions.key("win-tab")

    def toggle_fullscreen():
        # TODO: alt-enter is another combination - how do I want to do this
        #   one? Maybe implement per-app?
        actions.key("f11")


@module.action_class
class WindowsUserActions:
    # On Windows, to alt-tab through multiple windows, you have to hold alt (or
    # alt-shift) - letting go resets. We need custom actions that eat the
    # repeat to handle this.

    def window_next_hold(number: int):
        """Windows-specific implementation that holds alt while tabbing."""
        # TODO: Port to newapi once down/up implemented
        ctrl.key_press("alt", down=True)
        for i in range(number):
            actions.key("tab")
            time.sleep(0.1)
        ctrl.key_press("alt", up=True)

    def window_previous_hold(number: int):
        """Windows-specific implementation that holds alt while tabbing."""
        # TODO: Port to newapi once down/up implemented
        ctrl.key_press("alt", down=True)
        ctrl.key_press("shift", down=True)
        for i in range(number):
            actions.key("tab")
            time.sleep(0.1)
        ctrl.key_press("shift", up=True)
        ctrl.key_press("alt", up=True)


@context.action_class("app")
class BuiltInActions:
    def window_hide():
        # This doesn't actually minimize the window, just moves it to the back.
        # The effect should be similar though.
        actions.key("alt-esc")

    def window_next():
        actions.key("alt-tab")

    def window_previous():
        actions.key("alt-shift-tab")

    def window_open():
        actions.key("ctrl-n")

    def window_close():
        actions.key("alt-f4")
