"""Default browser settings for Windows and Linux.

Written for Firefox. Some of these will need to be overridden in specific
browsers.

NOTE: These are UNTESTED on Linux. Some are definitely wrong.

TODO: Audit on Linux

"""

import time

from talon import Context, actions

key = actions.key
user = actions.user
browser = actions.browser


context = Context()
context.matches = r"""
os: windows
os: linux

app: /firefox/
app: /chrome/
# NOTE: Doesn't work properly with Internet Explorer. Will need its own module.
app: /iexplore/
app: /opera/

# TODO: Compatibility with Edge?
# title: /- Microsoft Edge/
"""
context.tags = ["browser"]


@context.action_class("app")
class AppActions:
    def tab_close():
        key("ctrl-w")
        # Can't kill tabs too quickly in firefox, or it will drop inputs.
        time.sleep(0.3)

    def tab_next():
        key("ctrl-tab")

    def tab_previous():
        key("ctrl-shift-tab")

    def tab_open():
        key("ctrl-t")

    def tab_reopen():
        key("ctrl-shift-t")


@context.action_class("edit")
class EditActions:
    def find(text: str = None):
        key("ctrl-f")
        if text:
            actions.insert(text)


@context.action_class("user")
class UserActions:
    def search() -> None:
        browser.focus_search()

    def search_text(text: str) -> None:
        user.search()
        time.sleep(0.2)
        actions.insert(text)
        key("enter")


@context.action_class("browser")
class BrowserActions:
    # TODO: Talon seems to register a pre:phrase hook that triggers this
    #   action. This causes the bar to focus before each phrase, so remove for
    #   now. Probably have to use APIs or extensions (or maybe accessibility
    #   interfaces)
    #
    # def address():
    #     actions.browser.focus_address()
    #     time.sleep(0.1)
    #     actions.edit.copy()
    #     actions.browser.focus_page()

    def bookmark():
        key("ctrl-d")

    def bookmark_tabs():
        key("ctrl-shift-d")

    # TODO: Individual implementations
    # def bookmarks():
    #     key("")

    def bookmarks_bar():
        key("ctrl-b")

    def focus_address():
        key("ctrl-l")

    def focus_page():
        # TODO: Firefox only?
        key("shift-f6")

    def focus_search():
        key("ctrl-e")

    # def go():
    #     raise NotImplementedError()

    def go_back():
        key("alt-left")

    def go_forward():
        key("alt-right")

    # def go_blank():
    #     raise NotImplementedError()

    def go_home():
        key("alt-home")

    def open_private_window():
        key("ctrl-shift-p")

    def reload():
        key("f5")

    # def reload_hard():
    #     raise NotImplemetedError()

    def reload_hardest():
        key("ctrl-f5")

    def show_clear_cache():
        key("ctrl-shift-delete")

    def show_downloads():
        # TODO: Different on Linux
        key("ctrl-j")

    # def show_extensions():
    #     raise NotImplementedError()

    def show_history():
        key("ctrl-h")

    # def submit_form():
    #     raise NotImplementedError()

    # def title():
    #     raise NotImplementedError()

    def toggle_dev_tools():
        key("f12")
