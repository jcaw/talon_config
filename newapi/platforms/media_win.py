import math

from talon import Context, actions

context = Context()


@context.action_class("user.newapi.media")
class Actions:
    def set_volume(percent: int) -> None:
        """Set the volume to a specific percentage using media keys.

        Windows should adjust the volume in increments of two - we rely on that.

        """
        # HACK: Hacky heuristic. Will lower the volume first.
        assert 0 <= percent <= 100
        repeats = math.ceil(float(percent) / 2)
        # Normalize the volume to zero.
        for i in range(50):
            actions.key("voldown")
        # Now set it to the target.
        for i in range(repeats):
            actions.key("volup")
