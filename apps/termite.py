from talon import Context, actions

ctx = Context()
ctx.matches = r"""
app: termite
"""
ctx.tags = ["user.terminal"]


@ctx.action_class("edit")
class EditActions:
    def copy():
        actions.key("ctrl-shift-c")

    def paste():
        actions.key("ctrl-shift-v")
