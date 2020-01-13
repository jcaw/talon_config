"""Exposes a type of Context that gets checked automatically."""


import threading
import logging
from copy import copy

from talon import cron
from talon.voice import Context


# TODO: Maybe just use `SnapshotQueue` here?
_AUTO_CONTEXTS_LOCK = threading.Lock()
_AUTO_CONTEXTS = []


def AutoContext(name, func, group=None):
    """Create a function context that evaluates automatically.

    Under the hood, this is just checking `func` on a short interval, so only
    use it with very inexpensive functions (e.g. checking a boolean). Make sure
    `func` is thread-safe.

    :param callable() func: the function to check. Unlike a normal `Context`,
      this does not take any arguments.

    """
    # This is a function that returns a `Context`, rather than a subclass of
    # `Context`, because subclassing caused it to behave unexpectedly.

    global _AUTO_CONTEXTS_LOCK, _AUTO_CONTEXTS
    # Check now to prevent deferred errors.
    assert callable(func), type(func)
    if group:
        context = Context(name, group)
    else:
        context = Context(name)
    context.enabled = False
    with _AUTO_CONTEXTS_LOCK:
        _AUTO_CONTEXTS.append((context, func))
    return context


def _evaluate_context(context, func):
    """Check a context, enabling/disabling as needed."""
    should_be_enabled = func()
    if should_be_enabled:
        if not context.enabled:
            context.enabled = True
    elif context.enabled:
        context.enabled = False


def _check_auto_contexts():
    global _AUTO_CONTEXTS_LOCK, _AUTO_CONTEXTS
    with _AUTO_CONTEXTS_LOCK:
        contexts = copy(_AUTO_CONTEXTS)
    for (context, func) in contexts:
        try:
            _evaluate_context(context, func)
        except Exception as e:
            logging.exception("Error automatically checking context")


cron.interval("20ms", _check_auto_contexts)
