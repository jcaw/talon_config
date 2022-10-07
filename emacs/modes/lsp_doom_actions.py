from talon import Context, actions
ctx = Context()
ctx.matches = r"""
# Generic actions powered by LSP
tag: user.emacs
user.emacs-minor-mode: lsp-mode
# Doom overrides with its own behaviour
not user.emacs-is-doom: True
# TODO: Spacemacs may override with its own behaviour, maybe check at some point
# not user.emacs-is-spacemacs: True
"""

@ctx.action_class('user')
class UserActions:
    def find_definition() -> None:      actions.user.emacs_command('lsp-find-definition')
    def find_references() -> None:      actions.user.emacs_command('lsp-find-references')
    def find_implementations() -> None: actions.user.emacs_command('lsp-find-implementation')
    def show_documentation() -> None:   actions.user.emacs_command('lsp-describe-thing-at-point')
