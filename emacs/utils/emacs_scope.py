# TODO: Derive scope from data
import logging

from talon import Module

from user.emacs.utils.voicemacs import emacs_state

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# Valid types for scope values.
LEGAL_SCOPE_TYPES = (str, int, float, bool)


module = Module()


def _add_to_scope(scope, key, value):
    """Add a key to the scope."""
    scope[f"emacs-{key}"] = value


def _add_legal_values(scope, state):
    """Add all keys with scope-legal values in ``state`` to ``scope``."""
    for key, value in state.items():
        if isinstance(key, str):
            if isinstance(value, LEGAL_SCOPE_TYPES):
                _add_to_scope(scope, key, value)
            elif _is_list_of_strings(value):
                _add_to_scope(scope, key, set(value))


def _is_list_of_strings(thing):
    """Is ``thing`` a list of strings?"""
    if isinstance(thing, list):
        for element in thing:
            if not isinstance(element, str):
                return False
        return True
    else:
        return False


def _duplicate_key(scope, original_key, new_key):
    """Create another reference to the value of ``original_key``.

    Use to create nicer key names. A reference is only created when the
    original key exists.

    """
    try:
        scope[f"emacs-{new_key}"] = scope[f"emacs-{original_key}"]
    except KeyError:
        pass


@module.scope
def scope(*_):
    """Update the scope with relevant Emacs keys."""
    state = emacs_state.freeze()
    scope = {}
    # Allow the user to automatically match on any value that's legal within a
    # scope.
    _add_legal_values(scope, state)
    # Referencing `major-mode` and `minor-mode` in .talon files is nicer than
    # referencing the set names passed by Voicemacs.
    _duplicate_key(scope, "major-mode-chain", "major-mode")
    _duplicate_key(scope, "minor-modes", "minor-mode")
    LOGGER.debug("Emacs scope synced. Keys: {}".format(list(scope.keys())))
    LOGGER.debug("Emacs state keys:         {}".format(list(state.keys())))
    return scope


# Update the scope whenever the Emacs state updates.
emacs_state.hook(scope.update)
