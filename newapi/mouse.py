from typing import Callable, List
import time

from talon import Module, Context, actions, ctrl
from talon.track.geom import Point2d
from talon_plugins import eye_mouse, eye_zoom_mouse

from user.misc import basic
from user.utils.eye_mouse import FrozenEyeMouse
from user.utils.mouse_history import backdated_position


CLICKS_MAP = {
    "click": actions.self.left_click,
    "rickle": actions.self.right_click,
    "middle": actions.self.middle_click,
    "double": actions.self.double_click,
    "triple": actions.self.triple_click,
    "drag": actions.self.drag,
    "drop": actions.self.drop,
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

module.list("clicks", "all available click types")


@module.action_class
class Actions:
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
        with basic.Modifiers(modifiers):
            actions.mouse_click(button=0)

    def right_click(modifiers: List[str] = []):
        """Right click at current position."""
        with basic.Modifiers(modifiers):
            actions.mouse_click(button=1)

    def middle_click(modifiers: List[str] = []):
        """Middle click at current position."""
        with basic.Modifiers(modifiers):
            actions.mouse_click(button=2)

    def double_click(modifiers: List[str] = []):
        """Double left click at current position."""
        with basic.Modifiers(modifiers):
            for i in range(2):
                actions.mouse_click(button=0)

    def triple_click(modifiers: List[str] = []):
        """Triple left click at current position."""
        with basic.Modifiers(modifiers):
            for i in range(3):
                actions.mouse_click(button=0)

    def drag(modifiers: List[str] = []):
        """Hold a mouse button at current position (default left)."""
        basic.Modifiers(modifiers).__enter__()
        # TODO: Switch to newapi action once I know the interface
        ctrl.mouse_click(button=0, down=True)

    def drop(modifiers: List[str] = []):
        """Release a mouse button at current position (default left)."""
        # TODO: Switch to newapi action once I know the interface
        print("Default drag")
        ctrl.mouse_click(button=0, up=True)
        basic.Modifiers(modifiers).__exit__(None, None, None)

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


@module.capture
def click(m) -> Click:
    """Get click info from a phrase."""


context = Context()
context.lists["self.clicks"] = CLICKS_MAP.keys()


@context.capture(rule="{self.clicks}")
def click(m) -> Click:
    click_command = m["clicks"][0]
    click_function = CLICKS_MAP[click_command]
    # TODO: Cover no backdated position
    position = backdated_position(m)
    modifiers = []
    # TODO: Add modifiers, once they're ported to newapi
    # modifiers = m.modifiers
    return Click(click_function, position, modifiers)


@context.action_class("user.newapi.noise")
class NoiseActions:
    def on_pop():
        actions.mouse_click()

    def on_hiss(start: bool):
        # TODO: Replace with newapi actions once I know the interface
        #
        # TODO: Maybe use audio cues to notify user of premature release?
        if start:
            ctrl.mouse_click(button=0, down=True)
        else:
            ctrl.mouse_click(button=0, up=True)
