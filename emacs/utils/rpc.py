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
        except porthole.ServerNotRunningError:
            # Emacs servers can be volatile. If it appears not to be running, it
            # might have just rejected our request. With remote command calls, this
            # matters, so we retry.
            if attempts >= max_attempts:
                raise
            # If we're past the timeout, always raise.
            #
            # TODO: Should this strictly produce a timeout error? Does it matter?
            if time.monotonic() - start_time >= timeout:
                raise
        LOGGER.info(
            f"Failed to call ({function_}, {params}) on attempt {attempts}. Retrying."
        )


def run_command(command, prefix_arg=None):
    timeout = 5
    start_time = time.monotonic()
    try:
        return call(
            "voicemacs-inject-command", params=[command, prefix_arg], timeout=timeout
        )
    except porthole.TimeoutError:
        # Ignore short timeout errors, Porthole is reporting two different
        # problems the same way. This is a weird `web-server` behaviour. The
        # command still should have gotten through, even though it didn't
        # return a response.
        #
        # FIXME: Weird short timeout error in Porthole
        #   - Perhaps could add a nonce to all calls to circumvent it?
        if time.monotonic() - start_time >= timeout:
            raise


def pull_data(full_refresh=False):
    try:
        return call("voicemacs-pull-data", [full_refresh])
    except porthole.PortholeCallError:
        # Don't interrupt if it fails.
        #
        # FIXME: This could lead to desync if Emacs thinks its updated us. Add
        #   a handshake
        return {}
