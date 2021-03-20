import re
from typing import Optional, Callable, List


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


# All formatting functions must conform to this type signature.
FORMATTING_FUNC_TYPE = Callable[[str, Optional[SurroundingText]], ComplexInsert]


_RE_ALL_ALPHANUMERIC = re.compile(r"^[a-zA-Z0-9]+$")
_RE_ALL_WHITESPACE = re.compile(r"^[ \n\t\r]+$")
_RE_PUNCTUATION = re.compile(r"[^a-zA-Z0-9]")
_RE_NUMERIC = re.compile(r"^[0-9]+$")
_RE_ALPHA = re.compile(r"^[a-zA-Z]+$")
_RE_MANY_SPACES = re.compile(r"\ +")


# TODO: Extract generic string methods?
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


_RE_FIRST_LETTER = re.compile("[a-zA-Z]")


def capitalize(string):
    match = _RE_FIRST_LETTER.search(string)
    if match:
        m = match.start()
        return string[:m] + string[m].upper() + string[m+1:]
    else:
        return string


def uncapitalize(string):
    match = _RE_FIRST_LETTER.search(string)
    if match:
        m = match.start()
        return string[:m] + string[m].lower() + string[m+1:]
    else:
        return string


# Lots of punctuation could come before speech close. If the speech mark is
# joined to something, assume it's the end.
_RE_CLOSING_SPEECH = re.compile(r"[^ \t\n\r\"'][\"'`]+\Z")
# Different approach to starts because speech marks can have punctuation
# immediately after close. However, openings will probably not have punctuation
# at the start - it'll be an alphanumeric char (normally a letter).
#
# Note single apostrophes are ignored, because they could be part of a
# contraction.
_RE_OPENING_SPEECH = re.compile(r"^\"[\"']*[a-zA-Z0-9]")
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
    solid_before = _RE_SOLID_BEFORE.search(before) or _RE_CLOSING_SPEECH.search(before)
    # TODO: I don't think `match` should work here, but it does seem to. Figure
    #   out if `search` is needed.
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


# TODO: Rename this to "separated" or something
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


def apply_programming_keywords(
    text: str, surrounding_text: Optional[SurroundingText] = None
) -> ComplexInsert:
    """Insert language keywords, like "if", "return", "public static void".

    Text is inserted lowercase, with padding spaces in most contexts. The
    purpose is to reduce the amount of spacing that needs to be done manually.

    """
    text = text.lower()
    space_before = surrounding_text and re.search(
        r"[^ \t\n([{<]\Z", surrounding_text.text_before
    )
    if space_before:
        text = " " + text
    # We always want a space at the end, so variable/function names can be
    # inserted easily. For example (pipe is cursor):
    #
    #   "keyword static int camel my variable" -> "static int myVariable|"
    text += " "
    return ComplexInsert(text)


def apply_euler_function_call(
    text: str, surrounding_text: Optional[SurroundingText] = None
) -> ComplexInsert:
    # We don't want the vanilla `text_after` but we do want the text before, so
    # allow it to be generated then discard it.
    complex = apply_snake(text, surrounding_text)

    if (
        surrounding_text
        and is_alphanumeric(surrounding_text.char_after)
        or surrounding_text.char_after == "_"
    ):
        complex.text_after = ") "
    else:
        complex.text_after = ")"
    complex.insert += "("
    return complex


def apply_elisp_private(
    text: str, surrounding_text: Optional[SurroundingText] = None
) -> ComplexInsert:
    complex = apply_spine(text, surrounding_text)
    # Note this can do two quite different things:
    #
    # "this-is-a-var"  -> "this--is-a-var"
    #
    # "-this-is-a-var" -> "--this-is-a-var"
    #
    # Both are desirable. It's up to the user to use spine if they want to
    # extend an existing private var.
    complex.insert = complex.insert.replace("-", "--", 1)
    return complex


def _lisp_pad_after(surrounding_text):
    """Helper for lisps that determines whether trailing padding is needed."""
    return surrounding_text and surrounding_text.char_after not in [
        *")]}\n\r\t ",
        "",
        None,
    ]


def _lisp_pad_before(surrounding_text):
    """Helper for lisps that determines whether leading padding is needed."""
    return not (
        surrounding_text and surrounding_text.char_before in [*"([{@,\n\r\t ", "", None]
    )


def apply_lisp_function_call(
    text: str, surrounding_text: Optional[SurroundingText] = None
) -> ComplexInsert:
    # TODO: Nicer apply spaced.

    # Note we explicitly ignore the surrounding text.
    complex = apply_spine(text, surrounding_text=None)

    # Does it need a space before?
    if _lisp_pad_before(surrounding_text):
        prefix = " ("
    else:
        prefix = "("
    complex.insert = prefix + complex.insert

    # Does it need a space after?
    if _lisp_pad_after(surrounding_text):
        complex.text_after = ") "
    else:
        complex.text_after = ")"
    return complex


def apply_lisp_keyword(
    text: str, surrounding_text: Optional[SurroundingText] = None
) -> ComplexInsert:
    complex = add_prefix(":", apply_spine)(text, surrounding_text)
    # We can space the leader on keyword args automatically
    if _lisp_pad_before(surrounding_text):
        complex.insert = " " + complex.insert
    return complex


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
_RE_LOWERCASE_LETTER = re.compile(r"[a-z]")


def _is_new_sentence(text_before: str) -> bool:
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
    if words:
        words[0] = capitalize(words[0])
    return _language_spaced(words, surrounding_text)


def apply_speech(text, surrounding_text=None):
    """Format `text` as a capitalized quotation wrapped in speech marks."""
    # Fixme: doesn't capitalize.
    words = text.split(" ")
    if words:
        words[0] = '"' + capitalize(words[0])
    insert = _language_spaced(words, surrounding_text)
    insert.text_after = '"' + insert.text_after
    return insert


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


def add_prefix(prefix: str, formatting_func: FORMATTING_FUNC_TYPE):
    """Create a function that adds a prefix, then applies ``formatting_func``."""

    # TODO: A prefix here probably implies we always want this to be a new
    #   object, so add a leading space when necessary. Or at least expose that
    #   option.

    def apply_formatting(
        text: str, surrounding_text: Optional[SurroundingText] = None
    ) -> ComplexInsert:
        """Apply prefix, then the formatter."""
        nonlocal prefix, formatting_func
        text = prefix + text
        return formatting_func(text, surrounding_text)

    return apply_formatting


_KEEP_PUNCTUATION = [
    apply_title,
    apply_sentence,
    apply_capitalized_sentence,
    apply_lowercase,
    apply_uppercase,
]


def preserve_punctuation(formatters):
    """Do all these ``formatters`` want punctuation preserved?"""
    for formatter in formatters:
        if formatter not in _KEEP_PUNCTUATION:
            return False
    return True


def _chain_formatters(
    text: str,
    formatters: List[FORMATTING_FUNC_TYPE],
    surrounding_text: SurroundingText = None,
):
    if not formatters:
        raise ValueError("Must provide at least 1 formatter.")
    # There's no consistent way to combine complex inserts, so we convert all
    # but the last into text.
    for formatter in formatters[:-1]:
        complex_insert = formatter(text, surrounding_text)
        text = complex_insert.insert + complex_insert.text_after
    return formatters[-1](text, surrounding_text)


def formatter_chain(*formatters: List[FORMATTING_FUNC_TYPE]) -> FORMATTING_FUNC_TYPE:
    """Create a formatter than chains a list of multiple other formatters."""

    def apply_chain(text: str, surrounding_text: Optional[ComplexInsert] = None):
        nonlocal formatters
        return _chain_formatters(text, formatters, surrounding_text)

    return apply_chain


def single_spaces(text: str):
    """Convert multiple spaces to single spaces in ``text``."""
    return _RE_MANY_SPACES.sub(" ", text)


def _separate_punctuation(text: str):
    """Separate ``text`` into a list of words and punctuation."""
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


def is_alpha(text: str):
    """Is ``text`` solely composed of alphabetical characters?"""
    return _RE_ALPHA.match(text)


def is_numeric(text: str):
    """Is ``text`` solely composed of numeric characters?"""
    return _RE_NUMERIC.match(text)


def _split_word(word: str) -> str:
    """Split a word into component camel/studley components.

    E.g: thisIsATest -> this Is A Test

    This method assumes `word` is entirely alphanumeric.

    """
    # TODO: Cope with non-alphanumeric
    result = ""
    last_char = ""
    has_lowercase = _RE_LOWERCASE_LETTER.search(word)
    for char in word:
        start_of_number = is_alpha(last_char) and is_numeric(char)
        end_of_number = is_numeric(last_char) and is_alpha(char)
        # A capital letter means a new word, unless the entire symbol is
        # uppercase. Numbers are also their own "word".
        if (has_lowercase and char.isupper()) or start_of_number or end_of_number:
            # This will miss the first letter of the first word. That's good -
            # we don't want to pad the front.
            result += " "
        result += char
        last_char = char
    return result.strip()


def separate_words(text) -> str:
    """Separate ``text`` into a string of its constituent words.

    E.g:

        thisIsATest -> this Is A Test
        This, is a sentence. -> This, is a sentence.

    """
    # Separate off each word, *then* split each word into component words.
    result = ""
    for component in _separate_punctuation(text):
        if is_alphanumeric(component):
            result += _split_word(component)
        else:
            result += component
    return result


def _strip_formatting(text: str) -> str:
    return (
        single_spaces(_RE_PUNCTUATION.sub(" ", text.replace("'", ""))).lower().strip()
    )


def format_text(
    text: str,
    formatters: List[FORMATTING_FUNC_TYPE],
    surrounding_text: SurroundingText = None,
) -> ComplexInsert:
    # TODO: Some way to force capitalization for natural language, e.g. if
    #   we're at the start of a comment
    if not preserve_punctuation(formatters):
        text = _strip_formatting(text)
    return _chain_formatters(text, formatters, surrounding_text)


def reformat_text(
    text: str,
    formatters: List[FORMATTING_FUNC_TYPE],
    surrounding_text: SurroundingText = None,
) -> ComplexInsert:
    return format_text(separate_words(text), formatters, surrounding_text)
