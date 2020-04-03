from typing import List

from talon import Module, actions

key = actions.key
user = actions.user

module = Module()


@module.action_class
class Actions:
    def emacs_jump(keys: List[str]) -> None:
        """Jump to a char or sequence of chars."""
        user.emacs_command("avy-goto-word-or-subword-1")
        for current_key in keys:
            key(current_key)
