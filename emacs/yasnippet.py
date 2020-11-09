"""Automatic snippet extraction from Emacs."""


import re

from talon import Module, Context

from user.utils import spoken_form
from user.emacs.utils.voicemacs import rpc_call, emacs_state


SNIPPET_TABLES_KEY = "yasnippets"
ACTIVE_TABLES_KEY = "active-yasnippet-tables"
SNIPPET_LIST_NAME = "emacs_active_yasnippets"
SNIPPET_LIST_PATH = f"self.{SNIPPET_LIST_NAME}"


module = Module()
module.list(
    SNIPPET_LIST_NAME,
    desc="list of active yasnippet utterances, mapped to the snippet name",
)


@module.capture
def emacs_snippet(m) -> str:
    """A single Emacs snippet, without prefix."""


@module.action_class
class Actions:
    def emacs_insert_yasnippet(snippet_name: str) -> None:
        """Insert a yasnippet by name."""
        rpc_call("voicemacs-insert-snippet", [snippet_name])


context = Context()
context.matches = r"""
tag: user.emacs
user.emacs-minor-mode: yas-global-mode
user.emacs-minor-mode: yas-minor-mode
"""

context.lists[SNIPPET_LIST_PATH] = {}


@context.capture("self.emacs_snippet", rule="{" + SNIPPET_LIST_PATH + "}")
def emacs_snippet(m) -> str:
    return getattr(m, SNIPPET_LIST_NAME)


def _speech_snippet_list(state):
    """Extract active snippets, in speakable form."""
    new_snippets = {}
    snippet_tables = state.get(SNIPPET_TABLES_KEY, {})
    active_tables = state.get(ACTIVE_TABLES_KEY, [])
    for table_name in active_tables:
        for snippet in snippet_tables.get(table_name, []):
            key = snippet["key"]
            name = snippet["name"]
            spoken_name = spoken_form(name)
            spoken_key = spoken_form(key)
            if spoken_key:
                new_snippets[spoken_key] = name
            # Names are generally a better way to speak a snippet. Update names
            # second so they override keys when there's a clash.
            #
            # Note it's possible that by converting to spoken form, we create
            # identical spoken references to different snippets. Those clashes
            # will need to be renamed.
            if spoken_name:
                new_snippets[spoken_name] = name
    return new_snippets


def _update_snippets(state):
    """Update the active snippets from ``state``."""
    # TODO: This updates the entire snippet list every time there's a buffer
    #   switch. Time it, make sure it doesn't take prohibitively long.
    new_snippets = _speech_snippet_list(state)
    # TODO: Is this check necessary? Is it done by Talon?
    #   - Would the Talon check be order-agnostic?
    if context.lists[SNIPPET_LIST_PATH] != new_snippets:
        context.lists[SNIPPET_LIST_PATH] = new_snippets


# Wait until the second add to run.
emacs_state.hook_key(SNIPPET_TABLES_KEY, _update_snippets, run_now=False)
emacs_state.hook_key(ACTIVE_TABLES_KEY, _update_snippets, run_now=True)
