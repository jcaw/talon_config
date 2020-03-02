from talon import Module, actions
from talon_plugins import eye_mouse, eye_zoom_mouse


module = Module()


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
