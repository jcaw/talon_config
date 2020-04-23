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


def _call(function_, params=[], timeout=5, max_attempts=5, changes_state=True):
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
        except porthole.TimeoutError:
            # Ignore short timeout errors when possible, so we can try again.
            # This is a weird `web-server` behavior - Porthole is reporting two
            # different types of timeout the same way.
            #
            # The command still should have gotten through, even though it
            # didn't return a response, so we can only do this when our command
            # doesn't change Emacs' state.
            #
            # FIXME: Weird short timeout error in Porthole, fix upstream
            #   - Perhaps could add a nonce to all calls to circumvent it?
            if changes_state or time.monotonic() - start_time >= timeout:
                raise
        LOGGER.info(
            f"Failed to call ({function_}, {params}) on attempt {attempts}. Retrying."
        )


def call(function_, params=[], timeout=5, max_attempts=5, changes_state=True):
    """Send an RPC call to Emacs (safely)."""
    # HACK: We empty the command loop first to ensure all input (keyboard,
    #   command injection & direct RPC) is processed in the same order it was
    #   issued.

    # t1 = time.monotonic()

    # _call("voicemacs-process-input", [], timeout, max_attempts, changes_state=False)
    # remaining_time = time.monotonic() - t1
    # if remaining_time < 0:
    #     raise porthole.TimeoutError("Command loop could not be emptied in time.")

    remaining_time = timeout
    start_time = time.monotonic()
    while True:
        if not _call(
            "voicemacs-input-pending?", [], timeout, max_attempts, changes_state=False
        ):
            break
        remaining_time = time.monotonic() - start_time
        if remaining_time <= 0:
            raise porthole.TimeoutError("Command loop could not be emptied in time.")
    return _call(function_, params, remaining_time, max_attempts, changes_state)


def run_command(command, prefix_arg=None):
    return call("voicemacs-inject-command", params=[command, prefix_arg])


def pull_data(full_refresh=False):
    try:
        return call(
            "voicemacs-pull-data", [full_refresh], changes_state=not full_refresh
        )
    except porthole.PortholeCallError:
        # Don't interrupt if it fails.
        #
        # FIXME: This could lead to desync if Emacs thinks its updated us. Add
        #   a handshake
        return {}
