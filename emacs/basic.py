from typing import Optional

from talon import Context, Module, actions, ui
from talon_init import TALON_USER

from user.emacs.utils import rpc

key = actions.key
insert = actions.insert
user = actions.user
emacs_command = actions.user.emacs_command
emacs_fallbacks = actions.user.emacs_fallbacks


module = Module()


@module.action_class
class Actions:
    def select_number(number: int):
        """Select item ``number``. Meaning of \"select\" depends on context."""

    def open_in_emacs(path: Optional[str] = None) -> None:
        """Open `path` in Emacs. Required Emacs to initialize as a server.

        Note this requires Emacs to already be open.

        """
        # TODO: Start Emacs if it's not already running.
        rpc.call("x-focus-frame", [None])
        if path:
            # FIXME: Porthole can't handle unencodable return values
            rpc.call("voicemacs-find-file", [path])

    def emacs_search_directory(text: Optional[str] = None) -> None:
        """Search for some `text` in the current project."""
        emacs_fallbacks(
            ["spacemacs/helm-dir-smart-do-search", "helm-do-grep-ag", "grep",]
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
        user.emacs_command("projectile-find-file")
        insert(text)


context = Context()
context.matches = """
app: /emacs/
"""


@context.action_class("edit")
class EditActions:
    def copy():
        emacs_fallbacks(["kill-ring-save"], keypress="alt-w")

    def cut():
        emacs_fallbacks(["kill-region"], keypress="shift-delete")

    def paste():
        emacs_fallbacks(["yank"], keypress="ctrl-y")

    def undo():
        emacs_fallbacks(["undo-tree-undo"], keypress="ctrl-/")

    def redo():
        emacs_fallbacks(["undo-tree-redo"], keypress="ctrl-shift-/")


@context.action_class("user")
class UserActions:
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
