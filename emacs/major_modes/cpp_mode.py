from talon import Context

from user.misc.chunked_phrase import chainable_formatters


context = Context()
context.matches = """
tag: user.emacs
user.emacs-major-mode: cpp-mode
"""
context.lists["user.chainable_formatters"] = {
    **chainable_formatters,
    # TODO: cpp formatters?
}
