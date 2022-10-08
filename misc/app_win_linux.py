from talon import Context, actions
ctx = Context()
ctx.matches = r"""
os: windows
os: linux
"""

@ctx.action_class('app')
class AppActions:
    def window_open(): actions.key('ctrl-n')
