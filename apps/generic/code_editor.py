from talon import Module, Context


module = Module()
# HACK: Can't figure out OR syntax for context matching, this is an alternative
module.apps.code_editor = "app: jetbrains"
module.apps.code_editor = "tag: user.emacs"


@module.action_class
class ModuleActions:
    def find_definition() -> None:
        """Navigate to the definition of the symbol under point."""

    def find_implementations() -> None:
        """Find implementations of the symbol under point."""

    def find_references() -> None:
        """Find references to the symbol under point."""

    def show_documentation() -> None:
        """Show documentation for the symbol under point."""
