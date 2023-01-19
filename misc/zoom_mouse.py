from typing import Callable, List, Optional
import logging
import time
from random import randint

from talon import Module, Context, actions, settings, ctrl, cron, speech_system, noise
from talon.types import Point2d
from talon_plugins import eye_zoom_mouse

from user.utils import sound, Modifiers
from user.misc.mouse import Click


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


# TODO: Pull this out once talon exposes mouse mode scopes by default
@module.scope
def scope(*_):
    zoom_mouse = zoom_mouse_active()
    return {
        "zoom_mouse_active": zoom_mouse,
        "zoom_mouse_zooming": zoom_mouse and is_zooming(),
    }


speech_system.register("pre:phrase", scope.update)
# Noises won't trigger pre:phrase - bind them so we definitely catch the zoom.
noise.register("pre:pop", scope.update)
noise.register("pre:hiss", scope.update)


@module.action_class
class Actions:
    def end_zoom() -> Point2d:
        """Terminate the zoom.

        Mouse will be moved to the user's gaze position.

        :returns: the final position

        """
        # TODO: Will this be reactive enough, or should we make this accessible
        #   anywhere in the zoom mouse?
        _, origin = eye_zoom_mouse.zoom_mouse.get_pos()
        if origin:
            eye_zoom_mouse.zoom_mouse.cancel()
            actions.mouse_move(origin.x, origin.y)
        return origin

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

    def toggle_gaze_track_dot():
        """Toggle whether a small dot tracks your gaze outside zoom."""
        eye_zoom_mouse.config.track_gaze_with_dot = (
            not eye_zoom_mouse.config.track_gaze_with_dot
        )
        if eye_zoom_mouse.zoom_mouse.enabled:
            eye_zoom_mouse.zoom_mouse.disable()
            eye_zoom_mouse.zoom_mouse.enable()

    def maybe_queue_drag() -> None:
        """Queue a drag + drop iff in zoom mouse mode."""
        pass


context = Context()
context.matches = r"""
user.zoom_mouse_active: True
"""


@context.action_class("user")
class MouseActions:
    def drag(modifiers: List[str] = []):
        Modifiers(modifiers).__enter__()
        actions.mouse_drag()
        actions.user.shake_mouse()

    def drop(modifiers: List[str] = []):
        # Some drag actions require that the mouse wait in the drop position
        # for a little while before dropping. Movement is instant with the zoom
        # mouse, so insert an artificial wait.
        #
        # Also shake the mouse around a bit for cases like tab dragging in
        # firefox, where instant warping won't register as movement.
        actions.user.shake_mouse()
        actions.mouse_release()
        # TODO: Change this. Context manager is yuck. Introduce lower
        #   abstraction for hold/release modifiers.
        Modifiers(modifiers).__exit__(None, None, None)

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

    def maybe_queue_drag() -> None:
        # TODO: Use `self` or `user` consistently for actions
        actions.self.queue_zoom_action(lambda: actions.self.drag())

        def drop_after_pause():
            """Undrag the mouse, after a short pause. Gives time for visual feedback."""
            actions.sleep("1000ms")
            actions.self.drop()

        cron.after("150ms", lambda: actions.self.queue_zoom_action(drop_after_pause))


# HACK: Unbind the default zoom_mouse pop, manually bind it ourselves so we can
#   override the pop binding with other contexts.
#
#   Unbind before every pop to reset the unbind when the zoom mouse is
#   restarted.
noise.register(
    "pre:pop", lambda *_: noise.unregister("pop", eye_zoom_mouse.zoom_mouse.on_pop)
)


@context.action_class("user")
class NoiseActions:
    def on_pop():
        # Manually invoke zoom mouse's own handler
        eye_zoom_mouse.zoom_mouse.on_pop(True)

    def on_hiss(start: bool):
        try:
            from user.settings import scroll
        except ImportError:
            print("Scroll module not found. It must be manually added.")
        if start:
            scroll.start()
        else:
            scroll.stop()


zooming_context = Context()
zooming_context.matches = r"""
user.zoom_mouse_zooming: True
"""


@zooming_context.action_class("user")
class MouseActions:
    def default_click(click_info: Click):
        actions.user.end_zoom()
        click_info.function(click_info.modifiers)


@zooming_context.action_class("user")
class SoundActions:
    def on_hiss(start: bool):
        if start:
            actions.user.clear_zoom_queue()
            actions.self.end_zoom()
