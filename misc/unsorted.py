"""Behaviours, captures & actions that aren't in a dedicated module yet."""

from talon import Module, Context, actions, imgui, app, clip
from typing import Optional, List
from pathlib import Path
import os
import shlex
import subprocess
import webbrowser
import logging

LOGGER = logging.getLogger()


module = Module()


# Stores the previous microphone, for when the microphone is disabled with
# `toggle_mic_off`
_previous_mic = None


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

    def rename() -> None:
        """Open the rename dialogue."""

    def rename_with_phrase(chunked_phrase: Optional[List] = None) -> None:
        """Open the rename dialogue and (optionally) insert a phrase."""
        actions.self.rename()
        if chunked_phrase:
            actions.self.chunked_phrase(complex_insert, "lowercase")

    def opening_number_action(number: int) -> None:
        """Context-specific command that fires on an opening number."""
        # Override this with any DWIM number action that is useful in a specific
        # context.
        #
        # This is defined here so the DFA graph doesn't have to be recompiled
        # every time there is a context switch between states with/without
        # opening number actions. This is particularly important in Emacs,
        # specifically popping up autocomplete boxes - ideally, a recompile
        # shouldn't be necessary when the autocomplete box pops up, even if
        # items can be selected by number.
        print("Got repeat {number} without prior command, ignoring.")
        app.notify(
            "Number DWIM", "No opening number actions available in this context."
        )

    def document_start() -> None:
        """Move cursor to the start of the document."""
        actions.key("ctrl-up")

    def document_end() -> None:
        """Move cursor to the end of the document."""
        actions.key("ctrl-down")

    def tab_right() -> None:
        """Move the current tab to the right in the tab order."""

    def tab_left() -> None:
        """Move the current tab to the left in the tab order."""

    def terminal_command(command: str) -> None:
        """Execute a terminal command."""
        p = subprocess.Popen(shlex.split(command), start_new_session=True)

    def quit_talon() -> None:
        """Exit Talon."""

    def restart_talon() -> None:
        """Restart Talon."""

    def quit_talon_with_sound() -> None:
        """Exit Talon, with a confirmation sound."""
        # TODO: Only play the sound if `actions.self.quit_talon` is implemented
        actions.user.play_cancel()
        # Let the sound play out
        actions.sleep("1s")
        actions.self.quit_talon()

    def restart_talon_with_sound() -> None:
        """Restart Talon, with a confirmation sound."""
        if actions.self.restart_talon:
            # TODO: Only play the sound if `actions.self.quit_talon` is implemented
            actions.user.play_ding()
            # Let the sound play out
            actions.sleep("1s")
            actions.self.restart_talon()

    def toggle_mic_off() -> None:
        """Toggle the active microphone on/off. Bind this to a keychord."""
        global _previous_mic

        active_mic = actions.sound.active_microphone()
        if active_mic == "None":
            mic = _previous_mic or "System Default"
            actions.sound.set_microphone(mic)
            _previous_mic = None
            new_mic = actions.sound.active_microphone()
            actions.app.notify(
                # Explicitly notify the user if system default was used. Square
                # brackets because mic names often have round parens in them
                f"System Default [{new_mic}]" if mic == "System Default" else new_mic,
                "Microphone Activated",
            )
        else:
            _previous_mic = active_mic
            actions.sound.set_microphone("None")
            actions.app.notify("Toggle again re-enable", "Microphone Disabled")

    def project_root() -> str:
        """Get the path to the root of the current project.

        The meaning of "project" depends on the program.

        """

    def debug(text: str):
        """Print and notify with a string."""
        LOGGER.info(text)
        app.notify("Talon Debug", text)

    def paste_insert(text: str):
        """Insert `text` by pasting it, rather than typing."""
        with clip.revert():
            clip.set_text(text)
            # While the clipboard will have updated, the underlying program may
            # not have synchronised to the new clipboard state (Jetbrains seems
            # to have this problem). Sleep to allow it to sync.
            actions.sleep("50ms")
            actions.edit.paste()
            # Also sleep after to ensure the paste doesn't happen after the
            # clipboard is reverted.
            actions.sleep("50ms")


# TODO: Dedicated settings file?
global_context = Context()
global_context.settings["imgui.dark_mode"] = 1
global_context.settings["imgui.scale"] = 1.8


@global_context.action_class("self")
class GlobalActions:
    pass


@global_context.action_class("app")
class AppActions:
    def path() -> str:
        raise NotImplementedError("`path` action not implemented in this context.")


windows_context = Context(name="unsorted_windows")
windows_context.matches = r"os: windows"
linux_context = Context(name="unsorted_linux")
linux_context.matches = r"os: linux"
mac_context = Context(name="unsorted_mac")
mac_context.matches = r"os: mac"
win_linux_context = Context(name="unsorted_win_linux")
win_linux_context.matches = r"""
os: linux
os: windows
"""


@windows_context.action_class("self")
class WindowsActions:
    def lock_screen():
        key("win-l")


# @linux_context.action_class("self")
# class LinuxActions:
#     def action():
#         pass


@win_linux_context.action_class("self")
class WinLinuxActions:
    def open_file() -> None:
        actions.key("ctrl-o")


@mac_context.action_class("self")
class MacActions:
    def open_file() -> None:
        actions.key("cmd-o")
