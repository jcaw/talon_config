"""Eye tracking control utilities.

Uses the modern Talon tracking API (actions.tracking).
"""

import logging

from talon import actions


LOGGER = logging.getLogger(__name__)


def zoom_mouse_enabled() -> bool:
    """Check if zoom mouse is currently enabled."""
    return actions.tracking.control_zoom_enabled()


def cancel_zoom():
    """Cancel any active zoom overlay."""
    actions.tracking.zoom_cancel()


def enable_zoom_mouse():
    """Enable the zoom mouse."""
    actions.tracking.control_zoom_toggle(True)


def disable_zoom_mouse():
    """Disable the zoom mouse."""
    actions.tracking.control_zoom_toggle(False)


def enable_gaze_control():
    """Enable gaze control (direct eye mouse)."""
    actions.tracking.control_gaze_toggle(True)


def disable_gaze_control():
    """Disable gaze control."""
    actions.tracking.control_gaze_toggle(False)


class FrozenEyeMouse:
    """Context manager to temporarily disable eye tracking.

    Example:
        with FrozenEyeMouse():
            # Eye tracking is disabled here
            do_something()
        # Eye tracking is restored
    """

    def __init__(self):
        self._zoom_was_enabled = False

    def __enter__(self):
        cancel_zoom()
        self._zoom_was_enabled = zoom_mouse_enabled()
        if self._zoom_was_enabled:
            disable_zoom_mouse()
        return self

    def __exit__(self, *args):
        if self._zoom_was_enabled:
            enable_zoom_mouse()


class TempEyeMouse:
    """Context manager to temporarily switch to direct gaze control.

    Designed so the user can use normal eye tracking during a hiss.
    """

    def __init__(self):
        self._zoom_was_enabled = False

    def __enter__(self):
        LOGGER.debug("Enabling temporary gaze control")
        self._zoom_was_enabled = zoom_mouse_enabled()
        if self._zoom_was_enabled:
            disable_zoom_mouse()
        enable_gaze_control()
        return self

    def __exit__(self, *args):
        LOGGER.debug("Disabling temporary gaze control")
        disable_gaze_control()
        if self._zoom_was_enabled:
            enable_zoom_mouse()
