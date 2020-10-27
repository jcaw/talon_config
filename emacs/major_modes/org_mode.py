import re
import itertools
from typing import List, Dict, Optional

from talon import Module, Context, actions

from user.emacs.utils.voicemacs import rpc_call, emacs_state

key = actions.key
insert = actions.insert
emacs_command = actions.self.emacs_command
insert_formatted = actions.user.insert_formatted


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


@module.capture(rule="{self.org_todo_keywords}")
def org_todo_keyword(m) -> str:
    """A valid Emacs `org-mode` TODO keyword."""
    return m.org_todo_keywords


@module.action_class
class Actions:
    def org_set_todo(state: str) -> None:
        """Set the current item to a specific TODO state."""
        rpc_call("org-todo", [str(state)])

    def org_code_block(language: Optional[str] = None) -> None:
        """Insert an `org-mode` code block.

        :param language: Optional. The block's language, this will be formatted
          as spine-case.

        """
        insert("#+BEGIN_SRC ")
        if language:
            insert_formatted(language, "spine")
        insert("\n\n#+END_SRC\n")
        if language:
            key("up:2")
        else:
            # Still need to input the language.
            key("up:3")
            emacs_command("end-of-line")
