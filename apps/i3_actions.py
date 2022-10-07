from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.i3
"""

@ctx.action_class('user')
class UserActions:
    def toggle_fullscreen() -> None: actions.key('f11')
    def lock_screen() -> None:       actions.key('super-x')

@ctx.action_class('app')
class AppActions:
    def window_close(): actions.key('super-shift-q')
