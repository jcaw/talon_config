from typing import Callable

from talon import actions, Module, Context, cron
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys


key = actions.key
surrounding_text = actions.user.surrounding_text


module = Module()
module.tag("zap_querying_char", "Active when `zap_to_char.py` is querying a char.")

context = Context()


def assert_single_character(character: str):
    if not isinstance(character, str) or len(character) != 1:
        raise TypeError(
            f"Provide a single character as the target. You provided: `{character}`"
        )


_queued_command = None
_last_killed_text = ""


def zap_initiate_kill(kill_command: Callable[[str], None]):
    global _queued_command
    _queued_command = kill_command
    context.tags = ["user.zap_querying_char"]


@module.action_class
class Actions:
    def zap_kill_left_inclusive(character: str):
        """Delete between the cursor and the nearest `character` to the left.

        Inclusive - it will also delete the character.

        """
        global _last_killed_text
        assert_single_character(character)
        before = surrounding_text().text_before
        i = 1
        while i <= len(before):
            if before[-i] in [character.lower(), character.upper()]:
                _last_killed_text = before[-i:]
                # TODO: Maybe use the accessibility interface here?
                for _ in range(i):
                    actions.edit.extend_left()
                key(f"backspace")
                return
            i += 1
        raise ValueError(
            "Character `{character}` could not be found in the text before the cursor."
        )

    def zap_kill_right_inclusive(character: str):
        """Delete between the cursor and the nearest `character` to the right.

        Inclusive - it will also delete the character.

        """
        global _last_killed_text
        assert_single_character(character)
        after = surrounding_text().text_after
        i = 0
        while i < len(after):
            if after[i] in [character.lower(), character.upper()]:
                _last_killed_text = after[: i + 1]
                # TODO: Maybe use the accessibility interface here?
                # TODO: Switch to highlight, then delete, for good undo behaviour?
                for _ in range(i + 1):
                    actions.edit.extend_right()
                key(f"backspace")
                return
            i += 1
        raise ValueError(
            "Character `{character}` could not be found in the text after the cursor."
        )

    def zap_initiate_kill_left_inclusive():
        """Start an inclusive zap to char kill to the left."""
        zap_initiate_kill(actions.user.zap_kill_left_inclusive)

    def zap_initiate_kill_right_inclusive():
        """Start an inclusive zap to char kill to the right."""
        zap_initiate_kill(actions.user.zap_kill_right_inclusive)

    def zap_execute_queued_kill(letter: str):
        """Execute the currently queued "zap to char" kill command."""
        try:
            assert callable(_queued_command), _queued_command
            _queued_command(letter)
        finally:
            actions.user.zap_cancel_kill()

    def zap_cancel_kill():
        """Cancel the currently queued "zap to char" kill command."""
        global _queued_command
        context.tags = []
        _queued_command = None

    def zap_undo_last_kill():
        """Re-insert the text from the previous zap.

        Note this will insert the text at the current position regardless, so it
        will only work reliably when used immediately after an accidental zap.

        """
        actions.insert(_last_killed_text)
        # We keep the last killed text in case the undo fails. This is because
        # the user should still have access to it, but we don't want to put it
        # on the clipboard and overwrite the clipboard.


vimfinity_bind_keys(
    {
        "left": (actions.user.zap_initiate_kill_left_inclusive, "Zap Left"),
        "right": (actions.user.zap_initiate_kill_right_inclusive, "Zap Right"),
        "down": (actions.user.zap_undo_last_kill, "Undo Last Zap"),
    }
)
