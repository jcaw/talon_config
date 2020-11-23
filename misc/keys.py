"""Basic key mapping.

Originally written by lunixbochs, version taken from the knausj_talon repo:
https://github.com/knausj85/knausj_talon/blob/d330a6eb1fbfcc13f99a732a097f220fd0c10950/code/keys.py

"""


from typing import Set, List

from talon import Module, Context, actions

from user.utils import dictify, multi_map, spoken_form


default_alphabet = "air bat cap drum each fine gust harp sit jury crunch look made near odd pit quench red sun trap urge vest whale plex yank zip"
# My setup has trouble with some words. Probably my accent.
modified_alphabet = (
    default_alphabet.replace("air", "arch")
    .replace("bat", "batch")
    .replace("harp", "hip")
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
mod.list("complex_symbol", desc="Symbols that take multiple characters, e.g. := or ->")


ctx = Context()
ctx.lists["self.modifier"] = {
    "command": "cmd",
    "control": "ctrl",
    "troll": "ctrl",
    "shift": "shift",
    "schiff": "shift",
    # TODO: Sky should affect multiple characters.
    "sky": "shift",
    "alt": "alt",
    "option": "alt",
    "super": "super",
}

ctx.lists["self.letter"] = dict(zip(chosen_alphabet, letters_string))
ctx.lists["self.symbol"] = multi_map(
    {
        ("back tick", "grave"): "`",
        ("comma", "cam"): ",",
        ("dot", "period", "full stop"): ".",
        ("semicolon", "semi"): ";",
        ("apostrophe", "post", "poess"): "'",
        ("speech mark", "speech", "quote"): '"',
        # FIXME: slash and blash recognition conflicts
        ("forward slash", "slash"): "/",
        ("backslash", "blash"): "\\",
        ("minus", "dash"): "-",
        (
            "equals",
            # "eek",
            "quals",
            "qual",
        ): "=",
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
        ("left paren", "lub"): "(",
        ("right paren", "rub"): ")",
        ("left brace", "lace"): "{",
        ("right brace", "race"): "}",
        ("left angle", "langle"): "<",
        ("right angle", "rangle"): ">",
        ("space", "gap"): " ",
        # TODO: Extract these into a separate list
        ("walrus", "wally"): ": =",
        "rittoe": "- >",
        "leffoe": "< -",
        "riteek": "= >",
        "leffeek": "< =",
    }
)

ctx.lists["self.number"] = dict(zip(default_digits, ints))
basic_arrows = {
    "left": "left",
    # Allow dropping the "t" in left
    "leff": "left",
    "right": "right",
    "down": "down",
}
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


# TODO: Merge these into one dictionary, use multi map
simple_keys = dictify(
    [
        #
        "tab",
        "escape",
        "enter",
        "pageup",
        "pagedown",
        "backspace",
        "delete",
        "home",
        # Interferes with dictation
        # "end",
    ]
)
alternate_keys = {
    # b[ackward k]ill
    "bill": "backspace",
    # f[orward k]ill
    "fill": "delete",
    "scape": "escape",
    "knock": "end",
    # "home" is unreliable and requires a lot of "h" sound - tiring
    "con": "home",
    # Explicitly don't allow "return" because it's a common programming keyword.
    "slap": "enter",
    # TODO: Extract compound keys, shouldn't really be here
    "squares": "[ ] left",
    "parens": "( ) left",
    "braces": "{ } left",
    "angles": "< > left",
    "loon": "end enter",
}
f_keys = {
    # Auto-generate 1-9
    **{spoken_form(f"F {i}"): f"{i}" for i in range(1, 9)},
    "F ten": "f10",
    "F eleven": "f11",
    "F twelve": "f12",
}
keys = {**simple_keys, **alternate_keys}
ctx.lists["self.special"] = keys


@mod.capture(rule="[{self.modifier}+]")
def modifiers(m) -> Set[str]:
    """Zero or more modifier keys"""
    try:
        return set(m.modifier)
    except AttributeError:
        return set()


@mod.capture(rule="{self.arrow}")
def arrow(m) -> str:
    """One directional arrow key"""
    return m.arrow


@mod.capture(rule="<self.arrow>+")
def arrows(m) -> str:
    """One or more arrows separate by a space"""
    return m.arrow_list


@mod.capture(rule="{self.standalone_arrow}")
def standalone_arrow(m) -> str:
    """One arrow that can be spoken on its own (without modifiers).

    Standalone arrows are separated to avoid "up" being misrecognized.

    """
    return m.standalone_arrow


@mod.capture(rule="(numb | num) <digits>")
def number_key(m) -> str:
    """One number key"""
    return str(m.digits)


@mod.capture(rule="(numb | num) <number>")
def number_keys(m) -> str:
    """Multiple number keys"""
    return str(m.number)


@mod.capture(rule="{self.letter}")
def letter(m) -> str:
    """One letter key"""
    return m.letter


@mod.capture(rule="{self.letter}+")
def letters(m) -> list:
    """Multiple letter keys"""
    return m.letter


@mod.capture(rule="{self.symbol}")
def symbol(m) -> str:
    """One symbol key"""
    return m.symbol


@mod.capture(rule="{self.special}")
def special(m) -> str:
    """One special key"""
    return m.special


@mod.capture(
    rule="(<self.arrow> | <self.digit> | <self.letter> | <self.special> | <self.symbol>)"
)
def any_key(m) -> str:
    """Any single key"""
    return str(m[0])


@mod.capture(rule="{self.modifier}+ <self.any_key>")
def keychord(m) -> str:
    """A single key with modifiers"""
    return "-".join(m.modifier_list + [m.any_key])


@mod.capture(rule="(<self.letter> | <self.symbol> | <self.number_key>)")
def character(m) -> str:
    """Any key that can be typed as a character."""
    return m[0]


@mod.capture(rule="<user.character> | {self.complex_symbol}")
def insertable(m) -> str:
    """A char, or a complex insert."""
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

    def type_number(number: float):
        """Press each key in a number"""
        # TODO: Allow leading zeros
        for char in str(number):
            actions.key(char)
