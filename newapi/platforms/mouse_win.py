from talon import Module, ctrl
from talon.track.geom import Point2d

from user.utils import ON_WINDOWS

if ON_WINDOWS:
    import win32api
    import win32con


module = Module("mouse_scroll")


@module.action_class
class MouseActions:
    def mouse_scroll(amount: int) -> None:
        """Scroll by a specific interval."""
        position = Point2d(*ctrl.mouse_pos())
        win32api.mouse_event(
            win32con.MOUSEEVENTF_WHEEL, position.x, position.y, amount, 0
        )
