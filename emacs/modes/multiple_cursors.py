from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.emacs
user.emacs-minor-mode: multiple-cursors-mode
"""

@ctx.action_class('user')
class UserActions:
    # TODO: Repeat previous extension?
    def on_pop(): actions.user.emacs_command('mc/mark-next-like-this')
