from talon import Context, actions

context = Context()
context.matches = r"""
# TODO: Does the helm cancel bug occur on other OSes?
os: windows
tag: user.emacs
user.emacs-in-helm-prompt: True
"""


@context.action("self")
def cancel():
    # On Windows, regular keyboard interrupt has to be pressed twice for Helm to
    # recognize it and terminate. Emulating the keypress (within Emacs) fixes
    # the behavior.
    actions.user.emacs_command("jcaw-simulate-C-g")
