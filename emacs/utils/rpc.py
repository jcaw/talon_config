import subprocess
import os
import logging
import time

from talon.voice import Context

from user.utils import ON_WINDOWS, ON_LINUX, ON_MAC

try:
    import emacs_porthole as porthole
except ImportError:
    logging.exception("Porthole python client not installed.")

LOGGER = logging.getLogger(__name__)


VOICEMACS_SERVER_NAME = "voicemacs"


def call(function_, params=[], timeout=5, max_attempts=5):
    """Send an RPC call to Emacs."""
    attempts = 0
    start_time = time.monotonic()
    while True:
        try:
            attempts += 1
            return porthole.call(
                VOICEMACS_SERVER_NAME, function_, params=params, timeout=timeout
            )
        except (
            porthole.ServerNotRunningError,
            # FIXME: Shouldn't need to explicitly compensate for a timeout
            #   that didn't actually exceed the timeout.
            porthole.TimeoutError,
        ):
            # Emacs servers can be volatile. If it appears not to be running, it
            # might have just rejected our request. With remote command calls, this
            # matters, so we retry.
            if attempts >= max_attempts:
                raise
            # If we're passed the timeout, always raise.
            #
            # TODO: Should this strictly produce a timeout error? Does it matter?
            if time.monotonic() - start_time > timeout:
                raise
        LOGGER.info(
            f"Failed to call ({function_}, {params}) on attempt {attempts}. Retrying."
        )


# TODO: Audit uses of this
def Call(function_, params=[], timeout=2):
    """Constuct a command that executes `call`."""

    def do_call(m):
        nonlocal function_, params, timeout
        return call(function_, params, timeout)

    return do_call


def run_command(command, prefix_arg=None):
    return call(
        "voicemacs-inject-command",
        params=[command, prefix_arg],
        # TODO: Is this long enough? What if Emacs is hanging?
        timeout=2,
    )


def pull_data(full_refresh=False):
    try:
        return call(
            "voicemacs-pull-data",
            [full_refresh],
            # Use a very long timeout in case Emacs is processing (e.g. if Helm
            # being opened).
            timeout=2,  # TODO: Make sure to comment this
        )
    except porthole.PortholeCallError:
        # Don't interrupt if it fails.
        #
        # FIXME: This could lead to desync if Emacs thinks its updated us. Add
        #   a handshake
        return {}
