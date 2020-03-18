import threading
import json
import time
import re

from talon import Context, ui

from user.newapi.emacs.utils import rpc
from user.newapi.utils.key_value_store import KeyValueStore


VOICEMACS_TITLE_PREFIX = "voicemacs:"
DATA_PENDING_KEY = "data"
TITLE_CHECK_PAUSE = 0.002


emacs_state = KeyValueStore()


# TODO: Yuck. Extract this, use tags?
emacs_context = Context()
emacs_context.matches = r"""
app: /.*emacs\.exe/
"""


def _extract_data(voicemacs_section):
    """Extract data from the ``voicemacs_section`` of the title."""
    json_part = voicemacs_section.replace(VOICEMACS_TITLE_PREFIX, "").strip()
    try:
        return json.loads(json_part)
    except json.JSONDecodeError:
        return None


def _split_title(title):
    """Split title into component parts."""
    parts = title.split(";")
    return list(map(str.strip, parts))


def _voicemacs_section(title_parts):
    """Get the voicemacs section of the title.

    :returns: The section as a string, or None if it was not found.
    :rtype: str or None

    """
    for part in title_parts:
        if part.startswith(VOICEMACS_TITLE_PREFIX):
            return part
    return None


def _parse_title(title):
    voicemacs_section = _voicemacs_section(_split_title(title))
    return _extract_data(voicemacs_section) if voicemacs_section else None


_synced_at_least_once = False


def _sync_data(title_data):
    global _synced_at_least_once
    data_pending = title_data.get(DATA_PENDING_KEY)
    # Emacs might have already synced data with a previous version of
    # Talon. If this is the case, it may try a partial update, so we need
    # to manually pull the entire state.
    if not _synced_at_least_once:
        emacs_state.update(rpc.pull_data(full_refresh=True))
        _synced_at_least_once = True
    elif data_pending:
        emacs_state.update(rpc.pull_data(full_refresh=False)),
    # Don't sync otherwise


def check_for_data():
    if emacs_context.enabled:
        title = ui.active_window().title
        # TODO: Handle invalid title (notify user that voicemacs needs to be
        #   installed.)
        title_data = _parse_title(title)
        if isinstance(title_data, dict):
            _sync_data(title_data)
        else:
            # We don't want to act on false data. Wipe it if voicemacs is no
            # longer active.
            #
            # TODO: This will fire regularly, guard it?
            # FIXME: `.enabled` doesn't work
            # emacs_state.reset()
            pass


# TODO: Hook updates to "pre:phrase" instead of polling indefinitely?
def sync_forever():
    while True:
        check_for_data()
        time.sleep(TITLE_CHECK_PAUSE)


# We use a thread instead of a cron job to prevent slow RPC blocking the cron
# thread.
sync_thread = threading.Thread(target=sync_forever)
sync_thread.start()
