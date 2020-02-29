import time
from typing import List

from talon import Module, Context, ui, actions
import talon.clip as clip

from user.newapi.utils.formatting import (
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
    format_text,
    reformat_text,
    ComplexInsert,
    SurroundingText,
)
from user.utils import multi_map, preserve_clipboard
from user.misc.numbers import extract_number, numeric


# TODO: Quote wrapped stuff. Double/single quotes
# TODO: Insert punctuation, like brackets.


# TODO: Separate atomic modifiers that can't be chained, e.g. Natural Language?
#   Own map, don't even allow chaining?
formatter_map = {
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
    "lower": apply_lowercase,
    "say": apply_sentence,
    "top": apply_capitalized_sentence,
    "title": apply_title,
}


# TODO: Wrapped, e.g. parens and string?
# wrapped_commands = multi_map(
#     {
#         ["sing string", "single string"]: apply_speechmarks,
#         ["dub string", "double string"]: apply_quotemarks,
#     }
# )


module = Module()
module.list("formatters", desc="List of formatters")


@module.action_class
class Actions:
    def surrounding_text() -> SurroundingText or None:
        """Get the text on either side of the next insert."""

    def cut_words_left(number: int) -> SurroundingText:
        """Cut `number` words left of the cursor."""

    # TODO: Maybe extract to a more generic context
    def insert_complex(complex_insert: ComplexInsert) -> None:
        """Input a ComplexInsert into the current program."""


@module.capture
def formatters(m) -> List[str]:
    """List of text formatters."""


@module.capture
def formatted_dictation(m) -> None:
    """Insert formatted dictation."""


@module.capture
def reformat_left(m) -> None:
    """Reformat a number of words left of the cursor."""


context = Context()
context.lists["self.formatters"] = formatter_map.keys()


def join_punctuation(words):
    # TODO: Extract to formatter_utils
    # TODO: Implement proper punctuation joining.
    return " ".join(words)


def extract_dictation(m) -> str:
    return join_punctuation(actions.dictate.parse_words(m.dgndictation))


@context.capture(rule="{self.formatters}+")
def formatters(m) -> List[str]:
    global formatter_map
    formatter_words = m.formatters
    return [formatter_map[word] for word in formatter_words]


@context.capture(rule="<self.formatters> <dgndictation>")
def formatted_dictation(m) -> None:
    text = extract_dictation(m)
    surrounding_text = actions.self.surrounding_text()
    actions.self.insert_complex(format_text(text, m.formatters, surrounding_text))


@context.capture(rule="<self.formatters> <number>")
def reformat_left(m):
    text = actions.self.cut_words_left(m.number)
    surrounding_text = actions.self.surrounding_text()
    actions.self.insert_complex(reformat_text(text, m.formatters, surrounding_text))


@context.action_class
class Actions:
    def surrounding_text():
        # TODO: Heuristic method for surrounding text in generic case. Try
        #   using clipboard until we have accessibility interfaces?
        return None

    @preserve_clipboard
    def cut_words_left(number: int) -> SurroundingText:
        for i in range(number):
            actions.key("ctrl-shift-left")
        time.sleep(0.1)
        actions.key("ctrl-x")
        time.sleep(0.1)
        return clip.get()

    def insert_complex(complex_insert: ComplexInsert) -> None:
        actions.insert(complex_insert.insert)
        actions.insert(complex_insert.text_after)
        for i in range(len(complex_insert.text_after)):
            actions.key("left")
