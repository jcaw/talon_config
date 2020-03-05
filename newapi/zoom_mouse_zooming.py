from typing import Callable, List

from talon import Module, actions
from talon.track.geom import Point2d
from talon_plugins import eye_zoom_mouse

from user.newapi.mouse import Click
from user.newapi.zoom_mouse import is_zooming
from user.newapi.utils.ticker_context import make_ticker_context


# TODO: Combine this with zoom_mouse.py


zooming_module = Module()


@zooming_module.action_class
class ZoomingActions:
    def end_zoom() -> Point2d:
        """Terminate the zoom.

        :returns: the final position

        """
        # TODO: Will this be reactive enough, or should we make this accessible
        #   anywhere in the zoom mouse?
        _, origin = eye_zoom_mouse.zoom_mouse.get_pos()
        eye_zoom_mouse.zoom_mouse.cancel()
        actions.mouse_move(origin.x, origin.y)


zooming_context = make_ticker_context(None, is_zooming)


@zooming_context.action_class("user.newapi.mouse")
class MouseActions:
    def default_click(click_info: Click):
        actions.user.newapi.zoom_mouse_zooming.end_zoom()
        click_info.function(click_info.modifiers)


@zooming_context.action_class("user.newapi.noise")
class SoundActions:
    def on_hiss(start: bool):
        if start:
            actions.user.newapi.zoom_mouse.clear_zoom_queue()
            actions.user.newapi.zoom_mouse_zooming.end_zoom()