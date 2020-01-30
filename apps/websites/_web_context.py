import re

from user.utils.regex_context import RegexContext

# HACK: This entire thing is a really gross hack. Probably fragile.


class Browser(object):
    def __init__(self, exe_regex, title_suffix):
        self.exe_regex = re.compile(exe_regex)
        self.title_suffix = title_suffix

    def matches(self, exe, title, website_title_regex):
        if exe and title:
            exe_matches = self.exe_regex.search(exe)
            # Trim off the browser branding, then compare.
            trimmed_title = title.replace(self.title_suffix, "").strip()
            title_matches = re.search(website_title_regex, trimmed_title)
            return exe_matches and title_matches
        else:
            return False


_FIREFOX = Browser(r"firefox\.exe$", "- Mozilla Firefox")
# Edge reports super weird exe and title
_EDGE = Browser(r"ApplicationFrameHost\.exe$", "â€Ž- Microsoft Edge")
# FIXME: Doesn't work in Chrome. Talon reports it as cmd.exe (??)
_CHROME = Browser(r"chrome\.exe$", "- Google Chrome")

BROWSERS = [_FIREFOX, _EDGE, _CHROME]


# TODO: This just uses a dumb heuristic atm, long-term we want to extract the
#   url to inspect directly.
def WebContext(name, title_regex):
    # TODO: How to do this? regexp?
    def matches(app, win):
        global BROWSERS
        nonlocal title_regex
        for browser in BROWSERS:
            if browser.matches(app.exe, win.title, title_regex):
                return True
        return False

    return RegexContext(name, func=matches)
