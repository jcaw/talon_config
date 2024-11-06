import sys
import re

from talon import ui, Module, Context, actions, cron
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys

if ui.platform == "windows":
    import win32api as win32
    import win32con
    import pywintypes


def find_matching_screen(index):
    previous_matched_index = -1
    for direct_index in range(0, 255):
        try:
            device = win32.EnumDisplayDevices(None, direct_index)
            dm = win32.EnumDisplaySettings(
                device.DeviceName, win32con.ENUM_CURRENT_SETTINGS
            )
            previous_matched_index += 1
            if previous_matched_index == index:
                return device, dm
        except pywintypes.error:
            # Invalid screen
            pass
    raise ValueError(f"No screen could be found matching index: {index}")


module = Module()


@module.action_class
class Actions:
    def set_screen_rotation(screen_index: int, rotation_degrees: int):
        """Set a screen to a specific counter-clockwise rotation."""
        assert rotation_degrees in [0, 90, 180, 270], rotation_degrees
        win_rot_mapping = {
            0: win32con.DMDO_DEFAULT,
            90: win32con.DMDO_90,
            180: win32con.DMDO_180,
            270: win32con.DMDO_270,
        }
        win_rot_value = win_rot_mapping[rotation_degrees]
        # TODO: Another method that rotates the screen relative to current orientation.
        device, dm = find_matching_screen(screen_index)
        if (dm.DisplayOrientation + win_rot_value) % 2 == 1:
            dm.PelsWidth, dm.PelsHeight = dm.PelsHeight, dm.PelsWidth
        dm.DisplayOrientation = win_rot_value

        win32.ChangeDisplaySettingsEx(device.DeviceName, dm)

    def rotate_screen_clockwise(screen_index: int, rotation_degrees: int = 90):
        """Rotate screen N degrees clockwise. Defaults to 90 degrees."""
        assert rotation_degrees in [90, 180, 270], rotation_degrees
        _, dm = find_matching_screen(screen_index)
        # Windows' rotation is counter-clockwise, so subtract the degrees
        new_degrees = (dm.DisplayOrientation * 90 - rotation_degrees + 360) % 360
        actions.self.set_screen_rotation(screen_index, new_degrees)

    def flip_screen_rotation(screen_index: int):
        """Flip screen's orientation (rotate by 180 degrees)."""
        actions.self.rotate_screen_clockwise(screen_index, 180)

    def open_display_settings():
        """Open the OS's display settings option window."""
        actions.user.automator_close_start_menu()
        # actions.user.switch_or_start("Display settings")
        actions.key("win")
        actions.insert("Display settings")
        actions.key("enter")


windows_context = Context()
windows_context.matches = "os: windows"


# Set vimfinity bindings
#############################################################################


def screen_set_rotation(screen_index, rotation_degrees):
    return (
        lambda: actions.user.set_screen_rotation(screen_index, rotation_degrees),
        f"Set rotation: {rotation_degrees} degrees",
    )


bindings = {"w d": actions.self.open_display_settings}
for screen_i in range(9):
    prefix = f"w f{screen_i + 1}"
    bindings.update(
        {
            f"{prefix}": f"Monitor {screen_i + 1} Actions",
            f"{prefix} up": screen_set_rotation(screen_i, 0),
            f"{prefix} left": screen_set_rotation(screen_i, 90),
            f"{prefix} down": screen_set_rotation(screen_i, 180),
            f"{prefix} right": screen_set_rotation(screen_i, 270),
            f"{prefix} r": (
                lambda i=screen_i: actions.user.rotate_screen_clockwise(i),
                "Rotate 90 degrees clockwise",
            ),
            f"{prefix} f": (
                lambda i=screen_i: actions.user.flip_screen_rotation(i),
                "Flip Orientation",
            ),
        }
    )

vimfinity_bind_keys(bindings, windows_context)
