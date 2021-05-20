from talon import Context

from user.misc.chunked_phrase import chainable_formatters


context = Context()
context.matches = """
tag: user.emacs
user.emacs-major-mode: emacs-lisp-mode
"""
context.lists["user.chainable_formatters"] = {
    **chainable_formatters,
    "private": "elisp_private",
    "funk": "lisp_function_call",
    # NOTE: Private functions must be called with "private func" to get the
    #   right behavior - not "func private"
    "key": "lisp_keyword_arg",
    "sim": "elisp_doc_symbol",
}
