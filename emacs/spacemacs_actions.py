from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.emacs
user.emacs-is-spacemacs: True
"""

@ctx.action_class('user')
class UserActions:
    ## Navigation
    def emacs_find_definition(): actions.user.emacs_command('spacemacs/jump-to-definition')
    # TODO: Pop mesages
    
    def emacs_restart() -> None: actions.user.emacs_command('spacemacs/restart-emacs-resume-layouts')
    def emacs_exit():            actions.user.emacs_command('spacemacs/prompt-kill-emacs')
