from typing import Callable

from enum import Enum
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


def initiate_character_action(command: Callable[[str], None]):
    global _queued_command
    _queued_command = command
    context.tags = ["user.zap_querying_char"]


class Direction(Enum):
    LEFT = 0
    RIGHT = 1


def get_character_offset(character: str, direction: Direction):
    """Get the offset of the specified `character` in `direction`.

    Note this returns the point BEFORE that character, and will always be
    positive. Also returns the surrounding text, in case you want to do
    something with it.

    """
    assert_single_character(character)
    surrounding = surrounding_text()
    options = [character.lower(), character.upper()]
    if direction == Direction.LEFT:
        before = surrounding.text_before
        i = 1
        while i <= len(before):
            if before[-i] in options:
                return i, surrounding_text
            i += 1
        raise ValueError(
            f"Character `{character}` could not be found in the text before the cursor."
        )
    else:
        after = surrounding.text_after
        i = 0
        while i < len(after):
            if after[i] in options:
                return i, surrounding_text
            i += 1
        raise ValueError(
            f"Character `{character}` could not be found in the text after the cursor."
        )


@module.action_class
class Actions:
    def zap_kill_left_inclusive(character: str):
        """Delete between the cursor and the nearest `character` to the left.

        Inclusive - it will also delete the character.

        """
        global _last_killed_text
        i, surrounding_text = get_character_offset(character, Direction.LEFT)
        # TODO: Maybe use the accessibility interface here?
        # We highlight, then delete as a single action, so it creates a single
        # undo point.
        #
        # HACK: Select from the opposite direction, so undo will place the
        #   cursor back to where it was.
        key(f"left:{i}")
        for _ in range(i):
            actions.edit.extend_right()
        key(f"backspace")
        _last_killed_text = surrounding_text.before[-i:]

    def zap_kill_right_inclusive(character: str):
        """Delete between the cursor and the nearest `character` to the right.

        Inclusive - it will also delete the character.

        """
        global _last_killed_text

        i, surrounding_text = get_character_offset(character, Direction.RIGHT)
        # TODO: Maybe use the accessibility interface here?
        # We highlight, then delete as a single action, so it creates a single
        # undo point.
        #
        # HACK: Select from the opposite direction, so undo will place the
        #   cursor back to where it was.
        key(f"right:{i}")
        for _ in range(i + 1):
            actions.edit.extend_left()
        key(f"backspace")
        _last_killed_text = surrounding_text.after[: i + 1]

    def zap_initiate_kill_left_inclusive():
        """Start an inclusive zap to char kill to the left."""
        initiate_character_action(actions.user.zap_kill_left_inclusive)

    def zap_initiate_kill_right_inclusive():
        """Start an inclusive zap to char kill to the right."""
        initiate_character_action(actions.user.zap_kill_right_inclusive)

    def zap_execute_queued_command(letter: str):
        """Execute the currently queued command."""
        try:
            assert callable(_queued_command), _queued_command
            _queued_command(letter)
        finally:
            actions.user.zap_cancel_command()

    def zap_cancel_command():
        """Cancel the current character read and queued zap command."""
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

    def zip_move_left_inclusive(character: str):
        """Move left past the first instance of `character`."""
        i, _ = get_character_offset(character, Direction.LEFT)
        key(f"left:{i}")

    def zip_move_right_inclusive(character: str):
        """Move right past the first instance of `character`."""
        i, _ = get_character_offset(character, Direction.RIGHT)
        key(f"right:{i}")

    def zip_initiate_move_left_inclusive():
        """Read in a char, then move past the first instance of it to the left."""
        initiate_character_action(actions.self.zip_move_left_inclusive)

    def zip_initiate_move_right_inclusive():
        """Read in a char, then move past the first instance of it to the right."""
        initiate_character_action(actions.self.zip_move_right_inclusive)


vimfinity_bind_keys(
    {
        # TODO: bindings for movement. Make them more convenient than the kill
        #   bindings (perhaps e.g. demote kill to shift-right, or up?)
        "up": (actions.user.zap_initiate_kill_left_inclusive, "Zap Left"),
        "down": (actions.user.zap_initiate_kill_right_inclusive, "Zap Right"),
        "left": (actions.user.zip_initiate_move_left_inclusive, "Zip Left"),
        "right": (actions.user.zip_initiate_move_right_inclusive, "Zip Right"),
        # "down": (actions.user.zap_undo_last_kill, "Undo Last Zap"),
    }
)
