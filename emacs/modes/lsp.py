from typing import Optional, List

from talon import Context, actions


context = Context()
context.matches = r"""
tag: user.emacs
user.emacs-minor-mode: lsp-mode
"""


@context.action_class("self")
class LSPActions:
    def rename() -> None:
        actions.self.emacs_command("lsp-rename")

    def rename_with_phrase(chunked_phrase: Optional[List] = None) -> None:
        actions.self.emacs_command("lsp-rename")
        if chunked_phrase:
            # It will have a default value, need to clear that.
            actions.self.emacs_command("clear-buffer")
            actions.self.complex_insert(chunked_phrase)
