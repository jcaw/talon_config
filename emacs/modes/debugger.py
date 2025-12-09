from talon import Context, actions

context = Context()
context.matches = """
tag: user.emacs
user.emacs-major-mode: debugger-mode
"""


@context.action_class("user")
class UserActions:
    def on_pop():
        actions.user.emacs_command("debugger-step-through")
