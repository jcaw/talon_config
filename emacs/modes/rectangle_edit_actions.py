from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.emacs
emacs.emacs-minor-mode: rectangle-edit-mode
"""

@ctx.action_class('edit')
class EditActions:
    def cut():   actions.user.emacs_command('kill-rectangle')
    def copy():  actions.user.emacs_command('copy-rectangle-as-kill')
    def paste(): actions.user.emacs_command('yank-rectangle')
