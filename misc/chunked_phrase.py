from typing import Callable, List, Optional
import itertools

from talon import Module, Context, actions

user = actions.user
key = actions.key
insert = actions.insert

from user.utils.formatting import (
    add_prefix,
    apply_camel_case,
    apply_capitalized_sentence,
    apply_dotword,
    apply_dunder,
    apply_elisp_private,
    apply_euler_function_call,
    apply_lisp_function_call,
    apply_lisp_keyword,
    apply_lowercase,
    apply_programming_keywords,
    apply_sentence,
    apply_snake,
    apply_speech,
    apply_spine,
    apply_squash,
    apply_studley_case,
    apply_title,
    apply_uppercase,
    ComplexInsert,
    format_text,
    formatter_chain,
    make_apply_delimiter,
    preserve_punctuation,
    reformat_text,
    SurroundingText,
)
from user.utils import multi_map


# Pass this to repeat the previous formatter.
PREVIOUS_FORMATTERS_SIGNIFIER = "previous"


# TODO: Formatter after punctuation, like brackets.
formatter_functions = {
    "camel": apply_camel_case,
    "studley": apply_studley_case,
    "snake": apply_snake,
    "spine": apply_spine,
    "dotword": apply_dotword,
    "squash": apply_squash,
    "dunder": apply_dunder,
    "uppercase": apply_uppercase,
    "lowercase": apply_lowercase,
    "sentence": apply_sentence,
    "capitalized_sentence": apply_capitalized_sentence,
    "title": apply_title,
    "keywords": apply_programming_keywords,
    # Special case
    PREVIOUS_FORMATTERS_SIGNIFIER: PREVIOUS_FORMATTERS_SIGNIFIER,
    "speech": apply_speech,
    "uppercase_snake": formatter_chain(apply_snake, apply_uppercase),
    # Language-specific
    "c_path": make_apply_delimiter("::"),
    "python_private": add_prefix("_", apply_snake),
    "elisp_private": apply_elisp_private,
    "lisp_keyword_arg": apply_lisp_keyword,
    "lisp_function_call": apply_lisp_function_call,
    "euler_function_call": apply_euler_function_call,
    "dot_prefix_snake": add_prefix(".", apply_snake),
    "rparen_prefix_snake": add_prefix("(", apply_snake),
    # Other
    "forward_slash_path": make_apply_delimiter("/"),
}

# Many of these formatters may be chained and applied to a single chunk.
chainable_formatters = multi_map(
    {
        "camel": "camel",
        "studley": "studley",
        ("snake", "snik"): "snake",
        ("spine", "spin"): "spine",
        # TODO: Settle on one/two of these
        ("dotword", "knob", "pebble"): "dotword",
        "squash": "squash",
        "dunder": "dunder",
        "upper": "uppercase",
        # Common combination, so contract it.
        ("upsnake", "upsnik"): "uppercase_snake",
        # TODO: Maybe don't allow this to be chained?
        ("lower", "bot"): "lowercase",
        # Function calls are euler-style by default. Lisps can override this.
        "funk": "euler_function_call",
        # Language-specific
        # TODO: Where is this delimiter used again?
        "see path": "c_path",  # c path
        # TODO: Clashes with C path?
        "path": "forward_slash_path",
    }
)
# Only one of these formatters can be applied to each chunk.
standalone_formatters = {
    "say": "sentence",
    "top": "capitalized_sentence",
    "quote": "speech",
    "title": "title",
    # TODO: Settle on one of these
    "prog": "keywords",
    "pog": "keywords",
}

# Sanity check
for spoken_form, formatter_name in itertools.chain(
    chainable_formatters.items(), standalone_formatters.items()
):
    assert formatter_name in formatter_functions, f"{spoken_form}: {formatter_name}"


# TODO: Maybe swap these from inheritance to a single type & distinguish with
#   metadata.


class BasePhraseChunk(object):
    """Base class for all phrase chunks.

    A chunked phrase is a list of these chunks. Each subclass (different chunk
    types) may be handled differently by the action executing on these chunks.

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


class FileSuffixChunk(BasePhraseChunk):
    """Holds the dotted suffix for a filetype (or URL)."""


class FormatterChunk(BasePhraseChunk):
    """Holds a space-separated string of formatter(s)."""


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


# TODO: Audit complex phrase keypresses
@module.capture(rule="<user.special>")
def keypress_chunk(m) -> KeypressChunk:
    """Chunk corresponding to a keypress or key sequence."""
    return KeypressChunk(m.special)


@module.capture(rule="<user.file_suffix>")
def file_suffix_chunk(m) -> FileSuffixChunk:
    return FileSuffixChunk(m.file_suffix)


# FIXME: Why can't I just create an empty capture that's only implemented by
#   some contexts?
@module.capture(rule="dsafhakdshlhgsjghlskggkhasdklghsdjh")
def action_chunk(m) -> ActionChunk:
    """Chunk corresponding to an action.

    This capture won't match by default. It should be overridden by contexts
    that want to allow actions to be called during a chunked phrase.

    """
    return ActionChunk(None)


module.list("chainable_formatters", desc="List of text formatters that can be chained")
module.list(
    "standalone_formatters", desc="List of text formatters that cannot be chained"
)

context.lists["self.chainable_formatters"] = chainable_formatters
context.lists["self.standalone_formatters"] = standalone_formatters


def to_formatter_funcs(formatters: str) -> List[Callable]:
    """Get a list of formatter functions from a string of formatter names."""
    # TODO: Meaningful error messages
    return [formatter_functions[name] for name in formatters.split()]


@module.capture(rule="({self.standalone_formatters} | {self.chainable_formatters}+)")
def formatters(m) -> str:
    """One or more text formatters, as a space-separated string."""
    if hasattr(m, "standalone_formatters"):
        return m.standalone_formatters
    else:
        return " ".join(m.chainable_formatters_list)


@module.capture(rule="<user.formatters>")
def formatter_chunk(m) -> None:
    return FormatterChunk(m.formatters)


@module.capture(
    rule=(
        "("
        "   <user.dictation_chunk>"
        " | <user.character_chunk>"
        # For now, disallow keypresses because they are too intrusive
        # " | <user.keypress_chunk>"
        " | <user.action_chunk>"
        " | <user.file_suffix_chunk>"
        " | (<user.formatter_chunk> <user.dictation_chunk>)"
        ")+"
    )
)
def complex_phrase(m) -> List[BasePhraseChunk]:
    """Phrase consisting of one or more phrase chunks.

    Each chunk may be some dictation, a symbol, a keypress, etc, spoken in
    series.

    Note that formatters must have pure dictation directly afterwards. This is
    to allow the user to type words that would otherwise be inserted as
    punctuation.

    """
    return list(m)


# TODO: Allow formatters to take whole symbols? (Perhaps only if they're more
#   than one word).
# @module.capture(rule="<user.dictation_chunk> ")
# def dictation_phrase(m) -> List[BasePhraseChunk]:
#     """A phrase that must start with a dictation chunk."""
#     if hasattr(m, "complex_phrase"):
#         return [m[0], *m[1]]
#     else:
#         return list(m)


@module.capture(
    rule=("<user.formatter_chunk> <user.dictation_chunk> [<user.complex_phrase>]")
)
def formatter_phrase(m) -> List[BasePhraseChunk]:
    """A formatter, dictation, then a regular complex phrase.

    This capture can be used to have phrase insertion be triggered exclusively
    by a formatter.

    """
    if hasattr(m, "complex_phrase"):
        return [m[0], m[1], *m[2]]
    else:
        return [m[0], m[1]]


def format_contextually(text: str, formatters: List[Callable]) -> ComplexInsert:
    """Format `text`, taking into account the surrounding text (if possible).

    If the `surrounding_text` action is not implemented in the current context,
    surrounding text will be ignored.

    """
    # Get the surrounding text at formatting time to ensure it's as up-to-date
    # as possible (e.g. it should take into account changes from previous
    # actions).
    surrounding_text = actions.self.surrounding_text()
    return format_text(text, formatters, surrounding_text)


_last_used_formatters = None


def _insert_complex_insert(complex_insert: ComplexInsert) -> None:
    """Input a `ComplexInsert` into the current program."""
    actions.insert(complex_insert.insert)
    actions.insert(complex_insert.text_after)
    for i in range(len(complex_insert.text_after)):
        actions.key("left")


@module.action_class
class ModuleActions:
    def surrounding_text() -> SurroundingText:
        """Get the text on either side of the next insert."""
        # TODO: Heuristic method for surrounding text in generic case. Try
        #   using clipboard until we have accessibility interfaces?
        return None

    def reformat_left(formatters: str, number: int) -> None:
        """Reformat a number of words left of the cursor."""
        formatter_funcs = to_formatter_funcs(formatters)
        text = actions.self.cut_words_left(number)
        surrounding_text = actions.self.surrounding_text()
        _insert_complex_insert(reformat_text(text, formatter_funcs, surrounding_text))

    def insert_formatted(text: str, formatters: Optional[str] = "sentence") -> None:
        """Insert ``text``, formatted with ``formatters``.

        :param formatters: a space-separated list of formatter names.

        """
        formatter_funcs = to_formatter_funcs(formatters)
        _insert_complex_insert(format_contextually(str(text), formatter_funcs))

    # FIXME: Talon complains (spuriously) about the types being passed here.
    def insert_complex(
        phrase_chunks: List[BasePhraseChunk], formatters: Optional[str] = "sentence"
    ) -> None:
        """Insert a complex phrase.

        Complex phrases can be made up of many different \"chunks\". Each chunk
        is interpreted differently. Dictation is formatted & inserted,
        punctuation is just inserted, keypresses are pressed, etc.

        :param formatters: the set of formatters to use to initially format
          text. It should be supplied as a space-separated string. Whenever a
          formatter chunk is reached, the formatters will be switched.

        """
        global _last_used_formatters
        if not phrase_chunks:
            # Allow empty values to be passed.
            return
        if formatters == PREVIOUS_FORMATTERS_SIGNIFIER:
            if formatters is None:
                raise ValueError("No previously used formatter.")
            formatters = _last_used_formatters
        else:
            _last_used_formatters = formatters

        for chunk in phrase_chunks:
            if isinstance(chunk, DictationChunk):
                actions.self.insert_formatted(chunk, formatters)
            elif isinstance(chunk, CharacterChunk):
                formatter_funcs = to_formatter_funcs(formatters)
                # FIXME: Letters will be inserted with padding in natural language.
                if preserve_punctuation(formatter_funcs):
                    # Format contextually if the formatter preserves
                    # punctuation.
                    actions.self.insert_formatted(chunk, formatters)
                else:
                    # When punctuation would be stripped, insert it literally.
                    insert(chunk)
            elif isinstance(chunk, KeypressChunk):
                key(str(chunk))
            elif isinstance(chunk, ActionChunk):
                chunk.execute()
            elif isinstance(chunk, FormatterChunk):
                assert isinstance(chunk.payload, str), type(chunk.payload)
                _last_used_formatters = formatters = chunk.payload
            elif isinstance(chunk, FileSuffixChunk):
                # File suffixes should be inserted without formatting or
                # padding.
                insert(chunk.payload)
            else:
                raise ValueError(f"Unrecognized chunk type, {type(component)}.")

    # TODO: Still need this? Works as an example I guess
    def insert_previous_formatter(phrase: List[BasePhraseChunk]) -> None:
        """Insert a complex phrase using the last used formatter."""
        actions.self.insert_complex(phrase, "previous")


# Because the default limitation of `surrounding_text` returns `None`, we need
# to overwrite to explicitly or Talon will think there is no implementation.
@context.action
def surrounding_text() -> SurroundingText:
    return None
