from typing import List, Callable

from talon import Module, actions

from user.utils.formatting import preserve_punctuation


module = Module()


class BasePart(object):
    def __init__(self, item):
        self.item = str(item)

    def __str__(self):
        return self.item


class PhrasePart(BasePart):
    """Holds a spoken phrase component."""


class CharacterPart(BasePart):
    """Holds a spoken character or series of characters."""


class KeypressPart(BasePart):
    """Holds a keypress that must be pressed as a key."""


class FormattedPhrase(object):
    """Holds a formatted phrase."""

    def __init__(
        self,
        formatters: List[Callable],
        # TODO: Call this something other than phrase
        phrase_components=List[BasePart],
    ):
        self.formatters = formatters
        self.phrase_components = phrase_components


# TODO: Work out which options we need to cover
@module.capture(rule="<user.character>")
def phrase_character(m) -> CharacterPart:
    return CharacterPart(m.character)


@module.capture(rule="<user.special>")
def phrase_keypress(m) -> KeypressPart:
    return KeypressPart(" ".join(m))


@module.capture(rule="<user.dictation>")
def phrase_dictation(m) -> PhrasePart:
    return PhrasePart(m.dictation)


@module.capture(
    rule="(<user.phrase_dictation> | <user.phrase_character> | <user.phrase_keypress>)+"
)
def mixed_phrase(m) -> List[BasePart]:
    return list(m)


# TODO: Explain the need for strict phrase
@module.capture(rule="<user.phrase_dictation> [<user.mixed_phrase>]")
def mixed_phrase_strict(m) -> List[BasePart]:
    if hasattr(m, "mixed_phrase"):
        return [m.phrase_dictation, *m.mixed_phrase]
    else:
        return [m.phrase_dictation]


# TODO: Simple keys, enter, page up, page down, etc?


@module.capture(rule="<user.formatters> <user.mixed_phrase_strict>")
def formatted_phrase(m) -> FormattedPhrase:
    return FormattedPhrase(m.formatters, m.mixed_phrase_strict)


@module.action_class
class Actions:
    def insert_formatted_phrase(
        formatters: List[Callable], components: List[BasePart]
    ) -> None:
        """TODO"""
        for component in components:
            if isinstance(component, PhrasePart):
                actions.user.insert_formatted(component, formatters)
            elif isinstance(component, CharacterPart):
                # TODO: This is a dodgy structure. Maybe refactor formatters
                #   from the ground up?
                if preserve_punctuation(formatters):
                    # Format contextually if the formatter preserves
                    # punctuation.
                    actions.user.insert_formatted(component, formatters)
                else:
                    # When punctuation would be stripped, insert it literally.
                    actions.insert(component)
            elif isinstance(component, KeypressPart):
                actions.key(str(component))
            else:
                raise ValueError(f"Unrecognised text type, {type(component)}.")

    def insert_formatted_phrases(formatted_phrases: List[FormattedPhrase]) -> None:
        """TODO"""
        for phrase in formatted_phrases:
            actions.self.insert_formatted_phrase(
                phrase.formatters, phrase.phrase_components
            )
