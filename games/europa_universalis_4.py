"""Setup for playing Europa Universalis 4 hands-free.

# NOTES

  EU4 is very picky about virtual input. At the time of writing, it won't pick
  up Talon's keypresses, so we override them with the `keyboard` PyPI module.
  This only partially helps - some keys still won't work (and neither will the
  mouse wheel). Because of this, buttons are used instead, with hard-coded
  positions. These positions are hard-coded for 1920 by 1080. I haven't tested
  it, but it seems like the EU4 UI is actually hard-coded, so these values may
  transfer to other resolutions automatically.

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

import time

from talon import Module, Context, actions

from user.utils import apply_function, prepend_to_map, multi_map
from user.misc import zoom_mouse
from user.games.utils import eu4_locations, map_scroll
from user.games.utils.switch_input import switch_to_keyboard_module
from user.games.utils.hard_coded_buttons import Corner


key = actions.key
user = actions.user
insert = actions.insert


class Buttons:
    ZOOM_IN = Corner(Corner.BOTTOM_RIGHT, -14, -43)
    ZOOM_OUT = Corner(Corner.BOTTOM_RIGHT, -14, -11)
    SPEED_UP = Corner(Corner.TOP_RIGHT, -77, 26)
    SPEED_DOWN = Corner(Corner.TOP_RIGHT, -65, 51)
    # Use the bottom right position so the mouse doesn't obscure the
    # notification.
    FIRST_NOTIFICATION = Corner(Corner.TOP_LEFT, 184, 117)


# TODO: Extract to setting?
#
# Distance between notification centers, horizontally.
NOTIFICATION_WIDTH = 45


def _generate_hovers():
    """Generate list of hoverable buttons."""
    TOP_ROW_Y = 21
    POWER_ROW_Y = 62
    return apply_function(
        Corner,
        prepend_to_map(
            Corner.TOP_LEFT,
            multi_map(
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
                    ("administrative power", "admin power"): (508, POWER_ROW_Y),
                    ("diplomatic power", "diplo power"): (567, POWER_ROW_Y),
                    ("military power", "mill power"): (627, POWER_ROW_Y),
                    "age info": (832, 63),
                }
            ),
        ),
    )


hoverable_buttons = _generate_hovers()

clickable_buttons = multi_map(
    {
        "outline": Corner(Corner.TOP_RIGHT, -16, 80),
        "messages": Corner(Corner.BOTTOM_RIGHT, -14, -237),
        "history": Corner(Corner.BOTTOM_RIGHT, -167, -24),
        ("modifiers", "triggered modifiers"): Corner(Corner.BOTTOM_RIGHT, -125, -22),
        # Log does have a shortcut, "<", but EU4 doesn't always recognize it
        # (even from an actual keyboard).
        "show log": Corner(Corner.BOTTOM_RIGHT, -289, -23),
        "great powers": Corner(Corner.TOP_LEFT, 122, 92),
    }
)


#############################################################################


module = Module()

module.list("eu4_hoverables", desc="named buttons that may be hovered over")
module.list("eu4_clickables", desc="named buttons that may be clicked")


@module.capture(rule="{user.eu4_hoverables}")
def eu4_hoverable(m) -> int:
    """Get the location of a hoverable button by its name."""
    return hoverable_buttons.get(m.eu4_hoverables)


@module.capture(rule="{user.eu4_clickables}")
def eu4_clickable(m) -> int:
    """Get the location of a clickable button by its name."""
    return clickable_buttons.get(m.eu4_clickables)


@module.action_class
class ModuleActions:
    def eu4_adjust_zoom(amount: int):
        """Zoom the camera ``amount`` notches, negative or positive."""
        # FIXME: Not 100% reliable, zoom is sometimes off by one (commonly on
        # "zoom five").

        # Virtualized scroll wheel rarely registers, so click hard-coded
        # buttons.
        if amount > 0:
            button = Buttons.ZOOM_IN
        elif amount < 0:
            button = Buttons.ZOOM_OUT
        else:
            raise ValueError("`amount` may not be zero.")
        for i in range(abs(amount)):
            user.corner_click(button)
            time.sleep(0.02)
        user.center_mouse()

    def eu4_zoom_in(notches: int) -> None:
        """Zoom the camera in by ``notches``."""
        actions.self.eu4_adjust_zoom(notches)

    def eu4_zoom_out(notches: int) -> None:
        """Zoom the camera out by ``notches``."""
        actions.self.eu4_adjust_zoom(-notches)

    def eu4_set_zoom(level: int) -> None:
        """Zoom the camera to a specific notch (from fully zoomed)."""
        # Zoom in as far as possible first, then zoom out to the target level.
        user.eu4_adjust_zoom(10)
        user.eu4_adjust_zoom(-level)

    def eu4_hover_notification(number: int) -> None:
        """Move mouse over a specific notification."""
        assert number >= 1
        # TODO: Second row of notifications
        x = Buttons.FIRST_NOTIFICATION.x + NOTIFICATION_WIDTH * (number - 1)
        actions.mouse_move(x, Buttons.FIRST_NOTIFICATION.y)

    def eu4_switch_map(number: int) -> None:
        """Switch to a specific map, by number. Counts from 1."""
        assert number in range(0, 11)
        # Allow the user to refer to the tenth map with "0".
        if number is 0:
            number = 11
        # Map keys by default are mapped to the top row of qwerty.
        map_keys = "qwertyuiop"
        key(map_keys[number - 1])

    def eu4_close_menus() -> None:
        """Close all open menus - return to a neutral screen."""
        # We use an esoteric combination of keys to ensure we close menus
        # without ending up in the escape menu, no matter what was open. This
        # combination works everywhere and doesn't flash, but it will briefly
        # half-pop the production menu.
        #
        # Mostly reliable, but occasionally throws you into the esc menu or
        # takes too long, eating subsequent menu actions.
        key("b")
        key("esc")
        key("esc")
        # Minimum pause so it doesn't interfere with the next command.
        time.sleep(0.6)

    def eu4_set_game_speed(speed: int) -> None:
        """Set the game to a specific speed."""
        assert speed in range(1, 6)
        # There's no keyboard shortcut for adjusting the speed in eu4, so we
        # have to use the buttons, but the buttons have very weird quirks. This
        # is a complex heuristic to get around them.
        SPEED_PAUSE = 0.02
        # We have to go from a known base, make sure we go from the _slowest_
        # speed to avoid time speeding up while we transition.
        for i in range(4):
            # The speed adjuster has a huge consecutive click deadzone
            # (probably to stop users accidentally speeding up too quickly).
            # Double clicking seems to get around it, lets us input way faster.
            user.corner_click(Buttons.SPEED_DOWN)
            user.corner_click(Buttons.SPEED_DOWN)
            time.sleep(SPEED_PAUSE)
        # If we pause between it reduces missed clicks.
        time.sleep(0.2)
        up_notches = speed - 1
        if up_notches >= 2:
            for i in range(up_notches - 1):
                user.corner_click(Buttons.SPEED_UP)
                user.corner_click(Buttons.SPEED_UP)
                time.sleep(SPEED_PAUSE)
            # Single click on the last to prevent occasional overextension.
            time.sleep(0.5)
            user.corner_click(Buttons.SPEED_UP)
        elif up_notches == 1:
            # Once notch is a special case. We have to double click or it won't
            # register.
            user.corner_click(Buttons.SPEED_UP)
            user.corner_click(Buttons.SPEED_UP)
        user.center_mouse()

    def eu4_open_menu(keys: str) -> None:
        """Open a specific menu, closing others."""
        actions.self.eu4_close_menus()
        for keypress in keys.split(" "):
            key(keypress)
            time.sleep(0.4)

    def eu4_jump_to_location(location: str):
        """Jump to an EU4 location by name (using the find dialogue).

        If it doesn't work, enable non-exact matches in-game.

        """
        key("f")
        time.sleep(0.2)
        insert(location)
        time.sleep(0.2)
        key("enter")

    def assign_control_group(number: int) -> None:
        """Assign the current units to a numbered control group."""
        assert 0 <= number <= 9
        key(f"ctrl-{number}")

    def select_control_group(number: int) -> None:
        """Select a control group by number."""
        assert 0 <= number <= 9
        key(f"{number}")

    def go_to_control_group(number: int) -> None:
        """Go to a control group by number."""
        assert 0 <= number <= 9
        actions.self.eu4_close_menus()
        key(f"{number}:2")

    def move_control_group(number: int) -> None:
        """Go to a control group, and queue a move."""
        actions.self.go_to_control_group()
        # Yucky approach
        if zoom_mouse.zoom_mouse_active():
            zoom_mouse.queue_zoom_action(actions.user.right_click)
        else:
            raise RuntimeError("Can only queue a move when the zoom mouse is active.")


context = Context()
context.matches = r"""
app: /eu4\./
"""

context.lists["self.eu4_hoverables"] = hoverable_buttons.keys()
context.lists["self.eu4_clickables"] = clickable_buttons.keys()

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
context.lists["self.eu4_locations"] = eu4_locations.load_locations()


@context.action_class
class ContextActions:
    def corner_click(position: Corner) -> None:
        user.corner_hover(position)
        # Need to add a slight pause or we can get misclicks
        time.sleep(0.05)
        # TODO: Is there a setting for mouse click hold?
        actions.mouse_click(hold=16000)


# Overriding hiss for the map scroll would also override hiss-to-move, so we
# create a dedicated context which avoids it.
map_move_context = Context()
map_move_context.matches = r"""
app: /eu4\./
user.zoom_mouse_zooming: False
"""

_map_scroller = map_scroll.EyeScroller(map_scroll.edge_mouse_scroll)


@map_move_context.action_class
class MapMoveActions:
    def on_hiss(start: bool):
        if start:
            _map_scroller.start()
        else:
            _map_scroller.stop()


# Talon's regular input method doesn't work properly with EU4. `keyboard` from
# PyPI is more reliable.
switch_to_keyboard_module(context)
