"""Web actions that can be invoked outside the browser."""

import urllib
import webbrowser
from typing import Dict

from talon import Module, actions, Context


module = Module()
context = Context()

module.list(
    "subsearch_site", desc="Websites that can be subsearched on google with a command"
)
context.lists["user.subsearch_site"] = {
    "papers": "paperswithcode.com",
    "papers with code": "paperswithcode.com",
}

module.list("quick_site", desc="Quick names for easy-access websites")
context.lists["user.quick_site"] = {
    "whatsapp": "web.whatsapp.com",
    "twitter": "twitter.com",
    "google": "google.com",
    "amazon": "amazon.com",
    "github": "github.com",
    "jist": "gist.github.com",
    "youtube": "youtube.com",
    "history": "youtube.com/feed/history",
    "discord": "discord.com/channels/@me",
}


@module.action_class
class Actions:
    def open_website(url: str) -> None:
        """Navigate to a website in the default browser."""
        # HACK: If a URL doesn't open with an explicit HTTP protocol
        #   declaration, Windows will always open it in Edge, so add one
        lower_url = url.lower()
        if not (lower_url.startswith("http://") or lower_url.startswith("https://")):
            url = f"https://{url}"
        print(f'Opening URL: "{url}"')
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
