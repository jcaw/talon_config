from typing import List

from talon import Context, actions

from user.misc.mouse import Click


# TODO: Combine this with zoom_mouse.py


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
