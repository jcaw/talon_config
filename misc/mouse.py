from typing import Callable, List
import time
from random import randint

from talon import Module, Context, actions, ctrl, ui
from talon.types import Point2d

# from talon_plugins import eye_mouse, eye_zoom_mouse

from user.utils import Modifiers

# from user.utils.eye_mouse import FrozenEyeMouse
# from user.utils.mouse_history import backdated_position


CLICKS_MAP = {
    "click": actions.self.left_click,
    "rickle": actions.self.right_click,
    "middle": actions.self.middle_click,
    "double": actions.self.double_click,
    "triple": actions.self.triple_click,
    "drag": actions.self.drag,
    # "drop" has a high misrecognition rate, so use "undrag"
    "undrag": actions.self.drop,
}


class Click:
    """Stores information about a click command."""

    def __init__(
        self, function: Callable, position_at: Point2d = None, modifiers: List[str] = []
    ):
        """Create a new Click.

        :param function: Function to call to perform the click.
        :param Point2d: Position when the action was spoken. (Usually this is
          the mouse position.) This position can be used to backdate the click.
        :param modifiers: Modifiers to hold while executing ``function``.

        """
        self.function = function
        self.position_at = position_at
        self.modifiers = modifiers


module = Module()

module.list("clicks", desc="all available click types")

# Currently in a click-drag operation? Left mouse is held?
_left_mouse_dragging = False


@module.action_class
class Actions:
    def center_mouse() -> None:
        """Move the mouse to the center of the active window."""
        rect = ui.active_window().rect
        center = (rect.x + round(rect.width / 2), rect.y + round(rect.height / 2))
        actions.mouse_move(*center)

    # TODO: Pull these over to new eye system?
    def debug_overlay():
        """Toggle the eye mouse debug overlay."""
        eye_mouse.debug_overlay.toggle()

    def toggle_eye_mouse():
        """Toggle the eye mouse on/off. Disables zoom mouse."""
        eye_zoom_mouse.active.disable()
        eye_mouse.control_mouse.toggle()

    def toggle_zoom_mouse():
        """Toggle the zoom mouse on/off. Disables regular eye mouse."""
        eye_mouse.control_mouse.disable()
        eye_zoom_mouse.active.toggle()

    def camera_overlay():
        """Toggle the camera overlay on/off."""
        eye_mouse.camera_overlay.toggle()

    def calibrate_tracker():
        """Run eye tracker calibration."""
        eye_mouse.calib_start()

    def left_click(modifiers: List[str] = []):
        """Left click at current position."""
        with Modifiers(modifiers):
            actions.mouse_click(button=0)

    def right_click(modifiers: List[str] = []):
        """Right click at current position."""
        with Modifiers(modifiers):
            actions.mouse_click(button=1)

    def middle_click(modifiers: List[str] = []):
        """Middle click at current position."""
        with Modifiers(modifiers):
            actions.mouse_click(button=2)

    def double_click(modifiers: List[str] = []):
        """Double left click at current position."""
        with Modifiers(modifiers):
            for i in range(2):
                actions.mouse_click(button=0)

    def shift_left_click():
        """Hold shift and left click at the current mouse position."""
        actions.self.left_click(["shift"])

    def control_left_click():
        """Hold control and left click at the current mouse position."""
        actions.self.left_click(["ctrl"])

    def triple_click(modifiers: List[str] = []):
        """Triple left click at current position."""
        with Modifiers(modifiers):
            for i in range(3):
                actions.mouse_click(button=0)

    def drag(modifiers: List[str] = []):
        """Hold a mouse button at current position (default left)."""
        global _left_mouse_dragging
        _left_mouse_dragging = True
        Modifiers(modifiers).__enter__()
        actions.mouse_drag()

    def drop(modifiers: List[str] = []):
        """Release a mouse button at current position (default left)."""
        global _left_mouse_dragging
        actions.mouse_release()
        Modifiers(modifiers).__exit__(None, None, None)
        _left_mouse_dragging = False

    def drag_or_drop(modifiers: List[str] = []):
        """Click and hold the left mouse button, or if already dragging, release it (plus modifiers)."""
        if _left_mouse_dragging:
            actions.self.drop(modifiers)
        else:
            actions.self.drag(modifiers)

    # TODO: Port this to new eye system?
    # TODO: Rename this to `eye_click` or something?
    def default_click(click_info: Click):
        """Perform ``click_function`` according to the context."""
        with FrozenEyeMouse():
            # Backdating clicks is a good default for arbitrary pointing
            # devices.
            actions.mouse_move(*click_info.position_at)
            click_info.function(click_info.modifiers)
            # Sleep for enough time for the click to complete.
            time.sleep(0.1)

    def click_current(click_info: Click):
        """Click where the mouse is currently."""
        click_info.function()

    def shake_mouse(seconds: float = 0.1, allowed_deviation: int = 5):
        """Briefly shake the cursor around its current position.

        Can be used to compensate for instantaneous mouse movement not being
        detected as a drag, e.g. when clicking + dragging Firefox tabs.

        """
        FRAME_PAUSE = 0.016  # In secs
        PIXEL_RANGE = 5
        # Use a defined number of moves (not time) so behaviour is predictable.
        n_moves = max(int(seconds // FRAME_PAUSE), 1)

        start_x = actions.mouse_x()
        # Technically a race condition, but never going to come up
        start_y = actions.mouse_y()
        for i in range(n_moves):
            # NOTE: This will move in a square pattern, not a circle. That's
            #   probably fine.
            actions.mouse_move(
                start_x + randint(-PIXEL_RANGE, PIXEL_RANGE),
                start_y + randint(-PIXEL_RANGE, PIXEL_RANGE),
            )
            time.sleep(FRAME_PAUSE)
        actions.mouse_move(start_x, start_y)

    def shake_click(button: int = 0, seconds: float = 0.1, allowed_deviation: int = 5):
        """Hold down `button`, shake the cursor around, then release.

        Use to register certain types of click that won't register otherwise.

        """
        actions.mouse_drag(button=button)
        try:
            actions.self.shake_mouse(
                seconds=seconds, allowed_deviation=allowed_deviation
            )
        finally:
            actions.mouse_release(button=button)

    def spline_mouse(x: int, y: int, seconds: float = 1.0) -> None:
        """Move mouse gradually to point `(x, y)`."""
        FRAME_PAUSE_MS = 16
        # Use a defined number of moves (not time) so movement is smooth.
        n_steps = max(int(seconds // (FRAME_PAUSE_MS / 1000)), 1)

        start_x = actions.mouse_x()
        start_y = actions.mouse_y()
        delta_x = (x - start_x) / n_steps
        delta_y = (y - start_y) / n_steps
        for i in range(n_steps):
            actions.mouse_move(start_x + (i * delta_x), start_y + (i * delta_y))
            actions.sleep(f"{FRAME_PAUSE_MS}ms")
        actions.mouse_move(x, y)


context = Context()
context.lists["self.clicks"] = CLICKS_MAP.keys()


@module.capture(rule="[<user.modifiers>] {self.clicks}")
def click(m) -> Click:
    """Get click info from a phrase."""
    click_command = m["clicks"]
    click_function = CLICKS_MAP[click_command]
    # TODO: Cover no backdated position
    #
    # NOTE: This has quirks. If you say "shift click", it will backdate to the
    #   start of "click", not "shift".
    #
    # TODO: Maybe defer to the backdated position of the voice activity if
    #   timestamps aren't available?
    #
    # FIXME: port backdated_position to new eye mouse system
    # position = backdated_position(m[-1])
    position = None
    modifiers = m["modifiers"] if hasattr(m, "modifiers") else []
    return Click(click_function, position, modifiers)


# TODO: Port these to the new eye mouse and noise systems?
# @context.action_class("user")
# class NoiseActions:b
#     def on_pop():
#         actions.mouse_click()

#     def on_hiss(start: bool):
#         # TODO: Maybe use audio cues to notify user of premature release?
#         if start:
#             actions.mouse_drag()
#         else:
#             actions.mouse_release()
