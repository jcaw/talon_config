""""Module to assist playing Magic The Gathering: Arena"""

import random
from typing import Optional

from talon import Module, Context, cron, actions, ui, ctrl
from talon.ui import Rect, Point2d


module = Module()


def random_wait(a: int = 50, b: int = 350):
    wait = random.randint(a, b)
    actions.sleep(f"{wait}ms")


def offset_point(x: int, y: int, area_rect: Rect, divisor: Optional[float] = 5.0):
    x_offset = area_rect.width / random.randint(
        -area_rect.width / 5, area_rect.width / 5
    )
    y_offset = area_rect.height / random.randint(
        -area_rect.height / 5, area_rect.height / 5
    )
    return Point2d(x + x_offset, y + y_offset)


@module.action_class
class Actions:
    def mtg_arena_play_card():
        """Play hovered card onto the field by dragging it."""
        mouse_start_pos = ctrl.mouse_pos()
        rect = ui.active_window().rect
        play_target = offset_point(*rect.center, rect)
        actions.mouse_drag()
        try:
            random_wait()
            actions.self.spline_mouse(*play_target, random.uniform(0.05, 0.2))
            random_wait()
        finally:
            actions.mouse_release()
        random_wait()
        actions.self.spline_mouse(
            *offset_point(*mouse_start_pos, rect, 15.0), random.uniform(0.05, 0.15)
        )


context = Context()
context.matches = r"""
app: MTGA.exe
"""


def bind():
    try:
        actions.user.vimfinity_bind_keys(
            {
                "enter": (
                    actions.self.mtg_arena_play_card,
                    "Play Hovered Card",
                )
            },
            context=context,
        )
    except KeyError:
        print("Failed to bind MTG Duelist shortcuts. Retrying in 1s.")
        cron.after("1s", bind)


cron.after("1s", bind)
