from talon import Module

module = Module()


@module.action_class
class Actions:
    def set_volume(percent: int) -> None:
        """Set the volume to a specific percentage value."""
