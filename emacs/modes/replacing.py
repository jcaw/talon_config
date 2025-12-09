from talon import Context, actions

ctx = Context()
ctx.matches = r"""
# Active during a find/replace session

tag: user.emacs
# This covers projectile-replace too.
user.emacs-current-message: /Query replacing /
# erefactor
user.emacs-current-message: /Rename? (y or n)/
"""


@ctx.action_class("user")
class UserActions:
    # Pop to replace, hiss to skip
    def on_pop():
        actions.key("y")

    def on_hiss(active: bool):
        if active:
            actions.key("n")
