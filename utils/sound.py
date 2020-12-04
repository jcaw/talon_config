import os
import logging
from talon import Module

from ._wav import load_wav, play_wav


LOGGER = logging.getLogger(__name__)


_sounds = "user/assets/sounds"

BELL = f"{_sounds}/bike_bell_low.wav"
BELL_HIGH = f"{_sounds}/bike_bell_high.wav"
ERROR = f"{_sounds}/error.wav"
FAILURE = f"{_sounds}/failure.wav"
GLASS_TAP = f"{_sounds}/glass_tap.wav"
TAP = f"{_sounds}/tap.wav"
THUNK = f"{_sounds}/thunk.wav"
WOOD_HIT = f"{_sounds}/wood_hit.wav"

# Cache all the sound effects up-front to avoid a pause on first play.
for path in [BELL, BELL_HIGH, ERROR, FAILURE, GLASS_TAP, TAP, THUNK, WOOD_HIT]:
    try:
        load_wav(path)
    except Exception:
        pass


def play(path, ignore_missing_file=True):
    """Play a sound.

    :param bool ignore_missing_file: Optional. Catch error if the sound file is
      missing. Default is True.

    """
    if not path.lower().endswith("wav"):
        raise RuntimeError("Can only play wav files.")

    if os.path.isfile(path):
        play_wav(path)
    elif ignore_missing_file:
        LOGGER.error(f'`safe_play_sound`: file not found: "{path}".')
    else:
        raise IOError(f'Could not find sound file: "{path}"')


# Some convenience methods to abstract the specific sound choice and make
# the soundscape more consistent.
def play_ding(**kwargs):
    """Play a pleasant confirmation ding."""
    play(BELL, **kwargs)


def play_cancel(**kwargs):
    """Play a gentle cancellation sound."""
    play(FAILURE, **kwargs)


# TODO: Refactor whole module into actions, use strings to reference sounds
module = Module()


@module.action_class
class Actions:
    def play_thunk():
        """Play a thunk sound."""
        play(THUNK)

    def play_glass_tap():
        """Play a glass tap sound."""
        play(GLASS_TAP)

    def play_ding():
        """Play a confirmation ding."""
        play(BELL)

    def play_cancel():
        """Play a cancellation sound."""
        play(FAILURE)

    def play_tap():
        """Play a tap sound."""
        play(TAP)

    def play_bell_high():
        """Play a high bell sound (higher than ding)."""
        play(BELL_HIGH)
