import logging

from talon import Module, Context, actions, noise

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


module = Module()


@module.action_class
class Actions:
    def on_pop():
        """Will be called on a pop."""
        LOGGER.debug(f"Default `on_pop`")

    # TODO: How to handle contexts switching in the middle of a hiss, and never
    #   closing? Maybe track open hisses?
    def on_hiss(start: bool):
        """Will be called on a hiss (at the start + end)."""
        LOGGER.debug(f"Default `on_hiss`, start={start}")


default_noise_context = Context()


def _on_pop(start: bool):
    if not start:
        actions.self.on_pop()


noise.register("pop", _on_pop)
noise.register("hiss", actions.self.on_hiss)
