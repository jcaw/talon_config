from talon import Context

from user.misc.chunked_phrase import chainable_formatters


context = Context()
context.matches = """
tag: user.emacs
user.emacs-major-mode: python-mode
"""
context.lists["user.chainable_formatters"] = {
    **chainable_formatters,
    "private": "python_private",
    "dot": "dot_prefix_snake",
    "lub": "rparen_prefix_snake",
}
