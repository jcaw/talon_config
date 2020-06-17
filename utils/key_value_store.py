import threading
from copy import copy
from collections import defaultdict

from user.utils import Hook


class KeyValueStore:
    def __init__(self):
        """Create a new key-value store."""
        self._store = {}
        self._lock = threading.Lock()
        self._key_hooks = defaultdict(Hook)
        self._update_hook = Hook()

    def set(self, key, value):
        """Set ``key`` to ``value``."""
        self.update({key: value})

    def get(self, key, default=None):
        """Get the value associated with ``key``."""
        with self._lock:
            return self._store.get(key, default)

    def get_many(self, *keys):
        """Get the value of multiple keys, as a dict."""
        with self._lock:
            return {key: self._store.get(key) for key in keys}

    def freeze(self):
        """Get a thread-safe snapshot of the store.

        It's only a shallow copy.

        """
        return copy(self._store)

    def update(self, dict_):
        """Update all keys in ``dict_`` to their respective values."""
        # TODO: Probably don't want to run hooks within the lock.
        if dict_:
            with self._lock:
                for key, value in dict_.items():
                    self._store[key] = value
                    self._key_hooks[key].run(self._store)
                self._update_hook.run(self._store)

    def delete(self, *keys):
        """Delete keys from the store.

        This counts as an update and will run hooks.

        """
        # First check is to avoid unnecessary computation.
        if self._store:
            # NOTE: Could be a race here, but it doesn't matter#?.
            with self._lock:
                # Second check is to avoid a race.
                if self._store:
                    for key in keys:
                        del self._store[key]
                        self._key_hooks[key].run(self._store)
                    self._update_hook.run(self._store)

    def reset(self):
        """Delete all keys."""
        self.delete(*self._store.keys())

    def hook(self, function, run_now=True):
        """Hook a function to fire whenever the store is updated.

        `function` should take the store as its argument.

        """
        self._update_hook.add(function)
        if run_now:
            function(self.freeze())

    def hook_key(self, key, function, run_now=True):
        """Hook a function to fire when `key` is updated."""
        self._key_hooks[key].add(function)
        if run_now:
            function(self.freeze())
