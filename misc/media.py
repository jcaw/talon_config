from talon import Module, actions, cron
from user.plugins.vimfinity.vimfinity import vimfinity_bind_keys

key = actions.key
set_volume = actions.self.set_volume

module = Module()


@module.action_class
class Actions:
    def set_volume(percent: int) -> None:
        """Set the volume to a specific percentage value."""


play_pause = (lambda: key("play_pause"), "Play/Pause")
vimfinity_bind_keys(
    {
        "x": "Media",
        "x p": (lambda: key("volup"), "Volume Up"),
        "x p": (lambda: key("voldown"), "Volume Down"),
        "x m": (lambda: key("mute"), "Volume Mute"),
        "x p": play_pause,
        # TODO: Pure play button - but it doesn't work to control Firefox.
        "x s": (lambda: key("stop"), "Stop"),
        "x ]": (lambda: key("next"), "Next Track"),
        "x [": (lambda: key("prev"), "Previous Track"),
        # Also bind pause to space for max convenience.
        "x space": play_pause,
        # This matches the keychron
        # "f8": play_pause,
        "x v": "Volume",
        "x v `": (lambda: set_volume(0), "0%"),
        "x v 0": (lambda: set_volume(0), "0%"),
        "x v 1": (lambda: set_volume(10), "10%"),
        "x v 2": (lambda: set_volume(20), "20%"),
        "x v 3": (lambda: set_volume(30), "30%"),
        "x v 4": (lambda: set_volume(40), "40%"),
        "x v 5": (lambda: set_volume(50), "50%"),
        "x v 6": (lambda: set_volume(60), "60%"),
        "x v 7": (lambda: set_volume(70), "70%"),
        "x v 8": (lambda: set_volume(80), "80%"),
        "x v 9": (lambda: set_volume(90), "90%"),
        "x v =": (lambda: set_volume(100), "100%"),
    }
)
