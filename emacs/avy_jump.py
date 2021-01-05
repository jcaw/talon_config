from typing import List

from talon import Module, actions

key = actions.key
user = actions.user

module = Module()


@module.action_class
class Actions:
    def emacs_jump(char: str) -> None:
        """Jump to a specific character."""
        user.emacs_command("avy-goto-word-or-subword-1")
        key(char)

    def emacs_jump_chars(chars: List[str]) -> None:
        """Jump to a sequence of chars."""
        user.emacs_fallbacks(["evil-avy-goto-char-timer", "avy-goto-char-timer"])
        for char in chars:
            key(char)
