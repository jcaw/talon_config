"""Behaviours, captures & actions that aren't in a dedicated module yet."""

from talon import Module, Context, actions, imgui, app


module = Module()


@module.action_class
class ModuleActions:
    def open_file() -> None:
        """Bring up a dialogue to open a file."""

    def next_error() -> None:
        """Go to the next error."""

    def previous_error() -> None:
        """Go to the previous error."""


global_context = Context()
global_context.settings["imgui.dark_mode"] = 1


@global_context.action_class("self")
class GlobalActions:
    pass


win_linux_context = Context(name="unsorted_win_linux")
win_linux_context.matches = r"""
os: linux
os: windows
"""


@win_linux_context.action_class("self")
class WinLinuxActions:
    def open_file() -> None:
        actions.key("ctrl-o")


mac_context = Context(name="unsorted_mac")
mac_context.matches = r"""
os: mac
"""


@mac_context.action_class("self")
class MacActions:
    def open_file() -> None:
        actions.key("cmd-o")
