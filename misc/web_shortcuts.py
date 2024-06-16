"""Web actions that can be invoked outside the browser."""

import urllib
import webbrowser
from typing import Dict, Optional

from talon import Module, actions


module = Module()

module.list(
    "subsearch_site", desc="Websites that can be subsearched on google with a command"
)
module.list("quick_site", desc="Quick names for easy-access websites")


@module.action_class
class Actions:
    def open_website(url: str) -> None:
        """Navigate to a website in the default browser."""
        # HACK: If a URL doesn't open with an explicit HTTP protocol
        #   declaration, Windows will always open it in Edge, so add one
        lower_url = url.lower()
        if not (lower_url.startswith("http://") or lower_url.startswith("https://")):
            url = f"https://{url}"

        # TODO: Determine default browser with method from following link:
        #   https://stackoverflow.com/a/68292700
        #   Then, focus it after browsing.
        print("Browser: ", webbrowser.get(using=None))
        webbrowser.open(url, new=2, autoraise=True)

    def open_website_with_params(base_url: str, params: Dict[str, str]):
        """Encode ``params``, attach them to ``base_url`` and open in the browser.

        ``base_url`` should be a clean base url with no parameters.

        """
        encoded_params = urllib.parse.urlencode(params)
        # TODO:
        actions.self.open_website(f"{base_url}?{encoded_params}")

    def web_search(text: str) -> None:
        """Search the default search engine for some ``text``."""
        # Default to Google, the user can override this if they need to.
        actions.self.google_search(text)

    def google_search(text: str) -> None:
        """Search Google for some ``text``."""
        actions.self.open_website_with_params("https://google.com/search", {"q": text})

    def duckduckgo_search(text: str) -> None:
        """Search DuckDuckGo for some ``text``."""
        actions.self.open_website_with_params("https://duckduckgo.com/", {"q": text})

    def bing_search(text: str) -> None:
        """Search Bing for some ``text``."""
        actions.self.open_website_with_params("https://bing.com/search", {"q": text})

    def amazon_search(text: str) -> None:
        """Search Amazon for some ``text``."""
        # TODO: Generic link that points to local amazon
        actions.self.open_website_with_params("https://www.amazon.co.uk/s", {"k": text})

    def youtube_search(text: str) -> None:
        """Search YouTube for some ``text``."""
        actions.self.open_website_with_params(
            "https://www.youtube.com/results", {"search_query": text}
        )

    def wikipedia_search(text: str) -> None:
        """Search Wikipedia for some ``text``."""
        actions.self.open_website_with_params(
            "https://en.wikipedia.org/wiki/Special:Search", {"search": text}
        )

    def reddit_search(text: str) -> None:
        """Search Reddit for some ``text``"""
        actions.self.web_search(text + "    site:reddit.com")

    def stackoverflow_search(text: str) -> None:
        """Search StackOverflow (and StackExchange) for ``text``"""
        actions.self.google_search(
            text + "    site:stackoverflow.com OR site:stackexchange.com"
        )

    def letterboxd_search(text: str) -> None:
        """Search Letterboxd for ``text``"""
        actions.self.open_website(
            "https://letterboxd.com/search/{}".format(urllib.parse.quote(text))
        )

    def google_subsearch(site: str, text: str) -> None:
        """Google search, restricting results to a specific website."""
        actions.self.google_search(text + f"    site:{site}")

    def search_that_dwim(text: Optional[str] = None):
        """Search current thing with the default search engine,

        DWIM behaviour depends on context (usually, highlighted text). Provide a
        string to override, and search `text` instead.

        """
        actions.self.web_search(actions.user.get_that_dwim_plus_text(text))

    def google_that_dwim(text: Optional[str] = None):
        """Google current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.google_search(actions.user.get_that_dwim_plus_text(text))

    def bing_that_dwim(text: Optional[str] = None):
        """Search Bing for current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.bing_search(actions.user.get_that_dwim_plus_text(text))

    # TODO: All duckduckgo actions should have underscores e.g. duck_duck_go
    def duck_duck_go_that_dwim(text: Optional[str] = None):
        """Seach Duck Duck Go for the current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.bing_search(actions.user.get_that_dwim_plus_text(text))

    def amazon_that_dwim(text: Optional[str] = None):
        """Search Amazon for current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.amazon_search(actions.user.get_that_dwim_plus_text(text))

    def youtube_that_dwim(text: Optional[str] = None):
        """Search Youtube for current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.youtube_search(actions.user.get_that_dwim_plus_text(text))

    def reddit_that_dwim(text: Optional[str] = None):
        """Search Reddit for current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.reddit_search(actions.user.get_that_dwim_plus_text(text))

    def stackoverflow_that_dwim(text: Optional[str] = None):
        """Search Stack Overflow for current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.stackoverflow_search(actions.user.get_that_dwim_plus_text(text))

    def wikipedia_that_dwim(text: Optional[str] = None):
        """Search Wikipedia for current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.wikipedia_search(actions.user.get_that_dwim_plus_text(text))

    def google_subsearch_that_dwim(subsearch_site: str, text: Optional[str] = None):
        """Search Bing for current "thing" - depends on context (usually, highlighted text).

        Provide a string to override the dwim behaviour, and search `text` instead.

        """
        actions.self.google_subsearch(
            subsearch_site, actions.user.get_that_dwim_plus_text(text)
        )
