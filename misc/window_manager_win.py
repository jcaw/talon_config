import ctypes
import time
from typing import List

from talon import Context, Module, actions, ctrl


module = Module()
context = Context()
context.matches = r"""
os: windows
"""


def _with_win_move(key_sequence):
    """Press ``keys`` while holding the Windows key down."""
    keys = list(key_sequence.strip().split())
    for key in keys:
        assert key in {"up", "down", "left", "right"}

    # Start with a predictable state - maximized window.
    actions.self.maximize()
    actions.sleep("100ms")
    actions.key("win:down")
    try:
        for keychord in key_sequence.split():
            actions.key(f"{keychord}")
            # Need a relatively long pause to eliminate errors.
            actions.sleep("100ms")
    finally:
        actions.key("win:up")


def set_show_window_state(state: int):
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    user32.ShowWindow(hwnd, state)


@context.action_class("user")
class UserActions:
    def maximize() -> None:
        SW_MAXIMIZE = 3
        set_show_window_state(SW_MAXIMIZE)

    def minimize() -> None:
        # This approach doesn't actually take focus away from the window. E.g.
        # maximising after will re-maximise the same window, not the window that
        # should be focussed.
        SW_MINIMIZE = 2
        set_show_window_state(SW_MINIMIZE)
        # In order to focus the window below it, we'll alt-tab. This works ok
        # but isn't perfect - e.g. it won't allow us to minimize two windows in
        # a row, it will just cycle them.
        actions.key("alt-tab")

        # This will minimize, but it won't restore the window's state perfectly.
        # actions.self.snap_window_win("down down")

    def snap_window_right():
        actions.self.snap_window_win("right")

    def snap_window_left():
        actions.self.snap_window_win("left")

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
        _with_win_move(alignment_keys)

    # On Windows, to alt-tab through multiple windows, you have to hold alt (or
    # alt-shift) - letting go resets. We need custom actions that eat the
    # repeat.

    def alt_tab_win(number: int):
        """Windows-specific - holds alt while tabbing."""
        _alt_tab(number)

    def alt_backtab_win(number: int):
        """Windows-specific - holds shift+alt while tabbing."""
        with Modifiers(["shift"]):
            _alt_tab(number)

    def snap_screen_win(direction: str):
        """Move current window to another screen, by direction (left or right).

        MS Windows only. Maximizes the window.

        """
        assert direction in ("left", "right")
        # 5 times so the arrangement dialogue doesn't pop
        # TODO: Need 4 times on win 10, I think, 5 on 11.
        _with_win_move(f"{direction} " * 5)


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
