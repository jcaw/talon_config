from typing import Callable, List, Optional
import itertools

from talon import Module, Context, actions, clip

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
    apply_elisp_doc_symbol,
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
    make_apply_brackets,
    preserve_punctuation,
    reformat_text,
    SurroundingText,
)
from user.utils import multi_map


# Pass this to repeat the previous formatter.
PREVIOUS_FORMATTERS_SIGNIFIER = "previous"


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
    "parens_sentence": make_apply_brackets("(", ")"),
    "crotchet_sentence": make_apply_brackets("[", "]"),
    "title": apply_title,
    "keywords": apply_programming_keywords,
    # "padded": apply_padded,
    # Special case
    PREVIOUS_FORMATTERS_SIGNIFIER: PREVIOUS_FORMATTERS_SIGNIFIER,
    "speech": apply_speech,
    "uppercase_snake": formatter_chain(apply_snake, apply_uppercase),
    # Language-specific
    # TODO: Find some way to extract this stuff
    "c_path": make_apply_delimiter("::"),
    # TODO: Will this go lowercase?
    "c_directive": add_prefix("#", apply_squash),
    "hlsl_define": add_prefix("_", apply_studley_case),
    "python_private": add_prefix("_", apply_snake),
    "elisp_private": apply_elisp_private,
    "lisp_keyword_arg": apply_lisp_keyword,
    "lisp_function_call": apply_lisp_function_call,
    "euler_function_call": apply_euler_function_call,
    "dot_prefix_snake": add_prefix(".", apply_snake),
    "rparen_prefix_snake": add_prefix("(", apply_snake),
    "elisp_doc_symbol": apply_elisp_doc_symbol,
    # Other
    "https_url": add_prefix("https://", apply_squash),
    "forward_slash_path": make_apply_delimiter("/"),
}

# Many of these formatters may be chained and applied to a single chunk.
chainable_formatters = multi_map(
    {
        "camel": "camel",
        # "studley": "studley",
        "stud": "studley",
        # ("snake", "snik", "nick"): "snake",
        "nick": "snake",
        ("spine", "spin"): "spine",
        # TODO: Settle on one/two of these
        ("dotword", "knob", "pebble"): "dotword",
        # ("squash", "smash", "mash"): "squash",
        "mash": "squash",
        "dunder": "dunder",
        "upper": "uppercase",
        # TODO: padded formatting
        # "pad": "padded",
        # Common combination, so contract it.
        ("upsnake", "upsnik", "up nick"): "uppercase_snake",
        # TODO: Maybe don't allow this to be chained?
        (
            "lower",
            # "bot",
            # "low",
            # "small",
            # "case",
            "word",
        ): "lowercase",
        # Function calls are euler-style by default. Lisps can override this.
        "funk": "euler_function_call",
        # FIXME: This adds https:// in front of every dictation chunk, not just the first one.
        ("H T T P S", "H T T P S /", "url"): "https_url",
        "see path": "c_path",  # c path
        # FIXME: Clashes with C path?
        "path": "forward_slash_path",
    }
)
# Only one of these formatters can be applied to each chunk.
standalone_formatters = {
    "say": "sentence",
    "top": "capitalized_sentence",
    "quote": "speech",
    "paren": "parens_sentence",
    "crotchet": "crotchet_sentence",
    "title": "title",
    # TODO: Settle on one of these
    "prog": "keywords",
    "pog": "keywords",
    "direct": "c_directive",
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

    def __init__(self, character, pad):
        super().__init__(character)
        self.pad = pad


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


class ActiveSymbolChunk(BasePhraseChunk):
    """Corresponds to the `symbol_section` capture."""


module = Module()
context = Context()


@module.capture(rule="<user.dictation>")
def dictation_chunk(m) -> DictationChunk:
    """Chunk corresponding to some dictation."""
    return DictationChunk(m.dictation)


@module.capture(rule="[pad] <user.character>")
def character_chunk(m) -> CharacterChunk:
    """Chunk corresponding to a spoken character."""
    return CharacterChunk(m.character, m[0] == "pad")


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


# TODO: See if this is too trigger-happy to work properly.
# TODO: Maybe centralise the active symbol prefix, it's duplicated here and in
#   the talon file.
@module.capture(rule="<user.active_symbol>")
def active_symbol_chunk(m) -> None:
    return ActiveSymbolChunk(m.active_symbol)


@module.capture(
    rule=(
        "("
        # FIXME: Don't allow dictation next to whole symbol?
        "   <user.dictation_chunk>"
        # For now, disallow characters. They fire a lot, impeding dictation.
        " | <user.character_chunk>"
        # For now, disallow keypresses because they are too intrusive
        # " | <user.keypress_chunk>"
        # " | <user.action_chunk>"
        " | <user.file_suffix_chunk>"
        # " | <user.active_symbol_chunk>"
        " | (<user.formatter_chunk> <user.dictation_chunk>)"
        ")+"
    )
)
def complex_phrase(m) -> List:
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
    rule=(
        "<user.formatter_chunk> "
        "("
        "<user.dictation_chunk> "
        # "| <user.active_symbol_chunk>"
        ")"
        "[<user.complex_phrase>]"
    )
)
def formatter_phrase(m) -> List:
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


@module.action_class
class ModuleActions:
    def surrounding_text() -> Optional[SurroundingText]:
        """Get the text on either side of the next insert."""
        # TODO: Heuristic method for surrounding text in generic case. Try
        #   using clipboard until we have accessibility interfaces?
        return None

    def reformat_left(formatters: str, number: int) -> None:
        """Reformat a number of words left of the cursor."""
        formatter_funcs = to_formatter_funcs(formatters)
        text = actions.self.cut_words_left(number)
        surrounding_text = actions.self.surrounding_text()
        reformat_text(text, formatter_funcs, surrounding_text).do_insert()

    def reformat_dwim(formatters: str) -> None:
        """Reformat the current 'thing' - see `actions.user.cut_that_dwim`."""
        formatter_funcs = to_formatter_funcs(formatters)
        with clip.capture() as c:
            actions.self.cut_that_dwim()
        surrounding_text = actions.self.surrounding_text()
        reformat_text(c.get(), formatter_funcs, surrounding_text).do_insert()

    def insert_formatted(text: str, formatters: Optional[str] = "sentence") -> None:
        """Insert ``text``, formatted with ``formatters``.

        :param formatters: a space-separated list of formatter names.

        """
        formatter_funcs = to_formatter_funcs(formatters)
        format_contextually(str(text), formatter_funcs).do_insert()

    # FIXME: Talon complains (spuriously) about the types being passed here.
    def insert_complex(
        phrase_chunks: List, formatters: Optional[str] = "sentence"
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
                if chunk.pad:
                    actions.self.insert_key_padded(chunk)
                elif preserve_punctuation(formatter_funcs):
                    # FIXME: Letters will be inserted with padding in natural language.
                    #
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
            elif isinstance(chunk, ActiveSymbolChunk):
                # TODO: Maybe insert these with contextually-appropriate
                #   *preceeding* padding? Also maybe pad after, if something
                #   currently exists (might not work - e.g. inserting a
                #   function then wrapping with it)?
                insert(chunk.payload)
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


# Because the default implementation of `surrounding_text` returns `None`, we
# need to overwrite to explicitly or Talon will think there is no
# implementation.
@context.action("self.surrounding_text")
def surrounding_text() -> Optional[SurroundingText]:
    return None
