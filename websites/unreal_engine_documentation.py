import re

from talon import Module, actions, clip


CURRENT_UNREAL_VERSION = "5.1"


module = Module()


@module.action_class
class Actions:
    def unreal_docs_switch_to_current_version() -> None:
        """Switch the doc page to the current Unreal Engine version.

        Useful when Google is returning old versions of the docs. Current engine
        version is a constant specified in this action's Python file.

        Note the docs page may not exist for newer engine versions, in which
        case this will 404.

        """
        # Get the URL
        # HACK: Not implemented at time of writing - instead do it manually.
        # url = actions.browser.address()
        actions.browser.focus_address()
        actions.edit.select_all()
        with clip.capture() as c:
            actions.edit.copy()
        url = c.text()

        # regex for official unreal docs (for the URL). Do the docs follow the
        # normal URL format?
        docs_regex = r"docs\.unrealengine\.com\/([0-9]+[.][0-9]+)\/"
        if re.search(docs_regex, url):
            # Replace the old version (e.g. "4.27") in the URL with the current
            # version (e.g. "5.1")
            current_url = re.sub("[0-9]+[.][0-9]+", CURRENT_UNREAL_VERSION, url)

            # Navigate to the newer version of the URL
            # HACK: Not implemented at time of writing - instead do it manually.
            # actions.browser.go(current_url)
            clip.set_text(current_url)
            actions.edit.paste()
            actions.key("enter")
