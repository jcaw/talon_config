from talon import Context, Module, actions, clip

key = actions.key
insert = actions.insert
user = actions.user
sleep = actions.sleepb


module = Module()


@module.action_class
class Actions:
    def open_current_page_in_chrome():
        """Open the current web page in Google Chrome."""

    def browser_address_backup() -> str:
        """Backup action to get the current URL.

        This can be used in place of `broser.address` when implementing
        `browser.address` would cause Talon to start automatically calling
        invasive procedures.

        """
        actions.browser.focus_address()
        actions.edit.select_all()
        with clip.capture() as c:
            actions.edit.copy()
        url = c.text()
        if not isinstance(url, str):
            raise ValueError(
                f"`url` should be a string. Was: {type(url)}, value: {url}"
            )
        return url

    def switch_start_chrome():
        """Switch to Chrome if it's running, otherwise start it."""


ctx = Context()
ctx.matches = r"""
tag: user.browser
"""


@ctx.action_class("edit")
class EditActions:
    def zoom_in():
        actions.key("ctrl-plus")

    def zoom_out():
        actions.key("ctrl-minus")


@ctx.action_class("browser")
class BrowserActions:
    def go(url: str):
        actions.browser.focus_address()
        clip.set_text(url)
        actions.edit.paste()
        key("enter")


@ctx.action_class("user")
class UserActions:
    def go_back() -> None:
        key("alt-left")

    def go_forward() -> None:
        key("alt-right")

    def open_current_page_in_chrome():
        url = actions.user.browser_address_backup()
        print(f"URL: {url}")
        actions.self.switch_start_chrome()

        actions.browser.go(url)


windows_context = Context()
windows_context.matches = r"""os: windows"""


@windows_context.action_class("user")
class WindowsActions:
    def switch_start_chrome():
        try:
            user.switcher_focus("chrome.exe")
            switched = True
        except ValueError:
            # TODO: Launch from command line with url as pareameter?
            key("win")
            sleep("50ms")
            insert("chrome")
            sleep("100ms")
            key("enter")
            # Give it time to start up
            sleep("2000ms")
            switched = False

        if switched:
            actions.edit.new_tab()


i3_context = Context()
i3_context.matches = r"""tag: i3"""


@i3_context.action_class("user")
class i3Actions:
    def switch_start_chrome():
        try:
            user.switcher_focus("chrome")
            switched = True
        except ValueError:
            # TODO: Launch from command line with url as pareameter?
            key("super-d")
            sleep("50ms")
            insert("chrome")
            key("enter")
            # Give it time to start up
            sleep("2000ms")
            switched = False

        if switched:
            actions.edit.new_tab()
