"""For controlling media. Change volume, skip tracks, etc."""

import math

from talon.voice import Context, Key

from .vocab import NEXT, PREVIOUS
from user.misc.numbers import numeric, pass_number
from user.utils import ON_WINDOWS

context = Context("media_keys")


def hacky_set_volume_windows(percent):
    """Set the volume to a specific percentage using media keys.

    Windows should adjust the volume in increments of two - we rely on that.

    """
    assert 0 <= percent <= 100
    repeats = math.ceil(float(percent) / 2)
    # Normalize the volume to zero.
    for i in range(50):
        Key("voldown")(None)
    # Now set it to the target.
    for i in range(repeats):
        Key("volup")(None)


def not_implemented(percent):
    raise NotImplementedError("Not implemented on this platform.")


# HACK: Use heuristics until Talon has a formal API for setting the volume.
# Platform-dependent implementation.
if ON_WINDOWS:
    set_volume = hacky_set_volume_windows
else:
    set_volume = not_implemented


context.keymap(
    {
        "volume up": Key("volup"),
        "volume down": Key("voldown"),
        "volume (mute | unmute)": Key("mute"),
        "play track": Key("play"),
        "pause track": Key("pause"),
        "stop track": Key("stop"),
        NEXT + " track": Key("next"),
        PREVIOUS + " track": Key("prev"),
        numeric("[set] volume"): pass_number(set_volume),
    }
)
