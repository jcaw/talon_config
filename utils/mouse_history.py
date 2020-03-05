"""Tracks the mouse history.

This module can be used to get mouse positions in the past (for example, when
you started a word like \"right click\").

"""


import time
import collections
import threading
import math
import logging
import sys
from copy import deepcopy

from talon import cron, ctrl
from talon.track.geom import Point2d

# Amount of mouse history to record, in secs.
HISTORY_LENGTH = 30
# Time between position samples, in ms.
TICK_INTERVAL = 16


LOGGER = logging.getLogger(__name__)


class SnapshotQueue(object):
    """Queue that can have a thread-safe snapshot taken."""

    def __init__(self, maxlen):
        self._lock = threading.Lock()
        self._queue = collections.deque([], maxlen=maxlen)

    def append(self, item):
        with self._lock:
            self._queue.append(item)

    def snapshot(self, deep=False):
        """Get a snapshot of the current contents, as a list. Thread-safe.

        :param bool deep: Optional. If True, the snapshot will be a deep copy,
          otherwise a shallow copy (i.e. the members can mutate under you).
          Deeper copies will be slower. Default is False.

        """
        with self._lock:
            if deep:
                return [deepcopy(item) for item in self._queue]
            else:
                return list(self._queue)


class MouseHistory(object):
    def __init__(self, length_in_secs, tick_in_ms):
        """Create an object to store the mouse history.

        :param length: amount of history to store, in seconds.
        :param tick: tick length, in milliseconds.

        """
        self.length = length_in_secs
        self.tick = tick_in_ms

        self._mouse_capture_job = cron.interval(
            f"{tick_in_ms}ms", self._record_mouse_position
        )

        tick_in_secs = float(tick_in_ms) / 1000
        self.item_limit = math.ceil(float(length_in_secs) / tick_in_secs)
        self.history = SnapshotQueue(maxlen=self.item_limit)

    def __del__(self):
        try:
            cron.cancel(self._mouse_capture_job)
        except Exception:
            pass

    def _record_mouse_position(self):
        timestamp = time.time()
        position = ctrl.mouse_pos()
        self.history.append((position[0], position[1], timestamp))

    def position_at_time(self, timestamp):
        """Get the mouse position at a particular timestamp.

        :returns: a tuple of the timestamp the position was taken, plus the
          position.
        :rtype: tuple(int, (int, int))

        """
        self._log_size()
        # TODO: Remove these diagnostics
        # from pprint import pprint

        # pprint(self.history.snapshot()[:2])
        # pprint(self.history.snapshot()[-2:])
        diff, pos = min(
            [(abs(timestamp - pos[2]), pos) for pos in self.history.snapshot()]
        )
        # print(pos)
        # print("pos time: ", pos[2])
        # print("timestamp:", timestamp)
        return pos[2], pos[:2]

    def _log_size(self):
        """Log the size of the mouse history, iff debugging.

        """
        # On my Windows machine, 30 secs of history logs at around 4.7 Mb.
        if LOGGER.level >= logging.DEBUG:
            LOGGER.debug(
                "Size of mouse history: {} Mb".format(
                    sys.getsizeof(self.history) / (10 ^ 6)
                )
            )


_MOUSE_HISTORY = MouseHistory(HISTORY_LENGTH, TICK_INTERVAL)


def position_at_time(timestamp):
    global _MOUSE_HISTORY
    return _MOUSE_HISTORY.position_at_time(timestamp)


def restart_tracking():
    """Restart the history tracker.

    This must be called for changes in `HISTORY_LENGTH` or `TICK_INTERVAL` to
    propogate.

    """
    # TODO: Test this
    global _MOUSE_HISTORY, HISTORY_LENGTH, TICK_INTERVAL
    _MOUSE_HISTORY = MouseHistory(HISTORY_LENGTH, TICK_INTERVAL)


def actual_word_start(word):
    """`word.start` may not be exact - estimate a better timestamp."""
    estimate = word.start + min((word.end - word.start) / 2, 0.100)
    # Divide by 1000 to convert time units from Draconity to Python.
    return estimate / 1000.0


def backdated_position(word_meta):
    """Get the position of the mouse the user started to speak ``word_meta``.

    Note that on Windows, Draconity's timestamps seem to be able to drift out
    of sync with our timestamps, giving us the *wrong position*. If this
    happens, restarting Dragon seems to help.

    """
    _, position = position_at_time(actual_word_start(word_meta))
    return position
