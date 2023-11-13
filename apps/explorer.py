from talon import Context, actions, clip


context = Context()
context.matches = r"""
os: windows
app: /explorer/
"""


@context.action_class("app")
class AppActions:
    def path() -> str:
        actions.key("ctrl-l")
        with clip.capture() as c:
            actions.edit.copy()
        actions.key("escape")
        return c.text()


@context.action_class("user")
class UserActions:
    def project_root() -> str:
        return actions.app.path()
