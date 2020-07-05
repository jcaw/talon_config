"""Captures & actions that aren't in a dedicated module yet."""

from talon import Module, Context, actions


module = Module()


@module.action_class
class ModuleActions:
    def open_file() -> None:
        """Bring up a dialogue to open a file."""

    def next_error() -> None:
        """Go to the next error."""

    def previous_error() -> None:
        """Go to the previous error."""


global_context = Context()


@global_context.action_class
class GlobalActions:
    pass
