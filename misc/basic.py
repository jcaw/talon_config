from talon import app, ctrl
from talon.voice import Context, Str, press
import string

from . import numbers
from user.utils import dictify, multi_map

defaults = "air bat cap drum each fine gust harp sit jury crunch look made near odd pit quench red sun trap urge vest whale plex yank zip".split()
# With modifications for things that aren't recognizing well on this end.
modified_defaults = (
    " ".join(defaults)
    .replace("air", "arch")
    .replace("bat", "batch")
    .replace("zip", "zen")
    .split()
)
# my_old_alphabet = "arch brov char dell ed fomp goof hark ice jinks koop lug mowsh nerb ork pooch quash rosh souk tech unks verge womp trex yang zooch".split()
phonetic_alphabet = modified_defaults

alphabet = dict(zip(phonetic_alphabet, string.ascii_lowercase))


# FIXME: F keys don't work under Windows Dragon - guessing they might be
#   reserved, I don't think they work under NatLink either.
def make_f_keys():
    f_numbers = {
        **numbers.DIGITS,
        "ten": "10",
        "eleven": "11",
        "twelve": "12",
        "thirteen": "13",
    }
    del f_numbers["zero"]
    return {f"F {i}": f"f{i}" for spoken, i in f_numbers.items()}


f_keys = make_f_keys()
# we keep simple arrows separate because "up" has a high false positive rate.
# It's replaced with "pup".
arrows = {"pup": "up", **dictify(["down", "right", "left"])}
simple_keys = dictify(
    [
        "tab",
        "escape",
        "enter",
        "space",
        "pageup",
        "pagedown",
        "backspace",
        "delete",
        "home",
        "end",
    ]
)
alternate_keys = {
    # b[ackward k]ill
    "bill": "backspace",
    # f[orward k]ill
    "fill": "delete",
    # "pat": "space",
    "pack": "space",
    "scape": "escape",
    "knock": "end",
}
symbols = multi_map(
    {
        ("back tick", "grave"): "`",
        ("comma", "cam"): ",",
        ("dot", "period", "full stop"): ".",
        ("semicolon", "semi"): ";",
        ("apostrophe", "quote"): "'",
        ("double quote", "speech mark", "speech"): '"',
        # Parens
        ("lub", "left paren"): "(",
        ("rub", "right paren"): ")",
        "parens": "( ) left",
        # Curly Braces
        ("lace", "left brace"): "{",
        ("race", "right brace"): "}",
        "braces": "{ } left",
        # Square Braces
        ("lack", "left square"): "[",
        ("rack", "right square"): "]",
        "squares": "[ ] left",
        # Angles
        ("langle", "less than"): "<",
        ("rangle", "greater than"): ">",
        "angles": "< > left",
        # Currency
        "dollar": "$",
        "pound": "£",
        "euro": "€",  # FIXME: types "4"
        # Unsorted
        ("forward slash", "slash"): "/",
        "backslash": "\\",
        "plus": "+",
        ("minus", "dash"): "-",
        ("equals", "eek"): "=",
        "hash": "#",
        ("question mark", "question", "quess"): "?",
        ("exclamation", "exclamation mark", "bang"): "!",
        "tilde": "~",
        ("underscore", "score"): "_",
        ("colon", "coal"): ":",
        ("asterisk", "star"): "*",
        ("percent", "mod"): "%",
        "caret": "^",
        "at sign": "@",
        ("ampersand", "amper"): "&",
        "pipe": "|",
    }
)
modifiers = multi_map(
    {("control", "troll"): "ctrl", ("shift", "schiff"): "shift", "alt": "alt"}
)
if app.platform == "mac":
    modifiers["command"] = "cmd"
    modifiers["super"] = "cmd"
    modifiers["option"] = "alt"
elif app.platform == "windows":
    modifiers["windows"] = "win"
    modifiers["super"] = "win"
elif app.platform == "linux":
    modifiers["super"] = "super"

keys = {
    #
    **f_keys,
    **simple_keys,
    **alternate_keys,
    **symbols,
}

# map alnum and keys separately so engine gives priority to letter/number repeats
keymap = {
    #
    **keys,
    **arrows,
    **alphabet,
    **numbers.DIGITS,
}


def insert(s):
    Str(s)(None)


def get_modifiers(m):
    try:
        return [modifiers[mod] for mod in m["modifiers_list"]]
    except KeyError:
        return []


def get_keys(m):
    groups = [
        "keys_list",
        "arrows_list",
        "digits_list",
        "alphabet_list",
        "full_keymap_list",
    ]
    for group in groups:
        try:
            return [keymap[k] for k in m[group]]
        except KeyError:
            pass
    return []


def uppercase_letters(m):
    insert("".join(get_keys(m)).upper())


def press_keys(m):
    mods = get_modifiers(m)
    keys = get_keys(m)
    if mods:
        press("-".join(mods + [keys[0]]))
        keys = keys[1:]
    for k in keys:
        press(k)


class Modifiers(object):
    """Context manager that holds down modifiers during the context."""

    def __init__(self, modifiers):
        self.modifiers = modifiers

    # TODO: Replace these with key actions once they support up and down.
    def __enter__(self):
        for modifier in self.modifiers:
            ctrl.key_press(modifier, down=True)

    def __exit__(self, *_):
        for modifier in self.modifiers:
            ctrl.key_press(modifier, up=True)


ctx = Context("basic")
ctx.keymap(
    {
        "(uppercase | ship) {basic.alphabet}+ [(lowercase | sunk)]": uppercase_letters,
        "{basic.modifiers}* {basic.alphabet}+": press_keys,
        # Force straight numbers to be spoken with a prefix to avoid ambiguity
        # with repeats.
        "numb {numbers.digits}++": press_keys,
        # Allow the "numb" pattern to be used wherever we input number keys,
        # but don't make it mandatory.
        "{basic.modifiers}+ [numb] {numbers.digits}++": press_keys,
        "{basic.modifiers}* {basic.keys}+": press_keys,
        "{basic.modifiers}* {basic.arrows}+": press_keys,
    }
)
ctx.set_list("alphabet", alphabet.keys())
ctx.set_list("arrows", arrows.keys())
ctx.set_list("keys", keys.keys())
ctx.set_list("full_keymap", keymap.keys())
ctx.set_list("modifiers", modifiers.keys())
