from talon import Module, actions, clip

module = Module()


# TODO: Spritzlet changed their subscription model. Can't use it any more
@module.action
def spritzlet() -> None:
    """Speed-read the current page with Spritzlet. WARNING: Loads external JS.

    Requires the spritzlet bookmark to be accessible with the keyword
    "spritzlet". This is possible on Firefox and Chrome - I haven't tested on
    other browsers.

    """
    actions.browser.focus_address()
    # This requires the word "spritzlet" to be a keyword bookmark. Easy in
    # Firefox - in Chrome, just add it as a search engine with no "%s"
    # parameter.
    insert("spritzlet")
    actions.key("enter")
    actions.browser.focus_address()
    # Restore original URL in bar
    actions.edit.undo()
    actions.edit.undo()
    actions.browser.focus_page()
