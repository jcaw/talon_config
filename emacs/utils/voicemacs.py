import socket
import re
import json
from typing import Optional, List
import threading
import time
import logging
from user.utils import context_active
from user.utils.key_value_store import KeyValueStore
import platform
import os
import math

from talon import ui, cron, Module, app, Context, scope, actions, imgui, canvas
from talon.ui import Rect, Point2d


# TODO: Move everything associated with one connection into an object and deal
#   with it that way. Probably cleaner than a global socket which might become
#   null at any point (although it doesn't really matter if it does, the
#   architecture can cope fine with that).


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# Holds various keys & values passed to us by Voicemacs.
emacs_state = KeyValueStore()


# Interval between connection attempts, in ms
_CONNECT_ATTEMPT_INTERVAL = 1000
# Frequency with which to ping Emacs, in ms
_PING_INTERVAL = 1000
_AUTH_TIMEOUT = 5  # In secs
_RE_TERMINATION_CHAR = re.compile("\0")
DISCONNECT_DEADZONE = 5.0
# How long to wait after injecting a command, to ensure the command has been
# processed before pressing any keys.
POST_COMMAND_INJECTION_WAIT = "100ms"


# Unique ID for each sent request
_outgoing_nonce = 1

_receive_thread = None
_socket = None
_socket_lock = threading.RLock()
voicemacs_connected = False

emacs_context = Context()
emacs_context.matches = "tag: user.emacs"

# Maps request nonces to their `_DeferredResult`
_pending_requests = {}
# TODO: Simplify locking scheme? Do we need two locks?
_pending_lock = threading.Lock()


module = Module()


_LAST_NOTIFICATION = time.monotonic()


def _notify_with_deadzone(title, message, deadzone=1):
    """Send a notification, unless another was sent recently."""
    global _LAST_NOTIFICATION
    now = time.monotonic()
    if now > _LAST_NOTIFICATION + deadzone:
        _LAST_NOTIFICATION = now
        app.notify(title, message)


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


def emacs_focussed():
    """Is Emacs focussed?"""
    return "user.emacs" in scope.get("tag", [])


# TODO: Not happy with the threading model here. It's super messy.


def _connect() -> None:
    global _socket, _outgoing_nonce, _receive_thread, voicemacs_connected
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
                target=_receive_until_closed, args=(_socket,), daemon=True
            )
            _receive_thread.start()
            _authenticate(auth_key)
            # app.notify("Talon", "Voicemacs connected")
            voicemacs_connected = True
            LOGGER.info("Voicemacs authenticated. Ready to communicate with Emacs.")
    except:
        # _notify_with_deadzone(
        #     "Talon", "Voicemacs failed to connect.", deadzone=DISCONNECT_DEADZONE
        # )
        _force_disconnect()
        raise


# TODO: Maybe put voicemacs in the title to reduce polls on a non-Voicemacs
#   Emacs?

# def _is_voicemacs():
#     title = ui.active_window().title
#     parts = [s.strip() for s in title.split(";")]
#     return "voicemacs" in parts


def _try_connect():
    global _socket
    # TODO: Is this a reasonable check? `_socket` being None is not great info.
    with _socket_lock:
        # TODO: Something closer to `emacs_context.matches`
        if emacs_focussed() and not _socket:
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
                        LOGGER.info(f'Unexpected error handling message: "{e}"')
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
    global _socket, _socket_lock, voicemacs_connected
    try:
        with _socket_lock:
            if _socket:
                # TODO: Could this sometimes fail?
                try:
                    _socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                _socket.close()
                _socket = None
    except:
        pass
    finally:
        # _notify_with_deadzone(
        #     "Talon", "Voicemacs disconnected", deadzone=DISCONNECT_DEADZONE
        # )
        voicemacs_connected = False


def _handle_message(s, message_string):
    LOGGER.debug(f"Handling message: {message_string}")

    try:
        message = json.loads(message_string)
    except:
        _send(
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
        _send(_make_error(None, "invalid-message", '"nonce" was not provided.'))
    if type_ == -1:
        _send(_make_error(nonce, "invalid-message", '"type" was not provided.'))
    if data == -1:
        _send(_make_error(nonce, "invalid-message", '"data" was not provided.'))
    if direction == -1:
        _send(_make_error(nonce, "invalid-message", '"direction" was not provided.'))
    if not isinstance(type_, str):
        _send(_make_error(nonce, "invalid-message", '"type" must be a string.'))

    if direction == "request":
        _handle_request(nonce, type_, data)
    elif direction == "response":
        _handle_response(nonce, type_, data)
    else:
        _send(
            _make_error(
                nonce,
                "invalid-message",
                '"direction" must be "message" or "response".',
            ),
        )


def _handle_request(nonce: Optional[int], type_: str, data: dict):
    if type_ == "update":
        try:
            key = data["key"]
            value = data["value"]
            emacs_state.update({key: value})
        except Exception as e:
            _send(
                _make_error(
                    nonce, "internal-error", f'An internal error occurred: "{e}"'
                ),
            )
            return
        _send(_make_response(nonce, "confirm-update", {"key": key}))
    else:
        _send(
            _make_error(
                nonce,
                "invalid-request",
                f'Invalid request type: "{type_}". Ensure both server & client are up to date.',
            ),
        )


def _handle_response(nonce: Optional[int], type_: str, data: dict):
    # TODO: Timeout on callback? So it won't be called if the response comes in
    #   after the timeout.
    with _pending_lock:
        deferred = _pending_requests.get(nonce)
        if deferred:
            deferred.set((type_, data))
            del _pending_requests[nonce]


def _authenticate(auth_key) -> None:
    deferred = _send_request("authenticate", {"key": auth_key})
    type_, data = deferred.get(timeout=_AUTH_TIMEOUT)
    if type_ == "authentication-successful":
        return
    elif type_ == "error":
        raise ServerError("Authentication failed", type_, data)
    else:
        raise ServerError("Unknown response type", type_, data)


def rpc_call(method: str, params: List = [], async_: bool = False, timeout=5):
    deferred = send_request(
        "json-rpc-call",
        {
            # RPC call has to be sent as an *encoded* string.
            #
            # TODO: This is because of the separation in `json-rpc-server.el`.
            #   Remove that abstraction in the Emacs package?
            "call": json.dumps(
                {
                    "jsonrpc": "2.0",
                    # Just use the request nonce for the ID. It will be unique.
                    "id": str(_outgoing_nonce),
                    "method": method,
                    "params": params,
                }
            ),
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
    response = _send_request(type_, data)
    return response


def _send_request(type_: str, data: dict) -> DeferredResult:
    global _outgoing_nonce
    deferred = DeferredResult()
    # TODO: Maybe a better name for this lock now it also guards the outgoing
    #   nonce?
    with _pending_lock:
        # This will be used by the receiver to set the deferred result & invoke
        # the callback.
        nonce = _outgoing_nonce
        _outgoing_nonce += 1
        _pending_requests[_outgoing_nonce] = deferred
    _send(_make_request(_outgoing_nonce, type_, data))
    return deferred


def _send(message: dict):
    with _socket_lock:
        if not _socket:
            raise RuntimeError("Voicemacs not connected.")
        message_str = "\0" + json.dumps(message) + "\0"
        # TODO: Force D/C on error here?
        encoded_message = message_str.encode()
        try:
            _socket.sendall(encoded_message)
        except Exception as e:
            _force_disconnect()


def _ping():
    """Ping the socket to ensure it's alive & trigger latent disconnects.

    (This is done manually because Emacs seems to have dodgy support for TCP
    keepalive.)

    """
    with _socket_lock:
        if emacs_focussed() and _socket:
            try:
                # TODO: Why pending lock here
                with _pending_lock:
                    # TODO: What if the second half of a message gets dropped, will
                    #   this still work?
                    _socket.sendall("\0\1\0".encode())
            except:
                # Seems like even with this, sometimes the receive thread D/C isn't
                # triggered. Just force it.
                _force_disconnect()


def run_command(command, prefix_arg=None):
    # TODO: Still need to pause if e.g. a key was just pressed? Can it still
    #   inject too early?
    #
    # FIXME: With e.g. the it commands, this is too fast. Need to ensure the
    #   stuff gets into the command loop, I think.
    result = rpc_call("voicemacs-inject-command", params=[command, prefix_arg])
    # If a key is pressed too soon after injecting a command, it can cause a
    # race condition where Emacs processes the keypress before the injected
    # command. Injection is already hacky, pushing events into Emacs' internal
    # event loop - fixing this may be impossible without modifying Emacs' source
    # code. So, to avoid the race, just wait after injecting.
    actions.sleep(POST_COMMAND_INJECTION_WAIT)
    return result


# TODO: An overlay that shows voicemacs connection status (iff Emacs is active)


# -----------------------------------------------------------------------------
# - Canvas showing the connection state

connection_canvas = None
canvas_connection_state = None
canvas_screen = None


def redraw_connection_state(canvas):
    global canvas_connection_state
    color = "7bc44f" if voicemacs_connected else "d30000"
    canvas_connection_state = voicemacs_connected

    midpoint = int(round(canvas.width / 2))
    paint = canvas.paint
    paint.antialias = True
    paint.color = color

    # TODO: Scale based on DPI, not resolution
    half_bar_width = max(30, int(round(canvas_screen.width / 40)))
    bar_height = max(2, int(round(canvas_screen.height / 300)))
    corner_diam = int(math.floor(bar_height / 2))
    draw_rect = Rect(
        canvas.x + midpoint - half_bar_width,
        canvas.y,
        half_bar_width * 2,
        bar_height - corner_diam,
    )
    canvas.draw_rect(draw_rect)
    draw_rect.height = bar_height
    canvas.draw_round_rect(draw_rect, corner_diam, corner_diam)


def delete_canvas():
    global connection_canvas
    if connection_canvas:
        connection_canvas.unregister("draw", redraw_connection_state)
        connection_canvas.close()
        connection_canvas = None


def _calc_canvas_rect(emacs_window):
    # Bound the canvas to the edges of the screen - even if the window is poking
    # off.
    result = emacs_window.rect.intersect(emacs_window.screen.rect)
    # HACK: If we use the full height, screen goes black on Windows 11, so just
    #   take 1 off it.
    result.height -= 1
    # FIXME: Why have a full-screen canvas? Make it only as large as necessary.
    return result


_prior_emacs_rect = None


def _update_overlay():
    global connection_canvas, _prior_emacs_rect, canvas_screen
    if emacs_focussed():
        active_window = ui.active_window()
        if connection_canvas and active_window.rect != _prior_emacs_rect:
            # Layout has changed - just reset the canvas to reposition the bar.
            connection_canvas.rect = _calc_canvas_rect(active_window)
            _old_window_rect = active_window.rect
            canvas_screen = active_window.screen
            connection_canvas.resume()
            connection_canvas.freeze()
        if not connection_canvas:
            # Need to create a new canvas
            #
            canvas_rect = _calc_canvas_rect(active_window)
            connection_canvas = canvas.Canvas(*canvas_rect)
            # HACK: Canvas isn't being created with the dimensions specified
            #   (win 10), so manually set it.
            # FIXME: Report canvas being created with wrong rect as a bug
            connection_canvas.rect = canvas_rect
            canvas_screen = active_window.screen
            connection_canvas.register("draw", redraw_connection_state)
            connection_canvas.freeze()
        elif canvas_connection_state != voicemacs_connected:
            connection_canvas.resume()
            connection_canvas.freeze()
    else:
        delete_canvas()


# -----------------------------------------------------------------------------


cron.interval(f"{_CONNECT_ATTEMPT_INTERVAL}ms", _try_connect)
# HACK: Disconnect doesn't always trigger in the receive thread until a message
#   is sent. Manually ping to trigger these D/Cs.
#
# FIXME: Something is causing Talon to silently deadlock. I think it's Voicemacs
#   and I think it's probably the message system deadlocking.
cron.interval(f"{_PING_INTERVAL}ms", _ping)
cron.interval("100ms", _update_overlay)
