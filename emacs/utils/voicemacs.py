import socket
import re
import json
from typing import Optional, List
import threading
import time
import logging
from user.utils.key_value_store import KeyValueStore
from talon import ui, cron, Module, app, Context
import platform
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Holds various keys & values passed to us by Voicemacs.
emacs_state = KeyValueStore()


# Interval between connection attempts, in ms
_CONNECT_ATTEMPT_INTERVAL = 1000
# Frequency with which to ping Emacs, in ms
_PING_INTERVAL = 1000
_AUTH_TIMEOUT = 5
_RE_TERMINATION_CHAR = re.compile("\0")


# Unique ID for each sent request
_outgoing_nonce = 1

_receive_thread = None
_socket = None
_socket_lock = threading.Lock()

emacs_context = Context()
emacs_context.matches = "tag: user.emacs"

# Maps request nonces to their `_DeferredResult`
_pending_requests = {}
# TODO: Simplify locking scheme? Do we need two locks?
_pending_lock = threading.Lock()


module = Module()


class DeferredResult(object):
    # Time to sleep between each result check.
    _SLEEP_PERIOD = 1.0 / 1000  # ms

    def __init__(self):
        self._result = None
        self._result_set = False
        self._result_lock = threading.Lock()

    def get(self, timeout):
        t1 = time.monotonic()
        while time.monotonic() - t1 < timeout:
            with self._result_lock:
                if self._result_set:
                    return self._result
            time.sleep(self._SLEEP_PERIOD)
        raise TimeoutError("Request timed out.")

    def set(self, value):
        with self._result_lock:
            if self._result_set:
                raise RuntimeError("Result already set.")

            self._result = value
            self._result_set = True


class VoicemacsError(RuntimeError):
    """Base class for all errors raised by the Voicemacs client."""


class ServerError(VoicemacsError):
    """This can be raised when the server returns an error."""

    def __init__(self, summary, type_, data):
        self.type_ = type_
        self.data = data
        super().__init__(f"{summary}. Type: {type_}, Data: {data}")


class JsonRpcError(VoicemacsError):
    """Can be raised when the JSON RPC response is an error."""


def _get_temp_folder_linux():
    """Get the temp folder on a Linux system.
    This method may also be used by unknown operating systems.
    """
    # On Linux, we prefer to use "$XDG_RUNTIME_DIR", since it is dedicated to
    # this kind of purpose. If it's not available, Voicemacs will create a new
    # temporary directory in the user's home dir.
    if "XDG_RUNTIME_DIR" in os.environ:
        return os.environ["XDG_RUNTIME_DIR"]
    elif "HOME" in os.environ:
        return os.path.join(os.environ["HOME"], "tmp")
    else:
        raise IOError(
            "Neither $XDG_RUNTIME_DIR or $HOME could be read. Cannot "
            "automatically query server information on this system."
        )


def _get_temp_folder():
    """Get the temp folder where session information will be stored. The specific
    folder used depends on the platform. This method returns the same temp
    folder that Voicemacs will use to store session information. It should be a
    folder that's only accessible to the current user.

    """
    system = platform.system()
    if system.lower() == "linux":
        return _get_temp_folder_linux()
    elif system.lower() == "windows":
        # Windows is easy. %TEMP% should always exist, and be a user-restricted
        # directory.
        return os.environ["TEMP"]
    elif system.lower() == "mac":
        return os.path.join(os.environ["HOME"], "Library")
    else:
        # On unknown systems, Voicemacs falls back to the same method it uses on
        # Linux.
        return _get_temp_folder_linux()


_TEMP_FOLDER = _get_temp_folder()


# TODO: Not happy with the threading model here. It's super messy.


def _connect() -> None:
    global _socket, _outgoing_nonce, _receive_thread
    host = "localhost"
    session_file_path = os.path.join(_TEMP_FOLDER, "voicemacs", "session.json")
    if os.path.isfile(session_file_path):
        LOGGER.debug("Session file exists.")
        with open(session_file_path) as f:
            info = json.load(f)
            port = info.get("port", 5001)
            auth_key = info["auth-key"]
            LOGGER.debug(f'Session info -- port: {port}, auth-key: "{auth_key}"')
    else:
        raise IOError(
            f'Could not find Voicemacs session file at "{session_file_path}".'
            " Assuming the server is not running."
        )

    try:
        with _socket_lock:
            with _pending_lock:
                _outgoing_nonce = 1
            _socket = socket.socket()
            _socket.connect((host, port))
            LOGGER.info("Voicemacs connected")
            _receive_thread = threading.Thread(
                target=_receive_until_closed, args=(_socket,)
            )
            _receive_thread.start()
            _authenticate(_socket, auth_key)
            app.notify("Talon", "Voicemacs connected")
            LOGGER.info("Voicemacs authenticated. Ready to communicate with Emacs.")
    except:
        actions.user.notify("Talon", "Voicemacs failed to connect.", deadzone=5.0)
        _force_disconnect()


# TODO: Maybe put voicemacs in the title to reduce polls on a non-Voicemacs
#   Emacs?

# def _is_voicemacs():
#     title = ui.active_window().title
#     parts = map(str.strip, title.split(";"))
#     return "voicemacs" in parts


def _try_connect():
    global _socket
    if emacs_context.enabled and not _socket:
        LOGGER.debug(f"Emacs active & no socket. Trying to connect.")
        try:
            _connect()
            LOGGER.debug(f"Voicemacs connection successful: {_socket}")
        except Exception as e:
            LOGGER.debug(f"Problem connecting to Voicemacs server: {e}")


def _receive_until_closed(s: socket.socket) -> None:
    try:
        message_so_far = ""
        while True:
            chunk = _socket.recv(4096).decode("utf-8")
            remaining_chunk = chunk
            while True:
                next_terminator = _RE_TERMINATION_CHAR.search(remaining_chunk)
                if not next_terminator:
                    break
                full_message = (
                    message_so_far + remaining_chunk[: next_terminator.start()]
                )
                if full_message:
                    message_so_far = ""
                    try:
                        _handle_message(s, full_message)
                    except Exception as e:
                        # TODO: Error handling for broken handler?
                        LOGGER.info(
                            f'Unexpected error handling message: "{e}"',
                        )
                remaining_chunk = remaining_chunk[next_terminator.end() :]
            # If there's an unfinished message, store it for subsequent chunks.
            message_so_far += remaining_chunk
    except Exception as e:
        LOGGER.debug(f"Problem receiving voicemacs data: {e}")

    # Treat all issues as a disconnect & force it to be consistent.
    LOGGER.info("Voicemacs disconnected")
    _force_disconnect()


def _force_disconnect(*_, **__):
    """Force a disconnect.

    Use this to ensure the connection is terminated.

    """
    global _socket, _socket_lock
    try:
        with _socket_lock:
            if _socket:
                _socket.close()
                _socket = None
    except:
        pass
    finally:
        app.notify("Talon", "Voicemacs disconnected")


def _handle_message(s, message_string):
    LOGGER.debug(f"Handling message: {message_string}")

    try:
        message = json.loads(message_string)
    except:
        _send(
            s,
            _make_error(
                None,
                "mangled-message",
                "A mangled message was received. It could not be decoded.",
            ),
        )
    if not isinstance(message, dict):
        _send(s, _make_error("mangled-message", "Message was not a dictionary."))
    type_ = message.get("type", -1)
    nonce = message.get("nonce", -1)
    data = message.get("data", -1)
    direction = message.get("direction", -1)
    if nonce == -1:
        _send(s, _make_error(None, "invalid-message", '"nonce" was not provided.'))
    if type_ == -1:
        _send(s, _make_error(nonce, "invalid-message", '"type" was not provided.'))
    if data == -1:
        _send(s, _make_error(nonce, "invalid-message", '"data" was not provided.'))
    if direction == -1:
        _send(s, _make_error(nonce, "invalid-message", '"direction" was not provided.'))
    if not isinstance(type_, str):
        _send(s, _make_error(nonce, "invalid-message", '"type" must be a string.'))

    if direction == "request":
        _handle_request(s, nonce, type_, data)
    elif direction == "response":
        _handle_response(s, nonce, type_, data)
    else:
        _send(
            s,
            _make_error(
                nonce,
                "invalid-message",
                '"direction" must be "message" or "response".',
            ),
        )


def _handle_request(s: socket.socket, nonce: Optional[int], type_: str, data: dict):
    if type_ == "update":
        try:
            key = data["key"]
            value = data["value"]
            emacs_state.update({key: value})
        except Exception as e:
            _send(
                s,
                _make_error(
                    nonce, "internal-error", f'An internal error occurred: "{e}"'
                ),
            )
            return
        _send(s, _make_response(nonce, "confirm-update", {"key": key}))
    else:
        _send(
            s,
            _make_error(
                nonce,
                "invalid-request",
                f'Invalid request type: "{type_}". Ensure both server & client are up to date.',
            ),
        )


def _handle_response(s: socket.socket, nonce: Optional[int], type_: str, data: dict):
    # TODO: Timeout on callback? So it won't be called if the response comes in
    #   after the timeout.
    with _pending_lock:
        deferred = _pending_requests.get(nonce)
        if deferred:
            deferred.set((type_, data))
            del _pending_requests[nonce]


def _authenticate(s, auth_key) -> None:
    deferred = _send_request("authenticate", {"key": auth_key}, s)
    type_, data = deferred.get(timeout=_AUTH_TIMEOUT)
    if type_ == "authentication-successful":
        return
    elif type_ == "error":
        raise ServerError("Authentication failed", type_, data)
    else:
        raise ServerError("Unknown response type", type_, data)


def rpc_call(method: str, params: List = [], async_: bool = False, timeout=5):
    call = {
        "jsonrpc": "2.0",
        # Just use the request nonce for the ID. It will be unique.
        "id": str(_outgoing_nonce),
        "method": method,
        "params": params,
    }
    deferred = send_request(
        "json-rpc-call",
        {
            # RPC call has to be sent as an *encoded* string.
            "call": json.dumps(call),
        },
    )
    if async_:
        return None
    else:
        type_, data = deferred.get(timeout)
        if type_ == "json-rpc-result":
            # The remote procedure was called - now establish whether it
            # succeeded.
            data = json.loads(data["json-result"])
            if "result" in data:
                return data["result"]
            else:
                raise JsonRpcError(
                    'Error executing function: "{}"'.format(data["error"])
                )
        else:
            raise ServerError("Internal error", type_, data)


def _make_error(nonce: Optional[int], error_type: str, error_message: str):
    return _make_response(
        nonce, "error", {"error-type": error_type, "error-message": error_message}
    )


def _make_request(nonce: Optional[int], type_: str, data: dict):
    return _make_message("request", nonce, type_, data)


def _make_response(nonce: Optional[int], type_: str, data: dict):
    return _make_message("response", nonce, type_, data)


def _make_message(direction: str, nonce: Optional[int], type_: str, data: dict):
    return {
        #
        "direction": direction,
        "nonce": nonce,
        "type": type_,
        "data": data,
    }


def send_request(type_: str, data: dict) -> DeferredResult:
    global _pending_requests, _socket
    with _socket_lock:
        if not _socket:
            raise RuntimeError("Voicemacs not connected.")
        s = _socket
    return _send_request(type_, data, s)


def _send_request(type_: str, data: dict, s: socket.socket) -> DeferredResult:
    global _outgoing_nonce
    deferred = DeferredResult()
    # TODO: Maybe a better name for this lock now it also guards the outgoing
    #   nonce?
    with _pending_lock:
        # This will be used by the receiver to set the deferred result & invoke
        # the callback.
        _pending_requests[_outgoing_nonce] = deferred
        _send(s, _make_request(_outgoing_nonce, type_, data))
        _outgoing_nonce += 1
    return deferred


def _send(s: socket.socket, message: dict):
    LOGGER.debug(f"Sending: {message}")
    message_str = "\0" + json.dumps(message) + "\0"
    # TODO: Force D/C on error here?
    s.sendall(message_str.encode())


def _ping():
    """Ping the socket to ensure it's alive & trigger latent disconnects.

    (This is done manually because Emacs seems to have dodgy support for TCP
    keepalive.)

    """
    with _socket_lock:
        s = _socket
    if s:
        try:
            with _pending_lock:
                # TODO: What if the second half of a message gets dropped, will
                #   this still work?
                s.sendall("\0\1\0".encode())
        except:
            # Seems like even with this, sometimes the receive thread D/C isn't
            # triggered. Just force it.
            _force_disconnect()


def run_command(command, prefix_arg=None):
    # TODO: Still need to pause if e.g. a key was just pressed? Can it still
    #   inject too early?
    return rpc_call("voicemacs-inject-command", params=[command, prefix_arg])


cron.interval(f"{_CONNECT_ATTEMPT_INTERVAL}ms", _try_connect)
# HACK: Disconnect doesn't always trigger in the receive thread until a message
#   is sent. Manually ping to trigger these D/Cs.
#
# FIXME: Something is causing Talon to silently deadlock. I think it's Voicemacs
#   and I think it's probably the message system deadlocking.
cron.interval(f"{_PING_INTERVAL}ms", _ping)
