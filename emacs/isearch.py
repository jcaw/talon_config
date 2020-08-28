# TODO: Probably delete this file

from talon import Module, Context, actions

key = actions.key


module = Module()


@module.action_class
class Actions:
    # TODO: regex isearch?

    # TODO: Repeat last search, whatever that was?

    def emacs_isearch_forward():
        """Isearch forward - start or repeat."""
        key("ctrl-s")

    def emacs_isearch_backward():
        """Isearch backward - start or repeat."""
        key("ctrl-r")
