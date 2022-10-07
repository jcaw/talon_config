from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.emacs
"""

@ctx.action_class('edit')
class EditActions:
    def select_line(n: int=None): actions.user.emacs_command('it-mark-line')
