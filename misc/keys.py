"""Basic key mapping.

Originally written by lunixbochs, version taken from the knausj_talon repo:
https://github.com/knausj85/knausj_talon/blob/d330a6eb1fbfcc13f99a732a097f220fd0c10950/code/keys.py

"""


from typing import Set, List

from talon import Module, Context, actions

from user.utils import multi_map, dictify


default_alphabet = "air bat cap drum each fine gust harp sit jury crunch look made near odd pit quench red sun trap urge vest whale plex yank zip"
# My setup has trouble with some words. Probably my accent.
modified_alphabet = (
    default_alphabet.replace("air", "arch")
    .replace("bat", "batch")
    .replace("zip", "zen")
)
# chosen_alphabet = default_alphabet.split(" ")
chosen_alphabet = modified_alphabet.split(" ")
letters_string = "abcdefghijklmnopqrstuvwxyz"

# TODO: Use digits in number.py?
default_digits = "zero one two three four five six seven eight nine".split(" ")
ints = [str(i) for i in range(10)]

mod = Module()
mod.list("letter", desc="The spoken phonetic alphabet")
mod.list("symbol", desc="All symbols from the keyboard")
mod.list("arrow", desc="All arrow keys")
mod.list("standalone_arrow", desc="Arrow keys that can be spoken on their own")
mod.list("number", desc="All number keys")
mod.list("modifier", desc="All modifier keys")
mod.list("special", desc="All special keys")


@mod.capture
def modifiers(m) -> Set[str]:
    """Zero or more modifier keys"""


@mod.capture
def arrow(m) -> str:
    """One directional arrow key"""


@mod.capture
def arrows(m) -> str:
    """One or more arrows separate by a space"""


@mod.capture
def standalone_arrow(m) -> str:
    """One arrow that can be spoken on its own (without modifiers).

    Standalone arrows are separated to avoid "up" being misrecognized.

    """


@mod.capture
def number_key(m) -> str:
    """One number key"""


@mod.capture
def number_keys(m) -> str:
    """Multiple number keys"""


@mod.capture
def letter(m) -> str:
    """One letter key"""


@mod.capture
def letters(m) -> list:
    """Multiple letter keys"""


@mod.capture
def symbol(m) -> str:
    """One symbol key"""


@mod.capture
def special(m) -> str:
    """One special key"""


@mod.capture
def any_key(m) -> str:
    """Any single key"""


@mod.capture
def keychord(m) -> str:
    """A single key with modifiers"""


@mod.capture
def character(m) -> str:
    """Any key that can be typed as a character."""


ctx = Context()
ctx.lists["self.modifier"] = {
    "command": "cmd",
    "control": "ctrl",
    "troll": "ctrl",
    "shift": "shift",
    "schiff": "shift",
    "sky": "shift",
    "alt": "alt",
    "option": "alt",
    "super": "super",
}

ctx.lists["self.letter"] = dict(zip(chosen_alphabet, letters_string))
ctx.lists["self.symbol"] = multi_map(
    {
        ("enter", "return", "slap"): "enter",
        ("back tick", "grave"): "`",
        ("comma", "cam"): ",",
        ("dot", "period", "full stop", "point"): ".",
        ("semicolon", "semi"): ";",
        ("apostrophe", "quote"): "'",
        ("double quote", "dub quote", "speech mark", "speech"): '"',
        # FIXME: slash and blash recognition conflicts
        ("forward slash", "slash"): "/",
        ("backslash", "blash"): "\\",
        ("minus", "dash"): "-",
        ("equals", "eek"): "=",
        "plus": "+",
        ("question mark", "question", "quest"): "?",
        "tilde": "~",
        ("exclamation", "bang"): "!",
        ("dollar sign", "dollar"): "$",
        ("underscore", "score"): "_",
        ("colon", "coal"): ":",
        ("asterisk", "star"): "*",
        # "pound": "#",
        "hash": "#",
        "percent": "%",
        "caret": "^",
        "at sign": "@",
        ("ampersand", "amper"): "&",
        "pipe": "|",
        # Currency
        "dollar": "$",
        "pound": "£",
        "euro": "€",  # FIXME: comes out as "4"
        # Brackets
        ("left square", "lack"): "[",
        ("right square", "rack"): "]",
        "squares": "[ ] left",
        ("left paren", "lub"): "(",
        ("right paren", "rub"): ")",
        "parens": "( ) left",
        ("left brace", "lace"): "{",
        ("right brace", "race"): "}",
        "braces": "{ } left",
        ("left angle", "langle"): "<",
        ("right angle", "rangle"): ">",
        "angles": "< > left",
    }
)

ctx.lists["self.number"] = dict(zip(default_digits, ints))
basic_arrows = dictify(
    [
        #
        "left",
        "right",
        "down",
    ]
)
ctx.lists["self.arrow"] = {
    #
    **basic_arrows,
    "up": "up",
}
ctx.lists["self.standalone_arrow"] = {
    #
    **basic_arrows,
    "pup": "up",
}
# TODO: Separate standalone arrow list, use "pup" or something similar to
#   mitigate "up" misrecognition

simple_keys = dictify(
    [
        #
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
    #
    # b[ackward k]ill
    "bill": "backspace",
    # f[orward k]ill
    "fill": "delete",
    "scape": "escape",
    "knock": "end",
}
keys = {**simple_keys, **alternate_keys}
ctx.lists["self.special"] = keys


@ctx.capture(rule="[{self.modifier}+]")
def modifiers(m) -> Set[str]:
    try:
        return set(m.modifier)
    except AttributeError:
        return set()


@ctx.capture(rule="{self.arrow}")
def arrow(m) -> str:
    return m.arrow


@ctx.capture(rule="<self.arrow>+")
def arrows(m) -> str:
    return m.arrow_list


@ctx.capture(rule="{self.standalone_arrow}")
def standalone_arrow(m) -> str:
    return m.standalone_arrow


@ctx.capture(rule="numb <digits>")
def number_key(m):
    return str(m.digits)


@ctx.capture(rule="numb <number>")
def number_keys(m):
    return str(m.number)


@ctx.capture(rule="{self.letter}")
def letter(m):
    return m.letter


@ctx.capture(rule="{self.special}")
def special(m):
    return m.special


@ctx.capture(rule="{self.symbol}")
def symbol(m):
    return m.symbol


@ctx.capture(
    rule="(<self.arrow> | <number> | <self.letter> | <self.special> | <self.symbol>)"
)
def any_key(m) -> str:
    return str(m[0])


@ctx.capture(rule="{self.modifier}+ <self.any_key>")
def keychord(m) -> str:
    return "-".join(m.modifier_list + [m.any_key])


@ctx.capture(rule="{self.letter}+")
def letters(m):
    return m.letter


@ctx.capture(rule="(<self.letter> | <self.symbol> | <self.number_key>)")
def character(m) -> str:
    return m[0]


@mod.action_class
class Actions:
    def modifier_key(modifier: str, key: str):
        """(TEMPORARY) Presses the modifier plus supplied number"""
        res = "-".join([modifier, str(key)])
        actions.key(res)

    def uppercase_letters(chars: List[str]):
        """Inserts uppercase letters from list"""
        # TODO: Do we want insert here? What if someone wants to press an
        #   uppercase char?
        actions.insert("".join(chars).upper())

    # TODO: Switch to many_keys
    def many(keys: List[str]):
        """Press a list of keys in sequence."""
        for key in keys:
            actions.key(key)

    def press_number(number: float):
        """Press each key in a number"""
        # TODO: Allow leading zeros
        for char in str(number):
            actions.key(char)
