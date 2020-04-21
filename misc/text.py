from typing import List
import time

from talon import Module, actions, clip
from user.utils import preserve_clipboard


module = Module()


def join_punctuation(words: List[str]) -> str:
    # TODO: Implement proper punctuation joining.
    return " ".join(words)


def extract_dictation(phrase) -> str:
    """Extract raw dictation from a <phrase> capture."""
    return join_punctuation(actions.dictate.parse_words(phrase))


@module.capture(rule="<phrase>")
def dictation(m) -> str:
    """Arbitrary dictation."""
    return extract_dictation(m.phrase)


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
