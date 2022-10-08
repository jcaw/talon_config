from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.emacs
user.emacs-defining-macro: True
"""

@ctx.action_class('edit')
class EditActions:
    # Can't use helm-swoop during a macro, so revert to isearch.
    def find(text: str=None): actions.user.emacs_isearch_forward()
