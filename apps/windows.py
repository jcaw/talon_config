import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from talon import Context, Module, actions, ui

from user.utils.formatting import SurroundingText

key = actions.key
sleep = actions.sleep


module = Module()


@module.action_class
class Actions:
    def windows_cast_screen():
        """Open the Windows screen casting interface."""
        key("win:down")
        sleep("100ms")
        key("k")
        sleep("100ms")
        key("win:up")

    def os_dark_mode():
        """Switch to dark mode at the OS level."""

    def os_light_mode():
        """Switch to light mode at the OS level."""

    def toggle_os_dark_mode():
        """Switch between light/dark mode at the OS level."""

    def os_dark_mode_for_apps():
        """Switch to dark mode at the OS level, but just for apps."""

    def os_light_mode_for_apps():
        """Switch to light mode at the OS level, but just for apps."""

    def toggle_os_dark_mode_for_apps():
        """Switch between light/dark mode at the OS level."""


context = Context()
context.matches = """
os: windows
"""


PERSONALIZE_PATH = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
APP_LIGHT_THEME_KEY = "AppsUseLightTheme"
SYSTEM_LIGHT_THEME_KEY = "SystemUseLightTheme"


def set_dark_mode(app_only: bool, dark: bool):
    import winreg

    # Open the registry key with write access
    registry_key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, PERSONALIZE_PATH, 0, winreg.KEY_SET_VALUE
    )
    try:
        # Set the value of AppsUseLightTheme
        winreg.SetValueEx(
            registry_key,
            APP_LIGHT_THEME_KEY if app_only else SYSTEM_LIGHT_THEME_KEY,
            0,
            winreg.REG_DWORD,
            0 if dark else 1,
        )
    finally:
        winreg.CloseKey(registry_key)


def is_dark_mode(app_only: bool):
    import winreg

    # Open the registry key
    registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, PERSONALIZE_PATH)
    try:
        # Get the value of AppsUseLightTheme
        value, _ = winreg.QueryValueEx(
            registry_key, APP_LIGHT_THEME_KEY if app_only else SYSTEM_LIGHT_THEME_KEY
        )
        # If the value is 1, light mode is active. If 0, dark mode is active.
        return value == 0
    finally:
        winreg.CloseKey(registry_key)


# def set_dark_mode(app_only: bool, dark: bool):
#     """Create a command that switch between light/dark modes."""
#     subprocess.run(
#         [
#             "reg.exe",
#             "add",
#             "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
#             "/v",
#             APP_LIGHT_THEME_KEY if app_only else SYSTEM_LIGHT_THEME_KEY,
#             "/t",
#             "REG_DWORD",
#             "/d",
#             "0" if dark else "1",
#             "/f",
#         ]
#     )


# def is_dark_mode(app_only: bool):
#     """Is Windows currently in dark mode?"""
#     return int(subprocess.run(
#         [
#             "reg.exe",
#             "get",
#             "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
#             "/v",
#             APP_LIGHT_THEME_KEY if app_only else SYSTEM_LIGHT_THEME_KEY,
#             "/t",
#             "REG_DWORD",
#             "/d",
#             "0" if dark else "1",
#             "/f",
#         ]
#     ).strip())


def get_selection_hell_mode(document_range, selection_range) -> Tuple[int, int]:
    """Get the selection from the hellish Windows API (lol)."""
    range_before_selection = document_range.clone()
    range_before_selection.move_endpoint_by_range(
        "End",
        "Start",
        target=selection_range,
    )
    start = len(range_before_selection.text)

    range_after_selection = document_range.clone()
    range_after_selection.move_endpoint_by_range(
        "Start",
        "End",
        target=selection_range,
    )
    end = len(document_range.text) - len(range_after_selection.text)

    return start, end


@context.action_class("self")
class UserActions:
    # def quit_talon() -> None:
    #     # `taskkill` has weird access permissions, so access may be denied. Use
    #     # `wmic` instead, it's more reliable.

    #     # subprocess.Popen(["taskkill", "-pid", str(os.getpid())], start_new_session=True)
    #     # subprocess.Popen(["taskkill", "-im", "talon.exe"], start_new_session=True)

    #     subprocess.Popen(
    #         [
    #             "wmic",
    #             "process",
    #             "where",
    #             "name='talon.exe'",
    #             # "processID='{}'".format(os.getpid()),
    #             "delete",
    #         ],
    #         start_new_session=True,
    #     )

    def restart_talon() -> None:
        # Should be something like: "C:/Program Files/Talon/python/bin/python3"
        python_path = Path(sys.executable)
        # Find the closest parent to Talon's root folder, since Talon's root
        # folder could be named anything
        while not str(python_path.stem) == "python":
            if python_path.parent == python_path:
                raise IOError("Can't find parent python folder")
            else:
                python_path = python_path.parent
        # From there, assume the talon exe's path
        talon_path = python_path.parent / "talon.exe"
        print(f'Restarting Talon from path: "{talon_path}"')
        subprocess.Popen(
            f'wmic process where "name=\'talon.exe\'" delete && sleep 2 && "{talon_path}"',
            # "where processID='{}'".format(os.getpid())
            start_new_session=True,
            shell=True,
        )

    def os_dark_mode():
        set_dark_mode(app_only=False, dark=True)

    def os_light_mode():
        set_dark_mode(app_only=False, dark=False)

    def toggle_os_dark_mode():
        set_dark_mode(app_only=False, dark=not is_dark_mode(app_only=False))

    def os_dark_mode_for_apps():
        set_dark_mode(app_only=True, dark=True)

    def os_light_mode_for_apps():
        set_dark_mode(app_only=True, dark=False)

    def toggle_os_dark_mode_for_apps():
        # print(f"IS dark mode: {is_dark_mode(app_only=True)}")
        set_dark_mode(app_only=True, dark=not is_dark_mode(app_only=True))

    def surrounding_text() -> Optional[SurroundingText]:
        # Latency for this approach when I tested it with Slack in Firefox was <16ms.
        try:
            focused_element = ui.focused_element()
            textedit_pattern = focused_element.textedit_pattern
            text_pattern = focused_element.text_pattern
            if not (textedit_pattern and text_pattern):
                return None

            document_range = text_pattern.document_range
            document_text = document_range.text
            selection_ranges = text_pattern.selection
            if len(selection_ranges) > 1:
                # Just act like there is no selection if there are multiple selections.
                print(
                    "WARNING: Multiple selections detected. This is not supported. Ignoring surrounding text."
                )
                return None
            selection_range = selection_ranges[0]
            selection_start, selection_end = get_selection_hell_mode(
                document_range, selection_range
            )

            N_CHARS_BEFORE = 30000
            N_CHARS_AFTER = 30000
            chars_before_start = max(0, selection_start - N_CHARS_BEFORE)
            chars_after_end = min(len(document_text) - 1, selection_end + N_CHARS_AFTER)
            return SurroundingText(
                text_before=document_text[chars_before_start:selection_start],
                text_after=document_text[selection_end:chars_after_end],
            )
        except OSError:
            # Assume this means either that there's no available element, or it's missing the necessary patterns
            return None
