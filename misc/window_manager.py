import time

from talon import ctrl
from talon.voice import Context, Key

from user.utils import ON_WINDOWS, ON_LINUX, ON_MAC, invalid_platform
from user.misc.numbers import numeric, pass_number


def minimize(m=None):
    if ON_WINDOWS:
        # This doesn't actually minimize the window, just moves it to the back.
        # The effect should be similar though.
        Key("alt-esc")(None)
    else:
        invalid_platform()


def _with_win_press(keys):
    """Press ``keys`` with the windows key held down."""
    ctrl.key_press("win", down=True)
    try:
        for key in keys:
            Key(f"{key}")(None)
            # Need a relatively long pause to eliminate errors.
            time.sleep(0.1)
    finally:
        ctrl.key_press("win", up=True)


def maximize(m=None):
    if ON_WINDOWS:
        _with_win_press(["up"] * 3)
    else:
        invalid_platform()


# Alignment commands for windows. Structure: `{command_root: key_sequence}`
windows_alignments = {
    "right": ("right", "right"),
    "left": ("left", "left"),
    "top right": ("right", "right", "up"),
    "top left": ("left", "left", "up"),
    "bottom right": ("right", "right", "down"),
    "bottom left": ("left", "left", "down"),
}


def make_windows_align(directions):
    """Make a command that aligns the window with ``directions``."""

    def do_align(m):
        nonlocal directions
        # Maximize first to reset
        maximize()
        _with_win_press(directions)

    return do_align


windows_align_commands = {
    f"align {k}": make_windows_align(v) for k, v in windows_alignments.items()
}


windows_commands = {
    "[focus] (notifications | noteys)": Key("win-b"),
    "[focus] action center": Key("win-a"),
    "[focus] desktop": Key("win-d"),
    "(focus | show) time": Key("win-alt-d"),
    "game bar": Key("win-g"),
    "lock (computer | pee see)": Key("win-l"),
    "screenshot": Key("win-shift-s"),
    "search windows | windows search": Key("win-s"),
    "ease of access [center]": Key("win-u"),
    "[open] clipboard": Key("win-v"),
    numeric("notey"): pass_number(lambda n: [Key("win-shift-y") for i in range(n)]),
    "emoji | emojis": Key("win-."),
    "quick (link | links)": Key("win-x"),
    **windows_align_commands,
}


# Platform-specific commands
if ON_WINDOWS:
    platform_commands = windows_commands
else:
    platform_commands = {}


context = Context("manage_windows")
context.keymap({"maximize": maximize, "minimize": minimize, **platform_commands})
