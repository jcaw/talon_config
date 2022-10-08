from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.emacs
user.emacs-minor-mode: ein:notebook-mode
"""

@ctx.action_class('edit')
class EditActions:
    def save(): actions.user.emacs_command('ein:notebook-save-notebook-command-km')
