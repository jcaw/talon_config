from talon import Context, Module, speech_system, actions

speech = actions.speech

module = Module()


@module.action_class
class Actions:
    def sleep():
        """Sleep speech recognition."""
        speech.disable()

    def noisy_sleep():
        """Sleep speech recognition and play a sound."""
        actions.self.sleep()
        actions.user.play_thunk()

    def wake():
        """Wake speech recognition."""
        speech.enable()

    def engine_mimic(phrase: str):
        """Force the engine to mimic a phrase"""
        speech_system.engine_mimic(phrase)


dragon_context = Context("user.dragon_context")
dragon_context.matches = r"""
tag: user.dragon
"""


@dragon_context.action_class("self")
class DragonActions:
    def sleep():
        speech_system.engine_mimic("go to sleep")
