import re
import itertools
from typing import List, Dict

from talon import Module, Context

from user.emacs.utils import rpc
from user.emacs.utils.state import emacs_state


module = Module()
context = Context()

module.list(
    "org_todo_keywords",
    desc="List of TODO states valid in the current org-mode buffer.",
)

_RE_TODO_KEYBIND = re.compile(r"[(].*[)]")


def _extract_spoken_keywords(original_keywords: Dict[str, List[str]]) -> List[str]:
    """Extract a flat list of speakable keywords from org-mode's native dict."""
    keywords = {}
    for keyword in itertools.chain(*original_keywords.values()):
        # Pipe member breaks up active and terminated states, it's not
        # a keyword.
        if keyword != "|":
            # Sometimes they have a keybind attached, like:
            # `["TODO(t)", "|", "DONE(d)"]`
            #
            # TODO: Can we use "TODO" with `org-todo` if the value is "TODO(t)"?
            keywords[_RE_TODO_KEYBIND.sub("", keyword)] = keyword
    return keywords


def _update_todo_keywords(new_state: Dict):
    """Update the valid TODO keyword from a fresh state."""
    global context
    context.lists["user.org_todo_keywords"] = _extract_spoken_keywords(
        new_state.get("org-todo-keywords", {})
    )


emacs_state.hook_key("org-todo-keywords", _update_todo_keywords)
# Sync with current state immediately.
_update_todo_keywords(emacs_state.freeze())


@module.capture(rule="{self.org_todo_keywords}")
def org_todo_keyword(m) -> str:
    """A valid Emacs `org-mode` TODO keyword."""
    return m.org_todo_keywords


@module.action_class
class Actions:
    def org_set_todo(state: str) -> None:
        """Set the current item to a specific TODO state."""
        rpc.call("org-todo", [str(state)])
