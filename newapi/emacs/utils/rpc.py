import subprocess
import os
import logging

from talon.voice import Context

from user.utils import ON_WINDOWS, ON_LINUX, ON_MAC

try:
    import emacs_porthole as porthole
except ImportError:
    logging.exception("Porthole python client not installed.")


VOICEMACS_SERVER_NAME = "voicemacs"


# FIXME: Automatic installer isn't working.
# TODO: Using Porthole as a stopgap. Remove once Talon has RPC.
def install_porthole(m=None):
    print("Installing porthole")
    if ON_WINDOWS:
        pip_script = "pip.bat"
    elif ON_LINUX:
        raise NotImplementedError("Don't know where pip is on Linux.")
    elif ON_MAC:
        raise NotImplementedError("Don't know where pip is on Mac.")
    else:
        raise NotImplementedError("Unrecognized platform.")
    pip_path = os.path.join(".venv/Scripts/", pip_script)
    subprocess.run(
        [pip_path, "install", "emacs-porthole", "--upgrade"], capture_output=True
    )


context = Context("install_porthole_context")
context.keymap({"(update | upgrade | install) porthole": install_porthole})


def call(function_, params=[], timeout=2):
    """Send an RPC call to Emacs."""
    return porthole.call(
        VOICEMACS_SERVER_NAME, function_, params=params, timeout=timeout
    )


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
