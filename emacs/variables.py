import logging
from typing import List

from talon import Context, actions

from user.utils import spoken_form
from user.emacs.utils.voicemacs import rpc_call, emacs_state
from user.utils.formatting import separate_words

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


ACTIVE_SYMBOLS_KEY = "active-symbols"


context = Context()
context.matches = """
tag: user.emacs
"""


@context.action_class("user")
class EmacsActions:
    def insert_symbol(symbol: str) -> None:
        # TODO: Pad it appropriately (preceeding) based on context.
        actions.insert(symbol)

    def insert_symbol_from_section(symbol_section: str) -> None:
        # HACK: Insert the chunk & trigger autocomplete for now.
        LOGGER.debug(f"Inserting {symbol_section}")
        symbol_section = symbol_section.lower()
        active_symbols = emacs_state.get(ACTIVE_SYMBOLS_KEY)
        candidates = [
            symbol
            for symbol in active_symbols
            if symbol_section in map(str.lower, separate_words(symbol))
        ]
        if candidates:
            actions.insert(symbol_section)
            if len(candidates) > 1:
                actions.self.emacs_command("company-complete")
        else:
            raise ValueError(f'No active symbols found containing "{symbol_section}"')


def _update_symbols(state):
    """Update the currently active symbols."""
    global context
    # TODO: Maybe add a hard cap on the total number here? Might be better to do
    #   that in Emacs, but I think I want redundancy.
    symbols = state.get(ACTIVE_SYMBOLS_KEY, [])
    whole_symbols = {}
    symbol_sections = {}
    for symbol in symbols:
        # TODO: Clean up the `lower` calls here. Pull them into `spoken_form`.
        separated = separate_words(symbol)
        if len(separated) > 1:
            whole_symbols[spoken_form(separated).lower()] = separated.lower()
            for component in separated.split(" "):
                # TODO: Don't allow clashes here? E.g. "Target" & "target". Might
                #   not need to, Talon might optimize them.
                symbol_sections[spoken_form(component).lower()] = component.lower()
    LOGGER.debug(whole_symbols)
    LOGGER.debug(
        "Updating Emacs symbols: {} symbols, {} sections added.".format(
            len(whole_symbols), len(symbol_sections),
        )
    )
    context.lists["user.active_symbols"] = whole_symbols
    # Don't assign sections for now. Can integrate them later.
    # context.lists["user.active_symbol_sections"] = symbol_sections


emacs_state.hook_key(ACTIVE_SYMBOLS_KEY, _update_symbols)
