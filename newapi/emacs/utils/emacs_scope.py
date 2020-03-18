# TODO: Derive scope from data

from talon import Module

from user.newapi.emacs.utils.state import emacs_state


# Valid types for scope values.
LEGAL_SCOPE_TYPES = (str, int, float, bool)


module = Module()


def _add_to_scope(scope, key, value):
    """Add a key to the scope."""
    scope[f"emacs-{key}"] = value


def _add_scope_list(scope, state, key):
    """Temporary hack to allow context matching on lists of strings.

    Add lists as comma-separated strings. Match for individual items by regexp.

    """
    # Pad the ends so we can search like: /,some-mode,/
    joined = "," + ",".join(state.get(key, [])) + ","
    _add_to_scope(scope, key, joined)


def _add_string_values(scope, state):
    """Add all keys with string values in ``state`` to ``scope``."""
    for key, value in state.items():
        if isinstance(key, str) and isinstance(value, LEGAL_SCOPE_TYPES):
            _add_to_scope(scope, key, value)


@module.scope
def scope(*_):
    """Update the scope with relevant Emacs keys."""
    state = emacs_state.freeze()
    scope = {}
    # Allow the user to match on any string value.
    _add_string_values(scope, state)
    # We have to treat lists of strings differently, for now.
    #
    # TODO: Maybe do this automatically?
    _add_scope_list(scope, state, "minor-modes")
    _add_scope_list(scope, state, "active-yasnippet-tables")
    return scope


# Update the scope whenever the Emacs state updates.
emacs_state.hook(scope.update)
# Update immediately.
scope.update()
