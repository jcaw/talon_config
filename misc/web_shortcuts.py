"""Web actions that can be invoked outside the browser."""

import urllib
import webbrowser

from talon import Module, actions


module = Module()


def standard_search(base_search_url: str, params: Dict[str, str]):
    """Perform a search on an arbitrary website using common URL structure.

    Encodes ``params`` and attaches them to ``base_search_url``. May not be
    compatible with all websites' search procedures.

    """
    encoded_params = urllib.parse.urlencode(params)
    actions.self.open_website(f"{base_search_url}?{encoded_params}")


@module.action_class
class Actions:
    def open_website(url: str) -> None:
        """Navigate to a website in the default browser."""
        webbrowser.open(url, new=2, autoraise=True)

    def web_search(text: str) -> None:
        """Search the default search engine for some ``text``."""
        # Default to Google, the user can override this if they need to.
        actions.self.google_search(text)

    def google_search(text: str) -> None:
        """Search Google for some ``text``."""
        standard_search("https://google.com/search", {"q": text})

    def duckduckgo_search(text: str) -> None:
        """Search DuckDuckGo for some ``text``."""
        standard_search("https://duckduckgo.com/", {"q": text})

    def bing_search(text: str) -> None:
        """Search Bing for some ``text``."""
        standard_search("https://bing.com/search", {"q": text})

    def amazon_search(text: str) -> None:
        """Search Amazon for some ``text``."""
        # TODO: Generic link that points to local amazon
        standard_search("https://www.amazon.co.uk/s", {"k": text})

    def youtube_search(text: str) -> None:
        """Search YouTube for some ``text``."""
        standard_search("https://www.youtube.com/results", {"search_query": text})

    def wikipedia_search(text: str) -> None:
        """Search Wikipedia for some ``text``."""
        standard_search(
            "https://en.wikipedia.org/wiki/Special:Search", {"search": text}
        )
