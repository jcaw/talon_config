"""Setup for playing Europa Universalis 4 hands-free.

# NOTES

  Some of this will be transferable to other paradox games. The intention is to
  pull that out into a generic "paradox" module.

  EU4 is very picky about virtual input. At the time of writing, it won't pick
  up Talon's keypresses, so we override them with the `keyboard` PyPi module.
  This only partially helps - some keys still won't work (and neither will the
  mouse wheel). Because of this, buttons are used instead, with hard-coded
  positions. These positions are hard-coded for 1920 by 1080. The EU4 UI
  appears hard-coded itself - it doesn't seem to scale between resolutions.
  Extra code may not needed to accommodate other resolutions.

# INSTRUCTIONS

  You must install the "keyboard" module into Talon's environment. From your
  \"~/talon\" folder, run:

    ./.venv/Scripts/pip.bat install --upgrade keyboard

  Play in 1080p, windowed mode. Use default hotkeys.

  This is designed to be run with an eye tracker mouse, in particular the zoom
  mouse. It won't work without some way to use the mouse.

  Hiss (and look) to move the map.

  Please install the \"Better UI 2\" mod (checksum-independent mod - it won't
  disable achievements). It's recommended (but not required) that you install
  the \"Better UI 2 Verdana Font\" too, for more readable text. This module may
  work with the default UI, but since button positions are hard-coded, the mod
  may introduce incompatibilities.

  Adjust your in-game zoom speed to the MAXIMUM, so the zoom commands work as
  expected. You don't need to adjust any other settings.

"""


# Note this is supposed to be run with an eye tracker mouse, plus voice keys.
#
# Please adjust your zoom speed to the MAXIMUM, or the zoom commands won't work
# properly.


import time

from talon import ctrl
from talon.voice import Key, Str

from user.utils import chain, multi_map, apply_function, prepend_to_map
from user.utils.regex_context import RegexContext
from user.utils.noise import hiss_mapper
from user.misc import mouse
from user.misc.numbers import numeric, pass_number
from .utils.map_scroll import EyeMapScroller
from .utils.switch_input import switch_to_keyboard
from .utils.eu4_locations import load_locations
from .utils.hard_coded_mouse import (
    corner_click,
    make_corner_move,
    make_corner_click,
    CORNERS,
)


# FIXME: Keypresses don't register in EU4 by default (currently using a hacky
#   half-fix).
#
#   Some notes:
#     - Apparently DirectInput might be necessary.
#     - Have tested other modules
#       - `pyautogui` same issue - doesn't work
#       - `keyboard` DOES register
#       - `pynput` same issue - doesn't work
#
#   Current fix is to switch the Key input method to PyP's `keyboard` module
#   (in the EU4 Context only). This isn't a complete fix (some buttons + the
#   mouse wheel still don't work) but it allows us to get basic alphanumeric
#   input in, enabling the use of most hotkeys.


ctx = RegexContext("europa_universalis_4", exe=r"eu4\.exe$")


ZOOM_IN_BUTTON = (CORNERS.BOTTOM_RIGHT, -41, -36)
ZOOM_OUT_BUTTON = (CORNERS.BOTTOM_RIGHT, -15, -36)
SPEED_UP_BUTTON = (CORNERS.TOP_RIGHT, -77, 26)
SPEED_DOWN_BUTTON = (CORNERS.TOP_RIGHT, -65, 51)
# Use the bottom right position so the mouse doesn't obscure the
# notification.
FIRST_NOTIFICATION = (CORNERS.TOP_LEFT, 184, 117)
# Distance between notification centers, horizontally.
NOTIFICATION_WIDTH = 45


_MILITARY = "(mill | military)"
_ECONOMY = "(econ | economy)"
_ADMINISTRATIVE = "(admin | administrative)"
_DIPLOMACY = "(diplo | diplomacy)"
_DIPLOMATIC = "(diplo | diplomatic)"
_TECHNOLOGY = "(tech | technology)"
_PRODUCTION = "(prod | production)"
_DEVELOPMENT = "(divel | development)"
_NOTIFICATION = "(note | notey | notification)"
_POLITICAL = "(poly | political)"
_POWER_POINTS = "(power | points)"

_GREAT_POWERS = "great powers"
_MODIFIERS = "[triggered] modifiers"


def generate_hovers():
    TOP_ROW_Y = 21
    POWER_ROW_Y = 62
    return prepend_to_map(
        CORNERS.TOP_LEFT,
        {
            # Basic Stats
            "treasury": (160, TOP_ROW_Y),
            "manpower": (255, TOP_ROW_Y),
            "sailors": (350, TOP_ROW_Y),
            "stability": (450, TOP_ROW_Y),
            "corruption": (510, TOP_ROW_Y),
            "prestige": (575, TOP_ROW_Y),
            "legitimacy": (642, TOP_ROW_Y),
            "power projection": (711, TOP_ROW_Y),
            # Envoys
            "merchants": (796, TOP_ROW_Y),
            "colonists": (836, TOP_ROW_Y),
            "diplomats": (875, TOP_ROW_Y),
            "missionaries": (919, TOP_ROW_Y),
            # Power Points
            f"{_ADMINISTRATIVE} {_POWER_POINTS}": (508, POWER_ROW_Y),
            f"{_DIPLOMATIC} {_POWER_POINTS}": (567, POWER_ROW_Y),
            f"{_MILITARY} {_POWER_POINTS}": (627, POWER_ROW_Y),
            "age info": (832, 63),
        },
    )


def generate_clickers():
    return {
        "outline": (CORNERS.TOP_RIGHT, -16, 80),
        "messages": (CORNERS.BOTTOM_RIGHT, -14, -237),
        "history": (CORNERS.BOTTOM_RIGHT, -167, -24),
        _MODIFIERS: (CORNERS.BOTTOM_RIGHT, -125, -22),
        # Log does have a shortcut, "<", but EU4 doesn't always recognize it
        # (even from an actual keyboard).
        "show log": (CORNERS.BOTTOM_RIGHT, -289, -23),
        _GREAT_POWERS: (CORNERS.TOP_LEFT, 122, 92),
    }


# EU4 seems to be unreliable when it comes to accepting keyboard input. E.g.
# can't get virtualized arrow keys or the mouse wheel to work, whatever method
# I use. Can get around this by hard-coding actions in the UI. The engine
# appears to have been written in 1950 so it doesn't scale with resolution.
# Hoping this means hard-coded positions are transferable as long as we use
# them relative to their respective corner.
HOVER_COMMANDS = apply_function(make_corner_move, generate_hovers())
CLICK_COMMANDS = apply_function(make_corner_click, generate_clickers())


def hover_notification(number):
    assert number >= 1
    x = FIRST_NOTIFICATION[1] + NOTIFICATION_WIDTH * (number - 1)
    ctrl.mouse_move(x, FIRST_NOTIFICATION[2])


def close_menus(m=None):
    """Close all open menus.

    We have to use a heuristic for this. This method is 99% reliable, but it
    will sometimes throw you into the "esc" menu (or take slightly too long,
    which can eat a subsequent menu open.)

    """
    # We use an esoteric combination of keys to ensure we close menus without
    # ending up in the escape menu, no matter what was open. This combination
    # works everywhere and doesn't flash, but it will briefly half-pop the
    # production menu.
    Key("b")(None)
    Key("esc")(None)
    Key("esc")(None)
    # Minimum pause so it doesn't interfere with the next command.
    time.sleep(0.6)


def make_open_menu(*key_sequence):
    """Open a menu by pressing ``key_sequence``. Closes other menus first."""

    def do_open(m):
        nonlocal key_sequence

        close_menus()
        for key in key_sequence:
            Key(key)(None)
            time.sleep(0.4)

    return do_open


_COUNTRY_MENUS = prepend_to_map(
    "f1",
    {
        # Main menu
        "country [view]": "",
        # Submenus
        "court": "1",
        "government": "2",
        f"{_DIPLOMACY}": "3",
        f"{_ECONOMY}": "4",
        "trade": "5",
        f"{_TECHNOLOGY} [western]": "6",
        "ideas": "7",
        "missions": "8",
        "(decisions | policies | decisions and policies)": "9",
        "(stability | expansion | stability and expansion)": "0",
        "religion": ",",
        f"{_MILITARY}": ".",
        "subjects": "'",
        "estates": "k",
    },
)


_PRODUCTION_MENUS = prepend_to_map(
    "b",
    {
        # Main menu
        f"{_PRODUCTION} [interface]": "",
        # Submenus
        "land [units]": "1",
        "naval [units]": "2",
        "make core": "3",
        "send missionary": "4",
        "[local] autonomy": "5",
        "change culture": "6",
        "buildings": "7",
        f"{_DEVELOPMENT}": "8",
        "estates": "9",
    },
)

_LEDGER_MENUS = prepend_to_map(
    "l",
    {
        # Main menu
        "ledger": "",  # TODO: Will this conflict?
        # Sumenus
        "country ledger": ["f1"],
        # TODO: What's on f2? Colonization?
        f"{_MILITARY} ledger": ["f3"],
        f"({_ECONOMY} | economic) ledger": ["f4"],
        "trade ledger": ["f5"],
        "relations ledger": ["f6"],
    },
)

_MISC_MENUS = {"find": "f"}


MENU_COMMANDS = apply_function(
    make_open_menu,
    {
        #
        **_COUNTRY_MENUS,
        **_PRODUCTION_MENUS,
        **_LEDGER_MENUS,
        **_MISC_MENUS,
    },
)


# TODO: Maybe hard-code specific locations on the map for quick jumping?
#       - We have "jump <place>" now so not as necessary.


def zoom_map(levels):
    # FIXME: Not 100% reliable, zoom is sometimes off by one (commonly on "zoom
    # five").

    # Virtualized scroll wheel rarely registers, so click hard-coded buttons.
    if levels > 0:
        button = ZOOM_IN_BUTTON
    elif levels < 0:
        button = ZOOM_OUT_BUTTON
    else:
        raise ValueError("`levels` may not be zero.")
    for i in range(abs(levels)):
        corner_click(*button, hold=16000)
        time.sleep(0.02)
    mouse.center_mouse()


def zoom_to_level(level):
    """Set the zoom level to a specific notch (from fully zoomed)."""
    # Zoom in as far as possible first, then zoom out to the target level.
    zoom_map(10)
    zoom_map(-level)


def zoom_close(m):
    zoom_to_level(1)


def zoom_mid(m):
    zoom_to_level(3)


def zoom_far(m):
    zoom_to_level(6)


def set_speed(speed):
    assert speed in range(1, 6)
    SPEED_PAUSE = 0.02
    SPEED_HOLD = 16000
    # We have to go from a known base, make sure we go from the _slowest_ speed
    # to avoid time speeding up while we transition.
    for i in range(4):
        # The speed adjuster has a huge deadzone (probably to stop users
        # accidentally speeding up too much). Double clicking lets us input way
        # faster.
        corner_click(*SPEED_DOWN_BUTTON, hold=SPEED_HOLD)
        corner_click(*SPEED_DOWN_BUTTON, hold=SPEED_HOLD)
        time.sleep(SPEED_PAUSE)
    # If we pause between it reduces missed clicks.
    time.sleep(0.2)
    up_notches = speed - 1
    if up_notches >= 2:
        for i in range(up_notches - 1):
            corner_click(*SPEED_UP_BUTTON, hold=SPEED_HOLD)
            corner_click(*SPEED_UP_BUTTON, hold=SPEED_HOLD)
            time.sleep(SPEED_PAUSE)
        # Single click on the last to prevent occasional overextension.
        time.sleep(0.5)
        corner_click(*SPEED_UP_BUTTON, hold=SPEED_HOLD)
    elif up_notches == 1:
        # Once notch is a special case. We have to double click or it won't
        # register.
        corner_click(*SPEED_UP_BUTTON, hold=SPEED_HOLD)
        corner_click(*SPEED_UP_BUTTON, hold=SPEED_HOLD)
    mouse.center_mouse()


def switch_map(number):
    """Switch to a specific map in the quickbar."""
    print(f"Switching to map: {number}")
    assert number in range(0, 11)
    if number is 0:
        # Allow the user to refer to the tenth map with "0".
        number = 11
    # Map keys by default are mapped to the top row of qwerty.
    map_keys = "qwertyuiop"
    Key(map_keys[number - 1])(None)


def make_switch_map(number):
    """Make a function that switches to map ``number``."""

    def do_switch(m):
        nonlocal number
        switch_map(number)

    return do_switch


def assign_control_group(number):
    """Assign a unit to a control group."""
    assert 0 <= number <= 9
    Key(f"ctrl-{number}")(None)


def select_control_group(number):
    assert 0 <= number <= 9
    close_menus()
    Key(f"{number}")(None)


def go_to_control_group(number):
    """Center camera on a control group."""
    assert 0 <= number <= 9
    close_menus()
    Key(f"{number}")(None)
    Key(f"{number}")(None)


# User configured
NAMED_MAPS = [
    # The game defaults to these five.
    "(terrain | train)",  # 1
    f"{_POLITICAL}",  # 2
    "trade",  # 3
    "(religion | religious)",  # 4
    f"{_DIPLOMATIC}",  # 5
    # These are empty by default.
    "(areas | regions)",  # 6
    "empty",  # 7
    "(opinion | relations)",  # 8
    "culture",  # 9
    f"{_DEVELOPMENT}",  # 10
]
MAP_SUFFIX = "(map | mode)"
NAMED_MAP_COMMANDS = {
    " ".join([command, MAP_SUFFIX]): make_switch_map(i + 1)
    for i, command in enumerate(NAMED_MAPS)
}


# Injecting this list into Dragon can take a long time. Here, we're actually
# just queuing the injection - Talon doesn't push changes into Dragon until the
# context is activated. That means while EU4 first loads, Talon will be tied up
# for a while injecting this list.
#
# After that, the list is loaded. Repeated loads will be imperceptible.
#
# Note that under Dragon this huge list DOES NOT have a significant impact on
# recognition speed, even if it takes a while to inject. I don't know the
# performance characteristics with other backends.
ctx.set_list("locations", load_locations())


def jump_to_location(m):
    """Jump to a specific location on the map using \"find\".

    Note that the underlying list here only holds locations that exist on the
    default map. You won't be able to jump to randomly generated provinces in
    the random new world, or colonial countries with new names.

    """
    location = m.locations[0]
    # close_menus()
    Key("f")(None)
    time.sleep(0.2)
    Str(location)(None)
    time.sleep(0.5)
    Key("enter")(None)


ctx.keymap(
    multi_map(
        {
            "close": zoom_close,
            "middle": zoom_mid,
            "far": zoom_far,
            # Zoom to home country
            "go home": Key("backspace"),
            # Use "do" to stop this firing off too easily.
            "and pause": Key("space"),
            # TODO: Maybe allow level?
            numeric("(zoom | level)"): pass_number(zoom_to_level),
            # TODO: Do we want to allow zooming in/out? Maybe specific levels are
            # better?
            numeric("zoom in", optional=True): pass_number(zoom_map),
            numeric("zoom out", optional=True): pass_number(zoom_map, invert=True),
            numeric("speed"): pass_number(set_speed),
            numeric("map"): pass_number(switch_map),
            numeric(f"{_NOTIFICATION}"): pass_number(hover_notification),
            "(close all | kill all | close menus)": close_menus,
            **HOVER_COMMANDS,
            **CLICK_COMMANDS,
            **MENU_COMMANDS,
            **NAMED_MAP_COMMANDS,
            numeric("set group"): pass_number(assign_control_group),
            numeric("group"): pass_number(select_control_group),
            numeric("(go | jump) [to] group"): pass_number(go_to_control_group),
            numeric("move group"): pass_number(
                chain(go_to_control_group, mouse.queue_zoom_action(mouse.right_click))
            ),
            # Responses to menus
            # Confirming
            ("accept", "confirm", "OK", "maintain diplomat"): "c",
            # Declining
            ("decline", "cancel", "go to", "recall diplomat"): "z",
            # Misc shortcuts - most of these are contextual, but we can't evaluate
            # context so they're enabled globally.
            "merge": "g",
            "attach": "a",
            "create [[new] unit]": "b",
            "unit": "u",
            "siege": "j",
            # Intercept "sh" - if we don't do this it sometimes registers on hiss
            # and unpauses.
            # TODO: Do we still need this now we've removed the global "sh"
            # mapping?
            "sh": lambda m: None,
            # TODO: Exract this to generic "steam" context.
            # FIXME: Doesn't work (probably `keyboard` module's fault)
            "overlay": "shift-tab",
            # Dynamic location jumping
            "jump {europa_universalis_4.locations}": jump_to_location,
        }
    )
)

# Move the camera by hissing. We still want zoom hiss to move/cancel, so use a
# lower priority than that.
hiss_mapper.register(ctx, EyeMapScroller(), priority=9)

# Talon's native input doesn't work yet.
#
# TODO: Remove this once Talon's native input works.
switch_to_keyboard(ctx)
