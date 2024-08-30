from copy import copy
import threading
import re

from talon import canvas, actions, Module, cron, skia, ui, app
from talon.ui import Rect


class DrawableRect:
    def __init__(self, rect: Rect, color: str):
        self.rect = rect
        self.color = color


rects_lock = threading.Lock()
rects = []

error_color = "#FF1177"
translucent_append = "11"
# Based on a 1080p screen - will be scaled on other resolutions
RELATIVE_STROKE_THICKNESS = 3.0
RELATIVE_STROKE_RADIUS = 5.0


stroke_factor = 1920 / RELATIVE_STROKE_THICKNESS
corner_factor = 1920 / RELATIVE_STROKE_RADIUS


def draw(c):
    with rects_lock:
        _rects = copy(rects)

    paint = c.paint

    max_dim = max(c.width, c.height)
    stroke_width = int(max(1, round(max_dim / stroke_factor)))
    corner_radius = int(max(1, round(max_dim / corner_factor)))

    for draw_rect in _rects:
        try:
            paint.color = draw_rect.color
        # TODO: More specific error
        except:
            paint.color = error_color
        rrect = skia.RoundRect.from_rect(
            draw_rect.rect, x=corner_radius, y=corner_radius
        )

        paint.style = paint.Style.STROKE
        # TODO: Make this dynamic based on resolution
        paint.stroke_width = stroke_width
        c.draw_rrect(rrect)

        paint.style = paint.Style.FILL
        try:
            paint.color = draw_rect.color + translucent_append
        except:
            paint.color = error_color + translucent_append
        c.draw_rrect(rrect)


canvases = []


def canvas_from_screen(screen):
    """Create a canvas, avoiding Windows' display issues"""
    c = canvas.Canvas.from_screen(screen)
    if app.platform == "windows":
        hotfix_rect = Rect(*screen.rect)
        hotfix_rect.height -= 1
        c.rect = hotfix_rect
    return c


def create_canvases():
    destroy_canvases()
    # TODO: Current screen first?
    for screen in ui.screens():
        c = canvas_from_screen(screen)
        c.focusable = False
        c.register("draw", draw)
        c.freeze()
        canvases.append(c)


def destroy_canvases():
    for c in canvases:
        c.unregister("draw", draw)
        c.close()
    canvases.clear()


def refresh_canvases():
    destroy = False
    with rects_lock:
        if len(rects) == 0:
            destroy = True
    if destroy:
        destroy_canvases()
    elif len(canvases) == 0:
        create_canvases()
    else:
        for c in canvases:
            c.resume()
            c.freeze()


module = Module()


def validate_color(color: str):
    if not (isinstance(color, str) and re.match("#" + "[0-9A-F]" * 6, color)):
        raise ValueError(
            f'Color must be a 6-digit hex string with hash, e.g. "#FF0089". Was: "{color}"'
        )


@module.action_class
class Actions:
    def flash_rect(rect: Rect, duration: str = "500ms", color: str = "#000000"):
        """Flash a translucent filled rect on-screen for a short duration."""
        validate_color(color)

        draw_rect = DrawableRect(rect, color)

        def remove_rect():
            nonlocal draw_rect
            with rects_lock:
                rects.remove(draw_rect)
            refresh_canvases()

        cron.after(duration, remove_rect)

        with rects_lock:
            rects.append(draw_rect)
        refresh_canvases()
