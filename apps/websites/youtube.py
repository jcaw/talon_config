from talon.voice import Key

from user.misc.vocab import NEXT, PREVIOUS, VIDEO, SUBTITLES
from ._web_context import WebContext


# When watching videos, YouTube appends " - YouTube". This will probably be
# active elsewhere too - that's fine.
context = WebContext("youtube", r" \- YouTube$")


def reset_video_speed(m):
    for i in range(7):
        Key("<")(None)
    for i in range(3):
        Key(">")(None)


def max_video_speed(m):
    # Reset first in case the user has an addon that increases max speed.
    reset_video_speed(None)
    for i in range(4):
        Key(">")(None)


context.keymap(
    {
        f"play [{VIDEO}]": Key("k"),
        f"pause [{VIDEO}]": Key("k"),
        "speed up": Key(">"),
        "(speed | slow) down": Key("<"),
        "(max speed | speed max)": max_video_speed,
        "(reset speed | speed reset)": reset_video_speed,
        f"{SUBTITLES}": Key("c"),
        f"{SUBTITLES} size up": Key("+"),
        f"{SUBTITLES} size down": Key("-"),
        f"{VIDEO} volume up": Key("up"),
        f"{VIDEO} volume down": Key("down"),
        f"{NEXT} {VIDEO}": Key("shift-n"),
        f"{PREVIOUS} {VIDEO}": Key("shift-p"),
        "search box": Key("/"),
        "fullscreen": Key("f"),
        f"mute {VIDEO}": Key("m"),
        "theater [mode]": Key("t"),
        "mini player [mode] | pop out": Key("i"),
    }
)
