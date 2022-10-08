from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.emacs
# HACK: Tag extraction like this doesn't override OS based stuff, so manually
#   specify it.
os: windows
os: linux
os: mac
"""

@ctx.action_class('user')
class UserActions:
    # Fundamental Commands
    
    # "c-g" is the interrupt command. It's hardcoded in C - can't remap it.
    def cancel() -> None:         actions.key('ctrl-g')
    def toggle_comment() -> None: actions.user.emacs_command('spacemacs/comment-or-uncomment-lines')

@ctx.action_class('edit')
class EditActions:
    def select_all():
        actions.user.emacs_command('mark-whole-buffer')
    # TODO: Generic Unsorted
    #
    # TODO: Fallbacks
    def zoom_in():  actions.user.emacs_command('voicemacs-increase-text')
    def zoom_out(): actions.user.emacs_command('voicemacs-decrease-text')
    def save():     actions.user.emacs_command('save-buffer')
    # TODO: save as
    # def save_as():  actions.user.emacs_command('TODO')
    # FIXME: Doesn't work, "wrong type argument, listp". RPC problem?
    # def save_all(): actions.user.emacs_command("save-some-buffers")
    # Fall back to keypress for now. Should work everywhere anyway, who rebinds
    # this?
    def save_all(): actions.key('ctrl-x s')
    def undo():     actions.user.emacs_command('undo-fu-only-undo')
    def redo():     actions.user.emacs_command('undo-fu-only-redo')
