from talon import Module, Context, actions, imgui, app, speech_system, noise
from typing import Optional, List
from pathlib import Path
import os
import threading
import webbrowser
import subprocess


# Max number of most recent speech recordings to delete
MAX_DELETED_RECORDINGS = 10
MISRECOGNITIONS_SUBFOLDER = "possible_misrecognitions"


def recording_words(speech_file) -> List[str]:
    """Get the words held in `speech_file`."""
    return " ".join(speech_file.name.split("-")[:-1])


def most_recent_speech_recordings(n_files: int) -> List:
    """Get the most recent speech recording files."""
    base_path = actions.user.path_talon_recordings()
    files = [
        *base_path.glob("*.flac"),
        # Also include misrecognitions, so they can still be nuked if they were
        # quarantined by accident.
        *(base_path / MISRECOGNITIONS_SUBFOLDER).glob("*.flac"),
    ]
    # Sort by modification time - most recently modified first
    #
    # TODO: use `f.stat().st_mtime`? Does os.path.getmtime get less info (so
    #   maybe faster?) Probably limited by iops/seek anyway
    files.sort(key=lambda f: os.path.getmtime(str(f)), reverse=True)
    return files[:n_files]


def nth_speech_recording(n) -> str:
    """Get the path to the speech recording numbered by `n`, as a string."""
    assert n >= 1, n
    return str(most_recent_speech_recordings(n)[n - 1])


def is_misrecognition(recording):
    """Is file `recording` in the misrecognitions folder?"""
    return recording.parent.name == MISRECOGNITIONS_SUBFOLDER


module = Module()


@module.action_class
class Actions:
    def path_talon_recordings() -> Path:
        """Path to Talon speech clip recordings."""
        return Path(actions.path.talon_home()) / "recordings"

    def quarantine_speech_recording(file_number: Optional[int] = 1) -> None:
        """Move a specific speech recording to the potential misrecognitions folder."""
        files = most_recent_speech_recordings(file_number)
        if files:
            flac = files[file_number - 1]
            alignment = flac.with_suffix(".txt")
            if is_misrecognition(flac):
                # Delete
                flac.unlink()
                if alignment.is_file():
                    alignment.unlink()
                app.notify("Deleted Recording", f'"{recording_words(flac)}"')
            else:
                misrecognition_folder = flac.parent / MISRECOGNITIONS_SUBFOLDER
                misrecognition_folder.mkdir(exist_ok=True)
                flac.rename(misrecognition_folder / flac.name)
                # Also delete word alignment file
                if alignment.is_file():
                    alignment.rename(misrecognition_folder / alignment.name)

                app.notify("Moved Recording", f'"{recording_words(flac)}"')

    def delete_last_speech_recording(n_files: Optional[int] = 1) -> None:
        """Delete the last n speech recordings."""
        # Add 1 because "prior" will add one to the index of those displayed in
        # the notification
        max_deleted = MAX_DELETED_RECORDINGS + 1
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

    # TODO: Probably remove - just use the imgui approach
    # def show_last_speech_recordings(
    #     n_recordings: Optional[int] = MAX_DELETED_RECORDINGS,
    # ) -> None:
    #     """Notify with the most recent `n_recordings` speech recordings."""
    #     # TODO: Show a list of loads of the previous recordings, in a window.

    #     app.notify(
    #         f"{n_recordings} Newest Recordings",
    #         ", ".join(
    #             [
    #                 f"{recording_words(s)} ({i+2})"
    #                 for i, s in enumerate(most_recent_speech_recordings(n_recordings))
    #             ]
    #         ),
    #     )

    # TODO: Specify by index
    def play_last_speech_recording(n: int = 1):
        """Play the last speech recording using the `webbrowser` default."""
        webbrowser.open(nth_speech_recording(n))

    def audacity_last_speech_recording(n: int = 1) -> None:
        """Open the last speech recording. Use to check mic setup."""
        # TODO: Switch to the proper method for launching subprocesses from
        #   Talon
        subprocess.Popen(["audacity", nth_speech_recording(n)])


# Command history
#############################################################################

history_n_items = module.setting(
    "command_history_items",
    int,
    desc="Number of items to display in the command history window.",
    default=30,
)


module.tag("command_history_showing", "Active when the command history is showing")
global_context = Context()


_history = []
_history_lock = threading.Lock()


# TODO: dynamic rect?
@imgui.open()
def history_gui(gui: imgui.GUI):
    # print(dir(gui))
    with _history_lock:
        if _history:
            for item in _history:
                gui.text(item)
        else:
            gui.text("< Listening... >")


# The command history is always hidden on the next utterance.
#
# In order to include the latest command in the history, the command history is
# re-shown at the end of every phrase. However, we also wait until the end of
# command parsing to even show the history, so it isn't hidden prematurely.
_command_history_flag = False
_history_showing = False


def _reset_show_flag(*args):
    global _command_history_flag
    _command_history_flag = False


def _hide_history(*args):
    if history_gui.showing:
        history_gui.hide()
        global_context.tags = []


def _push_history_state(*args):
    global _command_history_flag, _history_showing, _history
    if _command_history_flag:
        # imgui calls the render function every frame, but only updates when the
        # state changes, so precalculate data here to alleviate pressure.
        with _history_lock:
            _history = []
            for i, recording in enumerate(
                most_recent_speech_recordings(history_n_items.get())
            ):
                # Label prefixed commands with "[M]"
                prefix = "[M] " if is_misrecognition(recording) else "-     "
                # Add 1 so deletion commands can index correctly
                _history.append(f"{prefix}{i+1}: {recording_words(recording)}")
        if not history_gui.showing:
            # history_gui.unfreeze()
            history_gui.show()
            history_gui.freeze()
            global_context.tags = ["user.command_history_showing"]
    else:
        _hide_history()
    _command_history_flag = False


speech_system.register("pre:phrase", _reset_show_flag)
speech_system.register("post:phrase", _push_history_state)
# Hide on any noise too
noise.register("pre:pop", _hide_history)
noise.register("pre:hiss", _hide_history)


history_module = Module()


@history_module.action_class
class HistoryActions:
    def command_history_show():
        """Show the command_history."""
        global _command_history_flag
        _command_history_flag = True

    def command_history_hide():
        """Hide the command history."""
        global _command_history_flag
        _command_history_flag = False
        _hide_history()

    def command_history_set_size(n: int):
        """Set number of items displayed in the command history."""
        context.settings["user.command_history_items"] = n
