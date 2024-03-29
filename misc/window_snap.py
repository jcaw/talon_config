"""Tools for voice-driven window management.

Originally from dweil/talon_community - modified for newapi by jcaw.

"""

# TODO: Map keyboard shortcuts to this manager once Talon has key hooks on all
#   platforms

import time
import re
import os
from operator import xor
from typing import Optional
import logging

from talon import ui, Module, Context, actions

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def sorted_screens():
    """Return screens sorted by their topmost, then leftmost, edge.

    Screens will be sorted left-to-right, then top-to-bottom as a tiebreak.

    """

    return sorted(
        sorted(ui.screens(), key=lambda screen: screen.visible_rect.top),
        key=lambda screen: screen.visible_rect.left,
    )


def _set_window_pos(window, x, y, width, height):
    """Helper to set the window position."""
    # TODO: Special case for full screen move - use os-native maximize, rather
    #   than setting the position?
    window.rect = ui.Rect(round(x), round(y), round(width), round(height))
    actions.sleep("10ms")
    # HACK: Windows doesn't necessarily move it properly the first time.
    window.rect = ui.Rect(round(x), round(y), round(width), round(height))


def _bring_forward(window):
    current_window = ui.active_window()
    try:
        window.focus()
        current_window.focus()
    except Exception as e:
        # We don't want to block if this fails.
        print(f"Couldn't bring window to front: {e}")


def _get_app_window(app_name: str) -> ui.Window:
    return actions.self.get_running_app(app_name).active_window


def _window_to_screen(window: ui.Window, dest_screen: ui.Screen):
    src_screen = window.screen
    if src_screen == dest_screen:
        return

    dest = dest_screen.visible_rect
    src = src_screen.visible_rect
    # TODO: Test vertical screen with different aspect ratios
    # Does the orientation between the screens change? (vertical/horizontal)
    if (src.width / src.height > 1) != (dest.width / dest.height > 1):
        # Horizontal -> vertical or vertical -> horizontal
        # Retain proportional window size, but flip x/y of the vertical monitor to account for the monitors rotation.
        if src.width / src.height > 1:
            # horizontal -> vertical
            width = window.rect.width * dest.height / src.width
            height = window.rect.height * dest.width / src.height
        else:
            # vertical -> horizontal
            width = window.rect.width * dest.width / src.height
            height = window.rect.height * dest.height / src.width
        # Deform window if width or height is bigger than the target monitors while keeping the window area the same.
        if width > dest.width:
            over = (width - dest.width) * height
            width = dest.width
            height += over / width
        if height > dest.height:
            over = (height - dest.height) * width
            height = dest.height
            width += over / height
        # Proportional position:
        # Since the window size in respect to the monitor size is not proportional (x/y was flipped),
        # the positioning is more complicated than proportionally scaling the x/y coordinates.
        # It is computed by keeping the free space to the left of the window proportional to the right
        # and respectively for the top/bottom free space.
        # The if conditions account for division by 0. TODO: Refactor positioning without division by 0
        if src.height == window.rect.height:
            x = dest.left + (dest.width - width) / 2
        else:
            x = dest.left + (window.rect.top - src.top) * (dest.width - width) / (
                src.height - window.rect.height
            )
        if src.width == window.rect.width:
            y = dest.top + (dest.height - height) / 2
        else:
            y = dest.top + (window.rect.left - src.left) * (dest.height - height) / (
                src.width - window.rect.width
            )
    else:
        # Horizontal -> horizontal or vertical -> vertical
        # Retain proportional size and position
        proportional_width = dest.width / src.width
        proportional_height = dest.height / src.height
        x = dest.left + (window.rect.left - src.left) * proportional_width
        y = dest.top + (window.rect.top - src.top) * proportional_height
        width = window.rect.width * proportional_width
        height = window.rect.height * proportional_height
    _set_window_pos(window, x=x, y=y, width=width, height=height)


def _window_to_numbered_screen(
    window: ui.Window, offset: Optional[int] = None, screen_number: Optional[int] = None
):
    """Move a window to a different screen.

    Provide one of `offset` or `screen_number` to specify a target screen.

    Provide `window` to move a specific window, otherwise the current window is
    moved.

    """
    assert (
        screen_number or offset and not (screen_number and offset)
    ), "Provide exactly one of `screen_number` or `offset`."

    screens = sorted_screens()
    if offset:
        # TODO: Does this introduce a race condition? Can window.screen change
        #   under this method? Not a big deal if so but just in case.
        screen_number = (screens.index(window.screen) + offset) % len(screens)
    else:
        # Human to array index
        screen_number -= 1

    dest_screen = screens[screen_number]
    _window_to_screen(window, dest_screen)


def _snap_window_helper(window, pos):
    screen = window.screen.visible_rect

    _set_window_pos(
        window,
        x=screen.x + (screen.width * pos.left),
        y=screen.y + (screen.height * pos.top),
        width=screen.width * (pos.right - pos.left),
        height=screen.height * (pos.bottom - pos.top),
    )


class RelativeScreenPos(object):
    """Represents a window position as a fraction of the screen."""

    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.bottom = bottom
        self.right = right


mod = Module()
mod.list(
    "window_snap_positions",
    "Predefined window positions for the current window. See `RelativeScreenPos`.",
)


_snap_positions = {
    # Halves
    # .---.---.     .-------.
    # |   |   |  &  |-------|
    # '---'---'     '-------'
    "left": RelativeScreenPos(0, 0, 0.5, 1),
    "right": RelativeScreenPos(0.5, 0, 1, 1),
    "top": RelativeScreenPos(0, 0, 1, 0.5),
    "bottom": RelativeScreenPos(0, 0.5, 1, 1),
    # Thirds
    # .--.--.--.
    # |  |  |  |
    # '--'--'--'
    "middle third": RelativeScreenPos(1 / 3, 0, 2 / 3, 1),
    "left third": RelativeScreenPos(0, 0, 1 / 3, 1),
    "right third": RelativeScreenPos(2 / 3, 0, 1, 1),
    "left two thirds": RelativeScreenPos(0, 0, 2 / 3, 1),
    "right two thirds": RelativeScreenPos(1 / 3, 0, 1, 1,),
    # Quarters
    # .---.---.
    # |---|---|
    # '---'---'
    "top left": RelativeScreenPos(0, 0, 0.5, 0.5),
    "top right": RelativeScreenPos(0.5, 0, 1, 0.5),
    "bottom left": RelativeScreenPos(0, 0.5, 0.5, 1),
    "bottom right": RelativeScreenPos(0.5, 0.5, 1, 1),
    # Sixths
    # .--.--.--.
    # |--|--|--|
    # '--'--'--'
    "top right third": RelativeScreenPos(2 / 3, 0, 1, 0.5),
    "top left two thirds": RelativeScreenPos(0, 0, 2 / 3, 0.5),
    "top right two thirds": RelativeScreenPos(1 / 3, 0, 1, 0.5),
    "top middle third": RelativeScreenPos(1 / 3, 0, 2 / 3, 0.5),
    "bottom left third": RelativeScreenPos(0, 0.5, 1 / 3, 1),
    "bottom right third": RelativeScreenPos(2 / 3, 0.5, 1, 1),
    "bottom left two thirds": RelativeScreenPos(0, 0.5, 2 / 3, 1),
    "bottom right two thirds": RelativeScreenPos(1 / 3, 0.5, 1, 1),
    "bottom middle third": RelativeScreenPos(1 / 3, 0.5, 2 / 3, 1),
    # Special
    "middle": RelativeScreenPos(1 / 8, 1 / 6, 7 / 8, 5 / 6),
    "full": RelativeScreenPos(0, 0, 1, 1),
    "fullscreen": RelativeScreenPos(0, 0, 1, 1),
}


@mod.capture(rule="{user.window_snap_positions}")
def window_snap_position(m) -> RelativeScreenPos:
    return _snap_positions[m.window_snap_positions]


ctx = Context()
ctx.lists["user.window_snap_positions"] = _snap_positions.keys()


@mod.action_class
class Actions:
    def snap_window(pos: RelativeScreenPos) -> None:
        """Move the active window to a specific position on-screen.

        See `RelativeScreenPos` for the structure of this position.

        """
        _snap_window_helper(ui.active_window(), pos)

    def move_window_next_screen() -> None:
        """Move the active window to a specific screen."""
        _window_to_numbered_screen(ui.active_window(), offset=1)

    def move_window_previous_screen() -> None:
        """Move the active window to the previous screen."""
        _window_to_numbered_screen(ui.active_window(), offset=-1)

    def move_window_to_screen(screen_number: int) -> None:
        """Move the active window leftward by one."""
        _window_to_numbered_screen(ui.active_window(), screen_number=screen_number)

    def snap_app(app_name: str, pos: RelativeScreenPos):
        """Snap a specific application to another screen."""
        window = _get_app_window(app_name)
        _bring_forward(window)
        _snap_window_helper(window, pos)

    def move_app_to_screen(app_name: str, screen_number: int):
        """Move a specific application to another screen."""
        window = _get_app_window(app_name)
        # print(window)
        _bring_forward(window)
        _window_to_numbered_screen(
            window, screen_number=screen_number,
        )

    def swap_screens(source: int, target: Optional[int] = None):
        """Swap screen `source` with `target` (default main screen).

        This physically moves all windows from source to target.

        """
        # Invalid app names will not be moved to a different screen. Use this
        # for e.g. the Windows Taskbar
        if os.name == "nt":  # On Windows
            # excluded_titles = [
            #     "^Action Centre",
            #     "^System Clock",
            #     "^Program Manager$",
            #     "^Running applications$",
            #     "^Start$",
            #     "^Microsoft Text Input Application$",
            #     "^Settings$",
            #     "^Search$",
            #     "^Windows Shell Experience Host$",
            #     "^Task view$",
            #     "^New notification$",
            #     "^&Open$",
            #     "^Cancel$",
            #     "^action centre$",
            #     "^Task View$",
            #     "^Type here to search$",
            #     "^Windows Default Lock Screen$",
            # ]
            invalid_app_names = {
                # Lots of Window's native OS chrome (e.g. the taskbar, start
                # menu) needs to be ignored - moving it results in weird GUI
                # corruptions.
                "Windows Explorer",
                "Console Window Host",
                "COM Surrogate",
                "Runtime Broker",
                "Windows Shell Experience Host",
                "TextInputHost.exe",
                "StartMenuExperienceHost.exe",
                "Settings",
                "Application Frame Host",
                "Search application",
                "LockApp.exe",
                # Slack get moved even when it's minimized to the taskbar, which
                # makes the window unresponsive
                "Slack",
                # Talon right-click menus can show up otherwise
                "Talon",
            }
        else:
            # excluded_titles = []
            invalid_app_names = {}
        # excluded_titles = list(map(re.compile, excluded_titles))

        def _window_on_screen(window: ui.Window, screen: ui.Screen) -> bool:
            """Is `window` is currently on `screen`?

            This is a heuristic method to determine whether the window is
            primarily on the given screen, and unminimized.

            """
            return all(
                [
                    # `ui.Window.hidden` is pretty unreliable on Windows as of
                    # 2020/10/05.
                    not window.hidden,
                    window.rect,
                    window.rect.width > 0,
                    window.rect.height > 0,
                    window.screen == screen,
                    screen.rect.contains(*window.rect.center),
                ]
            )

        screens = sorted_screens()
        source_screen = screens[source - 1]
        target_screen = screens[target - 1] if target else ui.main_screen()
        # Overtly freeze the window list so we don't affect it by moving them.
        LOGGER.debug("---")
        print(source_screen)
        for window in list(ui.windows()):
            if (
                # HACK: Super hacky way of not affecting things like the taskbar
                #   icon popup is just to ignore windows with no title.
                window.title
                # Some title regexps are excluded
                # and not any(
                # map(lambda t: t.search(window.title.strip()), excluded_titles)
                # )
                and window.app.name not in invalid_app_names
            ):
                if _window_on_screen(window, source_screen):
                    LOGGER.debug(f"Source window: {window.app} {window.title}")
                    _window_to_screen(window, target_screen)
                elif _window_on_screen(window, target_screen):
                    LOGGER.debug(f"Target window: {window.app} {window.title}")
                    _window_to_screen(window, source_screen)
