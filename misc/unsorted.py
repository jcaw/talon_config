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

    def go_back() -> None:
        """Go back (usually to the previous page - depends on context)."""
        # TODO: Switch to XF86Back. This is just a reliable default
        actions.key("alt-left")

    def go_forward() -> None:
        """Go forward (usually to the next page - depends on context)."""
        # TODO: Switch to XF86Forward or equivalent. This is just a reliable
        #   default
        actions.key("alt-right")

    def cancel() -> None:
        """Cancel the current "thing" - e.g. by press escape.

        (Note this is not meant to be the most powerful context exiting command
        available.)

        """
        actions.key("escape")


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
