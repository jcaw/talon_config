from typing import List, Callable
import itertools

from talon import Module, Context, actions

from user.misc.chunked_phrase import (
    BasePhraseChunk,
    DictationChunk,
    CharacterChunk,
    KeypressChunk,
    ActionChunk,
)
from user.utils.formatting import preserve_punctuation
from user.utils.formatting import (
    apply_camel_case,
    apply_studley_case,
    apply_snake,
    apply_spine,
    apply_dotword,
    apply_squash,
    make_apply_delimiter,
    apply_dunder,
    apply_uppercase,
    apply_lowercase,
    apply_sentence,
    apply_capitalized_sentence,
    apply_title,
    apply_programming_keywords,
    add_prefix,
    format_text,
    reformat_text,
    ComplexInsert,
    SurroundingText,
)
from user.utils import multi_map

insert_formatted = actions.user.insert_formatted


# Pass this to repeat the previous formatter.
PREVIOUS_FORMATTERS_SIGNIFIER = "previous"


# TODO: Quote wrapped stuff. Double/single quotes
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
    # Language-specific
    "c_path": make_apply_delimiter("::"),
    "python_private": add_prefix("_", apply_snake),
}


# Many of these formatters may be chained and applied to a single chunk.
_chainable_formatters = multi_map(
    {
        "camel": "camel",
        "studley": "studley",
        ("snake", "snik"): "snake",
        ("spine", "spin"): "spine",
        # TODO: Maybe change this command. Dotty?
        "dotword": "dotword",
        "squash": "squash",
        "dunder": "dunder",
        "upper": "uppercase",
        # TODO: Maybe don't allow this to be chained?
        ("lower", "bot"): "lowercase",
        # Language-specific
        # TODO: Where is this delimiter used again?
        "see path": "c_path",  # c path
        # TODO: Maybe move this into a context-specific list
        "private": "python_private",
    }
)
# Only one of these formatters can be applied to each chunk.
_standalone_formatters = {
    "say": "sentence",
    "top": "capitalized_sentence",
    "title": "title",
    "key": "keywords",
}


# Sanity check
for spoken_form, formatter_name in itertools.chain(
    _chainable_formatters.items(), _standalone_formatters.items()
):
    assert formatter_name in formatter_functions, f"{spoken_form}: {formatter_name}"


# TODO: Wrapped, e.g. parens and string?
# wrapped_commands = multi_map(
#     {
#         ["sing string", "single string"]: apply_speechmarks,
#         ["dub string", "double string"]: apply_quotemarks,
#     }
# )


class FormattedPhrase:
    """Holds formatters, plus a series of phrase chunks."""

    def __init__(self, formatters: str, phrase_chunks=List[BasePhraseChunk]):
        self.formatters = formatters
        self.phrase_chunks = phrase_chunks


module = Module()
module.list("chainable_formatters", desc="List of text formatters that can be chained")
module.list(
    "standalone_formatters", desc="List of text formatters that cannot be chained"
)

context = Context()
context.lists["self.chainable_formatters"] = _chainable_formatters
context.lists["self.standalone_formatters"] = _standalone_formatters


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


@module.capture(rule="<user.formatters> <user.chunked_phrase_strict>")
def formatted_phrase(m) -> FormattedPhrase:
    """A list of formatters, plus a chunked phrase."""
    return FormattedPhrase(m.formatters, m.chunked_phrase_strict)


@module.capture(rule="<user.formatted_phrase>+")
def formatted_phrases(m) -> List[FormattedPhrase]:
    """One or more formatted phrases."""
    return list(m)


# TODO: Better name for this one.
@module.capture(rule="<user.chunked_phrase> [<user.formatted_phrases>]")
def open_formatted_phrases(m) -> List[FormattedPhrase]:
    """A chunked phrase, plus optional formatted phrases.

    The result is designed to be used with the `insert_many_formatted` action,
    which should be supplied a default formatter for the unformatted chunked
    phrase.

    """
    opening = FormattedPhrase("", m[0])
    if hasattr(m, "formatted_phrases"):
        return [opening, *m.formatted_phrases]
    else:
        return [opening]


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
class Actions:
    def surrounding_text() -> SurroundingText:
        """Get the text on either side of the next insert."""
        # TODO: Heuristic method for surrounding text in generic case. Try
        #   using clipboard until we have accessibility interfaces?
        return None

    def insert_complex(complex_insert: ComplexInsert) -> None:
        """Input a ComplexInsert into the current program."""
        actions.insert(complex_insert.insert)
        actions.insert(complex_insert.text_after)
        for i in range(len(complex_insert.text_after)):
            actions.key("left")

    def reformat_left(formatters: str, number: int) -> None:
        """Reformat a number of words left of the cursor."""
        formatter_funcs = to_formatter_funcs(formatters)
        text = actions.self.cut_words_left(number)
        surrounding_text = actions.self.surrounding_text()
        actions.self.insert_complex(
            reformat_text(text, formatter_funcs, surrounding_text)
        )

    def insert_formatted(text: str, formatters: str) -> None:
        """Insert ``text``, formatted with ``formatters``.

        :param formatters: a space-separated list of formatter names.

        """
        formatter_funcs = to_formatter_funcs(formatters)
        actions.self.insert_complex(format_contextually(str(text), formatter_funcs))

    def insert_chunked(
        phrase_chunks: List[BasePhraseChunk], formatters: str = "sentence"
    ) -> None:
        """Insert a chunked phrase formatted with one or more formatters.

        The formatters should be provided as a space-separated string.

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
        formatter_funcs = to_formatter_funcs(formatters)

        for chunk in phrase_chunks:
            if isinstance(chunk, DictationChunk):
                insert_formatted(chunk, formatters)
            elif isinstance(chunk, CharacterChunk):
                # TODO: Letters will be inserted with padding in natural language.
                if preserve_punctuation(formatter_funcs):
                    # Format contextually if the formatter preserves
                    # punctuation.
                    insert_formatted(chunk, formatters)
                else:
                    # When punctuation would be stripped, insert it literally.
                    actions.insert(chunk)
            elif isinstance(chunk, KeypressChunk):
                actions.key(str(chunk))
            elif isinstance(chunk, ActionChunk):
                chunk.execute()
            else:
                raise ValueError(f"Unrecognized text type, {type(component)}.")

    def insert_many_formatted(
        formatted_phrases: List[FormattedPhrase], default_formatter: str = "sentence"
    ) -> None:
        """Insert a series of formatted phrases."""
        for phrase in formatted_phrases:
            actions.self.insert_chunked(
                phrase.phrase_chunks,
                # TODO: Yuck. Must be a better way
                phrase.formatters or default_formatter,
            )

    # TODO: Still need this? Works as an example I guess
    def insert_previous_formatter(phrase_chunks: List[BasePhraseChunk]) -> None:
        """Insert a chunked phrase using the last used formatter."""
        actions.self.insert_complex(phrase_chunks, "previous")


# Because the default limitation of `surrounding_text` returns `None`, we need
# to overwrite to explicitly or Talon will think there is no implementation.
@context.action_class
class DefaultActions:
    def surrounding_text() -> SurroundingText:
        return None
