from typing import List
import time
from itertools import chain
from os import path
import re
import logging

from talon import Module, Context, actions, clip, app, cron
from talon_init import TALON_USER
from user.utils import preserve_clipboard

LOGGER = logging.getLogger(__name__)


CUSTOM_WORDS_PATH = path.join(TALON_USER, "words.dict")
RE_SPEAKABLE = re.compile(r"^[a-zA-Z ]+$")
RE_EMPTY = re.compile(r"^[ \t]*$")
RE_COMMENT = re.compile(r"^[ \t]*[#]")


module = Module()
module.list("custom_words", "List of words to be added to the base vocabulary.")


# Create custom words file if it doesn't exist.
if not path.isfile(CUSTOM_WORDS_PATH):
    with open(CUSTOM_WORDS_PATH, "w") as f:
        f.writelines(
            [
                "# Use this file to add words to the speech engine.\n",
                "#\n",
                "# You may add words on their own, or map spoken forms to written forms with a colon.\n"
                "# Spoken forms may contain spaces, written forms may contain any punctuation.\n",
                "\n",
            ]
        )


def parse_dict_file(file_path):
    def invalid_line(line_count, line, description="no description"):
        LOGGER.warn(
            f'Invalid mapping "{line}" on line {line_count + 1} of'
            + f' "{file_path}" ({description})'
        )

    def is_comment(line):
        return line.strip().startswith("#")

    words = {}
    with open(file_path, "r") as f:
        for line_count, line in enumerate(f):
            if RE_COMMENT.search(line):
                continue
            if RE_EMPTY.match(line):
                continue

            mapping = list(map(str.strip, line.split(":", 1)))
            spoken_form = mapping[0]
            if not RE_SPEAKABLE.match(spoken_form):
                print(f'"{spoken_form}"')
                invalid_line(
                    line_count, line, "spoken form may contain only letters and spaces"
                )
            if len(mapping) == 1:
                words[spoken_form] = spoken_form
            elif len(mapping) == 2:
                words[spoken_form] = mapping[1]
    return words


context = Context()


def _update_custom_words() -> None:
    global context
    words = parse_dict_file(CUSTOM_WORDS_PATH)
    context.lists["user.custom_words"] = words
    return words


_update_custom_words()


@module.action
def update_custom_words():
    """Reload the custom words from disk."""
    words = _update_custom_words()
    app.notify(f"{len(words)} word(s) loaded.")


def join_punctuation(words: List[str]) -> str:
    # TODO: Implement proper punctuation joining.
    return " ".join(words)


def extract_dictation(phrase) -> List[str]:
    """Extract raw dictation from a <phrase> capture."""
    return actions.dictate.parse_words(phrase)


@module.capture(rule="<phrase>")
def split_phrase(m) -> List[str]:
    return extract_dictation(m.phrase)


@module.capture(rule="{user.custom_words}")
def custom_word(m) -> str:
    "One custom word."
    return context.lists["user.custom_words"][m[0]]


@module.capture(rule="(<user.split_phrase> | <user.custom_word>)+")
def dictation(m) -> str:
    """Arbitrary dictation."""
    # Custom words are strings, phrases are lists
    normalized = [[chunk] if isinstance(chunk, str) else chunk for chunk in m]
    return join_punctuation(chain(*normalized))


@module.action_class
class Actions:
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
