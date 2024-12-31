# TODO: Figure out noises with Talon's built-in noise actions

# import logging

# from talon import Module, Context, actions, noise, settings, cron

# from user.utils import sound

# LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.INFO)


# module = Module()


# module.setting(
#     "hiss_start_deadzone",
#     type=int,
#     default=0,
#     desc="hisses will not be registered until they exceed this length (in ms)",
# )


# @module.action_class
# class Actions:
#     def on_pop():
#         """Will be called on a pop."""
#         LOGGER.debug(f"Default `on_pop`")

#     # TODO: How to handle contexts switching in the middle of a hiss, and never
#     #   closing? Maybe track open hisses?
#     def on_hiss(start: bool):
#         """Will be called on a hiss (at the start + end)."""
#         LOGGER.debug(f"Default `on_hiss`, start={start}")


# default_noise_context = Context()


# def _on_pop(start: bool):
#     if not start:
#         actions.self.on_pop()


# # Cron job to add leading deadzone to the hiss action.
# _hiss_start_job = None


# def _cued_start_hiss():
#     """Start hiss handler, with an audio cue."""
#     sound.play(sound.WOOD_HIT)
#     actions.self.on_hiss(True)


# def _on_hiss(start: bool):
#     global _hiss_start_job
#     if start:
#         start_deadzone = settings["user.hiss_start_deadzone"]
#         if start_deadzone:
#             _hiss_start_job = cron.after(f"{start_deadzone}ms", _cued_start_hiss)
#         else:
#             actions.self.on_hiss(True)
#     else:
#         if _hiss_start_job:
#             cron.cancel(_hiss_start_job)
#         actions.self.on_hiss(False)


# noise.register("pop", _on_pop)
# noise.register("hiss", _on_hiss)
