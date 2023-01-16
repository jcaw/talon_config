from talon import Context, actions

from user.misc.chunked_phrase import chainable_formatters


context = Context()
context.matches = """
tag: user.emacs
user.emacs-major-mode: emacs-lisp-mode
user.emacs-major-mode: lisp-interaction-mode
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


@context.action_class("self")
class EmacsLispActions:
    def rename():
        actions.self.emacs_command("erefactor-rename-symbol-in-buffer")
