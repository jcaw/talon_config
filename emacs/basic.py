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
        rpc_call("x-focus-frame", [None])
        if path:
            # FIXME: Porthole can't handle unencodable return values
            rpc_call("voicemacs-find-file", [path])

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


context = Context()
context.matches = """
tag: user.emacs

# HACK: Circumvent tags losing priority
os: windows
os: linux
os: mac
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
