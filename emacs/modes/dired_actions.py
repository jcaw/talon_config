from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.emacs
user.emacs-major-mode: dired-mode
"""

@ctx.action_class('user')
class UserActions:
    def rename() -> None: actions.user.emacs_dired_command('dired-do-rename', 0)
