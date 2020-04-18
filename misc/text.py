import time
from typing import List, Callable
import itertools

from talon import Module, Context, actions
import talon.clip as clip

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
    format_text,
    reformat_text,
    ComplexInsert,
    SurroundingText,
)
from user.utils import multi_map, preserve_clipboard


# TODO: Quote wrapped stuff. Double/single quotes
# TODO: Insert punctuation, like brackets.


formatter_functions = {
    "camel": apply_camel_case,
    "studley": apply_studley_case,
    "snake": apply_snake,
    "spine": apply_spine,
    "dotword": apply_dotword,
    "squash": apply_squash,
    "c_path": make_apply_delimiter("::"),
    "dunder": apply_dunder,
    "uppercase": apply_uppercase,
    "lowercase": apply_lowercase,
    "sentence": apply_sentence,
    "capitalized_sentence": apply_capitalized_sentence,
    "title": apply_title,
    "keywords": apply_programming_keywords,
}


# Many of these formatters may be chained and applied to a single chunk.
_chainable_formatters = multi_map(
    {
        "camel": "camel",
        "studley": "studley",
        "snake": "snake",
        "spine": "spine",
        # TODO: Maybe change this command. Dotty?
        "dotword": "dotword",
        "squash": "squash",
        # TODO: Where is this delimiter used again?
        "see path": "c_path",  # c path
        "dunder": "dunder",
        "upper": "uppercase",
        # TODO: Maybe don't allow this to be chained?
        ("lower", "bot"): "lowercase",
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


module = Module()
module.list("chainable_formatters", desc="List of text formatters that can be chained")
module.list(
    "standalone_formatters", desc="List of text formatters that cannot be chained"
)


@module.capture(rule="({self.standalone_formatters} | {self.chainable_formatters}+)")
def formatters(m) -> str:
    """One or more text formatters, as a space-separated string."""
    if hasattr(m, "standalone_formatters"):
        return m.standalone_formatters
    else:
        return " ".join(m.chainable_formatters_list)


@module.capture(rule="<phrase>")
def dictation(m) -> str:
    """Arbitrary dictation, optionally terminated with [over]."""
    return extract_dictation(m.phrase)


context = Context()
context.lists["self.chainable_formatters"] = _chainable_formatters
context.lists["self.standalone_formatters"] = _standalone_formatters


def join_punctuation(words: List[str]) -> str:
    # TODO: Extract to formatter_utils?
    # TODO: Implement proper punctuation joining.
    return " ".join(words)


def extract_dictation(phrase) -> str:
    """Extract raw dictation from a <phrase> capture."""
    return join_punctuation(actions.dictate.parse_words(phrase))


def to_formatter_funcs(formatters: str) -> List[Callable]:
    """Get a list of formatter functions from a string of formatter names."""
    # TODO: Meaningful error messages
    return [formatter_functions[name] for name in formatters.split()]


def format_contextually(text: str, formatters: List[Callable]) -> ComplexInsert:
    surrounding_text = actions.self.surrounding_text()
    return format_text(text, formatters, surrounding_text)


@module.action_class
class Actions:
    def surrounding_text() -> SurroundingText:
        """Get the text on either side of the next insert."""
        # TODO: Heuristic method for surrounding text in generic case. Try
        #   using clipboard until we have accessibility interfaces?
        return None

    @preserve_clipboard
    def cut_words_left(number: int) -> str:
        """Cut `number` words left of the cursor."""
        for i in range(number):
            # TODO: Use generic action
            actions.key("ctrl-shift-left")
        time.sleep(0.1)
        actions.edit.cut()
        time.sleep(0.1)
        return clip.get()

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

    # Convenience functions for very common formatters

    def insert_natural(text: str) -> None:
        """Insert text, formatted as natural language."""
        actions.self.insert_formatted(text, "sentence")

    def insert_capitalized(text: str) -> None:
        """Insert text, formatted as capitalized natural language."""
        actions.self.insert_formatted(text, "capitalized_sentence")

    def insert_lowercase(text: str) -> None:
        """Insert text, formatted as lowercase."""
        actions.self.insert_formatted(text, "lowercase")
