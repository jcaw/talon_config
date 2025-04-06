from talon import actions, Module, Context, ctrl, ui
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys


module = Module()

context = Context()
context.matches = r"""
app: v2game.exe
title: Victoria 2
"""


def zoom_map(steps: int, zooming_in: bool):
    # start_mouse_pos = ctrl.mouse_pos()
    # try:
    for i in range(steps):
        actions.mouse_scroll(by_lines=False, y=-100 if zooming_in else 100)
        actions.sleep("16ms")


# finally:
#     pass
#     actions.mouse_move(*start_mouse_pos)


@module.action_class
class Actions:
    def victoria_2_zoom_in(steps: int = 1):
        """Zoom into the map in Victoria 2."""
        zoom_map(steps, True)

    def victoria_2_zoom_out(steps: int = 1):
        """Zoom out of the map in Victoria 2."""
        zoom_map(steps, False)

    def victoria_2_set_zoom(level: int):
        """Zoom the map to a specific level."""
        factor = 32.0 / 9.0
        zoom_map(32, True)
        original_mouse_pos = ctrl.mouse_pos()
        actions.mouse_move(*ui.active_window().rect.center)
        try:
            zoom_map(round((level - 1) * factor), False)
        finally:
            actions.mouse_move(*original_mouse_pos)
