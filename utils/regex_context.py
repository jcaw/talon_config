"""Context that allows for regex matching."""


import re

from talon.voice import Context


def _matches(regex, string):
    """Does a property of the current window match the specification?"""
    if regex:
        return isinstance(string, str) and regex.search(string)
    else:
        # If there's no target specified, it always matches.
        return True


def RegexContext(name, exe=None, title=None, func=None):
    """Create a context that matches on regexes (using `re.search`).

    Separate properties are ANDed.

    """
    exe_regex = exe and re.compile(exe)
    title_regex = title and re.compile(title)

    def _func_matches(app, win):
        """Does `func` match?"""
        if func:
            return func(app, win)
        else:
            return True

    def _regex_context_match(app, win):
        nonlocal _func_matches, exe_regex, title_regex
        return (
            _matches(exe_regex, app.exe)
            and _matches(title_regex, win.title)
            and _func_matches(app, win)
        )

    return Context(name, func=_regex_context_match)
