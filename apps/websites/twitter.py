from user.misc.vocab import NEXT, PREVIOUS
from ._web_context import WebContext


context = WebContext("twitter", r" / Twitter$")


context.keymap(
    {
        f"{NEXT} [tweet]": "j",
        f"{PREVIOUS} [tweet]": "k",
        "like [tweet]": "l",
        "reply [to tweet]": "r",
        "favorite": "f",
        "retweet": "t",
        "mute account": "u",
        "block account": "b",
        "[tweet] details": "enter",
        "(open | expand) [photo]": "o",
        "search": "/",
        "go home": "g h",
        "moments": "g o",
        "notifications": "g n",
        "mentions": "g r",
        "likes": "g l",
        "lists": "g i",
        "[direct] messages": "g m",
        "settings": "g s",
        "search profile": "g u",
        "help | shortcuts": "?",
    }
)
