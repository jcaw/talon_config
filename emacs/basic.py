from typing import Optional

from talon import Context, Module, actions, ui
from talon_init import TALON_USER

from user.emacs.utils.voicemacs import rpc_call

key = actions.key
insert = actions.insert
user = actions.user
emacs_command = actions.user.emacs_command
emacs_prefix_command = actions.user.emacs_prefix_command
emacs_fallbacks = actions.user.emacs_fallbacks


module = Module()
module.tag("emacs", "Active when Emacs focused.")
module.tag("voicemacs", "Active when Emacs focused & Voicemacs is connected.")


@module.action_class
class Actions:
    # TODO: Extract from emacs module
    def select_number(number: int):
        """Select item ``number``. Meaning of \"select\" depends on context."""

    def open_in_emacs(path: Optional[str] = None) -> None:
        """Open `path` in Emacs. Required Emacs to initialize as a server.

        Note this requires Emacs to already be open.

        """
        # TODO: Start Emacs if it's not already running.
        user.open_emacs()
        # TODO: Still need this?
        # rpc_call("x-focus-frame", [None])
        print(rpc_call("voicemacs-find-file", [path]))

    def open_current_file_in_emacs():
        """Open the currently focussed file in Emacs."""
        path = actions.app.path()
        print(f"Path: {path}")
        user.open_in_emacs(path)

    def open_current_project_in_emacs():
        """Open the root folder of the currently active project in Emacs."""
        user.open_in_emacs(user.project_root())

    def send_to_magit_in_emacs():
        """Open the current git repo in magit, even if outside Emacs."""
        try:
            path = user.project_root()
        # TODO: Specific exception
        except:
            # Fall back to path, because it will probably more commonly be defined
            path = None
        if not path:
            path = actions.app.path()
        if not path:
            RuntimeError("No path found.")
        user.open_in_emacs(path)
        user.emacs_command("magit-status")

    def emacs_search_directory(text: Optional[str] = None) -> None:
        """Search for some `text` in the current directory."""
        emacs_fallbacks(
            [
                "spacemacs/helm-dir-smart-do-search",
                "+default/search-cwd",
                "helm-do-grep-ag",
                "grep",
            ]
        )
        if text:
            insert(text)

    def emacs_open_talon_user() -> None:
        """Open the Talon user directory in Emacs."""
        user.open_in_emacs(str(TALON_USER))

    def emacs_search_talon_user(text: Optional[str] = None) -> None:
        """Open Emacs & search the Talon user dir for `text`."""
        user.emacs_open_talon_user()
        # TODO: Proper lowercase formatting
        user.emacs_search_directory(text.lower() if text else text)

    def emacs_find_file_talon_user(text: Optional[str] = None) -> None:
        """Open Emacs & find a file in Talon user w/ name matching `text`."""
        user.emacs_open_talon_user()
        emacs_command("projectile-find-file")
        insert(text)

    def emacs_open_custom_words() -> None:
        """Open the custom words file in Emacs."""
        from user.misc.text import CUSTOM_WORDS_PATH

        user.open_in_emacs(CUSTOM_WORDS_PATH)
        emacs_command("end-of-buffer")
        emacs_command("sp-skip-backward-to-symbol")
        key("enter")

    def emacs_switch_buffer() -> None:
        """Switch the current buffer."""
        emacs_fallbacks(
            [
                # Spacemacs
                "spacemacs-layouts/non-restricted-buffer-list-helm",
                # Doom
                "+helm/workspace-mini",
                "switch-buffer",
            ]
        )

    def emacs_switch_theme() -> None:
        """Open the themes menu."""
        emacs_fallbacks(
            [
                "spacemacs/helm-themes",
                "load-theme",
            ]
        )

    def emacs_restart() -> None:
        """Restart Emacs. The implementation may restore the workspace."""
        emacs_command("restart-emacs")

    def emacs_quit() -> None:
        """Exit Emacs."""
        emacs_command("save-buffers-kill-emacs")

    def emacs_pop_mark(times: int = 1) -> None:
        """Pop the mark. Provide `times` to pop multiple."""
        for i in range(times):
            emacs_prefix_command("set-mark-command")

    def emacs_toggle_fold():
        """Toggle visibility folding for the current item."""

    def emacs_fold():
        """Fold (hide) the current item."""

    def emacs_unfold():
        """Unfold (show) the current item."""

    def emacs_fold_all():
        """Fold "all" items (meaning depends on context)."""

    def emacs_unfold_all():
        """Unfold all items in the document."""

    def emacs_next_fold():
        """Navigate to the next fold."""

    def emacs_previous_fold():
        """Navigate to the previous fold."""


context = Context()
context.matches = """
# Match like this for most instances
# TODO: This is depracated? Is it the case sensitivity?
# app: /Emacs/
app: /emacs/
# HACK: Circumvent tags losing priority
os: windows
os: linux
os: mac

# Use this for Cygwin X on Windows, displaying WSL Emacs
app: /XWin/
and title: /^emacs@/
and os: windows

# VC X Server on Windows, displaying WSL Emacs. Note this title will only work for Doom Emacs.
app: /vcxsrv/
and title: /Emacs$/
and os: windows
# Win 11 Version
app: /vcxsrv/
and title: /Emacs@/
and os: windows

# Native WSL Gui, displaying WSL Emacs
app: msrdc
and title: /Emacs/
and os: windows
"""
context.tags = ["user.emacs"]


voicemacs_context = Context()
voicemacs_context.matches = """
tag: user.emacs
user.emacs-voicemacs: True

# HACK: Circumvent tags losing priority
os: windows
os: linux
os: mac
"""
voicemacs_context.tags = ["user.voicemacs"]


@voicemacs_context.action_class("main")
class BaseActions:
    pass

    # def insert(text: str):
    #     """Insert directly into Emacs via RPC.+"""
    #     rpc_call("voicemacs-insert", [text])


@context.action_class("edit")
class EditActions:
    def copy():
        emacs_fallbacks(["kill-ring-save"], keypress="alt-w")

    def cut():
        emacs_fallbacks(["kill-region"], keypress="shift-delete")

    def paste():
        emacs_fallbacks(["yank"], keypress="ctrl-y")

    def undo():
        emacs_fallbacks(["undo-tree-undo", "undo-fu-only-undo"], keypress="ctrl-/")

    def redo():
        emacs_fallbacks(
            ["undo-tree-redo", "undo-fu-only-redo"], keypress="ctrl-shift-/"
        )

    def select_all():
        actions.user.emacs_command("mark-whole-buffer")

    # TODO: Generic Unsorted
    #
    # TODO: Fallbacks
    def zoom_in():
        actions.user.emacs_command("voicemacs-increase-text")

    def zoom_out():
        actions.user.emacs_command("voicemacs-decrease-text")

    def save():
        actions.user.emacs_command("save-buffer")

    # TODO: save as
    # def save_as():  actions.user.emacs_command('TODO')
    # FIXME: Doesn't work, "wrong type argument, listp". RPC problem?
    # def save_all(): actions.user.emacs_command("save-some-buffers")
    # Fall back to keypress for now. Should work everywhere anyway, who rebinds
    # this?
    def save_all():
        actions.key("ctrl-x s")

    def undo():
        actions.user.emacs_command("undo-fu-only-undo")

    def redo():
        actions.user.emacs_command("undo-fu-only-redo")


@context.action_class("user")
class UserActions:
    # Fundamental Commands

    # "c-g" is the interrupt command. It's hardcoded in C - can't remap it.
    def cancel() -> None:
        actions.key("ctrl-g")

    def toggle_comment() -> None:
        actions.user.emacs_command("spacemacs/comment-or-uncomment-lines")

    def open_file() -> None:
        emacs_fallbacks(
            ["helm-projectile-find-file", "projectile-find-file"],
            keypress="ctrl-x ctrl-f",
        )

    def next_error() -> None:
        emacs_fallbacks(["spacemacs/next-error", "flycheck-next-error", "next-error"])

    def previous_error() -> None:
        emacs_fallbacks(
            ["spacemacs/previous-error", "flycheck-previous-error", "previous-error"]
        )

    def search(text: str = None) -> None:
        emacs_fallbacks(
            [
                # Spacemacs
                "spacemacs/helm-project-smart-do-search",
                # Doom
                "+default/search-project",
            ]
        )
        if text:
            insert(text.lower())

    def toggle_comment_lines(num_lines: int) -> None:
        emacs_prefix_command("it-mark-forward-line", num_lines)
        user.toggle_comment()
        # TODO: This nicer or worse?
        user.emacs_pop_mark()

    def document_start() -> None:
        user.emacs_command("beginning-of-buffer")

    def document_end() -> None:
        user.emacs_command("end-of-buffer")

    def tiling_split_horizontal() -> None:
        # I have this method duplicated in my custom config so it should always
        # exist.
        user.emacs_command("spacemacs/split-window-horizontally-and-switch")

    def tiling_split_vertical() -> None:
        # I have this method duplicated in my custom config so it should always
        # exist.
        user.emacs_command("spacemacs/split-window-vertically-and-switch")
