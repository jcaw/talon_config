from talon import Context, actions

ctx = Context()
ctx.matches = r"""
tag: user.emacs
user.emacs-minor-modes: isearch-mode
"""


@ctx.action_class("user")
class UserActions:
    # TODO: Don't just go forwards, repeat prior
    def on_pop():
        actions.user.emacs_isearch_forward()

    def on_hiss(active: bool):
        if active:
            actions.user.emacs_isearch_backward()

    def cancel() -> None:
        actions.user.emacs_command("isearch-cancel")
