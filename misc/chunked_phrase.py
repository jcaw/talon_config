from typing import Callable, List

from talon import Module, Context


class BasePhraseChunk(object):
    """Base class for all phrase chunks.

    A chunked phrase is a list of these chunks. Each chunk may be handled
    differently, depending on the action or context.

    """

    def __init__(self, payload):
        self.payload = payload

    def __str__(self):
        return str(self.payload)


class DictationChunk(BasePhraseChunk):
    """Holds a chunk of spoken dictation."""


class CharacterChunk(BasePhraseChunk):
    """Holds a single insertable character, spoken as a command."""


class KeypressChunk(BasePhraseChunk):
    """Holds a keypress (or series) that must be pressed, not inserted."""


class ActionChunk(BasePhraseChunk):
    """Holds an action to be called."""

    def __init__(self, action: Callable[[], None]):
        super(action)

    def execute(self):
        """Execute this chunk's action."""
        self.payload()


module = Module()
context = Context()


@module.capture(rule="<user.dictation>")
def dictation_chunk(m) -> DictationChunk:
    """Chunk corresponding to some dictation."""
    return DictationChunk(m.dictation)


@module.capture(rule="<user.character>")
def character_chunk(m) -> CharacterChunk:
    """Chunk corresponding to a spoken character."""
    return CharacterChunk(m.character)


@module.capture(rule="<user.special>")
def keypress_chunk(m) -> KeypressChunk:
    """Chunk corresponding to a keypress or key sequence."""
    return KeypressChunk(m.special)


# FIXME: Why can't I just create an empty capture that's only implemented by
#   some contexts?
@module.capture(rule="{non_existant_list}")
def action_chunk(m) -> ActionChunk:
    """Chunk corresponding to an action.

    This capture won't match by default. It should be overridden by contexts
    that want to allow actions to be called during a chunked phrase.

    """
    # TODO: Audit docstring
    return ActionChunk(None)


@module.capture(
    rule=(
        "(<user.dictation_chunk> | <user.character_chunk>"
        " | <user.keypress_chunk> | <user.action_chunk>)+"
    )
)
def chunked_phrase(m) -> List[BasePhraseChunk]:
    """Phrase consisting of one or more phrase chunks.

    Each chunk may be some dictation, a symbol, a keypress, etc, spoken in
    series.

    """
    return list(m)


@module.capture(rule="<user.dictation_chunk> [<user.chunked_phrase>]")
def chunked_phrase_strict(m) -> List[BasePhraseChunk]:
    """A chunked phrase that must start with dictation.

    This capture can be used to insert keywords that would otherwise be handled
    as symbols or commands. For example, we could put this in a .talon file:

        snake <chunked_phrase_strict>:
            user.insert_complex(chunked_phrase_strict, "snake")

    Now let's say we want to insert the word "dot":

        "snake this is dot a test" -> "this_is.a_test"
        "snake dot a test"         -> "dot_a_test"
        "snake dot dot a test"     -> "dot.a_test"

    """
    if hasattr(m, "chunked_phrase"):
        return [m.dictation_chunk, *m.chunked_phrase]
    else:
        return [m.dictation_chunk]
