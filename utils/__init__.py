from talon import resource, actions, clip, app, Module, registry
import json
import platform
import time
import logging
import threading
from functools import wraps
import re
from pathlib import Path


ON_WINDOWS = platform.system() == "Windows"
ON_LINUX = platform.system() == "Linux"
ON_MAC = platform.system() == "Darwin"

# TODO: Switch this to `actions.path.talon_user` when possible
user_dir = Path(__file__).parents[1]


module = Module()


# overrides are used as a last resort to override the output. Some uses:
# - frequently misheard words
# - force homophone preference (alternate homophones can be accessed with homophones command)

# To add an override, add the word to override as the key and desired replacement as value in overrides.json
try:
    with resource.open(user_dir / "overrides.json") as f:
        mapping = json.load(f)
except Exception as e:
    app.notify(str(e))
    mapping = {}

# used for auto-spacing
punctuation = set(".,-!?")


# TODO: Remove all the old functions here I'm no longer using.


def remove_dragon_junk(word):
    return str(word).lstrip("\\").split("\\", 1)[0]


def parse_word(word):
    word = remove_dragon_junk(word)
    word = mapping.get(word.lower(), word)
    return word


def join_words(words, sep=" "):
    out = ""
    for i, word in enumerate(words):
        if i > 0 and word not in punctuation:
            out += sep
        out += word
    return out


def parse_words(m):
    return list(map(parse_word, m.dgndictation.words))


def insert(s):
    Str(s)(None)


def text(m):
    insert(join_words(parse_words(m)).lower())


def sentence_text(m):
    text = join_words(parse_words(m)).lower()
    insert(text.capitalize())


def word(m):
    text = extract_word(m)
    insert(text.lower())


def extract_word(m):
    return join_words(list(map(parse_word, m.dgnwords.words)))


# FIX ME
def surround(by):
    def func(i, word, last):
        if i == 0:
            word = by + word
        if last:
            word += by
        return word

    return func


# support for parsing numbers as command postfix
def numeral_map():
    numeral_map = dict((str(n), n) for n in range(0, 20))
    for n in [20, 30, 40, 50, 60, 70, 80, 90]:
        numeral_map[str(n)] = n
    numeral_map["oh"] = 0  # synonym for zero
    return numeral_map


def numerals():
    return " (" + " | ".join(sorted(numeral_map().keys())) + ")+"


def optional_numerals():
    return " (" + " | ".join(sorted(numeral_map().keys())) + ")*"


def text_to_number(m):
    tmp = [str(s).lower() for s in m]
    words = [parse_word(word) for word in tmp]

    result = 0
    factor = 1
    for word in reversed(words):
        if word not in optional_numerals():
            # we consumed all the numbers and only the command name is left.
            break

        result = result + factor * int(numeral_map()[word])
        factor = 10 * factor

    return result


number_conversions = {"oh": "0"}  # 'oh' => zero
for i, w in enumerate(
    ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
):
    number_conversions[str(i)] = str(i)
    number_conversions[w] = str(i)
    number_conversions["%s\\number" % (w)] = str(i)


def parse_words_as_integer(words):
    # TODO: Once implemented, use number input value rather than manually
    # parsing number words with this function

    # Ignore any potential non-number words
    number_words = [w for w in words if str(w) in number_conversions]

    # Somehow, no numbers were detected
    if len(number_words) == 0:
        return None

    # Map number words to simple number values
    number_values = list(map(lambda w: number_conversions[w.word], number_words))

    # Filter out initial zero values
    normalized_number_values = []
    non_zero_found = False
    for n in number_values:
        if not non_zero_found and n == "0":
            continue
        non_zero_found = True
        normalized_number_values.append(n)

    # If the entire sequence was zeros, return single zero
    if len(normalized_number_values) == 0:
        normalized_number_values = ["0"]

    # Create merged number string and convert to int
    return int("".join(normalized_number_values))


class Modifiers(object):
    """Context manager that holds down modifiers during the context."""

    def __init__(self, modifiers):
        # Catch easy mistake that otherwise will bite later
        assert not isinstance(
            modifiers, str
        ), "Provide a list of modifiers, not one modifier."
        self.modifiers = modifiers

    def __enter__(self):
        for modifier in self.modifiers:
            actions.key(f"{modifier}:down")

    def __exit__(self, *_):
        for modifier in self.modifiers:
            actions.key(f"{modifier}:up")


class WaitForClipChange:
    """Context manager that only exits when the clipboard has changed."""

    def __init__(self, timeout=2):
        self.original_clip = None
        self.timeout = timeout
        self.end_time = None

    def __enter__(self):
        self.original_clip = clip.get()
        self.end_time = time.monotonic() + self.timeout

    def __exit__(self, *_):
        while clip.get() == self.original_clip:
            if time.monotonic() > self.end_time:
                raise TimeoutError("Clipboard did not change before timeout.")
            else:
                time.sleep(0.01)


def clip_set_safe(new_value, timeout=2):
    """Set clipboard to `new_value`"""
    if clip.get() == new_value:
        return
    with WaitForClipChange(timeout):
        clip.set_text(new_value)


class PreserveClipboard:
    def __init__(self):
        self.old_clipboard = None

    def __enter__(self):
        self.old_clipboard = clip.get()

    def __exit__(self, *_):
        time.sleep(0.1)
        clip.set_text(self.old_clipboard)


def preserve_clipboard(fn):
    @wraps(fn)
    def wrapped_function(*args, **kwargs):
        with PreserveClipboard():
            return fn(*args, **kwargs)

    return wrapped_function


@preserve_clipboard
def jump_to_target(target):
    press("cmd-left", wait=2000)
    press("cmd-shift-right", wait=2000)
    press("cmd-c", wait=2000)
    press("left", wait=2000)
    line = clip.get()
    print("LINE")
    print(line)
    result = line.find(target)
    if result == -1:
        return
    for i in range(0, result):
        press("right", wait=0)
    for i in range(0, len(target)):
        press("shift-right")
    press("right", wait=0)


def chain(*commands, pause=0.05):
    """Chain multiple commands together.

    Creates a function that (when executed) calls each ``command``, one by one,
    pausing between each. Arguments are passed through directly. Designed to
    create a chain of speech commands, but it will work with any list of
    callables.

    """
    for command in commands:
        assert callable(command), "Positional arguments must all be callable"

    def do_commands(*args, **kwargs):
        nonlocal commands, pause
        for command in commands:
            command(*args, **kwargs)
            time.sleep(pause)

    return do_commands


def dictify(list_):
    """Pull `list_` into a dict where each item maps to itself.

    >>> dictify(["a", "b", "c"])
    {"a": "a", "b": "b", "c": "c"}

    """
    return {element: element for element in list_}


# TODO: Rename to `expand_map`
def multi_map(mapping):
    """Meta-function to allow multiple strings to be mapped to one value.

    The input `mapping` will be expanded like this:

    >>> multi_map({"a": "1", ("b", "c", "d"): "2"})
    {"a": "1", "b": "2", "c": "2", "d": "2"}

    (Note we use a tuple as the key because dictionary keys must be hashable).

    """
    result = {}
    for key, value in mapping.items():
        if isinstance(key, tuple):
            # Map each list element individually
            for element in key:
                result[element] = value
        else:
            result[key] = value
    return result


# TODO: Rename to `apply_dict`
def apply_function(function, dict_):
    """Apply a function to each value in a dict."""
    for command, args in dict_.items():
        dict_[command] = function(*args)
    return dict_


def invalid_platform(*_, **__):
    raise NotImplementedError("Not implemented on this platform.")


# def ctrl_cmd(key):
#     """Press a key with ctrl on Windows/Linux, cmd on Mac."""
#     # TODO 1: Move to newapi
#     if ON_WINDOWS or ON_LINUX:
#         return Key(f"ctrl-{key}")
#     elif ON_MAC:
#         return Key(f"cmd-{key}")
#     else:
#         # TODO: Add this to utils
#         invalid_platform()


def prepend_to_map(arg, dict_):
    """Prepend ``arg`` to each value in ``dict_``.

    For example:

    >>> prepend_arg("tuna", {"a": [1, 2], "b": [3, 4, 5]})
    {"a": ["tuna", 1, 2], "b": ["tuna", 3, 4, 5]}

    Use to make maps with many instances of identical data more concise.

    """
    for key, arg_list in dict_.items():
        # TODO: Documentation implies this is a list. Should it be a tuple like
        #   this?
        dict_[key] = (arg, *arg_list)
    return dict_


class Hook(object):
    """Emacs-style hook, allows arbitrary functions to be run at specific times.

    When the hook is `run`, every function attached to the hook is executed.
    Exceptions will not interrupt subsequent functions.

    """

    def __init__(self):
        self._lock = threading.Lock()
        self._functions = []

    def add(self, function_):
        """Add a function to the hook.

        The function will be called whenever the hook is run.

        """
        with self._lock:
            self._functions.append(function_)

    def remove(self, function_):
        """Remove a function from the hook. See `add`.

        Will not raise an error if the function is absent.

        """
        with self._lock:
            try:
                self._functions.remove(function_)
            except AttributeError:
                pass

    def run(self, *args, **kwargs):
        """Run all functions attached to the hook.

        Provide ``args`` or ``kwargs`` to run the functions with arguments.

        Errors will be logged, but otherwise ignored.

        """
        with self._lock:
            functions_copy = self._functions
        for func in functions_copy:
            try:
                func(*args, **kwargs)
            except Exception as e:
                logging.exception(f"Error running hooked function")


def echo(value, prompt="Value"):
    """Debug function to print a value, then return it.

    Talon debugging is limited. Wrap any value with this function to echo it
    without affecting functionality.

    """
    print(f"{prompt}: {value}")
    return value


_RE_DOUBLE_SPACES = re.compile("  +")


def single_spaces(text: str) -> str:
    """Return ``text``, but with instances of multiple spaces removed."""
    return _RE_DOUBLE_SPACES.sub(" ", text)


# TODO: This is repeated from the numbers module, probably
spoken_digits = {
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "0": "zero",
}


def _digits_to_words(text: str) -> str:
    """convert digits in ``text`` to their English words.

    Note this will NOT create multiple-digit forms. Digits will be separated."""
    for digit, english in spoken_digits.items():
        text = text.replace(digit, f" {english} ")
    return single_spaces(text)


_RE_NONALPHABETIC_CHARS = re.compile(r"[^a-zA-Z]+")


def spoken_form(text: str) -> str:
    """Convert ``text`` into a format compatible with speech lists."""
    # TODO: Replace numeric digits with spoken digits
    text = text.replace("'", " ")
    text = _digits_to_words(text)
    text = _RE_NONALPHABETIC_CHARS.sub(" ", text)
    return text.strip()


def expand_acronym(acronym: str) -> str:
    """Create a spoken form for an acronym, e.g. "mp3" -> "M P three"."""
    return spoken_form(" ".join(acronym).upper())


_recent_notifications = {}
_notifications_lock = threading.Lock()


@module.action
def notify(
    title: str = "",
    subtitle: str = "",
    body: str = "",
    sound: bool = False,
    deadzone: str = "",
) -> None:
    """Wraps `app.notify`, with optional deadzone to avoid notification spam."""
    global _notifications_lock, _private_notifications
    with _notifications_lock:
        if args not in _recent_notifications:
            if deadzone:
                # We suppress future notifications in the deadzone
                notification_id = (title, subtitle, body)
                _private_notifications += notification_id

                def purge_notification():
                    """Remove the notification from the set of recent ones."""
                    nonlocal notification_id
                    global _notifications_lock, _private_notifications
                    with _notifications_lock:
                        _private_notifications.remove(notification_id)

                cron.after(deadzone, purge_notification)
            return app.notify(title, subtitle, body, sound)


def context_active(context):
    """Is `context` currently active?

    WARNING: Only call this on the main thread.

    """
    raise RuntimeError(
        "Don't check for active contexts like this. It can race. Use a tag instead."
    )
    # FIXME: This can race, `active_contexts` changing under us. No idea how to
    #   fix it.
    return context in registry.active_contexts()
