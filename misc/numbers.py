from talon.voice import Context


DIGITS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}
REVERSE_DIGITS = {numeral: spoken for spoken, numeral in DIGITS.items()}


def number_from_digits(m):
    """Extract an integer from a command with digits.

    The assumption is the digits were gathered with:

       "{numbers.digits}++"

    """
    global DIGITS
    # Future-proof against merged digits? E.g. ["one two", "three"]
    try:
        messy_digits = m["numbers.digits"]
    except KeyError:
        return None
    number = ""
    for maybe_many in messy_digits:
        for english_digit in maybe_many.split():
            number += DIGITS[english_digit]
    return int(number)


def spoken_forms(number):
    """Get a list of all valid methods of saying a ``number``.

    >>> spoken_forms(5)
    ["five"]
    >>> spoken_forms(13)
    ["one three"]

    """
    global REVERSE_DIGITS
    # TODO: Integrate actual spoken numbers, e.g. "twenty one"
    words = [REVERSE_DIGITS[digit] for digit in str(number)]
    digit_form = " ".join(words)
    return [digit_form]


def extract_number(m):
    # TODO: Add other number forms as well as digits
    return number_from_digits(m)


def pass_number(function, invert=False):
    """Create a command that intercepts `m` and passes a number to `function`."""

    def do_function(m):
        nonlocal function, invert
        number = extract_number(m)
        if invert:
            number *= -1
        return function(number)

    return do_function


def numeric(command, optional=False):
    """Make a command numeric - have it take number as its suffix.

    Use the function `extract_number` to extract the number from `m`.

    For example:

        numeric("go to line")

    Would allow the user to speak:

        "go to line 5"
        "go to line 20"

    :param bool optional: Optional. Make the number optional (allow the command
      to be spoken without a number too). Default is False

    """
    assert isinstance(command, str), type(command)
    if optional:
        suffix = "[{numbers.digits}++]"
    else:
        suffix = "{numbers.digits}++"
    return command + " " + suffix


numbers_context = Context("numbers")
# NOTE: Always use this greedily if it's at the end of a command, or it will
# conflict with repeats.
numbers_context.set_list("digits", DIGITS.keys())
