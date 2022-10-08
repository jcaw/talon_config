from talon import Context, actions
ctx = Context()
ctx.matches = r"""
tag: user.browser
"""

@ctx.action_class('edit')
class EditActions:
    def zoom_in():  actions.key('ctrl-plus')
    def zoom_out(): actions.key('ctrl-minus')

@ctx.action_class('user')
class UserActions:
    def go_back() -> None:    actions.key('alt-left')
    def go_forward() -> None: actions.key('alt-right')
