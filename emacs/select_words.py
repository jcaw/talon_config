"""Module dedicated to selectable words on-screen."""

import re

from talon import Module, Context

from user.utils import spoken_form, single_spaces
from user.emacs.utils.voicemacs import emacs_state


module = Module()
module.list("selectable_words", desc="Words on screen that can be selected.")


context = Context()
context.lists["user.selectable_words"] = {}


_RE_NON_CHAR = re.compile(r"[^a-zA-Z0-9]")


def _extract_words(string):
    return single_spaces(_RE_NON_CHAR.sub(" ", string)).split(" ")


def _update_words(state):
    words = {}
    window_strings = state.get("visible-text", [])
    for window_string in window_strings:
        spoken_map = {spoken_form(word): word for word in _extract_words(window_string)}
        words.update(spoken_map)
    context.lists["user.selectable_words"] = words


# Temporarily disabled because it JIT-recompiles the grammar each time which
# is noticeably laggy.
# emacs_state.hook_key("visible-text", _update_words)
