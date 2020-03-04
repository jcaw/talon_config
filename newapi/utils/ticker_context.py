import threading
import logging
from copy import copy

from talon import cron, Context


# TODO: Maybe just use `SnapshotQueue` here?
_AUTO_CONTEXTS_LOCK = threading.Lock()
_AUTO_CONTEXTS = []


# TODO: Better signature
def make_ticker_context(path, func):
    """Create a function context that re-evaluates frequently.

    ``func`` is repeatedly checked on a short interval, so only use it with
    very inexpensive functions (e.g. checking a boolean). Make sure ``func`` is
    thread-safe.

    :param callable[] func: the function to check. Unlike a normal `Context`,
      this does not take any arguments.

    """
    # Check now to prevent deferred errors.
    assert callable(func), type(func)
    context = Context(path)
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
    with _AUTO_CONTEXTS_LOCK:
        for (context, func) in _AUTO_CONTEXTS:
            try:
                _evaluate_context(context, func)
            except Exception as e:
                logging.exception("Error automatically checking context")


cron.interval("20ms", _check_auto_contexts)
