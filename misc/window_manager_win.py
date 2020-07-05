import time
from typing import List

from talon import Context, Module, actions, ctrl


module = Module()
context = Context()
context.matches = r"""
os: windows
"""


def _with_win_press(key_sequence):
    """Press ``keys`` while holding the Windows key down."""
    # TODO: Convert this to newapi once up/down implemented
    actions.key("win:down")
    try:
        # TODO: Better way to get the inter-key pause?
        print("type: ", key_sequence, type(key_sequence))
        for keychord in key_sequence.split():
            actions.key(f"{keychord}")
            # Need a relatively long pause to eliminate errors.
            time.sleep(0.1)
    finally:
        actions.key("win:up")


@context.action_class("user")
class UserActions:
    def maximize() -> None:
        _with_win_press("up up up")

    def all_programs() -> None:
        actions.key("win-tab")

    def toggle_fullscreen():
        # TODO: alt-enter is another combination - how do I want to do this
        #   one? Maybe implement per-app?
        actions.key("f11")


def _alt_tab(number: int):
    """Alt-tab without releasing alt."""
    with Modifiers(["alt"]):
        for i in range(number):
            actions.key(tab)
            time.sleep(0.1)


@module.action_class
class ModuleActions:
    def snap_window_win(alignment_keys: str) -> None:
        """Move a window to a specific position (on Windows).

        ``alignment_keys`` should be a string-separated list of keys to press
        to align the window.

        """
        actions.user.maximize()
        _with_win_press(alignment_keys)

    # On Windows, to alt-tab through multiple windows, you have to hold alt (or
    # alt-shift) - letting go resets. We need custom actions that eat the
    # repeat to handle this.

    def alt_tab_win(number: int):
        """Windows-specific - holds alt while tabbing."""
        _alt_tab(number)

    def alt_backtab_win(number: int):
        """Windows-specific - holds shift+alt while tabbing."""
        with Modifiers(["shift"]):
            _alt_tab(number)


@context.action_class("app")
class AppActions:
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
