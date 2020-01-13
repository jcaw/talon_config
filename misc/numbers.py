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


numbers_context = Context("numbers")
numbers_context.set_list("digits", DIGITS.keys())
