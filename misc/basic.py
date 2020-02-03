from talon import app
from talon.voice import Context, Str, press
import string

from . import numbers

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

simple_keys = ["tab", "escape", "enter", "space", "pageup", "pagedown"]
alternate_keys = {"delete": "backspace", "forward delete": "delete"}
symbols = {
    "back tick": "`",
    "comma": ",",
    "dot": ".",
    "period": ".",
    "semi": ";",
    "semicolon": ";",
    "quote": "'",
    "L square": "[",
    "left square": "[",
    "square": "[",
    "R square": "]",
    "right square": "]",
    "forward slash": "/",
    "slash": "/",
    "backslash": "\\",
    "minus": "-",
    "dash": "-",
    "equals": "=",
}
modifiers = {
    "control": "ctrl",
    "shift": "shift",
    "alt": "alt",

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
}
if app.platform == "mac":
    modifiers["command"] = "cmd"
    modifiers["option"] = "alt"
elif app.platform == "windows":
    modifiers["windows"] = "win"
elif app.platform == "linux":
    modifiers["super"] = "super"

simple_keys = {k: k for k in simple_keys}
keys = {}
keys.update(f_keys)
keys.update(simple_keys)
keys.update(alternate_keys)
keys.update(symbols)

# map alnum and keys separately so engine gives priority to letter/number repeats
keymap = keys.copy()
keymap.update(arrows)
keymap.update(alphabet)
keymap.update(numbers.DIGITS)


def insert(s):
    Str(s)(None)


def get_modifiers(m):
    try:
        return [modifiers[mod] for mod in m["modifiers_list"]]
    except KeyError:
        return []


def get_keys(m):
    groups = ["keys_list", "arrows_list", "digits_list", "alphabet_list"]
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
ctx.set_list("modifiers", modifiers.keys())
