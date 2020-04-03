from talon import Context, Module, actions

key = actions.key
user = actions.user
emacs_command = actions.user.emacs_command
emacs_fallbacks = actions.user.emacs_fallbacks


module = Module()


@module.action_class
class Actions:
    def select_number(number: int):
        """Select item ``number``. Meaning of \"select\" depends on context."""

    def next_error() -> None:
        """Go to the next error."""
        emacs_fallbacks(["spacemacs/next-error", "flycheck-next-error", "next-error"])

    def previous_error() -> None:
        """Go to the previous error."""
        emacs_fallbacks(
            ["spacemacs/previous-error", "flycheck-previous-error", "previous-error"]
        )


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
