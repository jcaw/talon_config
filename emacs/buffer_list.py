from collections import defaultdict
from typing import List
import threading

from talon import Module, Context, actions

from user.utils import spoken_form
from user.utils.formatting import separate_words
from user.emacs.utils.voicemacs import emacs_state, rpc_call


BUFFER_LIST_KEY = "buffer-list"
TALON_BUFFER_LIST = "emacs_partial_buffer_names"
NAMESPACED_BUFFER_LIST = f"self.{TALON_BUFFER_LIST}"


module = Module()
module.list(
    TALON_BUFFER_LIST,
    desc="Partial names that can be used to switch to specific buffers.",
)


context = Context()
# TODO: Could also have two lists, one for exact matches and one for non-exact
#   matches.
context.lists[NAMESPACED_BUFFER_LIST] = {}


_partial_buffers_map = defaultdict(list)
_buffers_lock = threading.Lock()


@module.action
def emacs_partial_buffer_switch(partial_name: str) -> None:
    """Switch to buffer matching `partial_name`.

    If there is anything other than a single match, opens the buffer switching
    dialogue.

    """
    with _buffers_lock:
        candidates = _partial_buffers_map.get(partial_name, [])
    if len(candidates) == 1:
        try:
            rpc_call("voicemacs-switch-to-existing-buffer", [candidates[0]])
            return
        except Exception as e:
            # If this fails just fall back to normal method.
            print(f"Error switching to buffer: {e}")
            pass
    else:
        print(f"More than one candidate, falling back: {candidates}")

    # Fallback method
    actions.self.emacs_switch_buffer()
    actions.insert(partial_name.lower().replace(" dot ", " "))


def _split_name(text):
    # Note "dot" is special here, e.g. "formatting.py" should be
    # "formatting dot py", not "formatting py"
    return spoken_form(separate_words(text).replace(".", " dot ")).split(" ")


def _update_partial_buffer_names(state):
    buffer_names = state.get(BUFFER_LIST_KEY, [])
    partial_names = set()
    with _buffers_lock:
        _partial_buffers_map.clear()
        for name in buffer_names:
            words = _split_name(name)
            for i in range(0, len(words)):
                for j in range(i, len(words) + 1):
                    partial_name = " ".join(words[i:j])
                    _partial_buffers_map[partial_name].append(name)
                    partial_names.add(partial_name)
        if set(context.lists[NAMESPACED_BUFFER_LIST]) != partial_names:
            context.lists[NAMESPACED_BUFFER_LIST] = partial_names


emacs_state.hook_key(BUFFER_LIST_KEY, _update_partial_buffer_names)
