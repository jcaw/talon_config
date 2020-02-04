from talon.voice import Key

from user.misc.vocab import NEXT, PREVIOUS, VIDEO, SUBTITLES
from ._web_context import WebContext


# When watching videos, YouTube appends " - YouTube". This will probably be
# active elsewhere too - that's fine.
#
# HACK: Talon can't seem to get the title when YouTube is fullscreen - it's
#   just empty. Activate with all empty firefox titles.
context = WebContext("youtube", r"( \- YouTube$)|(^$)")


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
        f"play [{VIDEO}]": "k",
        f"pause [{VIDEO}]": "k",
        "speed up": ">",
        "(speed | slow) down": "<",
        "(max speed | speed max)": max_video_speed,
        "(reset speed | speed reset)": reset_video_speed,
        f"{SUBTITLES}": "c",
        f"{SUBTITLES} size up": "+",
        f"{SUBTITLES} size down": "-",
        f"{VIDEO} volume up": Key("up"),
        f"{VIDEO} volume down": Key("down"),
        f"{NEXT} {VIDEO}": Key("shift-n"),
        f"{PREVIOUS} {VIDEO}": Key("shift-p"),
        "search box": "/",
        "fullscreen": "f",
        f"mute {VIDEO}": "m",
        "theater [mode]": "t",
        "mini player [mode] | pop out": "i",
    }
)
