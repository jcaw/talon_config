from talon import Module, Context, actions

key = actions.key


module = Module()
module.tag("terminal", "Active in terminal emulators, Windows Terminal, etc.")


context = Context()
# HACK: Make "tag" override with more priority by including an extra specifier, "os".
context.matches = r"""
os: windows
os: linux
os: mac
tag: user.terminal
"""


@context.action_class("user")
class UserActions:
    def cancel():
        key("ctrl-c")
