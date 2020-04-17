import re


class SurroundingText:
    def __init__(self, text_before=None, text_after=None):
        self.text_before = text_before
        self.text_after = text_after

    @property
    def char_before(self):
        return self.text_before[-1] if self.text_before else None

    @property
    def char_after(self):
        return self.text_after[0] if self.text_after else None


class ComplexInsert:
    def __init__(self, insert, text_after=""):
        self.insert = insert
        self.text_after = text_after


_RE_ALL_ALPHANUMERIC = re.compile(r"^[a-zA-Z0-9]+$")
_RE_ALL_WHITESPACE = re.compile(r"^[ \n\t\r]+$")
_RE_PUNCTUATION = re.compile(r"[^a-zA-Z0-9]")
_RE_NUMERIC = re.compile(r"^[0-9]+$")
_RE_ALPHA = re.compile(r"^[a-zA-Z]+$")
_RE_MANY_SPACES = re.compile(r"\ +")


# TODO: Extract generic string methods
def is_alphanumeric(string):
    """Is `string` alphanumeric?"""
    if string:
        return _RE_ALL_ALPHANUMERIC.match(string)
    else:
        return False


def is_whitespace(string):
    """Is `string` just whitespace?"""
    if string:
        return _RE_ALL_WHITESPACE.match(string)
    else:
        return False


def capitalize(string):
    if len(string) >= 1:
        return string[0].upper() + string[1:]
    else:
        return string


def uncapitalize(string):
    if len(string) >= 1:
        return string[0].lower() + string[1:]
    else:
        return string


# Lots of punctuation could come before speech close. If the speech mark is
# joined to something, assume it's the end.
_RE_CLOSING_SPEECH = re.compile(r"[^ \t\n\r][\"']$")
# Different approach to starts because speech marks can have punctuation
# immediately after close. However, openings will probably not have punctuation
# at the start - it'll be an alphanumeric char (normally a letter).
_RE_OPENING_SPEECH = re.compile(r"^\"[a-zA-Z0-9]")
# Some information* being written
#
# *A footnote about the word "information"
_RE_ASTERISK_FOOTNOTE = re.compile(r"[\n\r][ \t]*\*+[ \t]?$")
# See `_should_space` for how these are used.
# TODO: why does the \Z anchor work here but $ doesn't? Switch all to \Z?
_RE_SOLID_BEFORE = re.compile(r"[^ \t\n\r\(\{\[\<\£\$\€\@\-\_\\\/\`\'\"]\Z")
_RE_SOLID_AFTER = re.compile(r"^[^ \t\n\r\,\.\!\?\…\;\:\@\*\%\'\"\/\\\)\}\]\>\-\_]")


def _should_space(before, after):
    """Should we insert a space between ``before`` and ``after``?

    Assumes natural language formatting. This is just a heuristic - it will get
    it wrong sometimes.

    """
    # We classify some characters as "solid" - these can have a space after.
    solid_before = (
        _RE_SOLID_BEFORE.search(before)
        # Asterisk-denoted footnotes are an edge case.
        and not _RE_ASTERISK_FOOTNOTE.match(before)
    ) or _RE_CLOSING_SPEECH.match(before)
    solid_after = _RE_SOLID_AFTER.match(after) or _RE_OPENING_SPEECH.match(after)
    return solid_before and solid_after


def _language_spaced(words, surrounding_text=None):
    text = " ".join(words)
    if text and surrounding_text:
        prefix = " " if _should_space(surrounding_text.text_before, text) else ""
        suffix = " " if _should_space(text, surrounding_text.text_after) else ""
    else:
        prefix, suffix = "", ""
    return ComplexInsert(insert=prefix + text, text_after=suffix)


def _delimiter_spaced(delimiter, text, surrounding_text=None):
    """Create a complex insert using `delimiter` as the separator."""
    # TODO: Test this, particularly empty string
    #
    # TODO: Have this cope with delimiters len > 1 (currently, won't extend
    #   partial delimiters)
    pad_start = (
        (len(text) == 0 or is_alphanumeric(text[0]))
        and surrounding_text
        and is_alphanumeric(surrounding_text.char_before)
    )
    pad_end = (
        (len(text) == 0 or is_alphanumeric(text[-1]))
        and surrounding_text
        and is_alphanumeric(surrounding_text.char_after)
    )
    prefix = delimiter if pad_start else ""
    suffix = delimiter if pad_end else ""
    center = delimiter.join(text.split(" "))
    return ComplexInsert(insert=prefix + center, text_after=suffix)


def apply_camel_case(text, surrounding_text=None):
    words = text.lower().split(" ")
    if len(words) >= 1:
        if surrounding_text and is_alphanumeric(surrounding_text.char_before):
            words[0] = capitalize(words[0])
        else:
            words[0] = uncapitalize(words[0])
    for i, word in enumerate(words[1:]):
        words[i + 1] = capitalize(word)
    # TODO: Allow camelling the middle of a word?
    #   e.g:
    #   "so|me" -> "soCamelInsertMe" (note the M near the end)
    return ComplexInsert("".join(words))


def apply_studley_case(text, surrounding_text=None):
    words = text.lower().split(" ")
    studley_words = map(capitalize, words)
    return ComplexInsert("".join(studley_words))


def apply_snake(text, surrounding_text=None):
    return _delimiter_spaced("_", text, surrounding_text)


def apply_spine(text, surrounding_text=None):
    return _delimiter_spaced("-", text, surrounding_text)


def apply_dotword(text, surrounding_text=None):
    return _delimiter_spaced(".", text, surrounding_text)


def make_apply_delimiter(delimiter):
    """Make a function that applies arbitrary delimiter spacing to the text."""

    def do_apply_delimiter(text, surrounding_text=None):
        nonlocal delimiter
        return _delimiter_spaced(delimiter, text, surrounding_text)

    return do_apply_delimiter


def apply_dunder(text, surrounding_text=None):
    if surrounding_text and is_alphanumeric(surrounding_text.char_before):
        prefix = "_"
    elif surrounding_text and "_" == surrounding_text.char_before:
        prefix = ""
    else:
        prefix = "__"
    center = "_".join(text.split(" "))
    if surrounding_text and is_alphanumeric(surrounding_text.char_after):
        inner_suffix = ""
        outer_suffix = "_"
    elif surrounding_text and "_" == surrounding_text.char_after:
        inner_suffix = ""
        outer_suffix = ""
    else:
        inner_suffix = "__"
        outer_suffix = ""
    return ComplexInsert(insert=prefix + center + inner_suffix, text_after=outer_suffix)


# Words to keep lowercase in titles. Very rough heuristic, add more as needed.
LOWERCASE_TITLE_WORDS = [
    # Keep these sorted alphabetically.
    "a",
    "an",
    "and",
    "as",
    "at",
    "but",
    "by",
    "for",
    "from",
    "in",
    "is",
    "nor",
    "of",
    "on",
    "or",
    "the",
    "to",
    "up",
    "with",
]


def _format_title_word(word):
    return uncapitalize(word) if word in LOWERCASE_TITLE_WORDS else capitalize(word)


# Matches if we're following a sentence termination, i.e. if we need to start a
# new sentence. Match on preceding text.
#
# Prior prefix: [a-zA-Z0-9][^ \t\r\n]*
#
# TODO: How to handle terminations within parens? e.g: "(something.) |"
_RE_SENTENCE_TERMINATOR = re.compile(r"[\.\…\!\?]+[^a-zA-Z0-9]*$")
_RE_START_OF_DOCUMENT = re.compile(r"^[ \n\t\r]*$")
_RE_START_OF_TODO = re.compile(r"((TODO)|(FIXME)|(HACK))[-: \t]*$")
_RE_DOUBLE_NEWLINE = re.compile(r"\n[ \r\t]*\n[ \r\t]*$")


def _is_new_sentence(text_before):
    """Given `text_before`, are we at the start of a new sentence?"""
    # TODO: Benchmark higher limit
    return (
        _RE_SENTENCE_TERMINATOR.search(text_before)
        or _RE_START_OF_DOCUMENT.match(text_before)
        # E.g in org mode:
        #   * TODO |
        # Emacs Lisp:
        #   ;; TODO: |
        or _RE_START_OF_TODO.search(text_before)
        # Double newline implies new paragraph.
        or _RE_DOUBLE_NEWLINE.search(text_before)
    )


def apply_title(text, surrounding_text=None):
    words = text.split(" ")
    title_words = [_format_title_word(word) for word in words]
    # First word in a new title should always be capitalized.
    if (
        len(title_words) >= 1
        # If there's no context, we have to guess. Assume we're continuing,
        # since the kinds of words that are lowercase will start titles
        # less often.
        and surrounding_text
        and _is_new_sentence(surrounding_text.text_before)
    ):
        title_words[0] = capitalize(title_words[0])
    return _language_spaced(title_words, surrounding_text)


def apply_sentence(text, surrounding_text=None):
    # TODO: Ideally we'd just pass this through a dedicated grammar formatter.
    words = text.split(" ")
    # New sentences should be capitalized.
    if (
        len(words) >= 1
        # When there's no context, we can't tell - so we never capitalize. The
        # user has to explicitly ask for it.
        and surrounding_text
        and _is_new_sentence(surrounding_text.text_before)
    ):
        words[0] = capitalize(words[0])
    return _language_spaced(words, surrounding_text)


def apply_capitalized_sentence(text, surrounding_text=None):
    words = text.split(" ")
    if len(words) >= 1:
        words[0] = capitalize(words[0])
    return _language_spaced(words, surrounding_text)


def apply_squash(text, surrounding_text=None):
    return ComplexInsert("".join(text.split(" ")))


def apply_lowercase(text, surrounding_text=None):
    return ComplexInsert(text.lower())


def apply_uppercase(text, surrounding_text=None):
    return ComplexInsert(text.upper())


def apply_spaced(text, surrounding_text=None):
    prefix = "" if is_whitespace(surrounding_text.char_before) else " "
    suffix = " " if is_whitespace(surrounding_text.char_after) else " "
    return ComplexInsert(prefix + text + suffix)


_KEEP_PUNCTUATION = [
    apply_title,
    apply_sentence,
    apply_capitalized_sentence,
    apply_lowercase,
    apply_uppercase,
]


def _preserve_punctuation(formatters):
    """Do all these ``formatters`` want punctuation preserved?"""
    for formatter in formatters:
        if formatter not in _KEEP_PUNCTUATION:
            return False
    return True


def _chain_formatters(text, formatters, surrounding_text=None):
    if not formatters:
        raise ValueError("Must provide at least 1 formatter.")
    # There's no consistent way to combine complex inserts, so we convert all
    # but the last into text.
    for formatter in formatters[:-1]:
        complex_insert = formatter(text, surrounding_text)
        text = complex_insert.insert + complex_insert.text_after
    return formatters[-1](text, surrounding_text)


def single_spaces(text):
    return _RE_MANY_SPACES.sub(" ", text)


def _separate_punctuation(text):
    components = []
    last_char = ""
    for char in text:
        start_of_punctuation = is_alphanumeric(last_char) and not is_alphanumeric(char)
        start_of_word = not is_alphanumeric(last_char) and is_alphanumeric(char)
        is_transition = start_of_punctuation or start_of_word or not last_char
        if is_transition:
            # Start a new word
            components.append("")
        components[-1] += char
        last_char = char
    return components


def is_alpha(text):
    return _RE_ALPHA.match(text)


def is_numeric(text):
    return _RE_NUMERIC.match(text)


def _split_word(word):
    """Split a word into component camel/studley components.

    This method assumes `word` is entirely alphanumeric.

    """
    result = ""
    last_char = ""
    for char in word:
        start_of_number = is_alpha(last_char) and is_numeric(char)
        end_of_number = is_numeric(last_char) and is_alpha(char)
        if char.isupper() or start_of_number or end_of_number:
            # This will miss the first letter of the first word. That's good -
            # we don't want to pad the front.
            result += " "
        result += char
        last_char = char
    return result.strip()


def _separate_words(text):
    # Separate off each word, *then* split each word into component words.
    result = ""
    for component in _separate_punctuation(text):
        if is_alphanumeric(component):
            result += _split_word(component)
        else:
            result += component
    return result


def _strip_formatting(text):
    return (
        single_spaces(_RE_PUNCTUATION.sub(" ", text.replace("'", ""))).lower().strip()
    )


def format_text(text, formatters, surrounding_text=None):
    # TODO: Some way to force capitalization for natural language, e.g. if
    #   we're at the start of a comment
    if not _preserve_punctuation(formatters):
        text = _strip_formatting(text)
    return _chain_formatters(text, formatters, surrounding_text)


def reformat_text(text, formatters, surrounding_text=None):
    return format_text(_separate_words(text), formatters, surrounding_text)
