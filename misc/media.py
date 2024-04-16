from talon import Module, actions, cron

key = actions.key


module = Module()


@module.action_class
class Actions:
    def set_volume(percent: int) -> None:
        """Set the volume to a specific percentage value."""


def bind():
    try:
        play_pause = (lambda: key("play_pause"), "Play/Pause")
        actions.user.vimfinity_bind_keys(
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
            }
        )
    except KeyError:
        print("Failed to register media key sequences. Retrying in 1s.")
        cron.after("1s", bind)


cron.after("50ms", bind)
