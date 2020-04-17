import time
from typing import List, Callable

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


# TODO: Separate atomic modifiers that can't be chained, e.g. Natural Language?
#   Own map, don't even allow chaining?
formatter_map = multi_map(
    {
        "camel": apply_camel_case,
        "studley": apply_studley_case,
        "snake": apply_snake,
        "spine": apply_spine,
        # TODO: Maybe change this command. Dotty?
        "dotword": apply_dotword,
        "squash": apply_squash,
        # TODO: Where is this delimiter used again?
        "see path": make_apply_delimiter("::"),  # c path
        "dunder": apply_dunder,
        "upper": apply_uppercase,
        ("lower", "bot"): apply_lowercase,
        "say": apply_sentence,
        "top": apply_capitalized_sentence,
        "title": apply_title,
        "key": apply_programming_keywords,
    }
)


# TODO: Wrapped, e.g. parens and string?
# wrapped_commands = multi_map(
#     {
#         ["sing string", "single string"]: apply_speechmarks,
#         ["dub string", "double string"]: apply_quotemarks,
#     }
# )


module = Module()
module.list("formatters", desc="List of formatters")


@module.capture
def formatters(m) -> List[str]:
    """List of text formatters."""


@module.capture(rule="<phrase>")
def dictation(m) -> str:
    """Arbitrary dictation, optionally terminated with [over]."""
    return extract_dictation(m.phrase)


context = Context()
context.lists["self.formatters"] = formatter_map.keys()


def join_punctuation(words: List[str]) -> str:
    # TODO: Extract to formatter_utils?
    # TODO: Implement proper punctuation joining.
    return " ".join(words)


def extract_dictation(phrase) -> str:
    """Extract raw dictation from a <phrase> capture."""
    return join_punctuation(actions.dictate.parse_words(phrase))


def format_contextually(text: str, formatters: List[Callable]) -> ComplexInsert:
    surrounding_text = actions.self.surrounding_text()
    return format_text(text, formatters, surrounding_text)


@context.capture(rule="{self.formatters}+")
def formatters(m) -> List[str]:
    global formatter_map
    formatter_words = m.formatters_list
    return [formatter_map[word] for word in formatter_words]


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

    def reformat_left(formatters: List[str], number: int) -> None:
        """Reformat a number of words left of the cursor."""
        text = actions.self.cut_words_left(number)
        surrounding_text = actions.self.surrounding_text()
        actions.self.insert_complex(reformat_text(text, formatters, surrounding_text))

    def insert_formatted(text: str, formatters: List[Callable]) -> None:
        """Insert ``text``, formatted with ``formatters``."""
        actions.self.insert_complex(format_contextually(str(text), formatters))

    def insert_natural(text: str) -> None:
        """Insert text, formatted as natural language."""
        actions.self.insert_formatted(text, [apply_sentence])

    def insert_capitalized(text: str) -> None:
        """Insert text, formatted as capitalized natural language."""
        actions.self.insert_formatted(text, [apply_capitalized_sentence])

    def insert_lowercase(text: str) -> None:
        """Insert text, formatted as lowercase."""
        actions.self.insert_formatted(text, [apply_lowercase])

    def insert_spine(text: str) -> None:
        """Insert text, formatted as spine case."""
        actions.self.insert_formatted(text, [apply_spine])
