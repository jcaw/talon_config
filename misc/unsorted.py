"""Behaviours, captures & actions that aren't in a dedicated module yet."""

from talon import Module, Context, actions, imgui, app
from typing import Optional, List
from pathlib import Path
import os
import shlex
import subprocess
import webbrowser


# Max number of most recent speech recordings to display
MAX_PRIOR_RECORDINGS = 5
MISRECOGNITIONS_SUBFOLDER = "possible_misrecognitions"


module = Module()


def recording_words(speech_file) -> List[str]:
    """Get the words held in `speech_file`."""
    return " ".join(speech_file.name.split("-")[:-1])


def most_recent_speech_recordings(n_files: int) -> List:
    """Get the most recent speech recording files."""
    files = list(actions.user.path_talon_recordings().glob("*.flac"))
    # Sort by modification time - most recently modified first
    #
    # TODO: use `f.stat().st_mtime`? Does os.path.getmtime get less info (so
    #   maybe faster?) Probably limited by iops/seek anyway
    files.sort(key=lambda f: os.path.getmtime(str(f)), reverse=True)
    return files[:n_files]


def last_speech_recording() -> str:
    """Get the path to the last speech recording as a string."""
    return str(most_recent_speech_recordings(1)[0])


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

    def path_talon_recordings() -> Path:
        """Path to Talon speech clip recordings."""
        return Path(actions.path.talon_home()) / "recordings"

    def quarantine_speech_recording(file_number: Optional[int] = 1) -> None:
        """Move a specific speech recording to the potential misrecognitions folder."""
        files = most_recent_speech_recordings(file_number)
        if files:
            flac = files[file_number - 1]
            misrecognition_folder = flac.parent / MISRECOGNITIONS_SUBFOLDER
            misrecognition_folder.mkdir(exist_ok=True)
            flac.rename(misrecognition_folder / flac.name)
            # Also delete word alignment file
            alignment = flac.with_suffix(".txt")
            if alignment.is_file():
                alignment.rename(misrecognition_folder / alignment.name)

            app.notify("Moved Recording", f'"{recording_words(flac)}"')

    def delete_last_speech_recording(n_files: Optional[int] = 1) -> None:
        """Delete the last n speech recordings."""
        # Add 1 because "prior" will add one to the index of those displayed in
        # the notification
        max_deleted = MAX_PRIOR_RECORDINGS + 1
        if n_files > max_deleted:
            app.notify(
                "Talon Warning",
                f"Truncating deleted noise files - only removing {max_deleted}.",
            )
            n_files = max_deleted

        files = most_recent_speech_recordings(n_files)

        files_deleted = []
        for f in files:
            # files_deleted.append(f.name)
            files_deleted.append(recording_words(f))
            f.unlink()
            # Also delete word alignment file
            alignment = f.with_suffix(".txt")
            if alignment.is_file():
                alignment.unlink()
        if len(files_deleted) > 0:
            app.notify("Deleted Recordings", f"{files_deleted}")

    def show_last_speech_recordings(
        n_recordings: Optional[int] = MAX_PRIOR_RECORDINGS,
    ) -> None:
        """Notify with the most recent `n_recordings` speech recordings."""
        # TODO: Show a list of loads of the previous recordings, in a window.

        app.notify(
            f"{n_recordings} Newest Recordings",
            ", ".join(
                [
                    f"{recording_words(s)} ({i+2})"
                    for i, s in enumerate(most_recent_speech_recordings(n_recordings))
                ]
            ),
        )

    def play_last_speech_recording():
        """Play the last speech recording using the `webbrowser` default."""
        webbrowser.open(last_speech_recording())

    def audacity_last_speech_recording() -> None:
        """Open the last speech recording. Use to check mic setup."""
        # TODO: Switch to the proper method for launching subprocesses from
        #   Talon
        subprocess.Popen(["audacity", last_speech_recording()])

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
        print(active_mic)
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


global_context = Context()
global_context.settings["imgui.dark_mode"] = 1


@global_context.action_class("self")
class GlobalActions:
    pass


windows_context = Context(name="unsorted_windows")
windows_context.matches = r"""
os: windows
"""


@windows_context.action_class("self")
class WindowsActions:
    def lock_screen():
        key("win-l")


linux_context = Context(name="unsorted_linux")
linux_context.matches = r"""
os: linux
"""


# @linux_context.action_class("self")
# class LinuxActions:
#     def action():
#         pass


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
