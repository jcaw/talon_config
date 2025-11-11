"""Module for smart navigation. Finding definitions, references, docs, etc.

"""


from talon import Module


module = Module()


@module.action_class
class ModuleActions:
    def find_definition_other_window() -> None:
        """Find definition of symbol under point, in the other window."""

    def find_implementations_other_window() -> None:
        """Find implementations of symbol under point, in the other window."""

    def find_references_other_window() -> None:
        """Find references of symbol under point, in the other window."""
