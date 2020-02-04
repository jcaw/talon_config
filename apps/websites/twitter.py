from talon.voice import Key

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
        "[tweet] details": Key("enter"),
        "(open | expand) [photo]": "o",
        "search": "/",
        "go home": "gh",
        "moments": "go",
        "notifications": "gn",
        "mentions": "gr",
        "likes": "gl",
        "lists": "gi",
        "[direct] messages": "gm",
        "settings": "gs",
        "search profile": "gu",
        "help | shortcuts": "?",
    }
)
