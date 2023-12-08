"""Allows accented letters to be inserted via key sequences, with visual hints."""

from unicodedata import normalize
from functools import partial

from talon import cron, actions, clip


ACCENT_SECTION_KEY = "a"

accents_mapping = {
    "'": "\u0301",  # Acute
    "`": "\u0300",  # Grave
    "^": "\u0302",  # Circumflex (caret)
    "c": "\u0327",  # Cedilla
    "~": "\u0303",  # Tilde
    "s": "\u0336",  # Streg
    "e": "\u1DD9",  # Eth
    "b": "\u030A",  # Bolle
    "m": "\u0304",  # Macron
    "h": "\u030C",  # Hacek
    "u": "\u0306",  # Crescent/Breve
    ".": "\u0307",  # Dot
}
# TODO: Special cases for ae and oe ligatures?


def insert_accented(accented_text):
    clip.set_text(accented_text)
    actions.sleep("100ms")
    actions.edit.paste()


def bind():
    keymap = {ACCENT_SECTION_KEY: "Accented Letters"}
    for letter in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        # Each letter needs a section
        keymap[f"{ACCENT_SECTION_KEY} {letter}"] = letter
        for accent_key, combination_code in accents_mapping.items():
            accented_letter = normalize("NFC", letter + combination_code)
            # If it's a valid accented character, it should have a length of 1.
            # Invalid chars will have a length of 2.
            if len(accented_letter) == 1:

                keymap[f"{ACCENT_SECTION_KEY} {letter} {accent_key}"] = (
                    partial(insert_accented, accented_letter),
                    accented_letter,
                )

    try:
        actions.user.vimfinity_bind_keys(keymap)
    except KeyError:
        print("Failed to register accent key sequence. Retrying in 1s.")
        cron.after("1s", bind)


cron.after("50ms", bind)
