# Adapted from https://github.com/talonvoice/examples

import time
import logging

from talon import ctrl, ui, cron
from talon.voice import Context, ContextGroup
from talon.track.geom import Point2d

from talon_plugins import eye_mouse, eye_zoom_mouse

from . import basic
from .. import utils
from ..utils import ON_WINDOWS
from ..utils import sound, multi_map
from ..utils.mouse_history import backdated_position
from ..utils.eye_mouse import (
    zooming,
    cancel_zoom,
    zoom_mouse_enabled,
    eye_mouse_enabled,
    FrozenEyeMouse,
    toggle_eye_mouse_exclusive,
    toggle_zoom_mouse_exclusive,
    clear_zoom_queue,
    TempEyeMouse,
)
from ..utils.auto_context import AutoContext
from ..utils.noise import hiss_mapper, pop_mapper

if ON_WINDOWS:
    import win32con
    import win32api


LOGGER = logging.getLogger(__name__)


def click(position=None, button=0, repeats=1, **kwargs):
    """Click the mouse. If zooming with the zoom mouse, finish zooming.

    Additional ``kwargs`` will be passed to Talon's `ctrl.mouse_click` method,
    e.g. `down`, `up` and `wait`.

    :param Point2d position: Optional. Provide this to click at a specific position.
      Default is None.
    :param int button: Optional. The button to click. Default is 0 (left click).
    :param int repeats: Optional. Number of times to click (pass 0 to move the
      mouse without clicking). Default is 1.

    """
    # TODO: Audit
    final_zoom_position = cancel_zoom()

    if position:
        ctrl.mouse_move(position.x, position.y)
    elif final_zoom_position:
        ctrl.mouse_move(final_zoom_position.x, final_zoom_position.y)

    if repeats > 0:
        for n in range(repeats):
            ctrl.mouse_click(button=button, **kwargs)


# Normal clicks
def right_click(m=None):
    click(button=1)


def middle_click(m=None):
    click(button=2)


def double_click(m=None):
    click(repeats=2)


def triple_click(m=None):
    click(repeats=3)


def drag(m=None):
    click(down=True)


def drop(m=None):
    click(up=True)


def _scroll_wheel(amount, position=None):
    if not position:
        position = Point2d(*ctrl.mouse_pos())
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, position.x, position.y, amount, 0)


# TODO: Multiplatform mouse wheels
def wheel_up(m=None, repeats=1, position=None):
    _scroll_wheel(repeats, position)


def wheel_down(m=None, repeats=1, position=None):
    _scroll_wheel(-repeats, position)


# Other
def center_mouse(m=None):
    win = ui.active_window()
    rect = win.rect
    center = (rect.x + rect.width / 2, rect.y + rect.height / 2)
    LOGGER.info("Moving mouse to center:", rect, center)
    ctrl.mouse_move(*center)


class DragAndDrop(object):
    """Holds the left mouse button."""

    def __enter__(self):
        drag()

    def __exit__(self, *_):
        drop()


# TODO: Maybe extract, possibly to utils? Keys?
class HeldKeys(object):
    """Context manager that holds down keys."""

    def __init__(self, *keys):
        self._keys = keys

    def __enter__(self):
        for key in self._keys:
            try:
                ctrl.key_press(key, down=True)
            except Exception as e:
                logging.exception()

    def __exit__(self, *_):
        for key in self._keys:
            try:
                ctrl.key_press(key, up=True)
            except Exception as e:
                logging.exception()


def with_keys(keys, action):
    def do_action(m):
        nonlocal keys, action
        with HeldKeys(*keys):
            action(m)

    return do_action


# Backdated clicks
def backdated(action):
    """Perform some action at the mouse position the command was spoken.

    For example:

        "rickle": backdated(right_click)

    When the user says "rickle", Talon will move the mouse to the position it
    was in when the user _started_ saying "rickle", and click there.

    This method may not work with actions longer than 100ms.

    """

    def do_backdated_action(m):
        nonlocal action
        with FrozenEyeMouse():
            ctrl.mouse_move(*backdated_position(m))
            action(m)
            # Sleep for enough time for the action to complete.
            time.sleep(0.1)

    return do_backdated_action


def queue_zoom_action(function):
    """Create a command that queues a specific click type on the next zoom.

    For example, we can queue a right click - next time the user pops out of
    the zoom, a right click will be performed instead of a left click.

    """

    def do_queue(m):
        """Queue the action."""
        nonlocal function

        def do_action(position):
            """Perform the queued action at `position`."""
            nonlocal function, m
            LOGGER.debug(f"Performing queued zoom function `{function}` at {position}")
            ctrl.mouse_move(position.x, position.y)
            function(m)

        LOGGER.debug(f"Queueing zoom function `{function}`")
        eye_zoom_mouse.zoom_mouse.queue_action(do_action)
        # TODO: Better config management
        if utils.eye_mouse.config.BUFFERED_CLICK_SOUNDS:
            sound.play_ding()

    return do_queue


# TODO: Maybe pull this out into something context-based?
def dynamic_action(action):
    """Perform `action` differently based on the mouse mode.

    1. If the zoom mouse is active, the action will be queued for the next zoom
       click.
    2. If the zoom mouse is NOT active, the action will be performed at the
       position the user was looking when `m` was spoken (see method
       `backdated` for more info).

    :param callable action: the action to perform. It will be passed either the
      Talon recognition, or None.

    """

    def do_action(m):
        nonlocal action

        if zoom_mouse_enabled():
            queue_zoom_action(action)(m)
        else:
            backdated(action)(m)

    return do_action


class ZoomMove(object):
    """Closes the zoom at the beginning of a long noise."""

    def __enter__(self):
        """Close the zoom, moving the mouse but not clicking it."""
        # TODO: Audit. Should we move and cancel? Cancel separately?
        clear_zoom_queue()
        final_position = cancel_zoom()
        if final_position:
            ctrl.mouse_move(final_position.x, final_position.y)

    def __exit__(self, *args):
        pass


mouse_group = ContextGroup("mouse_group")


zoom_mouse_context = AutoContext("zoom_mouse", func=zoom_mouse_enabled)
hiss_mapper.register(zoom_mouse_context, ZoomMove())


not_zoom_mouse_context = AutoContext(
    "not_zoom_mouse", func=lambda: not zoom_mouse_enabled(), group=mouse_group
)
pop_mapper.register(not_zoom_mouse_context, click)


zooming_context = AutoContext("zoom_mouse_zooming", func=zooming, group=mouse_group)
# We might want to use different hiss actions in specific contexts, but retain
# hiss to move when zooming.
hiss_mapper.register(zooming_context, ZoomMove(), priority=10)


eye_mouse_context = AutoContext("eye_mouse", func=eye_mouse_enabled, group=mouse_group)
hiss_mapper.register(eye_mouse_context, DragAndDrop(), gap_tolerance=200)


mouse_context = Context("mouse", group=mouse_group)

click_phrases = multi_map(
    {
        "click": click,
        ("rick", "rickle"): right_click,
        ("mickle", "middle"): middle_click,
        "double": double_click,
        "triple": triple_click,
        "drag": drag,
        "drop": drop,
    }
)

mouse_context.set_list("clicks", click_phrases.keys())


def click_from_phrase(m):
    # TODO: Maybe allow multiple clicks here?
    spoken_click = m.clicks[0]
    click_function = click_phrases.get(spoken_click)
    modifiers = basic.get_modifiers(m)

    with basic.Modifiers(modifiers):
        if click_function:
            click_function()


mouse_context.keymap(
    {
        "debug overlay": lambda m: eye_mouse.debug_overlay.toggle(),
        "(track | eye) mouse": toggle_eye_mouse_exclusive,
        "zoom mouse": toggle_zoom_mouse_exclusive,
        "camera overlay": lambda m: eye_mouse.camera_overlay.toggle(),
        "calibrate": lambda m: eye_mouse.calib_start(),
        # Clicks
        "{basic.modifiers}* {mouse.clicks}": dynamic_action(click_from_phrase),
        # TODO: How to handle drag/drop? Just procedural or have both?
        "drag": backdated(drag),
        "(drop | put)": backdated(drop),
        # Hiss misrecognitions:
        # "is": do_nothing,
        # "this is": do_nothing,
        # "this": do_nothing,
        # Click immediately, in the current location.
        "{basic.modifiers}* {mouse.clicks} (that | here | there)": click_from_phrase,
        # TODO: Remove, replace with something more generic.
        # "do paste": [dubclick, Key("ctrl-v")],
        # "do koosh": [dubclick, Key("ctrl-c")],
        "wheel down": wheel_down,
        "wheel up": wheel_up,
        # "wheel down here": [mouse_center, mouse_smooth_scroll(250)],
        # "wheel up here": [mouse_center, mouse_smooth_scroll(-250)],
        "center [mouse]": center_mouse,
        "(unqueue | clear [zoom] [mouse] queue)": clear_zoom_queue,
    }
)


def delayed_drop(m=None):
    """Wait, then drop.

    Some drag actions require that the mouse wait in the drop position for a
    little while before dropping.

    """
    time.sleep(0.3)
    drop()


def queue_drag_drop(m):
    """Queue a drag, plus the subsequent drop, on the zoom mouse."""
    queue_zoom_action(drag)(m)
    # Add drop on a delay so the ding rings twice.
    cron.after("150ms", lambda: queue_zoom_action(delayed_drop)(m))


zoom_mouse_context.keymap(
    {
        # A drag implies a drop. Since we're queuing, we can just queue both.
        "drag": queue_drag_drop,
        "(drop | put)": queue_zoom_action(delayed_drop),
    }
)
