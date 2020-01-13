import logging

from talon_plugins import eye_mouse, eye_zoom_mouse

from ..utils import sound
from ..patches import better_zoom_mouse

LOGGER = logging.getLogger(__name__)


# TODO: Use centralized config system, e.g. from community.
class config:
    # Play sounds when clicks are buffered/cancelled?
    BUFFERED_CLICK_SOUNDS = True


def zooming():
    """True iff the eye_zoom_mouse is currently zooming."""
    return eye_zoom_mouse.zoom_mouse.state == eye_zoom_mouse.STATE_OVERLAY


def cancel_zoom():
    """Cancel the zoom, iff it's open. Returns the final position.

    If not zooming, returns nothing. If an action is queued, always cancels it.

    :returns Point2d: the final position

    """
    if zooming():
        _, origin = eye_zoom_mouse.zoom_mouse.get_pos()
        eye_zoom_mouse.zoom_mouse.cancel()
        return origin
    return None


def zoom_mouse_enabled():
    try:
        return eye_zoom_mouse.zoom_mouse.enabled
    except AttributeError:
        return False


def eye_mouse_enabled():
    return eye_mouse.control_mouse.enabled


def disable_zoom_mouse():
    eye_zoom_mouse.active.disable()


def disable_eye_mouse():
    eye_mouse.control_mouse.disable()


def enable_zoom_mouse():
    eye_zoom_mouse.active.enable()


def enable_eye_mouse():
    eye_mouse.control_mouse.enable()


def clear_zoom_queue():
    if eye_zoom_mouse.zoom_mouse.queued_action:
        eye_zoom_mouse.zoom_mouse.cancel_action()
        if config.BUFFERED_CLICK_SOUNDS:
            sound.play_cancel()


def zoom_mouse_patched():
    """Has `eye_zoom_mouse` been patched with `better_zoom_mouse`?"""
    return hasattr(better_zoom_mouse, "BetterZoomMouse") and isinstance(
        eye_zoom_mouse.zoom_mouse, better_zoom_mouse.BetterZoomMouse
    )


class FrozenEyeMouse(object):
    """Disable eye input for the duration of the context."""

    def __init__(self):
        self.zoom_was_enabled = False
        self.eye_mouse_was_enabled = False

    def __enter__(self):
        cancel_zoom()
        if zoom_mouse_enabled():
            self.zoom_was_enabled = True
            disable_zoom_mouse()
        if eye_mouse_enabled():
            self.eye_mouse_was_enabled = True
            disable_eye_mouse()

    def __exit__(self, *args):
        if self.zoom_was_enabled:
            enable_eye_mouse()
        if self.eye_mouse_was_enabled:
            enable_eye_mouse()


def toggle_eye_mouse_exclusive(m):
    """Toggle the eye mouse. Also disables the zoom mouse."""
    disable_zoom_mouse()
    eye_mouse.control_mouse.toggle()


def toggle_zoom_mouse_exclusive(m):
    """Toggle the zoom mouse. Also disables regular eye mouse."""
    disable_eye_mouse()
    eye_zoom_mouse.active.toggle()


class TempEyeMouse(object):
    """Temporarily enable the eye mouse for the duration of the context.

    Designed so the user can use normal eye tracking during a hiss.

    """

    LOGGER = logging.getLogger(__name__ + ".TempEyeMouse")

    def __init__(self):
        # Was the zoom mouse active when the hiss started?
        self._zoom_was_active = False

    def __enter__(self):
        LOGGER.debug("Enabling temporary eye mouse")
        self._zoom_was_active = zoom_mouse_enabled()
        if self._zoom_was_active:
            disable_zoom_mouse()
            self._zoom_was_active = True
        enable_eye_mouse()

    def __exit__(self, *_):
        LOGGER.debug("Disabling temporary eye mouse")
        disable_eye_mouse()
        if self._zoom_was_active:
            enable_zoom_mouse()
            self._zoom_was_active = False
