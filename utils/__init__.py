from talon.voice import Str, press, Key
import talon.clip as clip
from talon import resource, actions
import json
import platform
import time
import logging
import threading
from functools import wraps


ON_WINDOWS = platform.system() == "Windows"
ON_LINUX = platform.system() == "Linux"
ON_MAC = platform.system() == "Darwin"


# overrides are used as a last resort to override the output. Some uses:
# - frequently misheard words
# - force homophone preference (alternate homophones can be accessed with homophones command)

# To add an override, add the word to override as the key and desired replacement as value in overrides.json
mapping = json.load(resource.open("../overrides.json"))

# used for auto-spacing
punctuation = set(".,-!?")


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
        self.modifiers = modifiers

    def __enter__(self):
        for modifier in self.modifiers:
            actions.key(f"{modifier}:down")

    def __exit__(self, *_):
        for modifier in self.modifiers:
            actions.key(f"{modifier}:up")


class PreserveClipboard:
    def __init__(self):
        self.old_clipboard = None

    def __enter__(self):
        self.old_clipboard = clip.get()

    def __exit__(self, *_):
        time.sleep(0.1)
        clip.set(self.old_clipboard)


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


def apply_function(function, dict_):
    """Apply a function to each value in a dict."""
    for command, args in dict_.items():
        dict_[command] = function(*args)
    return dict_


def invalid_platform(*_, **__):
    raise NotImplementedError("Not implemented on this platform.")


def ctrl_cmd(key):
    """Press a key with ctrl on Windows/Linux, cmd on Mac."""
    if ON_WINDOWS or ON_LINUX:
        return Key(f"ctrl-{key}")
    elif ON_MAC:
        return Key(f"cmd-{key}")
    else:
        # TODO: Add this to utils
        invalid_platform()


def prepend_to_map(arg, dict_):
    """Prepend ``arg`` to each value in ``dict_``.

    For example:

    >>> prepend_arg("tuna", {"a": [1, 2], "b": [3, 4, 5]})
    {"a": ["tuna", 1, 2], "b": ["tuna", 3, 4, 5]}

    Use to make maps with many instances of identical data more concise.

    """
    for key, arg_list in dict_.items():
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
