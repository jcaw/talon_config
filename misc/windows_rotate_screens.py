import sys
import re

from talon import ui, Module, actions, cron

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
        assert rotation_degrees in [0, 90, 180, 270]
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


def bind():
    try:

        def screen_rotate(screen_index, rotation_degrees):
            return (
                lambda: actions.user.set_screen_rotation(
                    screen_index, rotation_degrees
                ),
                f"Rotate {rotation_degrees} degrees",
            )

        actions.user.vimfinity_bind_keys(
            {
                "w f1": "Primary Monitor Actions",
                "w f2": "Second Monitor Actions",
                "w f3": "Third Monitor Actions",
                # Screen 1 actions
                "w f1 up": screen_rotate(0, 0),
                "w f1 left": screen_rotate(0, 90),
                "w f1 down": screen_rotate(0, 180),
                "w f1 right": screen_rotate(0, 270),
                # Screen 2 actions
                "w f2 up": screen_rotate(1, 0),
                "w f2 left": screen_rotate(1, 90),
                "w f2 down": screen_rotate(1, 180),
                "w f2 right": screen_rotate(1, 270),
                # Screen 3 actions
                "w f3 up": screen_rotate(2, 0),
                "w f3 left": screen_rotate(2, 90),
                "w f3 down": screen_rotate(2, 180),
                "w f3 right": screen_rotate(2, 270),
            }
        )
    except KeyError:
        print("Failed to map window rotation vimfinity shortcuts. Trying again in 1s.")
        cron.after("1s", bind)


cron.after("100ms", bind)
