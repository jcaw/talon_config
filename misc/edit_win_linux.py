"""Default edit actions for Windows & Linux"""


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

    def file_end():
        key("ctrl-end")

    def file_start():
        key("ctrl-start")

    def find(text: str = None):
        key("ctrl-f")
        actions.sleep("500ms")
        if text:
            actions.insert(text)

    def paragraph_end():
        key("ctrl-down")

    def paragraph_start():
        key("ctrl-up")

    def paste():
        key("ctrl-v")

    def print():
        key("ctrl-p")

    def save():
        key("ctrl-s")

    def save_all():
        key("ctrl-shift-s")

    def select_all():
        key("ctrl-a")

    def word_left():
        key("ctrl-left")

    def word_right():
        key("ctrl-right")

    def undo():
        key("ctrl-z")

    def redo():
        # TODO: Lots of apps use ctrl-shift-z.
        key("ctrl-y")
