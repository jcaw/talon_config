from talon import Context, actions

key = actions.key


context = Context()
context.matches = r"""
os: windows
os: linux
"""


@context.action_class("edit")
class BuiltInActions:
    def copy():
        key("ctrl-c")

    def cut():
        key("ctrl-x")

    def paste():
        key("ctrl-v")

    def undo():
        key("ctrl-z")

    def redo():
        # TODO: Lots of apps use ctrl-shift-z.
        key("ctrl-y")

    def page_up():
        key("pageup")

    def page_down():
        key("pagedown")
