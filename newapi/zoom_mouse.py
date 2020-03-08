from typing import Callable, List
import logging
import time

from talon import Module, actions, settings, ctrl, cron
from talon_plugins import eye_zoom_mouse

from user.misc import basic
from user.utils import sound
from user.newapi.mouse import Click
from user.newapi.utils.ticker_context import make_ticker_context


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def zoom_mouse_active():
    """Is the zoom mouse an active mouse mode?"""
    try:
        return eye_zoom_mouse.zoom_mouse.enabled
    except AttributeError:
        return False


def is_zooming():
    """Is the zoom mouse currently zooming?"""
    return eye_zoom_mouse.zoom_mouse.state == eye_zoom_mouse.STATE_OVERLAY


module = Module()
module.setting(
    "click_sounds",
    type=bool,
    default=True,
    desc="play sounds when zoom clicks are buffered (or cancelled)",
)


@module.action_class
class Actions:
    def queue_zoom_action(function: Callable):
        """Create a command that queues a specific click type on the next zoom.

        For example, we can queue a right click - next time the user pops out of
        the zoom, a right click will be performed instead of a left click.

        """

        def do_action(position):
            """Perform the queued action at `position`."""
            nonlocal function
            LOGGER.debug(f"Performing queued zoom function `{function}` at {position}")
            actions.mouse_move(position.x, position.y)
            function()

        LOGGER.debug(f"Queuing zoom function `{function}`")
        eye_zoom_mouse.zoom_mouse.queue_action(do_action)
        if settings["self.click_sounds"]:
            sound.play_ding()

    def clear_zoom_queue():
        """Clear all queued zoom mouse actions."""
        # Possible race here. Not important or likely to happen; tolerate it.
        if not eye_zoom_mouse.zoom_mouse.queued_actions.empty():
            eye_zoom_mouse.zoom_mouse.cancel_actions()
            if settings["self.click_sounds"]:
                sound.play_cancel()


context = make_ticker_context(None, zoom_mouse_active)


@context.action_class("user")
class MouseActions:
    def drop(modifiers: List[str] = []):
        # Some drag actions require that the mouse wait in the drop position
        # for a little while before dropping. Movement is instant with the zoom
        # mouse, so insert an artificial wait.
        time.sleep(0.3)
        # TODO: Port to newapi actions once I know the interface
        ctrl.mouse_click(button=0, up=True)
        basic.Modifiers(modifiers).__exit__(None, None, None)

    def default_click(click_info: Click):
        modifiers = click_info.modifiers
        actions.self.queue_zoom_action(lambda: click_info.function(modifiers))

        # If we're dragging, it means we intend to drop, so we can queue both
        # at once.
        #
        # HACK: Intercepting the function here is pretty hacky.
        #
        # TODO: Remove `str` cast once action path comparison works
        if str(click_info.function) == str(actions.user.drag):

            def queue_drop():
                nonlocal modifiers
                actions.user.queue_zoom_action(lambda: actions.user.drop(modifiers))

            # Add drop on a delay so the ding rings twice.
            cron.after("150ms", queue_drop)


@context.action_class("user")
class NoiseActions:
    def on_pop():
        # Explicitly defer to the zoom mouse's implementation.
        pass

    def on_hiss(start: bool):
        # Explicitly do nothing.
        #
        # TODO: Hiss to scroll?
        pass
